"""Tool layer: declare Python functions as tools the model can call.

A "tool" is really three thiings:
    1. a JSON schema (name + description + parameters) — sent to the model so it
     knows the tool exists and what args it takes;
  2. the actual Python callable we execute when the model asks for it;
  3. a registry that maps name -> (schema, callable).

The @tool decorator builds (1) automatically from type hints + docstring.
"""


import inspect
import dataclasses
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, get_type_hints
# Python type -> JSON schema type
_TYPE_MAP = {
    int: "integer",
    float: "number",
    str: "string",
    bool: "boolean",
}


class ToolError(Exception):
    """Raised when a tool call cannot be executed (unknown name, bad args)."""

@dataclass
class Tool:
    name: str
    description: str
    parameters: Dict[str, Any]  # a JSON-schema object
    fn: Callable[..., Any]

    def to_schema(self) -> dict:
        """The exact shape Ollama expects inside the `tools` list."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def names(self) -> List[str]:
        return list(self._tools)

    def schemas(self) -> List[dict]:
        """List of tool schema dicts, ready to pass to client.chat(tools=...)."""
        return [t.to_schema() for t in self._tools.values()]

    def call(self, name: str, **kwargs: Any) -> str:
        """Execute a tool by name and return its result as a string.

        Returning a string keeps the wire format simple: a `tool` message's
        `content` is always text.
        """
        if name not in self._tools:
            raise ToolError(f"Unknown tool: {name!r}. Available: {self.names()}")
        try:
            result = self._tools[name].fn(**kwargs)
        except TypeError as e:  # wrong/missing args
            raise ToolError(f"Bad arguments for {name!r}: {e}") from e
        if isinstance(result, str):
            return result
        return json.dumps(result)

def _schema_from_fn(fn: Callable) -> Dict[str, Any]:
    """Build a JSON-schema `parameters` object from a function's type hints."""
    hints = get_type_hints(fn)
    sig = inspect.signature(fn)

    properties: Dict[str, Any] = {}
    required: List[str] = []
    for param_name, param in sig.parameters.items():
        ptype = hints.get(param_name, str)  # default to string if unannotated
        properties[param_name] = {"type": _TYPE_MAP.get(ptype, "string")}
        if param.default is inspect.Parameter.empty:
            required.append(param_name)

    schema: Dict[str, Any] = {
        "type": "object",
        "properties": properties,
    }
    if required:
        schema["required"] = required
    return schema


def tool(fn: Callable[..., Any]) -> Callable:
    """Decorator: register `fn` as a Tool and stash the Tool on the function.

    Usage:
        @tool
        def get_weather(city: str) -> str:
            'Get current weather for a city.'
            return "11 celsius"

        registry = ToolRegistry()
        registry.register(get_weather.__tool__)
    """
    t = Tool(
        name=fn.__name__,
        description=(inspect.getdoc(fn) or "No description.").strip().splitlines()[0],
        parameters=_schema_from_fn(fn),
        fn=fn,
    )
    fn.__tool__ = t  # type: ignore[attr-defined]
    return fn
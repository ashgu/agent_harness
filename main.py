#!/usr/bin/env python3
"""Stage 1: single-shot chat with Ollama. No tools yet."""

import argparse
from harness import Config, OllamaClient, ToolRegistry
from examples.toy_tools import get_weather, get_current_time, compare_temps

def build_registry() -> ToolRegistry:
    reg = ToolRegistry()
    for f in (get_weather, get_current_time, compare_temps):
        reg.register(f.__tool__)
    return reg

def step1():
    p = argparse.ArgumentParser(description="Agent harness - Stage 1")
    p.add_argument("--say", required=True, help="Prompt to send")
    p.add_argument("--model", help="Override model")
    p.add_argument("--base-url", help="Override base URL")
    args = p.parse_args()

    cfg = Config.from_env()
    if args.model:
        cfg.model = args.model
    if args.base_url:
        cfg.base_url = args.base_url

    client = OllamaClient(cfg)
    msg = client.chat([{"role": "user", "content": args.say}])
    print(msg.get("content", ""))


def main():
    p = argparse.ArgumentParser(description="Agent harness - Stage 2")
    p.add_argument("--task", required=True, help="What to ask the agent")
    p.add_argument("--model", help="Override model")
    args = p.parse_args()

    cfg = Config.from_env()
    if args.model:
        cfg.model = args.model

    client = OllamaClient(cfg)
    tools = build_registry()

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use tools when they help."},
        {"role": "user", "content": args.task},
    ]

    # --- turn 1: ask the model ------------------------------------------
    resp = client.chat(messages, tools=tools.schemas())
    print("\n[turn 1] model response:")
    print(resp)

    if not resp.get("tool_calls"):
        # model answered directly — no tool needed
        print("\n[final] " + resp.get("content", ""))
        return

    # --- we execute the tool call ourselves -----------------------------
    call = resp["tool_calls"][0]["function"]
    name = call["name"]
    args_ = call.get("arguments", {})
    print(f"\n[tool] calling {name!r} with {args_}")

    # append the assistant's tool-call intent to the conversation...
    messages.append({"role": "assistant", "content": "", "tool_calls": resp["tool_calls"]})

    # ...run it...
    result = tools.call(name, **args_)
    print(f"[tool] result: {result}")

    # ...and feed the result back as a `tool` message.
    messages.append({"role": "tool", "content": result, "tool_name": name})

    # --- turn 2: let the model form the final answer ---------------------
    final = client.chat(messages, tools=tools.schemas())
    print("\n[turn 2] model response:")
    print(final)
    print("\n[final] " + final.get("content", ""))

if __name__ == "__main__":
    main()

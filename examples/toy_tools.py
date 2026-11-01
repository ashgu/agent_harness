"""Deterministic fake tools — no network, so the agent loop is fully testable."""
from harness.tools import tool

_FAKE_WEATHER = {
    "tokyo": 11, "paris": 7, "london": 9, "nyc": 15,
    "new york": 15, "berlin": 5, "sydney": 22,
}


@tool
def get_weather(city: str) -> str:
    "Get the current temperature (celsius) for a city. Only a few cities are known."
    c = city.strip().lower()
    if c in _FAKE_WEATHER:
        return f"{_FAKE_WEATHER[c]} celsius"
    return "no data for that city"


@tool
def get_current_time() -> str:
    "Return a fixed mock timestamp. Deterministic on purpose."
    return "12:00 UTC"


@tool
def compare_temps(a: int, b: int) -> str:
    "Compare two temperatures in celsius and report the difference."
    diff = abs(a - b)
    warmer = "first" if a > b else ("second" if b > a else "equal")
    return f"the {warmer} is warmer by {diff} celsius"
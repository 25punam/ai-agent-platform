import inspect
from typing import get_type_hints

_registry = {}

PYTHON_TO_JSON = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


# ─────────────────────────────
# REGISTER TOOL DECORATOR
# ─────────────────────────────
def register_tool(fn):
    hints = get_type_hints(fn)
    sig = inspect.signature(fn)

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        py_type = hints.get(name, str)
        properties[name] = {
            "type": PYTHON_TO_JSON.get(py_type, "string")
        }

        if param.default is inspect.Parameter.empty:
            required.append(name)

    _registry[fn.__name__] = {
        "fn": fn,
        "description": fn.__doc__ or "",
        "schema": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }

    return fn


# ─────────────────────────────
# GET SCHEMAS FOR CLAUDE
# ─────────────────────────────
def get_tool_schemas_for(tool_names=None):
    tools = []

    for name, meta in _registry.items():
        if tool_names and name not in tool_names:
            continue

        tools.append({
            "name": name,
            "description": meta["description"],
            "input_schema": meta["schema"]
        })

    return tools


# ─────────────────────────────
# EXECUTE TOOL (REAL WORK)
# ─────────────────────────────
def call_tool(name: str, inputs: dict):
    if name not in _registry:
        raise Exception(f"Tool {name} not found")

    return _registry[name]["fn"](**inputs)
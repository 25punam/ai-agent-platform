from tools.registry import get_all_tool_schemas, call_tool

def get_tools_for_agent(agent):
    tool_names = list(agent.tools.values_list("name", flat=True))
    return get_all_tool_schemas()
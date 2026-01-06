import datetime
from google.adk.tools import ToolContext


async def modelling_orch_tool(
    question: str,
    tool_context: ToolContext,
):
    print("initializing state variables...")
    tool_context.state["hitl_feedback"] = ""
    tool_context.state["data_model"] = None
    tool_context.state["entity_data_model"] = None
    tool_context.state["conceptual_data_model"] = None
    tool_context.state["logical_data_model"] = None
    tool_context.state["physical_data_model"] = None
    return

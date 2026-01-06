from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from google.adk.models.llm_response import LlmResponse
from .const import DDL_TASK, PDM_TASK, LDM_TASK, CONCEPTUAL_MODEL_TASK, config

import datetime
from pathlib import Path
from .utils import del_dir, save_artifacts
from google.adk.tools import google_search
from google.adk.tools import VertexAiSearchTool
from google.adk.agents import Agent, ParallelAgent
import os


async def modelling_orch_tool(
    question: str,
    tool_context: ToolContext,
):
    # from .agent import model_agent_seq

    print("Executing set_current_task()")
    tool_output = {}
    state = tool_context.state
    conceptual_folder_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    tool_context.state["hitl_feedback"] = ""
    tool_context.state["data_model"] = None
    tool_context.state["entity_data_model"] = None
    tool_context.state["conceptual_data_model"] = None
    tool_context.state["logical_data_model"] = None
    tool_context.state["physical_data_model"] = None
    # modeller_tool = AgentTool(agent=conceptual_model_agent)
    # modeller_agent_output = await modeller_tool.run_async(
    #     args={"request": ""},tool_context=tool_context
    # )
    return

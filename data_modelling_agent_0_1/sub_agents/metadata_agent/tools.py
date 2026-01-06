from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from pathlib import Path
from data_modelling_agent.sub_agents.metadata_agent.agent import metadata_agent
from .utils import store_extracted_metadata, check_if_exists, read_from_gcs
from .const import GCS_BUCKET_NAME, GCS_PREFIX, folder_name, file_name
from google.adk.tools import ToolContext


async def call_metadata_tool(tool_context: ToolContext, query: str):
    """Tool to invoke the metadata_agent to extract metadata from provided source data model"""

    full_folder_path = folder_name
    if not check_if_exists(full_folder_path, file_name):
        print("invoking metadata_agent..")
        Path(full_folder_path).mkdir()
        """Tool to call source search agent."""
        agent_tool = AgentTool(agent=metadata_agent)

        metadata_agent_output = await agent_tool.run_async(
            args={"request": query}, tool_context=tool_context
        )
        print("in call_metadata_tool 3")
        print(f"metadata_agent_output: {metadata_agent_output}")
        tool_context.state["extracted_metadata"] = metadata_agent_output
        print("in call_metadata_tool 4")
        gcs_uri = store_extracted_metadata(full_folder_path, metadata_agent_output)
        print("in call_metadata_tool 5")
        return
    else:
        print("metadata was already extracted! Loading... ")
        tool_context.state["extracted_metadata"] = read_from_gcs(
            full_folder_path, file_name
        )
        return

from google.adk.agents import Agent
from datetime import datetime
from typing import Any, Dict, Optional
from google.adk.tools.base_tool import BaseTool  # Required for type hinting in callback
from google.adk.tools.tool_context import ToolContext
from .utils.commons import get_metadata_from_gcs
from .tools import generate_data


def before_tool_callback_user_input(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
    tool_name = tool.name
    print(f"\n[BEFORE TOOL] Calling '{tool_name}' with original args: {args}")

    project_id = args.get("project_id")
    dataset_id = args.get("dataset_id")
    gcs_folder = args.get("gcs_folder")

    project_id = "development-000"
    dataset_id = "prayas_test"
    gcs_folder = "20250807102755"

    tool_context.state["project_id"] = project_id
    tool_context.state["dataset_id"] = dataset_id
    metadata = tool_context.state.get("metadata")

    if not metadata:
        if not gcs_folder:
            print(
                "[BEFORE MOCK METADATA EXECUTION] METADATA is missing. Blocking call."
            )
            return {"result": "Enter the gcs_folder where the metadata is stored."}
    metadata = get_metadata_from_gcs(gcs_folder)
    tool_context.state["metadata"] = metadata

    if (not project_id) and (not dataset_id):
        print(
            "[BEFORE MOCK METADATA EXECUTION] Project ID or Data Set ID is missing. Blocking call."
        )
        return {"result": "Project ID and Data Set ID are required"}

    if not project_id:
        print("[BEFORE MOCK METADATA EXECUTION] Project ID is missing. Blocking call.")
        return {"result": "Project ID is required"}

    if not dataset_id:
        print("[BEFORE MOCK METADATA EXECUTION] Data Set ID is missing. Blocking call.")
        return {"result": "Data Set ID is required"}
    print("\n")
    return None


synthetic_data_generator_agent = Agent(
    name="synthetic_data_generator_agent",
    model="gemini-2.5-flash",
    description="""Responsible to mock data/ generate synthetic data in target database like BigQuery.
    """,
    instruction="""You are an helpful assistant used to generate synthetic data in target database like BigQuery. The tables are already created in 
    target database. The metadata of the tables are available in session state. You must use the generate_data tool to generate synthetic data.
    """,
    tools=[
        generate_data,
    ],
    before_tool_callback=before_tool_callback_user_input,
)

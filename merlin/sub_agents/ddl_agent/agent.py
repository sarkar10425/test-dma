from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents import Agent
from .tools import ddl_execution
from typing import Any, Dict, Optional
from google.adk.tools.base_tool import BaseTool  # Required for type hinting in callback
from google.adk.tools.tool_context import ToolContext
from .utils.commons import get_ddl_from_gcs


#########callbacks##########


def before_tool_callback_user_input(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
    tool_name = tool.name
    print(f"\n[BEFORE TOOL] Calling '{tool_name}' with original args: {args}")

    dataset_to_be_deleted = args.get("dataset_to_be_deleted", False)
    tool_context.state["dataset_to_be_deleted"] = dataset_to_be_deleted

    dataset_id = args.get("dataset_id", None)
    if dataset_id:
        tool_context.state["dataset_id"] = dataset_id
    return None


ddl_agent = Agent(
    name="ddl_agent",
    model="gemini-2.5-flash",
    instruction="""You are a BigQuery DDL execution assistant. Your goal is to create tables by running pre-existing DDL statements.

**Your Task:**
1.  You must use the `ddl_execution` tool to create tables.
2.  The DDL statements are already available; you do not need to generate them.
3.  If the user is asked to provide the dataset_id, you must assign user response to the argument `dataset_id` .
4.  If user asked to delete the dataset, you must assign argument `dataset_to_be_deleted` to `True`.
""",
    description="You are an assistant who will create tables in target database like BigQuery.",
    output_key="ddl_agent_output",
    tools=[
        ddl_execution,
    ],
    before_tool_callback=before_tool_callback_user_input,
)

from google.adk.tools.tool_context import ToolContext
from google.genai import types
from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from .prompts import MERMAID_ERD_PROMPT

_memaid_erd_agent = Agent(
    model="gemini-2.5-flash",
    name="memaid_erd_agent",
    description="An agent which generates ER diagram in mermaid.",
    instruction=MERMAID_ERD_PROMPT,
    output_key="mermaid_erd_output"
)


async def generate_report_mermaid(
    tool_context: ToolContext,
):
    """Tool to call source search agent."""
    metadata = tool_context.state["metadata"]
    query = f"Generate ER diagram for the following DDLs: {metadata}"
    agent_tool = AgentTool(agent=_memaid_erd_agent)
    mermaid_erd_output = await agent_tool.run_async(
        args={"request": query}, tool_context=tool_context
    )
    await tool_context.save_artifact(
        "mermaid_erd_output.mmd",
        types.Part.from_bytes(
            data=mermaid_erd_output.encode("utf-8"), mime_type="text/vnd.mermaid"
        ),
    )
    return {
        "status": "success",
        "detail": "ER diagram generated successfully and stored in artifacts. This is a mermaid based ER diagram. Please use any mermaid viewer to view the diagram.",
        "filename": "mermaid_erd_output.mmd",
    }

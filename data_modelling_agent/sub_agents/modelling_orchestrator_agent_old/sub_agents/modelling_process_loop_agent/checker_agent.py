from google.adk.agents import Agent
import os

# from .prompt import CHECKER_PROMPT
# from .tools.loop_condition_tool import check_tool_condition
from google.adk.tools import ToolContext, FunctionTool


def check_state(tool_context: ToolContext):
    print("executing check_state()")
    if (
        tool_context.state["loop_exit_cue"] == 1
    ):  # if user satisfied, then exit the loop
        tool_context.actions.escalate = True
        print("Loop exited.")
        return {
            "status": "Exit condition met -> User satisfied with current model",
            "message": "Exiting Loop.",
        }
    return {
        "status": "User not satisfied with current model",
        "message": "Continuing Loop..",
    }


check_tool_condition = FunctionTool(func=check_state)

checker_agent_instance = Agent(
    name="checker_agent",
    model=os.getenv("GENAI_LLM_MODEL", "gemini-2.5-flash"),
    instruction="You are an intelligent assistant who invokes `check_tool_condition` tool",
    tools=[check_tool_condition],
)

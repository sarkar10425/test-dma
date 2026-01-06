from google.adk.tools import ToolContext


async def set_questionnaire_output(tool_context: ToolContext, query: str):
    """Tool to invoke the questionnaire_agent to get user responses for multiple questions provided as questionnaire"""

    print("setting questionnaire_agent response in state..")
    tool_context.state["questionnaire_responses"] = ""

    return

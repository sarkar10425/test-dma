from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

# from .agent import questionnaire_agent


# def display_questionnaire_tool(
#         callback_context: CallbackContext,
#         llm_response: LlmResponse
# )-> LlmResponse:
#     body_html = f"""
#             <!DOCTYPE html>
#             <html lang="en">
#             <head>
#             <meta charset="UTF-8">
#             <meta name="viewport" content="width=device-width, initial-scale=1.0">
#             <title>Assignment Review</title>
#             </head>
#             <body style="margin: 0; padding: 0; font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif; background-color: #f3f6fc;">
#             <p style="margin-bottom: 24px;">{questions.get("NFR", None).get(1, None)}</p>
#             </body>
# """
#     message = MIMEMultipart()
#     message.attach(MIMEText(body_html, "html"))

#     raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

#     return LlmResponse(
#                 content=types.Content(
#                     role="model",
#                     parts=[types.Part(text="Please provide answers for as much of these questions as you can \n" + raw_message)],
#                 )
#             )


async def set_questionnaire_output(tool_context: ToolContext, query: str):
    """Tool to invoke the questionnaire_agent to get user responses for multiple questions provided as questionnaire"""

    print("setting questionnaire_agent response in state..")
    # agent_tool = AgentTool(agent=questionnaire_agent)
    # questionnaire_agent_output = await agent_tool.run_async(
    #     args={"request": query}, tool_context=tool_context
    # )
    tool_context.state["questionnaire_responses"] = ""

    return

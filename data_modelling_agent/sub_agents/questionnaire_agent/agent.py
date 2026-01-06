from google.adk.agents import Agent
import os
from google.adk.tools import VertexAiSearchTool
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.genai import types
from .const import questions
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
from .tools import set_questionnaire_output


project_id = os.getenv("GOOGLE_CLOUD_PROJECT", None)
QUESTIONNAIRE_DATASTORE_ID_ONLY = os.getenv("QUESTIONNAIRE_DATASTORE_ID", None)
QUESTIONNAIRE_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{QUESTIONNAIRE_DATASTORE_ID_ONLY}"
questionnaire_tool = VertexAiSearchTool(data_store_id=QUESTIONNAIRE_DATASTORE_ID)
print(f"QUESTIONNAIRE_DATASTORE_ID: {QUESTIONNAIRE_DATASTORE_ID}")

# def display_questionnaire_tool(
#         callback_context: CallbackContext,
#         # llm_request: LlmRequest,
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
#     # return LlmResponse(
#     #             content=types.Content(
#     #                 role="model",
#     #                 parts=[types.Part(text=questions.get("NFR", None).get(1, None))],
#     #             )
#     #         )
#     return LlmResponse(
#                 content=types.Content(
#                     role="model",
#                     parts=[types.Part(inline_data=types.Blob(mime_type='text/html', data = body_html.encode('utf-8')))],
#                 )
#             )


questionnaire_agent = Agent(
    name="questionnaire_agent",
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-flash"),
    description="""Responsible retreive the user questions-answers from datastore""",
    instruction=f"""
      You are an helpful assistant who can retrieve for questions and their answers using VertexAISearchTool tool: 'questionnaire_tool'.
      **ALWAYS** use the VertexAISearchTool provided to you to retrieve inputs.
  
    **Guardrails**
    - Do not make up anything from your own knowledge.
    - Do not ask user to provide any answers or questions.
    - Do not ask any questions
    - Do not answer any questions.
    """,
    tools=[questionnaire_tool],
    # after_agent_callback = set_questionnaire_output,
    output_key="questionnaire_responses",
)

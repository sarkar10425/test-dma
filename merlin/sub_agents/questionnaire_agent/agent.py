from google.adk.agents import Agent
import os
from google.adk.tools import VertexAiSearchTool


project_id = os.getenv("GOOGLE_CLOUD_PROJECT", None)
QUESTIONNAIRE_DATASTORE_ID_ONLY = os.getenv("QUESTIONNAIRE_DATASTORE_ID", None)
QUESTIONNAIRE_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{QUESTIONNAIRE_DATASTORE_ID_ONLY}"
questionnaire_tool = VertexAiSearchTool(data_store_id=QUESTIONNAIRE_DATASTORE_ID)
print(f"QUESTIONNAIRE_DATASTORE_ID: {QUESTIONNAIRE_DATASTORE_ID}")

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
    output_key="questionnaire_responses",
)

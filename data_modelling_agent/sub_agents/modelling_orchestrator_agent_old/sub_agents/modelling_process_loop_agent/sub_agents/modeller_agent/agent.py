import os

# from google.adk.agents import Agent, ParallelAgent
# from google.adk.agents.callback_context import CallbackContext

# from .tools import fetch_extracted_metadata, bq_best_prac_tool, blueprint_tool, user_rules_datastore_tool, ddl_datastore_tool, hitl_loop_status, google_search_tool
# from sub_agents.questionnaire_agent.tools import call_questionnaire_tool
from .prompts import instructions_latest
from google.adk.agents import Agent
from .tools import user_feedback_sentiment_tool

# from google.adk.tools import google_search
# from google.adk import agents
# from google.adk.tools import VertexAiSearchTool
# from modelling_task_agent.const import CONCEPTUAL_MODEL_TASK
# from sub_agents.questionnaire_agent.agent import questionnaire_agent
from .tools import google_search_tool


# project_id=os.getenv("GOOGLE_CLOUD_PROJECT", None)
# BQ_BEST_PRACTICES_DATASTORE_ID=os.getenv("BQ_BEST_PRACTICES_DATASTORE_ID", None)
# BLUEPRINT_DATASTORE_ID_ONLY=os.getenv("BLUEPRINT_DATASTORE_ID", None)
# USER_RULES_DATASTORE_ONLY=os.getenv("USER_RULES_DATASTORE", None)
# DDL_DATASTORE_ONLY=os.getenv("DDLS_DATASTORE_ID", None)

# BQ_BEST_PRAC_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{BQ_BEST_PRACTICES_DATASTORE_ID}"
# BLUEPRINT_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{BLUEPRINT_DATASTORE_ID_ONLY}"
# USER_RULES_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{USER_RULES_DATASTORE_ONLY}"
# DDL_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{DDL_DATASTORE_ONLY}"


# bq_best_prac_tool = VertexAiSearchTool(data_store_id=BQ_BEST_PRAC_DATASTORE_ID)
# blueprint_tool = VertexAiSearchTool(data_store_id=BLUEPRINT_DATASTORE_ID)
# user_rules_datastore_tool = VertexAiSearchTool(data_store_id=USER_RULES_DATASTORE_ID)
# ddl_datastore_tool = VertexAiSearchTool(data_store_id=DDL_DATASTORE_ID)


# _search_agent = Agent(
#     model="gemini-2.5-flash",
#     name="google_search_tool",
#     description="An agent providing results for user queries using Google search",
#     instruction="You are a specialist in prov   iding information from Google Search. Use Google search to find the relevant information about the user provided error",
#     tools=[google_search],
# )

# _bq_best_prac_agent = Agent(
#     model="gemini-2.5-flash",
#     name="google_search_tool",
#     description="An agent providing BigQuery best practices to the further agents",
#     instruction="You are helpful assistant who invokes 'bq_best_prac_tool' tool",
#     tools=[bq_best_prac_tool],
# )

# _blueprint_agent = Agent(
#     model="gemini-2.5-flash",
#     name="google_search_tool",
#     description="An agent providing Industry Blueprints to the further agents",
#     instruction="You are helpful assistant who invokes 'blueprint_tool' tool",
#     tools=[blueprint_tool],
# )

# _user_rule_agent = Agent(
#     model="gemini-2.5-flash",
#     name="google_search_tool",
#     description="An agent providing BigQuery best practices to the further agents",
#     instruction="You are helpful assistant who invokes 'bq_best_prac_tool' tool",
#     tools=[user_rules_datastore_tool],
# )

# _ddl_agent = Agent(
#     model="gemini-2.5-flash",
#     name="google_search_tool",
#     description="An agent providing Industry Blueprints to the further agents",
#     instruction="You are helpful assistant who invokes 'blueprint_tool' tool",
#     tools=[ddl_datastore_tool],
# )


# def make_parallel_agents(
#         callback_context: CallbackContext,
#         # llm_response: LlmResponse
# )-> ParallelAgent:
#     parallel_agents = []
#     current_task = callback_context.state["current_task"]

#     if current_task == CONCEPTUAL_MODEL_TASK:
#         parallel_agents.append(_ddl_agent)
#         parallel_agents.append(_blueprint_agent)
#         parallel_agents.append(questionnaire_agent)
#     p_agent = ParallelAgent(
#         name="parallel_agent",
#         description="Generate multiple initial solutions for the given task in parallel.",
#         sub_agents=parallel_agents,
#         )
#     return p_agent


modeller_agent = Agent(
    name="modeller_agent",
    model="gemini-2.5-flash",
    instruction=instructions_latest,
    description="You are a helping assistant who will generate different types of models",
    # sub_agents = [parallel_agent],
    tools=[google_search_tool],
    output_key="data_model",
    before_agent_callback=user_feedback_sentiment_tool,
    after_agent_callback=user_feedback_sentiment_tool,
)

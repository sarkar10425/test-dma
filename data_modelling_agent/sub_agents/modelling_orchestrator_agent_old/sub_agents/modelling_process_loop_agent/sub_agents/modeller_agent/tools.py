import os

# from google.genai import types
from typing import Optional

# from google.adk.agents.llm_agent import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest

# from google.adk.tools import VertexAiSearchTool
from google.adk.tools import ToolContext
from google.adk.agents import Agent, ParallelAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import google_search
from google.genai import types
from typing import Optional

# from google.adk.tools import VertexAiSearchTool
# from .agent import modeller_agent
# from .const import config, DDL_TASK, BQ_METADATA_TASK, BQ_LOGICAL_MODEL_TASK, BASE_MODEL_TASK, LDM_TASK, PDM_TASK
# import datetime
# from pathlib import Path
# from modelling_orchestrator_agent.utils import del_dir, save_artifacts
# from data_modelling_agent.sub_agents.reporting_agent.utils.commons import cleanup_metadata
# from data_modelling_agent.sub_agents.reporting_agent.tools import generate_report
# from google.adk.tools.agent_tool import AgentTool
# from google.adk.tools import google_search
from google import genai
import os
from .const import CONCEPTUAL_MODEL_TASK, LDM_TASK, PDM_TASK

# from .tools import fetch_extracted_metadata, bq_best_prac_tool, blueprint_tool, user_rules_datastore_tool, ddl_datastore_tool, hitl_loop_status, google_search_tool
# from .tools import google_search_tool
# from data_modelling_agent.sub_agents.questionnaire_agent.agent import questionnaire_agent
# from .prompts import instructions_latest

# project_id=os.getenv("GOOGLE_CLOUD_PROJECT", None)
# BQ_BEST_PRACTICES_DATASTORE_ID_ONLY=os.getenv("BQ_BEST_PRACTICES_DATASTORE_ID", None)
# BLUEPRINT_DATASTORE_ID_ONLY=os.getenv("BLUEPRINT_DATASTORE_ID", None)
# USER_RULES_DATASTORE_ONLY=os.getenv("USER_RULES_DATASTORE_ID", None)
# DDL_DATASTORE_ONLY=os.getenv("DDLS_DATASTORE_ID", None)


# BQ_BEST_PRACTICES_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{BQ_BEST_PRACTICES_DATASTORE_ID_ONLY}"
# BLUEPRINT_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{BLUEPRINT_DATASTORE_ID_ONLY}"
# USER_RULES_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{USER_RULES_DATASTORE_ONLY}"
# DDL_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{DDL_DATASTORE_ONLY}"


# bq_best_prac_tool = VertexAiSearchTool(data_store_id=BQ_BEST_PRACTICES_DATASTORE_ID)
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
#     output_key = "bq_best_prac_output"
# )

# _blueprint_agent = Agent(
#     model="gemini-2.5-flash",
#     name="google_search_tool",
#     description="An agent providing Industry Blueprints to the further agents",
#     instruction="You are helpful assistant who invokes 'blueprint_tool' tool",
#     tools=[blueprint_tool],
#     output_key = "blueprint_output"
# )

# _user_rule_agent = Agent(
#     model="gemini-2.5-flash",
#     name="google_search_tool",
#     description="An agent providing BigQuery best practices to the further agents",
#     instruction="You are helpful assistant who invokes 'bq_best_prac_tool' tool",
#     tools=[user_rules_datastore_tool],
#     output_key = "user_rule_output"
# )

# _ddl_agent = Agent(
#     model="gemini-2.5-flash",
#     name="google_search_tool",
#     description="An agent providing Industry Blueprints to the further agents",
#     instruction="You are helpful assistant who invokes 'blueprint_tool' tool",
#     tools=[ddl_datastore_tool],
#     output_key = "ddl_output"
# )


_search_agent = Agent(
    model="gemini-2.5-flash",
    name="google_search_tool",
    description="An agent providing results for user queries using Google search",
    instruction="You are a specialist in providing information from Google Search. Use Google search to find the relevant information about the user provided error",
    tools=[google_search],
)


async def google_search_tool(query: str, tool_context: ToolContext):
    _google_search_tool = AgentTool(agent=_search_agent)
    _google_search_tool_output = await _google_search_tool.run_async(
        args={"request": query}, tool_context=tool_context
    )
    return _google_search_tool_output


def user_feedback_sentiment_tool(
    callback_context: CallbackContext,
    # tool_context: ToolContext,
    # llm_response: LlmResponse
):
    print("Executing user_feedback_sentiment_tool()")
    current_state = callback_context.state
    events = callback_context._invocation_context.session.events
    print(f"events: {events}")
    user_search_google_phrases = [
        "i am good",
        "confirm",
        "save",
        "finalize",
        "finalise",
    ]
    # logic to check sentiment of users response
    try:
        for ev in events:
            if ev.content:
                if ev.content.role:
                    if ev.content.role == "user":
                        for part in ev.content.parts:
                            for phrase in user_search_google_phrases:
                                if phrase in part.text:
                                    # logic to get user sentiment
                                    # TBA
                                    client = genai.Client()
                                    response = client.models.generate_content(
                                        model="gemini-2.5-flash",
                                        contents=f"""
                                                You are an intelligent assistant who can analyse user's text.
                                                You will be provided a user text
                                                If you find that the user is suggesting that they are satisfied by using any phrases from - {user_search_google_phrases}, then you **must** output 'True' as your output. You **must** not output anything else.
                                                If you find that the user is not suggesting by any means that they are satisfied, then you should output the **exact** User text
                                                User text:
                                                {part.text}
                                                """,
                                    )
                                    if (
                                        response.text == "True"
                                        or response.text == True
                                        or response.text == "true"
                                    ):
                                        current_state["loop_exit_cue"] = (
                                            1  # user satisfied
                                        )
                                        current_state["hitl_feedback"] = None
                                    else:
                                        current_state["loop_exit_cue"] = (
                                            0  # user not satisfied
                                        )
                                        current_state["hitl_feedback"] = part.text
    except Exception as e:
        print(f"Error: {e}")
    return
    # return LlmResponse(
    #                 content=types.Content(
    #                     role="model",
    #                     parts=[types.Part(text="")],
    #                 )
    #             )


# def fetch_extracted_metadata(
#   callback_context: CallbackContext
# ) -> LlmResponse:
#     print("Executing fetch_extracted_metadata()")
#     try:
#       state = callback_context.state
#       metadata = state.get("extracted_metadata", None)
#       agent_response_helper = "This is metadata that I will use to construct new data model for you: \n"
#       return LlmResponse(
#                   content=types.Content(
#                       role="model",
#                       parts=[types.Part(text=agent_response_helper+metadata)],
#                   )
#               )
#     except Exception as e:
#        return LlmResponse(
#                   content=types.Content(
#                       role="model",
#                       parts=[types.Part(text="Metadata not found! Continuing without metadata ... ")],
#                   )
#               )

# async def execute_parallel_agents(
#   callback_context: CallbackContext,
# ):
#     print("Executing execute_parallel_agents()")
#     task = callback_context.state["current_task"]
#     # callback_context.state["hitl_feedback"] = ""
#     # callback_context.state["questionnaire_responses"] = ""
#     print("Executing execute_parallel_agents(), here 1")
#     # parallel_agents = []
#     # if task == CONCEPTUAL_MODEL_TASK:
#     #     parallel_agents.append(_ddl_agent)
#     #     parallel_agents.append(_blueprint_agent)
#     #     parallel_agents.append(questionnaire_agent)
#     # if task == LDM_TASK:
#     #     # add more agents for parallel_agent here for LDM task
#     #     parallel_agents.append(_search_agent)
#     # if task == PDM_TASK:
#     #     # add more agents for parallel_agent here for PDM task
#     #     parallel_agents.append(_search_agent)

#     parallel_agent = ParallelAgent(
#         name="parallel_agent",
#         description="Generate multiple initial inputs by executing the paralle agents.",
#         sub_agents=parallel_agents,
#         )
#     # try:
#     #     agent_tool = AgentTool(agent=parallel_agent)
#     #     await agent_tool.run_async(
#     #         args={"request": ""},tool_context=callback_context
#     #     )
#     # except Exception as e:
#     #     print(f"Error: {e}")
#     return


# async def call_modeller_agent(
#     # question: str,
#     # tool_context: ToolContext,
#     callback_context: CallbackContext,
#     # llm_request: LlmRequest,
# ):
#     from .agent import modeller_agent
#     """Tool to call modeller_agent."""
#     print("Executing call_modeller_agent()")

#     #This will change to active persona in future. For now we are just performing all tasks
#     # tasks = config["output_personas"]["all"]
#     # folder_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
#     # Path(folder_name).mkdir()
#     # tool_output = {}

#     task = callback_context.state["current_task"]
#     print(f"&&&&&&& current_task: {task}")

#     # parallel_agents = []
#     # if task == CONCEPTUAL_MODEL_TASK and len(parallel_agents) == 0:
#     #     print("inside CONCEPTUAL_MODEL_TASK IF block ... ")
#     #     parallel_agents.append(_ddl_agent)
#     #     parallel_agents.append(_blueprint_agent)
#     #     parallel_agents.append(questionnaire_agent)
#     #     parallel_agent = ParallelAgent(
#     #         name="parallel_agent",
#     #         description="Generate multiple initial inputs by executing the paralle agents.",
#     #         sub_agents=parallel_agents,
#     #         )
#     #     try:
#     #         print("Executing parallel agents...")
#     #         agent_tool = AgentTool(agent=parallel_agent)
#     #         await agent_tool.run_async(
#     #             args={"request": ""},tool_context=callback_context
#     #         )
#     #     except Exception as e:
#     #         print(f"Error: {e}")
#     # if task == LDM_TASK and len(parallel_agents) == 0:
#     #     # add more agents for parallel_agent here for LDM task
#     #     parallel_agents.append(_search_agent)
#     #     parallel_agent = ParallelAgent(
#     #         name="parallel_agent",
#     #         description="Generate multiple initial inputs by executing the paralle agents.",
#     #         sub_agents=parallel_agents,
#     #         )
#     #     try:
#     #         print("Executing parallel agents...")
#     #         agent_tool = AgentTool(agent=parallel_agent)
#     #         await agent_tool.run_async(
#     #             args={"request": ""},tool_context=callback_context
#     #         )
#     #     except Exception as e:
#     #         print(f"Error: {e}")
#     # if task == PDM_TASK and len(parallel_agents) == 0:
#     #     # add more agents for parallel_agent here for PDM task
#     #     parallel_agents.append(_search_agent)
#     #     parallel_agent = ParallelAgent(
#     #         name="parallel_agent",
#     #         description="Generate multiple initial inputs by executing the paralle agents.",
#     #         sub_agents=parallel_agents,
#     #         )
#     #     try:
#     #         print("Executing parallel agents...")
#     #         agent_tool = AgentTool(agent=parallel_agent)
#     #         await agent_tool.run_async(
#     #             args={"request": ""},tool_context=callback_context
#     #         )
#     #     except Exception as e:
#     #         print(f"Error: {e}")


#     print("Executing call_modeller_agent(), here 1")
#     agent_tool = AgentTool(agent=modeller_agent)
#     modeller_agent_output = await agent_tool.run_async(
#          args={"request": ""},tool_context=callback_context
#     )
#     print("Executing call_modeller_agent(), here 2")
#     # args={"request": question}
#     if task == CONCEPTUAL_MODEL_TASK:
#         callback_context.state[task] = modeller_agent_output
#     if task == LDM_TASK:
#         callback_context.state[task] = modeller_agent_output
#     if task == PDM_TASK:
#         callback_context.state[task] = modeller_agent_output
#     # save_artifacts(task, modeller_agent_output, folder_name)
#     # if task == DDL_TASK:
#     #     tool_context.state["ddl"] = modeller_agent_output
#     # if task == BQ_METADATA_TASK:
#     #     tool_context.state["metadata"] = cleanup_metadata(modeller_agent_output)
#     # if task == BQ_LOGICAL_MODEL_TASK:
#     #     tool_output["summary"] = modeller_agent_output
#     # if task == BASE_MODEL_TASK:
#     #     tool_context.state["base_data_model"] = modeller_agent_output
#     # if task == LDM_TASK:
#     #     tool_context.state["logical_data_model"] = modeller_agent_output
#     # if task == PDM_TASK:
#     #     tool_context.state["physical_data_model"] = modeller_agent_output
#     # tool_context.state["gcs_folder"] = folder_name
#     # tool_output["gcs_folder"] = folder_name
#     # tool_output["project_id"] = os.getenv("GOOGLE_CLOUD_PROJECT", default="deid-sandbox")
#     # tool_context.state["project_id"] = os.getenv("GOOGLE_CLOUD_PROJECT", default="deid-sandbox")
#     # del_dir(folder_name)
#     return

# # async def call_modeller_agent(
# #     question: str,
# #     tool_context: ToolContext,
# # ):
# #     """Tool to call modeller_agent."""

# #     #This will change to active persona in future. For now we are just performing all tasks
# #     tasks = config["output_personas"]["all"]
# #     folder_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
# #     Path(folder_name).mkdir()
# #     tool_output = {}
# #     for task in tasks:
# #         tool_context.state["current_task"] = task
# #         agent_tool = AgentTool(agent=modeller_agent)
# #         modeller_agent_output = await agent_tool.run_async(
# #             args={"request": question}, tool_context=tool_context
# #         )
# #         print(task,"\n", modeller_agent_output)
# #         save_artifacts(task, modeller_agent_output, folder_name)
# #         if task == DDL_TASK:
# #             tool_context.state["ddl"] = modeller_agent_output
# #         if task == BQ_METADATA_TASK:
# #             tool_context.state["metadata"] = cleanup_metadata(modeller_agent_output)
# #         if task == BQ_LOGICAL_MODEL_TASK:
# #             tool_output["summary"] = modeller_agent_output
# #         if task == BASE_MODEL_TASK:
# #             tool_context.state["base_data_model"] = modeller_agent_output
# #         if task == LDM_TASK:
# #             tool_context.state["logical_data_model"] = modeller_agent_output
# #         if task == PDM_TASK:
# #             tool_context.state["physical_data_model"] = modeller_agent_output
# #     tool_context.state["gcs_folder"] = folder_name
# #     tool_output["gcs_folder"] = folder_name
# #     tool_output["project_id"] = os.getenv("GOOGLE_CLOUD_PROJECT", default="deid-sandbox")
# #     tool_context.state["project_id"] = os.getenv("GOOGLE_CLOUD_PROJECT", default="deid-sandbox")
# #     del_dir(folder_name)
# #     return tool_output

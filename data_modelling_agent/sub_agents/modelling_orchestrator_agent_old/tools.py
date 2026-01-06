from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

# from .sub_agents.modelling_task_agent.agent import modelling_task_agent
# from .sub_agents.modeller_agent.const import config, DDL_TASK, BQ_METADATA_TASK, BQ_LOGICAL_MODEL_TASK, BASE_MODEL_TASK, LDM_TASK, PDM_TASK
# from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from .const import DDL_TASK, PDM_TASK, LDM_TASK, CONCEPTUAL_MODEL_TASK, config

# import json
import datetime
from pathlib import Path

# from .sub_agents.modelling_process_loop_agent.agent import modelling_process_agent
# from .sub_agents.modelling_process_loop_agent.sub_agents.modelling_task_agent.agent import modelling_task_agent
from .sub_agents.modelling_process_loop_agent.sub_agents.modeller_agent.agent import (
    modeller_agent,
)
from .sub_agents.modelling_process_loop_agent.agent import modelling_process_loop_agent
from .utils import del_dir, save_artifacts
from google.adk.tools import google_search
from google.adk.tools import VertexAiSearchTool
from google.adk.agents import Agent, ParallelAgent

# from data_modelling_agent.sub_agents.questionnaire_agent.agent import questionnaire_agent
# from .utils import del_dir, save_artifacts
# from data_modelling_agent.sub_agents.ddl_agent.utils.bq import cleanup_ddl
# from data_modelling_agent.sub_agents.reporting_agent.utils.commons import cleanup_metadata
import os

project_id = os.getenv("GOOGLE_CLOUD_PROJECT", None)
BQ_BEST_PRACTICES_DATASTORE_ID_ONLY = os.getenv("BQ_BEST_PRACTICES_DATASTORE_ID", None)
BLUEPRINT_DATASTORE_ID_ONLY = os.getenv("BLUEPRINT_DATASTORE_ID", None)
USER_RULES_DATASTORE_ONLY = os.getenv("USER_RULES_DATASTORE_ID", None)
DDL_DATASTORE_ONLY = os.getenv("DDLS_DATASTORE_ID", None)
QUESTIONNAIRE_DATASTORE_ID_ONLY = os.getenv("QUESTIONNAIRE_DATASTORE_ID", None)


BQ_BEST_PRACTICES_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{BQ_BEST_PRACTICES_DATASTORE_ID_ONLY}"
BLUEPRINT_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{BLUEPRINT_DATASTORE_ID_ONLY}"
USER_RULES_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{USER_RULES_DATASTORE_ONLY}"
DDL_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{DDL_DATASTORE_ONLY}"
QUESTIONNAIRE_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{QUESTIONNAIRE_DATASTORE_ID_ONLY}"


_bq_best_prac_tool = VertexAiSearchTool(data_store_id=BQ_BEST_PRACTICES_DATASTORE_ID)
_blueprint_tool = VertexAiSearchTool(data_store_id=BLUEPRINT_DATASTORE_ID)
_user_rules_datastore_tool = VertexAiSearchTool(data_store_id=USER_RULES_DATASTORE_ID)
_ddl_datastore_tool = VertexAiSearchTool(data_store_id=DDL_DATASTORE_ID)
_questionnaire_tool = VertexAiSearchTool(data_store_id=QUESTIONNAIRE_DATASTORE_ID)


_bq_best_prac_agent = Agent(
    model="gemini-2.5-flash",
    name="bq_best_prac_search_agent",
    description="An agent who can automatically retrieve BigQuery best practices from provided datastore",
    instruction=f"""You are helpful assistant who **automatically** retreives BigQuery best practices from datastore: {BQ_BEST_PRACTICES_DATASTORE_ID} using VertexAISearchTool tool: 'bq_best_prac_tool' 
    **GUARDRAILS**
    - **Do not ask for any user input**.
    - **Always use 'bq_best_prac_tool' tool provided to you for search**

    """,
    tools=[_bq_best_prac_tool],
    output_key="bq_best_prac_output",
)
bq_best_prac_agent_tool = AgentTool(agent=_bq_best_prac_agent)


_blueprint_agent = Agent(
    model="gemini-2.5-flash",
    name="blueprint_search_agent",
    description="An agent who can automatically retrieve Industry Blueprints from provided datastore",
    instruction=f"""You are helpful assistant who **automatically** retreives Industry Blueprints. 
    You are provided with one as datastore {BLUEPRINT_DATASTORE_ID}. **Use 'blueprint_tool' tool for retrieving it.**
    
    **GUARDRAILS**
    - **Do not ask for any input**. 
    - **Always use 'blueprint_tool' tool provided to you for searching**

    """,
    tools=[_blueprint_tool],
    output_key="blueprint_output",
)

blueprint_agent_tool = AgentTool(agent=_blueprint_agent)

_user_rule_agent = Agent(
    model="gemini-2.5-flash",
    name="user_rule_search_agent",
    description="An agent who can automatically retrieve user defined rules from provided datastore",
    instruction=f"""You are helpful assistant who **automatically** retreives User Rules from datastore {USER_RULES_DATASTORE_ID} using VertexAISearchTool tool: 'user_rules_datastore_tool' 
    **GUARDRAILS**
    - **Do not ask for any user input**. 
    - **Always use 'user_rules_datastore_tool' tool provided to you for searching**
    
    """,
    tools=[_user_rules_datastore_tool],
    output_key="user_rule_output",
)

user_rule_agent_tool = AgentTool(agent=_user_rule_agent)

_ddl_agent = Agent(
    model="gemini-2.5-flash",
    name="ddl_search_agent",
    description="An agent who can automatically retrieve DDLs from provided datastore",
    instruction=f"""
    You are helpful assistant who **automatically** retreives all DDLs from datastore {DDL_DATASTORE_ID} using VertexAISearchTool tool: 'ddl_datastore_tool' 
    
    **GUARDRAILS**
    - **Do not ask for any user input**.
    - **Always use ''ddl_datastore_tool tool provided to you for searching**
    
    """,
    tools=[_ddl_datastore_tool],
    output_key="ddl_output",
)

ddl_agent_tool = AgentTool(agent=_ddl_agent)


_search_agent = Agent(
    model="gemini-2.5-flash",
    name="google_search_tool",
    description="An agent providing results for user queries using Google search",
    instruction="You are a specialist in providing information from Google Search. Use Google search to find the relevant information about the user provided error",
    tools=[google_search],
)

_questionnaire_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-flash"),
    name="questionnaire_agent",
    description="""An agent for automatically retreiving questions-answers from provided datastore""",
    instruction=f"""
      You are an helpful assistant who can **automatically** retrieve questions and their answers from datastore {QUESTIONNAIRE_DATASTORE_ID} using VertexAISearchTool tool: 'questionnaire_tool'.
  
    **Guardrails**
    - **Always use 'questionnaire_tool' tool provided to you for searching**
    - Do not make up anything from your own knowledge.
    """,
    tools=[_questionnaire_tool],
    # after_agent_callback = set_questionnaire_output,
    output_key="questionnaire_responses",
)

questionnaire_agent_tool = AgentTool(agent=_questionnaire_agent)

# async def google_search_tool_for_conceptual(query: str, tool_context: ToolContext):
#     _google_search_tool = AgentTool(agent=_search_agent)
#     _google_search_tool_output = await _google_search_tool.run_async(
#         args={"request": query}, tool_context=tool_context
#     )
#     return _google_search_tool_output

# async def google_search_tool_for_ldm(query: str, tool_context: ToolContext):
#     _google_search_tool = AgentTool(agent=_search_agent)
#     _google_search_tool_output = await _google_search_tool.run_async(
#         args={"request": query}, tool_context=tool_context
#     )
#     return _google_search_tool_output

# async def google_search_tool_for_pdm(query: str, tool_context: ToolContext):
#     _google_search_tool = AgentTool(agent=_search_agent)
#     _google_search_tool_output = await _google_search_tool.run_async(
#         args={"request": query}, tool_context=tool_context
#     )
#     return _google_search_tool_output


async def set_current_task(
    question: str,
    tool_context: ToolContext,
):
    print("Executing set_current_task()")
    state = tool_context.state
    tasks = config["output_personas"]["all"]
    folder_name = "extracted_metadata"

    # folder_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # Path(folder_name).mkdir()
    tool_output = {}
    for task in tasks:
        tool_context.state["current_task"] = task
        tool_context.state["hitl_feedback"] = 1
        tool_context.state["loop_exit_cue"] = 0
        tool_context.state["data_model"] = None
        parallel_agents = []
        if task == CONCEPTUAL_MODEL_TASK and len(parallel_agents) == 0:
            print(f"inside {CONCEPTUAL_MODEL_TASK} IF block ... ")
            parallel_agents.append(_ddl_agent)
            # parallel_agents.append(_blueprint_agent)
            parallel_agents.append(_questionnaire_agent)
            # tool_context.state["parallel_agents"] = parallel_agents
        if task == LDM_TASK and len(parallel_agents) == 0:
            print(f"inside {LDM_TASK} IF block ... ")
            # add more agents for parallel_agent here for LDM task
            parallel_agents.append(_search_agent)
            # tool_context.state["parallel_agents"] = parallel_agents
        if task == PDM_TASK and len(parallel_agents) == 0:
            print(f"inside {PDM_TASK} IF block ... ")
            # add more agents for parallel_agent here for PDM task
            parallel_agents.append(_search_agent)
            # tool_context.state["parallel_agents"] = parallel_agents

        parallel_agent = ParallelAgent(
            name="context_gathering_agent",
            description="Executes multiple agents in parallel to gather initial context",
            sub_agents=parallel_agents,
        )
        try:
            parallel_tool = AgentTool(agent=parallel_agent)
            await parallel_tool.run_async(
                args={"request": ""}, tool_context=tool_context
            )
            # reset the parent agent to None for all helper sub-agents
            for agent_name in parallel_agents:
                agent_name.parent_agent = None

        except Exception as e:
            print(f"Error: {e}")

        # agent_tool = AgentTool(agent=modelling_process_loop_agent)
        modeller_agent_output = ""
        # while tool_context.state["hitl_feedback"] != 1:
        agent_tool = AgentTool(agent=modeller_agent)
        modeller_agent_output = await agent_tool.run_async(
            args={"request": question}, tool_context=tool_context
        )

        # tool_context.state["data_model"] = modeller_agent_output

        # model_custom_output = AgentTool(agent=modeller_agent)
        # modeller_agent_output = await agent_tool.run_async(
        # args={"request": question}, tool_context=tool_context
        # )

        # print("STEP 3: Starting the feedback loop...")
        # loop_tool = AgentTool(agent=modelling_process_loop_agent)
        # final_output = await loop_tool.run_async(args={"request": ""}, tool_context=tool_context)

        # save_artifacts(task, modeller_agent_output, folder_name)
        # if task == DDL_TASK:
        #     tool_context.state["ddl"] = modeller_agent_output
        # if task == BQ_METADATA_TASK:
        #     tool_context.state["metadata"] = cleanup_metadata(modeller_agent_output)
        # if task == BQ_LOGICAL_MODEL_TASK:
        #     tool_output["summary"] = modeller_agent_output
        # if task == CONCEPTUAL_MODEL_TASK:
        #     tool_context.state["conceptual_model"] = modeller_agent_output
        # if task == LDM_TASK:
        #     tool_context.state["logical_data_model"] = modeller_agent_output
        # if task == PDM_TASK:
        #     tool_context.state["physical_data_model"] = modeller_agent_output
    # tool_context.state["gcs_folder"] = folder_name
    # tool_output["gcs_folder"] = folder_name
    # tool_output["project_id"] = os.getenv("GOOGLE_CLOUD_PROJECT", default="deid-sandbox")
    # tool_context.state["project_id"] = os.getenv("GOOGLE_CLOUD_PROJECT", default="deid-sandbox")
    # del_dir(folder_name)
    return modeller_agent_output

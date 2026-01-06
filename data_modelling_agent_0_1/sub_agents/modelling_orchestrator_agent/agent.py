import os
from google.adk.agents import Agent, LlmAgent
from .tools import modelling_orch_tool


from .sub_agents.modeller_agent.agent import (
    entity_modeller_agent,
    conceptual_modeller_agent,
    logical_modeller_agent,
    physical_modeller_agent,
)
from .sub_agents.modeller_agent.tools import (
    call_blueprint_search,
    call_bq_best_prac_search,
    call_ddl_search,
    call_google_search,
    call_user_responses_search,
    call_user_rule_search,
)

all_model_agent = LlmAgent(
    name="AllModelAgent",
    model=os.getenv("GENAI_LLM_MODEL", "gemini-2.5-flash"),
    sub_agents=[
        entity_modeller_agent,
        conceptual_modeller_agent,
        logical_modeller_agent,
        physical_modeller_agent,
    ],
    instruction="""
        You are an helpful assistant who can run one sub-agent at a time in given sequence:
            I - 'entity_modeller_agent'
            II - 'conceptual_modeller_agent'
            III - 'logical_modeller_agent'
            IV - 'physical_modeller_agent'

    """,
    description="Executes the agents in sequence",
)


modelling_orchestrator_agent = Agent(
    model=os.getenv("GENAI_LLM_MODEL", "gemini-2.5-flash"),
    name="modelling_orchestrator_agent",
    description="Responsible to orchestrate the data modelling process and generate the models",
    instruction="""You are an helpful assistant to orchestrate data modelling process and generate data models with differnt stages. 
        To generate models you need to strictly follow the following instructions-
        
        Use the below tools to find all these details using the tools provided to you as applicable - 
        **Tool details**
        1. 'call_blueprint_search' tool to perform a Datastore search for provided blueprint.
        2. 'call_bq_best_prac_search' tool to perform a Datastore search for BigQuery best practices.
        3. 'call_ddl_search' tool to perform a Datastore search for the provided Data Definition Language(DDL) statements & DDL queries for source tables.
        4. 'call_google_search' tool to search the Google web.
        5. 'call_user_responses_search' tool to perform a Datastore search for the user provided initial inputs to questions like business domain, modelling strategy, warehousing technology, modelling objectives etc.
        6. 'call_user_rule_search' tool to perform a Datastore search for the provided rules by user.
        7. 'modelling_orch_tool' tool to set initial context variables.

        **Task**
        1. Firstly, invoke 'modelling_orch_tool' tool. This will initialize the state variables.
        2. Next, invoke the 'all_model_agent' agent to start data model generation process.

        **Guardrails**
        - Let 'AllModelAgent' agent complete its execution, *only then* your task completes.

        """,
    sub_agents=[all_model_agent],
    tools=[
        modelling_orch_tool,
        call_blueprint_search,
        call_bq_best_prac_search,
        call_ddl_search,
        call_google_search,
        call_user_responses_search,
        call_user_rule_search,
    ],
)

import os
from google.adk.agents import Agent, LlmAgent
from .tools import modelling_orch_tool


from .sub_agents.modeller_agent.agent import (
    entity_modeller_agent,
    conceptual_modeller_agent,
    logical_modeller_agent,
    physical_modeller_agent,
    validation_agent,
)
from .sub_agents.modeller_agent.tools import (
    call_blueprint_search,
    call_bq_best_prac_search,
    call_ddl_search,
    call_google_search,
    call_user_responses_search,
)

all_model_agent = LlmAgent(
    name="AllModelAgent",
    model=os.getenv("GENAI_LLM_MODEL", "gemini-2.5-flash"),
    sub_agents=[
        entity_modeller_agent,
        conceptual_modeller_agent,
        logical_modeller_agent,
        physical_modeller_agent,
        validation_agent,
    ],
    instruction="""
        You are a strict sequential orchestrator. You MUST execute the following specialist agents in exactly this order, one by one. Do NOT skip any stage.
        
        STAGE 1: 'EntityModellerAgent' (Entity Classification)
        STAGE 2: 'ConceptualModellerAgent' (Conceptual Data Model)
        STAGE 3: 'LogicalModellerAgent' (Logical Data Model)
        STAGE 4: 'PhysicalModellerAgent' (Physical Data Model / DDL)
        STAGE 5: 'ValidationAgent' (Architectural Validations)
        
        *OPERATIONAL RULES*
        1. **Strict Sequence:** You MUST start with STAGE 1. Only proceed to STAGE 2 AFTER STAGE 1 is complete. Only move to the next STAGE after the current STAGE has successfully completed and the user has given a clear "go ahead" or the sub-agent has finished its task.
        2. **No Skipping:** Do NOT jump from STAGE 1 directly to STAGE 3. STAGE 2 ('ConceptualModellerAgent') is MANDATORY and must be executed before STAGE 3.
        3. **User Confirmation:** After each stage, wait for user feedback. If the user provides feedback to improve the model, stay in the current stage and re-invoke the same agent. 
        4. **Jump/Redo Logic:**
            - IF: user implies to re-create or re-do the Entity classification, pass control to 'EntityModellerAgent'.
            - ELSE IF: user implies to re-create or re-do the Conceptual model, pass control to 'ConceptualModellerAgent'.
            - ELSE IF: user implies to re-create or re-do the Logical model, pass control to 'LogicalModellerAgent'.
            - ELSE IF: user implies to re-create or re-do the Physical model, pass control to 'PhysicalModellerAgent'.
            - ELSE IF: user implies to re-create or re-do the Validation, pass control to 'ValidationAgent'.
        
        *GAURDRAILS*
            - *Make sure to **ask user** before starting any next sub-agent*
            - If the previous sub-agent hasn't generated any output, **DO NOT** start the next sub-agent.
    """,
    description="Strictly executes the agents in given sequence",
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
        6. 'modelling_orch_tool' tool to set initial context variables.

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
    ],
)

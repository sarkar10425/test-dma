import os
from .prompts import (
    entity_instructions,
    conceptual_instructions,
    logical_instructions,
    physical_instructions,
    validation_instructions,
)
from google.adk.agents import Agent


from .tools import (
    call_blueprint_search,
    call_ddl_search,
    call_google_search,
    call_user_responses_search,
    call_bq_best_prac_search,
    call_kpi_search,
    call_profile_data_search,
    save_output,
    read_input,
)


entity_modeller_agent = Agent(
    name="EntityModellerAgent",
    model=os.getenv("GENAI_LLM_MODEL", "gemini-2.5-flash"),
    instruction=entity_instructions,
    description="You are a helping assistant who will create an Entity model and then re-create it as many times as the user provides feedback",
    tools=[
        call_blueprint_search,
        call_ddl_search,
        call_google_search,
        call_user_responses_search,
        call_bq_best_prac_search,
        call_profile_data_search,
        call_kpi_search,
        save_output,
        read_input,
    ],
)


conceptual_modeller_agent = Agent(
    name="ConceptualModellerAgent",
    model=os.getenv("GENAI_LLM_MODEL", "gemini-2.5-flash"),
    instruction=conceptual_instructions,
    description="You are a helping assistant who will create a Conceptual data model and then re-create it as many times as the user provides feedback",
    tools=[
        call_blueprint_search,
        call_ddl_search,
        call_google_search,
        call_user_responses_search,
        call_bq_best_prac_search,
        call_profile_data_search,
        call_kpi_search,
        save_output,
        read_input,
    ],
)

logical_modeller_agent = Agent(
    name="LogicalModellerAgent",
    model=os.getenv("GENAI_LLM_MODEL", "gemini-2.5-flash"),
    instruction=logical_instructions,
    description="You are a helping assistant who will create a Logical data model and then re-create it as many times as the user provides feedback",
    tools=[
        call_blueprint_search,
        call_ddl_search,
        call_google_search,
        call_user_responses_search,
        call_bq_best_prac_search,
        call_profile_data_search,
        call_kpi_search,
        save_output,
        read_input,
    ],
)

physical_modeller_agent = Agent(
    name="PhysicalModellerAgent",
    model=os.getenv("GENAI_LLM_MODEL", "gemini-2.5-flash"),
    instruction=physical_instructions,
    description="You are a helping assistant who will create a Physical data model and then re-create it as many times as the user provides feedback",
    tools=[
        call_blueprint_search,
        call_ddl_search,
        call_google_search,
        call_user_responses_search,
        call_bq_best_prac_search,
        call_profile_data_search,
        call_kpi_search,
        save_output,
        read_input,
    ],
)

validation_agent = Agent(
    name="ValidationAgent",
    model=os.getenv("GENAI_LLM_MODEL", "gemini-2.5-flash"),
    instruction=validation_instructions,
    description="You are a helpful assistant who will validate the data models created by the previous agents against best practices and user requirements",
    tools=[
        call_blueprint_search,
        call_ddl_search,
        call_google_search,
        call_user_responses_search,
        call_bq_best_prac_search,
        call_profile_data_search,
        call_kpi_search,
        save_output,
        read_input,
    ],
)

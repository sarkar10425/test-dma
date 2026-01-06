import os
from .prompts import (
    entity_instructions,
    conceptual_instructions,
    logical_instructions,
    physical_instructions,
)
from google.adk.agents import Agent, LlmAgent
from google.adk.agents.callback_context import CallbackContext
from .tools import _confirmation_tool
from google.adk.tools import FunctionTool
from .tools import (
    call_blueprint_search,
    call_ddl_search,
    call_google_search,
    call_user_responses_search,
    call_user_rule_search,
    call_bq_best_prac_search,
    save_output,
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
        call_user_rule_search,
        call_bq_best_prac_search,
        # save_output,
        FunctionTool(func=_confirmation_tool),
    ],
    output_key="entity_data_model",
)


def check_if_entity_created(callback_context: CallbackContext):
    events = callback_context._invocation_context.session.events
    print(f"events: {events}")
    if not callback_context.state["entity_data_model"]:
        for event in events:
            if event.author == "ConceptualModellerAgent":
                print(f"transferring back to EntityModellerAgent")
                event.actions.transfer_to_agent = "EntityModellerAgent"
    return


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
        call_user_rule_search,
        call_bq_best_prac_search,
        # save_output,
        FunctionTool(func=_confirmation_tool),
    ],
    output_key="conceptual_data_model",
    # before_agent_callback=check_if_entity_created
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
        call_user_rule_search,
        call_bq_best_prac_search,
        # save_output,
        FunctionTool(func=_confirmation_tool),
    ],
    output_key="logical_data_model",
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
        call_user_rule_search,
        call_bq_best_prac_search,
        # save_output,
        FunctionTool(func=_confirmation_tool),
    ],
    output_key="physical_data_model",
)

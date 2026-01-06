import os
from google.genai import types
from typing import Optional
from google.adk.agents.llm_agent import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.tools import VertexAiSearchTool
from google.adk.tools import ToolContext
from google.adk.agents import Agent, ParallelAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import google_search
from google.adk.agents.invocation_context import InvocationContext
import json
from google.genai import types
from typing import Optional

from google import genai
import os

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
import datetime
from google.adk.tools import google_search
from google.adk.tools import VertexAiSearchTool

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


_search_agent = Agent(
    model="gemini-2.5-flash",
    name="google_search_tool",
    description="An agent providing results for user queries using Google search",
    instruction="You are a specialist in providing information from Google Search. Use Google search to find the relevant information about the user provided error",
    tools=[google_search],
)


async def call_google_search(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call source search agent."""

    agent_tool = AgentTool(agent=_search_agent)

    google_search_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    return google_search_agent_output


_bq_best_prac_agent = Agent(
    model="gemini-2.5-flash",
    name="blueprint_search_agent",
    description="An agent who can automatically retrieve Industry Blueprints from provided datastore",
    instruction=f"""You are helpful assistant who **automatically** retreives BigQuery best practices from datastore: {BQ_BEST_PRACTICES_DATASTORE_ID} using VertexAISearchTool tool: 'bq_best_prac_tool' 
    **GUARDRAILS**
    - **Do not ask for any user input**.
    - **Always use 'bq_best_prac_tool' tool provided to you for search**

    **GUARDRAILS**
    - Do not ask for any input to user or other sub-agents.
    
    """,
    tools=[VertexAiSearchTool(data_store_id=BQ_BEST_PRACTICES_DATASTORE_ID)],
    output_key="bq_best_practices_output",
)


async def call_bq_best_prac_search(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call source search agent."""

    agent_tool = AgentTool(agent=_bq_best_prac_agent)

    bq_best_prac_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    return bq_best_prac_agent_output


_blueprint_agent = Agent(
    model="gemini-2.5-flash",
    name="blueprint_search_agent",
    description="An agent who can automatically retrieve Industry Blueprints from provided datastore",
    instruction=f"""You are a self working agent who can find information from datastore: {BLUEPRINT_DATASTORE_ID}.
        You must follow below instructions:
        1. Use the VertexAiSearchTool to find information.
        2. Determine Core Industry Blueprint
        3. Do not ask for any input to user or other sub-agents.

    """,
    tools=[VertexAiSearchTool(data_store_id=BLUEPRINT_DATASTORE_ID)],
    output_key="blueprint_output",
)


async def call_blueprint_search(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call source search agent."""

    agent_tool = AgentTool(agent=_blueprint_agent)

    blueprint_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    return blueprint_agent_output


user_rule_agent = Agent(
    model="gemini-2.5-flash",
    name="user_rule_search_agent",
    instruction=f"""You are a self working agent who can find information from datastore: {USER_RULES_DATASTORE_ID}.
    You must follow below instructions:
    1. Use this VertexAiSearchTool to find information.
    2. You must extract all question and answers from the datastore
    3. **Do not ask any questions to user or other agents**
    
    """,
    description="Self working search assitant with Vertex AI Search capabilities, to extract information from existing user rules.",
    tools=[VertexAiSearchTool(data_store_id=USER_RULES_DATASTORE_ID)],
    output_key="user_rule_output",
)


async def call_user_rule_search(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call source search agent."""

    agent_tool = AgentTool(agent=user_rule_agent)

    user_rule_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    return user_rule_agent_output


ddl_agent = Agent(
    model="gemini-2.5-flash",
    name="ddl_search_agent",
    instruction=f"""You are a self working agent who can find information from datastore: {DDL_DATASTORE_ID}.
    You must follow below instructions:
    1. Use the VertexAiSearchTool to find information.
    2. You must extract all information from provided DDLs, that are needed to build a data model
    3. **Do not ask any questions to user or other agents**
    
    """,
    description="Self working search assitant with Vertex AI Search capabilities, to extract information from existing DDLs.",
    tools=[VertexAiSearchTool(data_store_id=DDL_DATASTORE_ID)],
    output_key="ddl_output",
)


async def call_ddl_search(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call source search agent."""

    agent_tool = AgentTool(agent=ddl_agent)

    ddl_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )

    return ddl_agent_output


_user_responses_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-flash"),
    name="UserResponseAgent",
    description="""An agent for automatically searching user's answers to already asked questions""",
    instruction=f"""
      You are a self working agent who can find information from datastore: {QUESTIONNAIRE_DATASTORE_ID}.
        You must follow below instructions:
        1. Use the VertexAiSearchTool to find information.
        2. You must extract all information from provided DDLs, that are needed to build a data model
        3. **Do not ask any questions to user or other agents**
    """,
    tools=[VertexAiSearchTool(data_store_id=QUESTIONNAIRE_DATASTORE_ID)],
    output_key="questionnaire_responses",
)


async def call_user_responses_search(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call source search agent."""

    agent_tool = AgentTool(agent=_user_responses_agent)

    user_responses_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    return user_responses_agent_output


def exit_loop(tool_context: ToolContext):
    """Call this function ONLY when the user indicates no further changes are needed, signaling the iterative process should end."""
    print(f"[Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True

    return {}


async def save_output(
    tool_context: ToolContext,
):
    report_artifact = types.Part.from_bytes(
        data=tool_context.state["data_model"], mime_type="text/plain"
    )
    filename = "model.txt"
    content = tool_context.state["data_model"]
    print(f"@@@content: {content}")
    print("\n")
    if content:
        with open(filename, "w") as f:
            f.write(content)
        print(f"@@@@@ saved artifact to local")
    try:
        await tool_context.save_artifact(
            filename=filename,
            artifact=types.Part(text=tool_context.state["data_model"]),
        )
        # The event generated after this callback will contain:
        # event.actions.artifact_delta == {"generated_report.pdf": version}
    except ValueError as e:
        print(
            f"Error saving Python artifact: {e}. Is ArtifactService configured in Runner?"
        )
    except Exception as e:
        print(f"An unexpected error occurred during Python artifact save: {e}")


def _confirmation_tool(tool_context: ToolContext, user_feedback: str):

    current_state = tool_context.state
    user_search_phrases = ["i am good", "confirm", "save", "finalize", "finalise"]

    tool_confirmation = tool_context.tool_confirmation
    if not tool_confirmation:
        print(f"taking user's review... ")
        tool_context.request_confirmation(
            hint=(
                "Please review the data model. I am ready to incorporate any feedback that you may have, and re-generate the model for you."
            ),
        )
        return {"status": "User Approval requested"}

    approved = tool_confirmation.payload
    events = tool_context._invocation_context.session.events
    print(f"@@@@events: {events}")
    # finding model generated resposne
    model_generated_response = None
    last_iteration_model_generated_content = None
    while not model_generated_response:
        for event in events:
            if event.content.role:
                if event.content.role == "model":
                    if event.content.parts:
                        print(f"event.content.parts: {event.content.parts}")
                        text_flag = False
                        for part in event.content.parts:
                            if part.text:
                                print(f"part.text: {part.text}")
                                last_iteration_model_generated_content = part.text
                                text_flag = True
                            if part.function_call and text_flag:
                                print(f"part.function_call: {part.function_call}")
                                if part.function_call.name == "_confirmation_tool":
                                    model_generated_response = (
                                        last_iteration_model_generated_content
                                    )
                                    print(
                                        f"model_generated_response INSIDE: {model_generated_response}"
                                    )

    print(f"@@@@model response:{model_generated_response}")
    print(f"@@ num of events: {len(events)}")
    #  {"payload":"ensure entities are same as source DDLs"}
    # {"payload":"i am good"}
    # capturing user feedback
    user_response_event = events[-1]
    print(f"@@@@user_response_event:{user_response_event}")
    if user_response_event.content:
        if user_response_event.content.parts:
            print(
                f"@@@@user_response_event.content.parts:{user_response_event.content.parts}"
            )
            user_reponse_event_parts = user_response_event.content.parts
    user_reponse_event_role = user_response_event.content.role
    print(f"@@@@user_reponse_event_role:{user_reponse_event_role}")
    response = None
    if user_reponse_event_role == "user":
        for part in user_reponse_event_parts:
            print(f"part.function_response: {part.function_response}")
            name_of_func = part.function_response.name
            print(f"name:{part.function_response.name}")
            response = part.function_response.response
            print(f"response:{part.function_response.response}")

    if response:
        if response.get("response", ""):
            payload_str = response.get("response", "")
            payload = json.loads(payload_str)

            user_feedback = payload.get("payload", "")
            print(f"@@@@user_feedback:{user_feedback}")
            if user_feedback in user_search_phrases:
                print(f"@@@@user approved")
                # current_state['entity_data_model'] = current_state['data_model']
                current_state["hitl_feedback"] = ""
            else:
                print(f"@@@@user provided a feedback")
                current_state["hitl_feedback"] = (
                    model_generated_response + "\n" + user_feedback
                )
                # current_state['data_model'] = model_generated_response
                # user_response_event.actions.transfer_to_agent='EntityModellerAgent'

    return {}

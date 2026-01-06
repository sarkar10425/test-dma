import os
import io
import json
import csv
import asyncio
from google import genai
from google.genai import types
from google.genai import types
from google.adk.agents.llm_agent import Agent
from google.adk.tools import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import VertexAiSearchTool
from google.adk.models import LlmResponse
from google.cloud import storage
from .const import (
    state_var_dict,
    gcs_path_dict,
    agent_name_dict,
    PHYSICAL_MODEL_SUFFIX,
    LOGICAL_MODEL_SUFFIX,
    ENTITY_CLASSIFICATION_SUFFIX,
    VALIDATION_REPORT_SUFFIX,
    CONCEPTUAL_MODEL_SUFFIX,
)
import sys

if sys.maxsize > 131072:
    csv.field_size_limit(sys.maxsize)

project_id = os.getenv("GOOGLE_CLOUD_PROJECT", None)
BQ_BEST_PRACTICES_DATASTORE_ID_ONLY = os.getenv("BQ_BEST_PRACTICES_DATASTORE_ID", None)
BLUEPRINT_DATASTORE_ID_ONLY = os.getenv("BLUEPRINT_DATASTORE_ID", None)
USER_RULES_DATASTORE_ONLY = os.getenv("USER_RULES_DATASTORE_ID", None)
DDL_DATASTORE_ONLY = os.getenv("DDLS_DATASTORE_ID", None)
QUESTIONNAIRE_DATASTORE_ID_ONLY = os.getenv("QUESTIONNAIRE_DATASTORE_ID", None)
SQL_QUERIES_DATASTORE_ID_ONLY = os.getenv("SQL_QUERIES_DATASTORE_ID", None)
KPI_DATASTORE_ID_ONLY = os.getenv("KPIS_AND_QUERIES_DATASTORE_ID", None)
SQL_QUERIES_BUCKET_ID = os.getenv("SQL_QUERIES_BUCKET_ID", None)
AGENT_OUTPUT_BUCKET_ID = os.getenv("AGENT_OUTPUTS_BUCKET", None)

DATA_PROFILE_DATASTORE_ID_ONLY = os.getenv("DATA_PROFILE_DATASTORE_ID", None)


BQ_BEST_PRACTICES_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{BQ_BEST_PRACTICES_DATASTORE_ID_ONLY}"
BLUEPRINT_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{BLUEPRINT_DATASTORE_ID_ONLY}"
USER_RULES_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{USER_RULES_DATASTORE_ONLY}"
DDL_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{DDL_DATASTORE_ONLY}"
QUESTIONNAIRE_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{QUESTIONNAIRE_DATASTORE_ID_ONLY}"
KPI_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{KPI_DATASTORE_ID_ONLY}"
DATA_PROFILE_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{DATA_PROFILE_DATASTORE_ID_ONLY}"


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
    """Tool to call google search agent."""

    agent_tool = AgentTool(agent=_search_agent)

    google_search_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    return google_search_agent_output


_data_profile_agent = Agent(
    model="gemini-2.5-flash",
    name="data_profile_search_agent",
    description="An agent who can automatically retrieve Profile Data from provided datastore",
    instruction=f"""You are a self working agent who can find information from datastore: {DATA_PROFILE_DATASTORE_ID}.
        You must follow below instructions:
        1. Use the VertexAiSearchTool to find information.
        2. Determine profile data to implement in logical and physical models.
        3. Do not ask for any input to user or other sub-agents.
    """,
    tools=[VertexAiSearchTool(data_store_id=DATA_PROFILE_DATASTORE_ID)],
    output_key="profile_data_output",
)


async def call_profile_data_search(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call data profile agent."""

    agent_tool = AgentTool(agent=_data_profile_agent)

    data_profile_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    return data_profile_agent_output


_bq_best_prac_agent = Agent(
    model="gemini-2.5-flash",
    name="bigquery_best_practices_search_agent",
    description="An agent who can automatically retrieve BigQuery Best Practices from provided datastore",
    instruction=f"""You are a self working agent who can find information from datastore: {BQ_BEST_PRACTICES_DATASTORE_ID}.
        You must follow below instructions:
        1. Use the VertexAiSearchTool to find information.
        2. Determine BigQuert Best practices to implement in logical and physical models.
        3. Do not ask for any input to user or other sub-agents.

    """,
    tools=[VertexAiSearchTool(data_store_id=BQ_BEST_PRACTICES_DATASTORE_ID)],
    output_key="bq_best_practices_output",
)


async def call_bq_best_prac_search(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call BigQuery best practices agent."""

    agent_tool = AgentTool(agent=_bq_best_prac_agent)

    bq_best_prac_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    return bq_best_prac_agent_output


_kpi_agent = Agent(
    model="gemini-2.5-flash",
    name="kpi_search_agent",
    description="An agent who can automatically retrieve KPIs from provided datastore",
    instruction=f"""You are a self working agent who can find KPIs and related information from datastore: {KPI_DATASTORE_ID}.
        You must follow below instructions:
        1. Use the VertexAiSearchTool to find information.
        2. Determine KPIs and their information
        3. Do not ask for any input to user or other sub-agents.

    """,
    tools=[VertexAiSearchTool(data_store_id=KPI_DATASTORE_ID)],
    output_key="kpi_output",
)


async def call_kpi_search(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call KPI search agent."""

    agent_tool = AgentTool(agent=_kpi_agent)

    kpi_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    return kpi_agent_output


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
    """Tool to call blueprint search agent."""

    agent_tool = AgentTool(agent=_blueprint_agent)

    blueprint_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    return blueprint_agent_output


_ddl_agent = Agent(
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
    """Tool to call DDL search agent."""

    agent_tool = AgentTool(agent=_ddl_agent)

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
    """Tool to call user response agent."""

    agent_tool = AgentTool(agent=_user_responses_agent)

    user_responses_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    return user_responses_agent_output


async def save_to_gcs(bucket, path, content, filename):
    """store the model outputs to GCS bucket"""
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(f"{path}/{filename}")
    blob.upload_from_string(content)
    print(f"Model output uploaded to {path}/{filename}.")


async def save_output(tool_context: ToolContext, task_name: str):
    """Saves the agent's output to GCS and registers it as an ADK artifact."""
    events = tool_context._invocation_context.session.events
    model_generated_response = None
    last_iteration_model_generated_content = None
    max_iterations = 20 #prevent the while loop from running forever
    iterations = 0
    while not model_generated_response and iterations<=max_iterations:
        events = tool_context._invocation_context.session.events
        for event in events:
            if event.content:
                if event.content.role:
                    if event.content.role == "model":
                        if event.content.parts:
                            text_flag = False
                            for part in event.content.parts:
                                if part.text:
                                    last_iteration_model_generated_content = part.text
                                    text_flag = True
                                if part.function_call and text_flag:
                                    if part.function_call.name == "save_output":
                                        model_generated_response = (
                                            last_iteration_model_generated_content
                                        )
        iterations+=1

    if not model_generated_response:
        return "Error: No model output found to save. Please ensure you provide the content as text before calling this tool."

    if task_name not in state_var_dict:
        return f"Error: Task name '{task_name}' is not recognized in state configuration."

    filename = state_var_dict[task_name]
    tool_context.state[filename] = model_generated_response
    tool_context.state["last_input"] = model_generated_response

    # Fix suffix detection logic using elif
    if "physical" in filename:
        suffix = PHYSICAL_MODEL_SUFFIX
    elif "conceptual" in filename:
        suffix = CONCEPTUAL_MODEL_SUFFIX
    elif "validation" in filename:
        suffix = VALIDATION_REPORT_SUFFIX
    elif "logical" in filename:
        suffix = LOGICAL_MODEL_SUFFIX
    elif "entity" in filename:
        suffix = ENTITY_CLASSIFICATION_SUFFIX
    else:
        suffix = ".csv"

    full_filename = filename + suffix

    try:
        # Strip markdown markers if present
        cleaned_content = model_generated_response
        if cleaned_content.startswith("```"):
            lines = cleaned_content.splitlines()
            if len(lines) > 2:
                # Remove first line (```...) and last line (```)
                cleaned_content = "\n".join(lines[1:-1]).strip()
            else:
                cleaned_content = cleaned_content.strip("`").strip()

        if suffix == ".csv":
            input_stream = io.StringIO(cleaned_content)
            reader = csv.reader(input_stream, delimiter="|")
            with open(full_filename, "w", newline="", encoding="utf-8") as outfile:
                writer = csv.writer(outfile, delimiter="|")
                writer.writerows(reader)
        else:
            with open(full_filename, "w", encoding="utf-8") as f:
                f.write(cleaned_content)

        # Register ADK Artifact
        mime_type = "text/csv" if suffix == ".csv" else "text/plain"
        model_artifact = types.Part(
            inline_data=types.Blob(
                mime_type=mime_type, data=cleaned_content.encode("utf-8")
            )
        )
        print(f"saving to ADK artifacts as {filename}...")
        await tool_context.save_artifact(
            filename=filename,
            artifact=model_artifact,
        )

        # Upload to GCS
        try:
            print(f"SAVING TO GCS: {full_filename}")
            await save_to_gcs(
                AGENT_OUTPUT_BUCKET_ID,
                gcs_path_dict[task_name],
                cleaned_content,
                full_filename,
            )
            return f"Successfully saved {task_name} output to {full_filename} and uploaded artifacts."
        except Exception as e:
            print(f"Error saving output to GCS: {str(e)}")
            return f"Error saving output to GCS: {str(e)}"
        
        

    except Exception as e:
        error_msg = f"Error saving output: {str(e)}"
        print(error_msg)
        return error_msg


async def read_file_and_set_state_variable(
    uploaded_file_name: str, user_uploaded_blob: str, tool_context: ToolContext
):
    print(f"the uploaded filename is: {uploaded_file_name}")
    if "entity" in uploaded_file_name:
        tool_context.state["entity_data_model"] = user_uploaded_blob
    elif "conceptual" in uploaded_file_name:
        tool_context.state["conceptual_data_model"] = user_uploaded_blob
    elif "logical" in uploaded_file_name:
        tool_context.state["logical_data_model"] = user_uploaded_blob
    elif "physical" in uploaded_file_name:
        tool_context.state["physical_data_model"] = user_uploaded_blob
    else:
        print(
            "the uploaded file does not have a valida name to determine the correct state variable! skipping ... "
        )


async def read_input(tool_context: ToolContext, task_name: str):
    print(f"uploaded file detected for - {state_var_dict[task_name]} task...")
    user_uploaded_blob = None
    timeout_seconds = 5
    check_interval = 1
    for _ in range(timeout_seconds):
        events = tool_context._invocation_context.session.events

        # Iterate through events to find the user upload
        for event in events:
            if event.content and event.content.role == "user" and event.content.parts:
                for part in event.content.parts:
                    if part.inline_data:
                        user_uploaded_blob = part.inline_data.data
                        uploaded_file_name = part.inline_data.display_name

                        # Set state and return immediately upon finding the file
                        print(
                            f"Setting state variable : {state_var_dict[task_name]} to latest uploaded csv ... "
                        )
                        # to handle any file upload by user during any agent interaction. user must provide model name in their uploaded files
                        await read_file_and_set_state_variable(
                            uploaded_file_name, user_uploaded_blob, tool_context
                        )
                        return f"Successfully read input from {uploaded_file_name}."
            if event.content and event.content.role == "model" and event.content.parts:
                for part in event.content.parts:
                    if part.function_call:
                        function_name = part.function_call.name
                        if function_name == "read_input":
                            if event.author == agent_name_dict[task_name]:
                                if user_uploaded_blob:
                                    tool_context.state[state_var_dict[task_name]] = (
                                        user_uploaded_blob
                                    )
                                    tool_context.state["last_input"] = (
                                        user_uploaded_blob
                                    )
                            else:
                                tool_context.state["last_input"] = user_uploaded_blob

        # If we haven't found the blob yet, wait asynchronously before the next check
        await asyncio.sleep(check_interval)

    # Logic to handle the case where the loop finishes without finding a file
    if not user_uploaded_blob:
        error_msg = f"Timeout: No file upload detected for {task_name} within 5 seconds."
        print(error_msg)
        return error_msg
    
    return f"Finished reading input for {task_name}."

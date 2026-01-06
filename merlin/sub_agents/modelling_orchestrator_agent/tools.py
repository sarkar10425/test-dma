import datetime
import os, io
from google.adk.tools import ToolContext
from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from google.cloud import storage
import pandas as pd

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", None)
SQL_QUERIES_BUCKET_ID = os.getenv("SQL_QUERIES_BUCKET_ID", None)


async def read_sql_extraction_content(
    tool_context: ToolContext,
):
    path = "inputs/sql_queries_extraction/"
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(SQL_QUERIES_BUCKET_ID)
    blobs = bucket.list_blobs(prefix=path)
    all_dataframes = []
    for blob in blobs:
        if blob.name.endswith(".csv"):
            print(f"Reading sql extarction file: {blob.name}")
            csv_content = blob.download_as_string()
            df = pd.read_csv(io.StringIO(csv_content.decode("utf-8")), sep=",")
            all_dataframes.append(df)
    combined_df = None
    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        tool_context.state["sql_queries_extraction_content"] = combined_df.to_string()
    else:
        tool_context.state["sql_queries_extraction_content"] = None
    return


async def modelling_orch_tool(
    question: str,
    tool_context: ToolContext,
):
    print("initializing state variables...")
    tool_context.state["hitl_feedback"] = ""
    tool_context.state["last_input"] = ""
    tool_context.state["data_model"] = None
    tool_context.state["entity_data_model"] = None
    tool_context.state["conceptual_data_model"] = None
    tool_context.state["logical_data_model"] = None
    tool_context.state["physical_data_model"] = None
    tool_context.state["validation_report"] = None

    await read_sql_extraction_content(tool_context=tool_context)
    return

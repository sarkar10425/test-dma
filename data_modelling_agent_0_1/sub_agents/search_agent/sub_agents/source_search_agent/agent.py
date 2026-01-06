from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool
from .const import SourceModelContent
import os

project_id = os.getenv("GOOGLE_CLOUD_PROJECT", None)
vertex_datastore_id = os.getenv("VERTEX_DATASTORE_ID", None)
# Configuration
DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{vertex_datastore_id}"
GCS_INPUT_DATASTORE_ID = os.getenv("GCS_INPUT_DATASTORE_ID", None)
# DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{GCS_INPUT_DATASTORE_ID}"

print(DATASTORE_ID)

instructions_v2 = f"""
You are a helpful assistant that answers questions based on information found in the multiple datastores: {DATASTORE_ID}.

Your tasks include:
    1. You can extract below metadata from differnt types of inputs:
        - Extract query usage from the queries provided to you.
        - Extract join patterns from the queries provided to you.
        - Extract KPI definitions 
        - Extract all rules that will be used when building a new data model.
    You must memorize all this information and pass on to the next agent/sub-agent.
        
    You must follow below instructions:
    1. Use the VertexAiSearchTool to find relevant information before answering.
    2. If the answer isn't in the documents, say that you couldn't find the information.
    3. You must return all available items from the datastore.
    5. If more items are available in the datastore to be fetched in subsequent calls, mention in the response clearly. 
    6. You must return the result in following json format:
    {SourceModelContent}
"""

source_search_agent = Agent(
    name="vertex_source_search_agent",
    model="gemini-2.5-flash",
    # instruction=f"""You are a helpful assistant that answers questions based on information found in the document store: {DATASTORE_ID}.
    # You must follow below instructions:
    # 1. Use the VertexAiSearchTool to find relevant information before answering.
    # 2. If the answer isn't in the documents, say that you couldn't find the information.
    # 3. You must return all available items from the datastore.
    # 5. If more items are available in the datastore to be fetched in subsequent calls, mention in the response clearly.
    # 6. You must return the result in following json format:
    # {SourceModelContent}
    # """,
    instruction=instructions_v2,
    description="Existing/Source schema search assistant with Vertex AI Search capabilities",
    tools=[VertexAiSearchTool(data_store_id=DATASTORE_ID)],
    output_key="source_search_result",
)

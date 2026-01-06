import os
from google.adk.agents import Agent
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from merlin.sub_agents.search_agent.tools import call_source_search_agent
from google.adk.tools.agent_tool import AgentTool
import datetime
from pathlib import Path
from google.adk.tools import VertexAiSearchTool
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool


OUTPUT_FORMAT = """
{
  "DataModelMetadataExtraction": {
    "ConceptualModelMetadata": {
      "CoreBusinessConcepts": [
        {"ConceptName": "Example Entity", "PriorityScore": 1, "HighLevelRelationship": "Relationship to another entity (e.g., 1:M with Order)"}
      ],
      "KeyBusinessProcesses": ["List major business activities"],
      "BusinessMetricsKPIs": ["List high-level metrics or KPIs (e.g., Revenue, CLV)"],
      "BusinessRulesHighLevel": ["Extract overarching constraints (e.g., 'Customer must have one primary address')"]
    },
    "LogicalModelMetadata": {
      "AttributesAndCharacteristics": [
        {"Entity": "Example Entity", "AttributeName": "example_field_name", "ConceptualDataType": "Identifier/Timestamp/Measurement", "Description": "Brief description of the field's business meaning"}
      ],
      "RelationshipCardinality": ["List entity relationships and their cardinality (e.g., Customer M:1 Address)"],
      "DataGranularityRequirements": ["Lowest level of detail required for analysis (e.g., transaction-level, daily summary)"]
    },
    "PhysicalModelMetadata_BigQuery": {
      "BigQueryDataTypes": [
        {"ConceptualDataType": "Identifier", "RecommendedBQType": "INT64 or STRING"},
        {"ConceptualDataType": "Measurement", "RecommendedBQType": "NUMERIC/BIGNUMERIC"}
      ],
      "StoragePerformanceStrategies": [
        {"Strategy": "Partitioning Key Recommendation", "Details": "Specify the recommended partitioning column (e.g., date, ingestion_time)", "PriorityScore": 1},
        {"Strategy": "Clustering Column Recommendation", "Details": "Specify recommended clustering columns (e.g., customer_id, product_sku)", "PriorityScore": 2},
        {"Strategy": "Modeling Pattern", "Details": "Denormalization/NESTED fields preference"}
      ],
      "NamingConventions": [
        {"Component": "Table/View", "Convention": "Style and Prefix/Suffix (e.g., snake_case, dim_)"},
        {"Component": "Column", "Convention": "Style (e.g., snake_case)"}
      ],
      "DataSecurityGovernance": ["Extract best practices (e.g., Authorized Views, Row-Level Security usage)"]
    },
    "PostProcessingSummary": {
      "PotentialConflicts": [
        {"Area": "Modeling Pattern", "BlueprintGuidance": "Suggests normalized 3NF", "BQGuidance": "Strongly recommends denormalized structures with NESTED fields", "ResolutionNote": "Flagged for review."}
      ]
    }
  }
}
"""
DATA_EXTRACTTION_INSTRUCTIONS_V2 = """
As an expert Data Modeling Agent, your task is to analyze two input documents: the "Industry Blueprint" and "BigQuery Best Practices." Your goal is to extract and structure essential metadata required for building **Conceptual, Logical, and Physical Data Models**.

### INSTRUCTIONS:
1.  **Analyze** the "Industry Blueprint" data to identify business context using '_blueprint_tool' tool.
2.  **Analyze** the "BigQuery Best Practices" to identify technical constraints and recommendations using '_bq_best_prac_tool' tool.
3.  **Analyze** the "User Responses" to identify user's response to some general queries using '_user_responses_tool' tool.
4.  **Populate** the required fields in the JSON output structure below. If a field is not explicitly present in the source documents, use the value "N/A".
5.  **Prioritization & Conflict Resolution:**
    * Assign a **Priority Score (1-5)** (1=Highest, 5=Lowest) to the extracted `CoreBusinessConcepts` and `StoragePerformanceStrategies` based on frequency and emphasis in the source texts.
    * Flag any direct contradictions between the Industry Blueprint's modeling needs and BigQuery's recommendations within the `PotentialConflicts` array.

    
"""

project_id = os.getenv("GOOGLE_CLOUD_PROJECT", None)
BQ_BEST_PRACTICES_DATASTORE_ID_ONLY = os.getenv("BQ_BEST_PRACTICES_DATASTORE_ID", None)
BLUEPRINT_DATASTORE_ID_ONLY = os.getenv("BLUEPRINT_DATASTORE_ID", None)
QUESTIONNAIRE_DATASTORE_ID_ONLY = os.getenv("QUESTIONNAIRE_DATASTORE_ID", None)

BQ_BEST_PRACTICES_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{BQ_BEST_PRACTICES_DATASTORE_ID_ONLY}"
BLUEPRINT_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{BLUEPRINT_DATASTORE_ID_ONLY}"
USER_RESPONSES_DATASTORE_ID = f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{QUESTIONNAIRE_DATASTORE_ID_ONLY}"


bigquery_best_practice_search_agent = Agent(
    name="bigquery_best_practice_search_agent",
    model="gemini-2.5-flash",
    instruction=f"""You are a helpful assistant that can find information in the datastore: {BQ_BEST_PRACTICES_DATASTORE_ID}.
    You must follow below instructions:
    1. Use the VertexAiSearchTool to find relevant information.
    2. You must capture all available items from the datastore and prepare a json like format to capture all information
    
    """,
    description="Existing/Source BigQuery best practices search assistant with Vertex AI Search capabilities",
    tools=[VertexAiSearchTool(data_store_id=BQ_BEST_PRACTICES_DATASTORE_ID)],
    output_key="bq_best_practices",
)

blueprint_search_agent = Agent(
    name="bigquery_best_practice_search_agent",
    model="gemini-2.5-flash",
    instruction=f"""You are a helpful assistant that can find information in the datastore: {BLUEPRINT_DATASTORE_ID}.
    You must follow below instructions:
    1. Use the VertexAiSearchTool to find relevant information.
    2. You must capture all available items from the datastore and prepare a json like format to capture all information
    
    """,
    description="Existing/Source Blueprint search assistant with Vertex AI Search capabilities",
    tools=[VertexAiSearchTool(data_store_id=BLUEPRINT_DATASTORE_ID)],
    output_key="blueprint_details",
)

user_responses_search_agent = Agent(
    name="bigquery_best_practice_search_agent",
    model="gemini-2.5-flash",
    instruction=f"""You are a helpful assistant that can find information in the datastore: {USER_RESPONSES_DATASTORE_ID}.
    You must follow below instructions:
    1. Use the VertexAiSearchTool to find relevant information.
    2. You must capture all available items from the datastore and prepare a json like format to capture all information
    
    """,
    description="Search assitant with Vertex AI Search capabilities, for user's existing responses for some questions.",
    tools=[VertexAiSearchTool(data_store_id=USER_RESPONSES_DATASTORE_ID)],
    output_key="user_responses",
)


async def call_bigquery_best_practice_search_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call source search agent."""

    agent_tool = AgentTool(agent=bigquery_best_practice_search_agent)

    bigquery_best_practice_search_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )

    return bigquery_best_practice_search_agent_output


async def call_blueprint_search_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call source search agent."""

    agent_tool = AgentTool(agent=blueprint_search_agent)

    blueprint_search_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )

    return blueprint_search_agent_output


async def call_user_responses_search_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call source search agent."""

    agent_tool = AgentTool(agent=user_responses_search_agent)
    user_responses_search_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    return user_responses_search_agent_output


metadata_agent = Agent(
    name="metadata_agent",
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-flash"),
    description="""Responsible to extract metadata from source data models""",
    instruction=f"""
      You are an helpful assistant to extract metadata **without any user's inputs**.
      
      **Tasks**
        - *Must* invoke the '_blueprint_tool', '_bq_best_prac_tool' and '_user_responses_tool' tools to search blueprint, bigquery best practices and user responses respectively.
        - Use '_blueprint_tool' tool to get information about industry blueprints, business domains, etc. Gather as many details as you can, do not miss anything
        - Use '_bq_best_prac_tool' tool to get information about destination data warehouse technology, best practices, etc. Gather as many details as you can, do not miss anything
        - Use '_user_responses_tool' tool to get user's responses that they provided as input. You will get information like modeling objective, business domain, current issues, etc. Gather as many details as you can, do not miss anything
        - If you are unable to fetch any data just put "N/A".
        - **Divide** your findings into 3 different parts, one for each tool. Make sure you are not missing out anything, and that you capture every minute detail available within these 3 tools.
    
    
    **Guardrails**
    - Do not ask the user for providing input data, always use the '_blueprint_tool', '_bq_best_prac_tool' and '_user_responses_tool' tools to get the blueprint, bigquery best practices, and user responses respectively, yourself.
    - Do not make up anything from your own knowledge.
    """,
    tools=[
        call_bigquery_best_practice_search_agent,
        call_blueprint_search_agent,
        call_user_responses_search_agent,
    ],
)

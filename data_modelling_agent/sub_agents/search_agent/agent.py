from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool
from .tools import call_source_search_agent, call_target_search_agent
from google.adk.agents.callback_context import CallbackContext

from google.adk.agents.invocation_context import InvocationContext
from google.adk.models.llm_response import LlmResponse


def update_response(callback_context: CallbackContext, llm_response: LlmResponse):
    print("inside 'update_response'")

    callback_context.state["readable_search_result"] = llm_response.content


# Configuration
# DATASTORE_ID = "projects/development-000/locations/global/collections/default_collection/dataStores/existing-schema_1753945258977"

EXTRACTION_OUTPUT_SCHEMA = """
{
  "METADATA_EXTRACTED_AT": null, // DateTime stamp of extraction
  "AGENT_ID": "SQL_AND_METADATA_EXTRACTOR_AGENT",

  "GOVERNANCE_AND_METHODOLOGY": {
    "PRECEDENCE_HIERARCHY": null, // e.g., ["USER_RULES", "KPI_LOGIC", "BEST_PRACTICES"] - To be filled by a prior/later agent.
    "TARGET_MODEL_PARADIGM": null, // e.g., "Dimensional Model (Star Schema)" - To be filled by a prior/later agent.
    "NAMING_CONVENTIONS": null,
    "AUDIT_FIELDS_MANDATED": [] // From instruction (k. Audit Fields)
  },

  "STRUCTURAL_REQUIREMENTS": { // From instruction (i. Data Structure Constraints)
    "DATA_VOLATILITY_INFO": { // For partitioning strategy
        "EXPECTED_REFRESH_FREQUENCY": null, // e.g., "Daily", "Hourly"
        "VOLATILITY_LEVEL": null // e.g., "High", "Low"
    },
    "RELATIONSHIP_CONSTRAINTS": [ // From instruction (i. Relationship and Cardinality)
      {
        "SOURCE_TABLE": null,
        "TARGET_TABLE": null,
        "CARDINALITY": null, // e.g., "One-to-Many", "Many-to-Many"
        "JOIN_KEY_REQUIREMENTS": [] // e.g., ["table_a.id = table_b.id"]
      }
    ]
  },

  "KPI_AND_LOGIC_DECOMPOSITION": { // From instruction (j. KPI and Logic Decomposition)
    "KPI_FORMULAS": [
      {
        "KPI_NAME": null,
        "AGGREGATION_LOGIC": null, // e.g., "SUM", "AVG"
        "CALCULATION_FORMULA": null, // The full formula or logic
        "REQUIRED_GRAIN": null, // e.g., "Daily, By Store"
        "TARGET_MODEL_FIELDS_REQUIRED": [] // Fields in the new model needed for this KPI
      }
    ],
    "MAPPING_GAPS": [] // From instruction (j. Mapping Gap Analysis)
  },

  "SQL_ANALYSIS_AND_LINEAGE": { // From instructions (a. through h.)
    "TABLE_NAMES": {
      "BASE_TABLES": [], // From instruction (a. Table_Names_base) e.g., [["SCHEMA.TABLE_A", "a"]]
      "DERIVED_TABLES": [] // From instruction (b. Table_Names_derived) e.g., [["cte_sales", "s"]]
    },

    "COLUMN_LINEAGE": {
      "COLUMN_LIST_BASE": [], // From instruction (c. Column_list_base) e.g., ["SCHEMA.TABLE_A.column1"]
      "COLUMN_LIST_DERIVED": [], // From instruction (d. Column_list_derived)
      "COLUMN_NESTED_QUERY": [], // From instruction (f. Column_nested_query)

      "DERIVED_COLUMN_LOGIC": [ // From instruction (e. Column_list_derived_logic)
        {
          "DERIVED_COLUMN": null, // e.g., "derived_table.calculated_metric"
          "LOGIC_ARRAY": [] // e.g., ["base.col1 + base.col2", "COALESCE(base.col1, 0)"]
        }
      ],
      "MISSING_COLUMNS": [] // From instruction (h. Missed_Columns)
    },

    "DETAILED_CONSTRUCTS": {
      "CASE_STATEMENTS": [ // From instruction (g. Case_Statements)
        {
          "ALIAS": null,
          "LOGIC_EXTRACTED": null, // The full WHEN/THEN/ELSE logic
          "FILTER_COLUMN": null // The table.column applied on the filter/condition
        }
      ],
      "ERROR_HANDLING": [] // From instruction (Error Handling) - List of errors encountered
    }
  },

  "BUSINESS_METADATA": { // From instruction (k. Documentation and Traceability)
    "TABLE_BUSINESS_DEFINITIONS": [], // e.g., [{"table_name": "dim_customer", "definition": "..."}]
    "COLUMN_BUSINESS_DEFINITIONS": [] // e.g., [{"column_name": "customer_pk", "term": "..."}]
  }
}
"""

DATA_EXTRACTTION_INSTRUCTIONS = f"""
    **You must act as an expert SQL parser and data lineage extractor** to analyze a set of SQL queries provided as input, which may contain User Defined Functions (UDFs) and comments.
        - **Robustness**: You must be robust to variations in SQL syntax (e.g., capitalization of keywords, different quoting styles for identifiers, etc.).
        - **Error Handling**: You must gracefully handle malformed or erroneous input SQL. In case of an error, indicate the query index and the error encountered, but still process valid queries.
        - You must **ignore all statements that are commented** within the SQL queries.
        - You must accurately process different SQL constructs: `SELECT`, `FROM`, `WHERE`, `JOIN`, `GROUP BY`, `HAVING`, subqueries, and Common Table Expressions (CTEs).
        - You must **Correctly resolve table and column aliases** to identify the underlying base tables and columns.
        - Your task is to identify and extract the following specific metadata from the analyzed queries:
            a. **Table_Names_base**: Identify all table names that are **base tables**. These are tables that are not derived or Common Table Expressions (CTEs), but may appear in subqueries or nested queries.
                - **Format**: Provide an array of the base table name along with any assigned table alias (e.g., `[["SCHEMA.TABLE_A", "a"], ["SCHEMA.TABLE_B", "b"]]`).

            b. **Table_Names_derived**: Identify all table names that are **derived tables** created *only* within the SQL query (e.g., from subqueries in the FROM clause or CTEs).
                - **Lineage Trace**: For derived tables built on top of other derived tables, **trace back to the ultimate base tables**.
                - **Format**: Provide an array of the derived table name (or alias) along with any assigned table alias (e.g., `[["derived_table_1", "d1"], ["cte_2", "c2"]]`).

            c. **Column_list_base**: Extract all column names that originate from **base tables**. These columns may be used in the `SELECT` list (including nested subqueries), `WHERE` clauses, `JOIN` conditions, aggregation functions, and `CASE` expressions. You must be very thorough in identifying all column usage.
                - **Restriction**: The columns must be from **base tables ONLY** and not derived tables.
                - **Format**: The list should follow the format `"table.column"` only if the table qualifier is available in the input SQL query.
                - **Wildcard Handling**: For `SELECT *`, list it as `table_name.*`. If possible, attempt to resolve `*` to individual columns (but do not assume schema availability).

            d. **Column_list_derived**: Extract all column names that are **derived columns** (columns created or calculated within the query). These columns may be used in subqueries, nested queries, filter conditions, join conditions, where clause, case statements using Derived tables ONLY and not base tables within the SQL query.
                - **Inclusion**: Include any derived columns that are part of the `SELECT` clause and fulfill the specified precedence condition.
                - **Format**: The list of column should follow the format `"table.column"` only if the table qualifier is available in the input SQL query.

            e. **Column_list_derived_logic**: Extract the **creation logic** for all derived columns identified.
                - **Explicit Mapping**: Show the explicit mapping from derived columns to their source columns (e.g., `derived_col = base_col1 + base_col2`), handling functions and complex expressions where possible. If a full derivation is not feasible, make a best effort.
                - **Multiple Logics**: If the same derived column name has multiple logics, provide all logics as an array.
                - **Inclusion**: Include the logic for any derived columns that are part of the `SELECT` clause and fulfill the specified precedence condition.
                - **Format**: The column reference should follow the format `"table.column"` only if the table qualifier is available.

            f. **Column_nested_query**: Select any columns that appear after the `SELECT` keyword within **nested queries or subqueries**, including those present in the `WHERE` clause.

            g. **Case_Statements**: Analyze all `CASE` statements and extract three components: the **logic** within the `CASE`, their final **alias** provided, and the **table_name.column_name** on which any internal filter or condition is applied.

            h. **Missed_Columns**: Use a dedicated array to flag any cases where you were unable to definitively identify the source of a column. Include a descriptive explanation of the issue if possible. This array should ideally be empty.
            i. **Data Structure Constraints**: You must extract explicit requirements for the new data model's structural integrity:
                - **Relationship and Cardinality**: Identify required **cardinality** (e.g., one-to-one, one-to-many) and the specific **join key requirements** for all new inter-table relationships.
                - **Data Integrity Constraints**: Extract rules regarding mandatory constraints, including required **NOT NULL** status, specified **unique keys** (beyond the primary key), and any mandatory **default values** for target columns.
                - **Data Volatility**: Extract metadata regarding the expected **data refresh frequency** and **data volatility** to inform partitioning and model persistence strategies.
            j. **KPI and Logic Decomposition**: You must meticulously decompose and map all provided KPI inputs:
                - **KPI Logic Extraction**: Extract the precise **aggregation logic** (`SUM`, `AVG`, `COUNT`), the full **calculation formula**, the required **grain** (level of detail), and the specific **target model fields** necessary for the calculation.
                - **Mapping Gap Analysis**: Analyze existing Source-to-Target (S2T) inputs and blueprints to identify and flag any **missing or incomplete field mappings** between source schemas and target model requirements.
            k. **Documentation and Traceability**: You must extract metadata essential for the final model's documentation and auditability:
                - **Business Definitions**: Extract all associated **business definitions or glossary terms** for all tables and columns from the input blueprints and rules.
                - **Audit Fields**: Extract all explicit requirements for **audit fields** (e.g., `created_timestamp`, `updated_by_user`) that must be mandated and included in the final target data model.
        **Capture the output in below format:**
        {EXTRACTION_OUTPUT_SCHEMA}
                """

RETRIEVE_INSTRUCTIONS = f"""

    1. Identify if the search is for source or target. If source or respective synonyms is present execute 'call_source_search_agent' tool.
    2. If target or respective synonyms is present execute 'call_target_search_agent' tool. If nothing is present return error to user.
    3. If root_agent tells that the user is looking to start from where they left off, then you must execute call_target_search_agent tool and fetch information about the saved data model that you generated when user left. 
        - Once call_target_search_agent tool is executed, you must execute the 'call_source_search_agent' tool also, and validate the model from 'call_target_search_agent' with the data received from call_source_search_agent tool.
        - Present the entire data model from call_target_search_agent to the user, and ask the user to validate it once.
        - If nothing is present return error to user.
"""

search_agent = Agent(
    name="search_agent",
    model="gemini-2.5-flash",
    # instruction="""
    # You are a search agent who retrieves relevant schema/metadata information from datastore using tools call_source_search_agent or call_target_search_agent.
    # You must be able to analyse the current data model, queries, schemas and data types.
    # You must follow below instructions:
    # 1. Identify if the search is for source or target. If source or respective synonyms is present execute call_source_search_agent tool.
    # 2. If target or respective synonyms is present execute call_target_search_agent tool. If nothing is present return error to user.
    # 3. If root_agent tells that the user is looking to start from where they left off, then you must execute call_target_search_agent tool and fetch information about the saved data model that you generated when user left.
    #     - Once call_target_search_agent tool is executed, you must execute the call_source_search_agent tool also, and validate the model from call_target_search_agent with the data received from call_source_search_agent tool.
    #     - Present the entire data model from call_target_search_agent to the user, and ask the user to validate it once.
    #     - If nothing is present return error to user.
    # 4. You must not generate any schema/metadata information by yourself.
    # 5.You must read the response from the tool in any format and return output in a human readale format
    # """,
    instruction=f"""
    You are a search agent who can do the following for the users:
    - Extract Metadata: Extract metadata for the inputs provided using tool - 'call_source_search_agent',and share all extracted information with the root_agent
    - Retrieve Information: Retrieve information from datastore using tools - 'call_source_search_agent' or 'call_target_search_agent', and share information with user directly.
    
    **STEP1**
    You must first identify :
    - If the root_agent tells you that user is looking to search information from provided or source data model, it means that you should go with **Retrieve Information** and **MUST** follow below Instructions:
    {RETRIEVE_INSTRUCTIONS}
    - If the 'modelling_orchestrator_agent' tell you that user is looking to create a new model, then it means that you should go with **Extract Metadata** and **MUST** follow below instructions:
    {DATA_EXTRACTTION_INSTRUCTIONS}
    
    You must follow below instructions:
    1. Identify if the search is for source or target. If source or respective synonyms is present execute 'call_source_search_agent' tool.
    2. If target or respective synonyms is present execute 'call_target_search_agent' tool. If nothing is present return error to user.
    3. If root_agent tells that the user is looking to start from where they left off, then you must execute call_target_search_agent tool and fetch information about the saved data model that you generated when user left. 
        - Once call_target_search_agent tool is executed, you must execute the 'call_source_search_agent' tool also, and validate the model from 'call_target_search_agent' with the data received from call_source_search_agent tool.
        - Present the entire data model from call_target_search_agent to the user, and ask the user to validate it once.
        - If nothing is present return error to user.
    
    **GUARDRAILS**
    - You must **NOT** generate any schema/metadata information by yourself.
    - You must read the response from the tool in any format and **return output in a human readale** format.

    """,
    description="An agent to search for schema or metadata information. Identifies whether the search is for a 'source' or 'target' schema. Accodingly it will use one of the two tools: call_source_search_agent, call_target_search_agent",
    tools=[
        call_source_search_agent,
        call_target_search_agent,
    ],
    after_model_callback=update_response,
    output_key="search_agent_result",
)

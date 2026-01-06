import os

GCS_BUCKET = os.getenv("MODEL_OUTPUT_BUCKET", "modelling_agent_output_dev")
GCS_PATH = ""
config = {
    "gcp_project_id": "deid-sandbox",
    "gcp_location": "us-central1",
    "gemini_model_name": "gemini-2.0-flash",
    "domain_context": "Retail E-commerce Analytics",
    "design_mode_params": {
        "kpis_config_file": "kpis.json",
        "existing_model_schema_file": "existing_schema.json",
    },
    "generation_config": {
        "temperature": 0.5,
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 8192,
    },
    "modeling_guidelines": {
        "dimension_table_prefix": "Dim",
        "fact_table_prefix": "Fact",
        "date_dimension_name": "Dim_Date",
        "raw_table_prefix": "raw",
        "staging_table_prefix": "stg",
        "bronze_table_prefix": "bronze",
        "gold_aggregate_table_prefix": "agg",
        "gold_mart_table_prefix": "mrt",
    },
    "output_personas": {
        "data_modeler": [
            "Logical Model & Physical Suggestions",
            "Mermaid ER Diagram Code",
            "Semantic Model Skeleton",
            "Refinement Questions (with Rationale)",
        ],
        "data_engineer": [
            "Logical Model & Physical Suggestions",
            "SQL DDL for Core Tables (Dims & Facts)",
            "BigQuery Detailed Metadata (JSON)",
            "Dataform SQLX (Core Tables)",
            "Conceptual Data Product Flow",
        ],
        "all": [
            "Create Entity Classification",
            "Create Conceptual Model",
            "Create Logical Data Model(LDM)",
            "Create Physical Data Model(PDM)",
        ],
    },
    "active_persona": "All",
}

DDL_TASK = "SQL DDL for Core Tables (Dims & Facts)"
BQ_METADATA_TASK = "BigQuery Detailed Metadata (JSON)"
BQ_LOGICAL_MODEL_TASK = "Logical Model & Physical Suggestions"
CONCEPTUAL_MODEL_TASK = "Create Conceptual Model"
LDM_TASK = "Create Logical Data Model(LDM)"
PDM_TASK = "Create Physical Data Model(PDM)"
VALIDATION_TASK = "Data Model Validation"

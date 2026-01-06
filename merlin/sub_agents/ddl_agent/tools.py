from google.adk.tools.tool_context import ToolContext
import os
from .utils.bq import cleanup_ddl, validate_ddl, execute_bq_ddl, create_bigquery_dataset


def ddl_execution(tool_context: ToolContext):
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", None)
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set.")

    dataset_id = os.getenv("BQ_DATASET_ID", None)
    if not dataset_id:
        return {
            "status": "error",
            "detail": "Please provide dataset_id where the table needs to be created.",
        }
    dataset_to_be_deleted = None
    try:
        error = create_bigquery_dataset(project_id, dataset_id, dataset_to_be_deleted)
        if error:
            return error
    except Exception as e:
        print("Dataset already exists.")
    ddl = tool_context.state["physical_data_model"]

    cleaned_ddl = cleanup_ddl(ddl, project_id, dataset_id)
    is_valid_ddl = validate_ddl(cleaned_ddl)
    if is_valid_ddl:
        os.system(f"bq {cleaned_ddl}")
        return execute_bq_ddl(cleaned_ddl)
    return is_valid_ddl

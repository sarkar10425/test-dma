from google.adk.tools.tool_context import ToolContext
import os
from .utils.bq import cleanup_ddl, validate_ddl, execute_bq_ddl, create_bigquery_dataset


def ddl_execution(tool_context: ToolContext):
    project_id = tool_context.state["project_id"]
    dataset_id = tool_context.state.get("dataset_id", None)
    if not dataset_id:
        return {
            "status": "error",
            "detail": "Please provide dataset_id where the table needs to be created.",
        }
    dataset_to_be_deleted = tool_context.state["dataset_to_be_deleted"]
    error = create_bigquery_dataset(project_id, dataset_id, dataset_to_be_deleted)
    if error:
        return error
    ddl = tool_context.state["ddl"]
    cleaned_ddl = cleanup_ddl(ddl, project_id, dataset_id)
    tool_context.state["ddl"] = ddl
    is_valid_ddl = validate_ddl(cleaned_ddl)
    if is_valid_ddl:
        os.system(f"bq {cleaned_ddl}")
        return execute_bq_ddl(cleaned_ddl)
    return is_valid_ddl

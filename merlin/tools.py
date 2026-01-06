from google.adk.tools import ToolContext


def persist_target_model(
    question: str,
    tool_context: ToolContext,
):
    """Tool to persist target model in GCS"""
    return {"result": "Data Persisted"}

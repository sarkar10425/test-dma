from google.cloud import storage

# from data_modelling_agent.sub_agents.modelling_orchestrator_agent.const import GCS_BUCKET
# from data_modelling_agent.sub_agents.modelling_orchestrator_agent.sub_agents.modeller_agent.const import BQ_METADATA_TASK
# from data_modelling_agent.sub_agents.modelling_orchestrator_agent.sub_agents.modelling_process_loop_agent.sub_agents.modeller_agent.const import BQ_METADATA_TASK


def cleanup_metadata(metadata):
    metadata_lines = metadata.split("\n")
    cleaned_metadata_lines = []
    for line in metadata_lines:
        if "```" in line:
            continue
        cleaned_metadata_lines.append(line.strip())
    cleaned_metadata = "\n".join(cleaned_metadata_lines)
    return cleaned_metadata

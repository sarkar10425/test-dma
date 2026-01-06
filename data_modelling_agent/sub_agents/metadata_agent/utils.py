from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from merlin.sub_agents.search_agent.tools import call_source_search_agent
from merlin.sub_agents.modelling_orchestrator_agent.utils import (
    copy_local_directory_to_gcs,
)
import os
import glob
from .const import GCS_BUCKET_NAME, GCS_PREFIX
from google.cloud import storage
import google.auth
import google.auth.transport.requests

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", None)


def check_if_exists(folder_path, file_name):
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f"{GCS_PREFIX}/{folder_path}/{file_name}")
        return blob.exists()
    except Exception as e:
        return f"Error occurred: {e}"


def read_from_gcs(folder_path, file_name):
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f"{GCS_PREFIX}/{folder_path}/{file_name}")
        return blob.download_as_text(encoding="utf-8")
    except Exception as e:
        return f"Error: {e}"


def copy_local_metadata_to_gcs(local_folder, bucket_name, gcs_path):
    print("****copying the generated metadata to GCS****")
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(bucket_name)
    except Exception as e:
        print(f"Error: {e}")

    # Ensure gcs_path ends with a slash if it's a folder prefix
    if gcs_path and not gcs_path.endswith("/"):
        gcs_path += "/"

    gcs_uri = None
    assert os.path.isdir(local_folder)

    for local_file in glob.glob(local_folder + "/**"):
        if not os.path.isfile(local_file):
            continue
        # Calculate remote path correctly
        relative_file_path = os.path.basename(local_file)
        remote_path = f"{gcs_path}{local_folder}/{relative_file_path}"

        blob = bucket.blob(remote_path)
        blob.upload_from_filename(local_file)
        # Capture the last uploaded URI (or modify to return a list if needed)
        gcs_uri = f"gs://{bucket_name}/{remote_path}"

    print(f"Last gcs_uri created: {gcs_uri}")
    return gcs_uri


def store_extracted_metadata(folder_name, metadata_content):
    print(f"folder_name: {folder_name}")

    with open(f"{folder_name}/metadata.txt", "w") as f:
        f.write(metadata_content)
    print("Artifact(s) saved locally!")
    GCS_PREFIX = "cooked_metadata"
    GCS_BUCKET_NAME = "extracted_metadata"
    gcs_uri = copy_local_metadata_to_gcs(
        folder_name, bucket_name=GCS_BUCKET_NAME, gcs_path=GCS_PREFIX
    )
    print(f"Artifact(s) saved to GCS bucket: {gcs_uri}")
    return gcs_uri

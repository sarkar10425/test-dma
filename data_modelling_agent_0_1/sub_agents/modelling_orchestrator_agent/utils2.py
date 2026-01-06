import os
import shutil
import glob
from google.cloud import storage
from .const import GCS_BUCKET, GCS_PATH
from typing import Optional
import google.auth
import google.auth.transport.requests
import requests

creds, project = google.auth.default()


project_id = os.getenv("GOOGLE_CLOUD_PROJECT", None)
DATASTORE_ID = os.getenv("VERTEX_DATASTORE_ID", None)
AGENT_OUTPUT_DATA_STORE_ID = os.getenv("GENERATED_DATA_MODEL_DATASTORE_ID", None)


def del_dir(directory_to_delete):
    if os.path.exists(directory_to_delete):
        try:
            shutil.rmtree(directory_to_delete)
            print("Directory and its contents deleted successfully.")
        except OSError as e:
            print(f"Error: {e}")


def ingest_to_datastore(
    URI,
    RECONCILIATION_MODE: Optional[str] = "INCREMENTAL",
    PROJECT_ID: Optional[str] = project_id,
    AGENT_OUTPUT_DATA_STORE_ID: Optional[str] = AGENT_OUTPUT_DATA_STORE_ID,
):
    try:
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        if "gs://" not in URI:
            URI = "gs://" + f"{GCS_BUCKET}/" + URI
        end_url = f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/collections/default_collection/dataStores/{AGENT_OUTPUT_DATA_STORE_ID}/branches/0/documents:import"
        print(f"end_url: {end_url}")
        headers = {
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json",
        }
        print(f"headers: {headers}")
        payload = {
            "gcsSource": {
                "inputUris": URI,
            },
            "reconciliationMode": {RECONCILIATION_MODE},
        }
        print(f"payload: {payload}")

        res = requests.post(end_url, json=payload, headers=headers)
        if res.status_code == 200:
            return f"Initiated an incremental import to the Datastore: {AGENT_OUTPUT_DATA_STORE_ID}"
        else:
            print(f"API Request Failed with Status Code: {res.status_code}")
            return res.json()
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}


def copy_local_directory_to_gcs(
    local_folder, bucket_name=GCS_BUCKET, gcs_path=GCS_PATH
):
    """Recursively copy a directory of files to GCS.

    local_path should be a directory and not have a trailing slash.
    """
    print("****copying the new artifact to GCS****")
    gcp_project = os.getenv("GOOGLE_CLOUD_PROJECT", default="deid-sandbox")
    storage_client = storage.Client(project=gcp_project)
    bucket = storage_client.bucket(bucket_name)

    gcs_path = gcs_path + local_folder
    gcs_uri = None
    assert os.path.isdir(local_folder)
    for local_file in glob.glob(local_folder + "/**"):
        if not os.path.isfile(local_file):
            continue
        remote_path = os.path.join(gcs_path, local_file[1 + len(local_folder) :])
        gcs_uri = remote_path
        blob = bucket.blob(remote_path)
        blob.upload_from_filename(local_file)
    print(f"gcs_uri created with artifact: {gcs_uri}")
    return gcs_uri


def save_artifacts(model_name, model_content, folder_name):
    with open(f"{folder_name}/{model_name}.txt", "w") as f:
        f.write(model_content)
    gcs_uri = copy_local_directory_to_gcs(folder_name)
    print("Artifact(s) saved successfully")

    # ingest new artifact to datastore
    # out = ingest_to_datastore(URI=gcs_uri)
    # print(f"out: {out}")
    # print("New artifact(s) ingested successfully")

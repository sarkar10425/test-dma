import os
import shutil
import glob
import json
from typing import Optional
import requests
from google.cloud import storage
import google.auth
import google.auth.transport.requests

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", None)
DATASTORE_ID = os.getenv("VERTEX_DATASTORE_ID", None)
AGENT_OUTPUT_DATA_STORE_ID = os.getenv("GENERATED_DATA_MODEL_DATASTORE_ID", None)
GCS_BUCKET_NAME = os.getenv("MODEL_OUTPUT_BUCKET", None)
GCS_PREFIX = os.getenv("TARGET_GCS_PREFIX", None)

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
creds, _ = google.auth.default(scopes=SCOPES)


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
    PROJECT_ID: Optional[str] = PROJECT_ID,
    AGENT_OUTPUT_DATA_STORE_ID: Optional[str] = AGENT_OUTPUT_DATA_STORE_ID,
):
    try:
        if not creds.valid:
            auth_req = google.auth.transport.requests.Request()
            creds.refresh(auth_req)

        if not URI.startswith("gs://"):
            final_uri = f"gs://{GCS_BUCKET_NAME}/{GCS_PREFIX}/{URI}".replace("//", "/")
            # incase prefix is empty, leave gs://
            final_uri = final_uri.replace("gs:/", "gs://")
        else:
            final_uri = URI

        print(f"Importing from URI: {final_uri}")

        end_url = f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/collections/default_collection/dataStores/{AGENT_OUTPUT_DATA_STORE_ID}/branches/0/documents:import"

        headers = {
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json",
        }
        print(f"headers: {headers}")

        payload = {
            "gcsSource": {
                "inputUris": [final_uri],
            },
            "reconciliationMode": RECONCILIATION_MODE,
        }

        print(f"Payload: {json.dumps(payload, indent=2)}")

        res = requests.post(end_url, json=payload, headers=headers)

        if res.status_code == 200:
            # Note: The API actually returns a long-running Operation object.
            print(f"Import LRO started: {res.json().get('name')}")
            return f"Initiated an incremental import to the Datastore: {AGENT_OUTPUT_DATA_STORE_ID}"
        else:
            print(f"API Request Failed with Status Code: {res.status_code}")
            print(f"Response: {res.text}")
            return res.json()

    except Exception as e:
        print(f"Exception Occurred: {e}")
        return {"error": f"An unexpected error occurred: {e}"}


def copy_local_directory_to_gcs(
    local_folder, bucket_name=GCS_BUCKET_NAME, gcs_path=GCS_PREFIX
):
    print("****copying the new artifact to GCS****")
    # Use the explicitly defined PROJECT_ID if possible for consistency
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)

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


def save_artifacts(model_name, model_content, folder_name):
    with open(f"{folder_name}/{model_name}.txt", "w") as f:
        f.write(model_content)
    gcs_uri = copy_local_directory_to_gcs(folder_name)
    print("Artifact(s) saved successfully")

    # ingest new artifact to datastore
    out = ingest_to_datastore(URI=gcs_uri)
    print(f"out: {out}")
    print("New artifact(s) ingested successfully")

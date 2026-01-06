# # import base64
# import json
# import vertexai
# from vertexai.generative_models import GenerativeModel, Part, SafetySetting
# import pandas as pd
# from google.cloud import storage
# import os
# import pdb
# from concurrent.futures import ThreadPoolExecutor, as_completed

# # from google.adk.tools import ToolContext
# from .prompt import extraction_prompt

# PROJECT_ID = "development-000"
# LOCATION_ID = "us-central1"
# BUCKET_NAME = "modelling_agent_inputs_dev"
# GCS_PATHS_LIST_FILE = "/Users/abhijat/Downloads/BigQueryModellingAgent/repo/BigQueryModellingAgent/data_modelling_agent_v2/sub_agents/metadata_agent/path_file.txt"
# CHECKPOINT_FILE = "processing_checkpoint.json"
# # OUTPUT_CSV_FILE = "/Users/abhijat/Downloads/BigQueryModellingAgent/repo/BigQueryModellingAgent/mis_output_test.csv"
# OUTPUT_CSV_FILE = "gs://sql_data_extraction/extracted_data/mis_output_test.csv"

# BATCH_SIZE = 40

# safety_settings = [
#     SafetySetting(
#         category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
#         threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE,
#     ),
#     SafetySetting(
#         category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
#         threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE,
#     ),
# ]


# def save_to_gcs(bucket_name):
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)


# # def get_gcs_file_paths(bucket_name):
# #     storage_client = storage.Client()
# #     bucket = storage_client.bucket(bucket_name)
# #     blobs = bucket.list_blobs()
# #     file_paths = [f"gs://{bucket_name}/{blob.name}" for blob in blobs]
# #     with open(GCS_PATHS_LIST_FILE, "w") as f:
# #         for file_path in file_paths:
# #             f.write(file_path + "\n")


# def extract_details(sql_query):  # for table-alias mapping
#     # try:
#     vertexai.init(project=PROJECT_ID, location=LOCATION_ID)
#     model = GenerativeModel(
#         "gemini-2.5-flash",
#         system_instruction="""You a database analyst expert in writing and understanding sql queries .you are also a business expert in financial investments like mutual funds (MFs), alternative investment funds (AIFs), insurance companies and other financial institutions.""",
#     )

#     generation_config = {
#         "max_output_tokens": 8192,
#         "temperature": 0.1,
#         "top_p": 0.9,
#     }
#     try:
#         responses = model.generate_content(
#             [extraction_prompt + sql_query],
#             generation_config=generation_config,
#             # safety_settings=safety_settings,
#             stream=False,
#         )
#         # return print(responses.text)
#         raw_text = str(responses.candidates[0].content.parts[0].text)
#         # 1. Aggressively strip markdown code fences and leading/trailing whitespace
#         cleaned_json = raw_text.strip()
#         if cleaned_json.startswith("```json"):
#             cleaned_json = cleaned_json[len("```json") :]
#         if cleaned_json.startswith("```"):
#             cleaned_json = cleaned_json[len("```") :]
#         if cleaned_json.endswith("```"):
#             cleaned_json = cleaned_json[: -len("```")]

#         print(f"@@@@@@text: {responses.candidates[0].content.parts[0].text}")
#         return cleaned_json.strip()
#     except Exception as e:
#         print(
#             f"Response Generation Error in extract_details(). Skipping this query : {sql_query} "
#         )
#         return ""


# def process_sql_from_gcs(gcs_path):
#     # pdb.set_trace()
#     try:
#         storage_client = storage.Client()
#         bucket = storage_client.bucket(BUCKET_NAME)
#         # Calculates blob name from gcs_path by removing the 'gs://BUCKET_NAME/' prefix
#         blob_name = gcs_path.replace(f"gs://{BUCKET_NAME}/", "")
#         blob = bucket.blob(blob_name)
#         content = blob.download_as_string()
#         if not content.strip():
#             print(f"Warning: File {gcs_path} is empty. Skipping.")
#             return None
#         print(f"content: {content.decode('utf-8')}")
#         queries = content.decode("utf-8").split("\n")
#         print(f"queries: {queries}")
#         try:
#             extracted_content = []
#             for sql_query in queries:
#                 try:
#                     response = extract_details(sql_query)
#                 except json.JSONDecodeError as e:
#                     response = ""
#                 if response != "" and response is not None:
#                     response_json = json.loads(response)
#                     response_json["GCS_Path"] = gcs_path
#                     print(f"response_json: {response_json}")
#                     extracted_content.append(response_json)
#             print(f"extracted_content type: {type(extracted_content)}")
#             print(f"extracted_content: {extracted_content}")
#             return extracted_content
#         except json.JSONDecodeError as e:
#             print(f""" Error decoding JSON for {sql_query}""")
#     except json.JSONDecodeError as e:
#         print(
#             f""" Error decoding JSON from model for file {gcs_path}. Response was: {response}. Error: {e}"""
#         )
#         # return None
#     except Exception as e:
#         print(f""" Error processing file {gcs_path} :{e}""")
#         # return False


# def process_file(gcs_path):
#     try:
#         if ".txt" in gcs_path:
#             response = process_sql_from_gcs(gcs_path)
#         if response:
#             return pd.json_normalize(response, meta=["Purpose"])
#         return None  # Indicate failure
#     except Exception as e:
#         print(f"Error processing {gcs_path}: {e}")
#         return None


# def process_file_future(gcs_path):
#     try:
#         if ".txt" in gcs_path:
#             print("in process_file_future() 1")
#             response = process_sql_from_gcs(gcs_path)
#         print(f"response inside process() :{response}")
#         if response:
#             print("in process_file_future() 2")
#             temp_df = pd.json_normalize(response, meta=["Purpose"])
#             return temp_df, gcs_path
#         print("in process_file_future() 3")
#         return None  # Indicate failure
#     except Exception as e:
#         print(f"Error processing {gcs_path}: {e}")
#         return None


# def main():
#     try:
#         final_df = pd.DataFrame()
#         processed_files = set()
#         skip_count = 0

#         # Check if output CSV exists and load it
#         if os.path.exists(OUTPUT_CSV_FILE):
#             try:
#                 final_df = pd.read_csv(OUTPUT_CSV_FILE)
#             except pd.errors.EmptyDataError:
#                 print("Output CSV is empty, starting fresh.")
#             except pd.errors.ParserError:
#                 print("Error parsing existing CSV. Starting fresh.")
#         else:
#             print("Output CSV not found!!! Creating one..")

#         # Load checkpoint or initialize
#         if os.path.exists(CHECKPOINT_FILE):
#             with open(CHECKPOINT_FILE, "r") as f:
#                 checkpoint = json.load(f)
#                 processed_files = set(checkpoint.get("processed_files", []))

#         # Read GCS paths from the text file
#         all_gcs_paths = []
#         with open(GCS_PATHS_LIST_FILE, "r") as f:
#             print("350")
#             for line in f:
#                 print(line.strip())
#                 all_gcs_paths.append(line.strip())
#         # Download the GCS path list file and then read from it
#         # if not download_gcs_file(GCS_PATHS_LIST_FILE, LOCAL_PATHS_LIST_FILE):
#         #     print("Could not download the GCS path file. Exiting.")
#         #     return

#         # with open(LOCAL_PATHS_LIST_FILE, "r") as f:
#         #     # Filter out any empty lines
#         #     all_gcs_paths = [line.strip() for line in f if line.strip()]

#         # Process files in batches
#         futures = None
#         with ThreadPoolExecutor(max_workers=20) as executor:
#             for i in range(0, len(all_gcs_paths), BATCH_SIZE):
#                 batch = all_gcs_paths[i : i + BATCH_SIZE]
#                 batch_df = pd.DataFrame()
#                 newly_processed = set()
#                 futures = [
#                     executor.submit(process_file_future, gcs_path)
#                     for gcs_path in batch
#                     if gcs_path not in processed_files
#                 ]

#             for future in as_completed(futures):
#                 result = future.result()
#                 print(f"result:{result}")

#                 if result is not None:
#                     df, gcs_path_from_future = result
#                     batch_df = pd.concat([batch_df, df], ignore_index=True)
#                     newly_processed.add(gcs_path_from_future)

#                 # The commented lines show an alternative/previous logic
#                 # batch_df = pd.concat([batch_df, result], ignore_index=True)
#                 # newly_processed.add(gcs_path) #Needs to be the original gcs_path, not the result
#                 else:
#                     skip_count += 1

#             # The original commented batch processing loop (Alternative to futures):
#             # for gcs_path in batch:
#             #     if gcs_path not in processed_files:
#             #         try:
#             #             if ".txt" in gcs_path:
#             #                 response = process_sql_from_gcs(gcs_path)
#             #                 if response:
#             #                     temp_df = pd.json_normalize(response, meta=['Purpose'])
#             #                     batch_df = pd.concat([batch_df, temp_df], ignore_index=True)
#             #                     newly_processed.add(gcs_path)
#             #         except Exception as e:
#             #             print(f"Error processing {gcs_path} in batch: {e}")
#             #             skip_count += 1
#             #         else:
#             #             skip_count += 1

#             if not batch_df.empty:  # only append if there are successful processes
#                 final_df = pd.concat([final_df, batch_df], ignore_index=True)
#                 processed_files.update(newly_processed)

#             # Update checkpoint after each batch (more frequent checkpoints)
#             checkpoint = {"processed_files": list(processed_files)}
#             with open(CHECKPOINT_FILE, "w") as f:
#                 json.dump(checkpoint, f)

#             final_df.to_csv(OUTPUT_CSV_FILE, index=False)

#             print(f"Completed batch. Processed {len(processed_files)} files.")

#         print(
#             f"Processing complete. Total processed: {len(processed_files)} files. Skipped {skip_count} files"
#         )

#     except Exception as e:
#         print(f"An error occurred: {e}")


# if __name__ == "__main__":
#     main()

# # async def extract_from_sql_queries(
# #         tool_context: ToolContext,
# #         ):
# #     """Run to extract information from provided source SQL queries"""
# # # def main():
# #     try:
# #         final_df = pd.DataFrame()
# #         processed_files = set()
# #         skip_count = 0

# #         # Check if output CSV exists and load it
# #         if os.path.exists(OUTPUT_CSV_FILE):
# #             try:
# #                 final_df = pd.read_csv(OUTPUT_CSV_FILE)
# #             except pd.errors.EmptyDataError:
# #                 print("Output CSV is empty, starting fresh.")
# #             except pd.errors.ParserError:
# #                 print("Error parsing existing CSV. Starting fresh.")
# #         else:
# #             print("Output CSV not found!!! Creating one..")

# #         # Load checkpoint or initialize
# #         if os.path.exists(CHECKPOINT_FILE):
# #             with open(CHECKPOINT_FILE, "r") as f:
# #                 checkpoint = json.load(f)
# #                 processed_files = set(checkpoint.get("processed_files", []))

# #         # Read GCS paths from the text file
# #         with open(GCS_PATHS_LIST_FILE, "r") as f:
# #             all_gcs_paths = [line.strip() for line in f]

# #         # Process files in batches
# #         with ThreadPoolExecutor(max_workers=20) as executor:
# #             for i in range(0, len(all_gcs_paths), BATCH_SIZE):
# #                 batch = all_gcs_paths[i:i + BATCH_SIZE]
# #                 batch_df = pd.DataFrame()
# #                 newly_processed = set()

# #                 futures = [
# #                 executor.submit(process_file_future, gcs_path)
# #                 for gcs_path in batch
# #                 if gcs_path not in processed_files
# #                 ]

# #             for future in as_completed(futures):
# #                 result = future.result()

# #                 if result is not None:
# #                     df, gcs_path_from_future = result
# #                     batch_df = pd.concat([batch_df, df], ignore_index=True)
# #                     newly_processed.add(gcs_path_from_future)

# #                 # The commented lines show an alternative/previous logic
# #                 # batch_df = pd.concat([batch_df, result], ignore_index=True)
# #                 # newly_processed.add(gcs_path) #Needs to be the original gcs_path, not the result
# #                 else:
# #                     skip_count += 1

# #             # The original commented batch processing loop (Alternative to futures):
# #             # for gcs_path in batch:
# #             #     if gcs_path not in processed_files:
# #             #         try:
# #             #             if ".txt" in gcs_path:
# #             #                 response = process_sql_from_gcs(gcs_path)
# #             #                 if response:
# #             #                     temp_df = pd.json_normalize(response, meta=['Purpose'])
# #             #                     batch_df = pd.concat([batch_df, temp_df], ignore_index=True)
# #             #                     newly_processed.add(gcs_path)
# #             #         except Exception as e:
# #             #             print(f"Error processing {gcs_path} in batch: {e}")
# #             #             skip_count += 1
# #             #         else:
# #             #             skip_count += 1

# #             if not batch_df.empty: # only append if there are successful processes
# #                 final_df = pd.concat([final_df, batch_df], ignore_index=True)
# #                 processed_files.update(newly_processed)

# #             # Update checkpoint after each batch (more frequent checkpoints)
# #             checkpoint = {"processed_files": list(processed_files)}
# #             with open(CHECKPOINT_FILE, "w") as f:
# #                 json.dump(checkpoint, f)

# #             final_df.to_csv(OUTPUT_CSV_FILE, index=False)
# #             tool_context.state["sql_extracted_file_path"] = OUTPUT_CSV_FILE
# #             tool_context.state["sql_extracted_info"] = final_df.to_dict("records")

# #             print(f"Completed batch. Processed {len(processed_files)} files.")

# #         print(f"Processing complete. Total processed: {len(processed_files)} files. Skipped {skip_count} files")

# #     except Exception as e:
# #         print(f"An error occurred: {e}")

# # # if __name__ == "__main__":
# #     # main()

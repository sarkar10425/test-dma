# import base64, json
# import vertexai
# from vertexai.generative_models import GenerativeModel, Part, SafetySetting
# import pandas as pd
# from google.cloud import storage
# import os
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import re
# import time
# from typing import Dict, Any, List, Tuple

# # --- CONSTANTS ---
# PROJECT_ID = "development-000"
# LOCATION_ID = "us-central1"
# BUCKET_NAME = "modelling_agent_inputs_dev"
# GCS_PATHS_LIST_FILE = "gcs_path_list.txt"  # Local file holding GCS paths to SQL files
# CHECKPOINT_FILE = "processing_checkpoint.json"
# # OUTPUT_CSV_FILE = "sql_extraction_output_final.csv"
# OUTPUT_CSV_FILE = "sql_queries_extracted_content"
# BATCH_SIZE = 40

# # Default table components for when full qualification is missing (used for placeholders)
# DEFAULT_PROJECT = "UNKNOWN_PROJECT"
# DEFAULT_DATASET = "UNKNOWN_DATASET"

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

# # --- HELPER FUNCTIONS ---


# def parse_full_table_name(full_name: str) -> Tuple[str, str, str]:
#     """Parses PROJECT.DATASET.TABLE from a fully qualified table name."""
#     parts = full_name.upper().split(".")
#     table_name = parts[-1] if parts else full_name.upper()
#     dataset_name = parts[-2] if len(parts) >= 2 else DEFAULT_DATASET
#     project_name = parts[-3] if len(parts) >= 3 else DEFAULT_PROJECT

#     # Handle the case where the name is just the table name or a CTE alias
#     if len(parts) == 1 or full_name == "UNKNOWNTABLE":
#         return (
#             DEFAULT_PROJECT,
#             DEFAULT_DATASET,
#             full_name.upper().replace("UNKNOWNTABLE", "UNKNOWN_TABLE"),
#         )

#     return project_name, dataset_name, table_name


# def format_aliases(aliases_list: List[List[str]]) -> str:
#     """Formats aliases into the required KEY: VALUE; format."""
#     if not aliases_list:
#         return ""

#     formatted_pairs = []
#     for alias, table_name in aliases_list:
#         # Resolve table_name to simple name for alias formatting
#         _, _, simple_name = parse_full_table_name(table_name)
#         formatted_pairs.append(f"{alias.upper()}: {simple_name.upper()}")

#     return "; ".join(formatted_pairs)


# # --- GEMINI EXTRACTION LOGIC ---


# def extract_details(sql_query: str, file_name: str) -> Dict[str, Any] | None:
#     """
#     Calls the Gemini API to extract lineage details, breaking down complex queries.
#     """
#     # Use the file name as the Query ID placeholder
#     query_id = file_name.upper().split(".")[0]

#     # Initializing Vertex AI client (should be outside loop in production, but included here for completeness)
#     vertexai.init(project=PROJECT_ID, location=LOCATION_ID)
#     model = GenerativeModel(
#         "gemini-2.5-flash",
#         system_instruction="You are an expert SQL parser and data lineage extractor. Analyze the input SQL query, break it down into its main query, CTEs, and subqueries. For each distinct component, you MUST perform full alias resolution and extraction. The output must strictly follow the JSON structure provided. All output strings must be in UPPERCASE. When resolving table names, use only the unqualified TABLE_NAME (e.g., 'ACCOUNTS' instead of 'PROJECT.DATASET.ACCOUNTS') in lists like ALL_TABLES_COMBINED and TABLES_IN_LOGIC. Use the full qualified name (PROJECT.DATASET.TABLE) only in the base_tables array for resolution purposes.",
#     )

#     extraction_prompt = f"""
#     # OUTPUT FORMAT INSTRUCTIONS:
#     1. The output must be a single JSON object containing a 'queries' array. Each element in 'queries' must represent ONE distinct SQL component.
#     2. 'query_link_id': Use the provided input file name/ID ({query_id}).
#     3. 'query_type': Must be one of: 'MAIN_QUERY', 'CTE', or 'SUB_QUERY'.
#     4. For all column lists (e.g., group_by_columns), use the strict format: TABLE_NAME.COLUMN_NAME.
#     5. KPILOGIC must refer to columns using the TABLE_NAME.COLUMN_NAME format (e.g., SUM(INVOICE.COST)). DO NOT use component IDs (Q1-SUB1).

#     # JSON OUTPUT STRUCTURE:
#     {{
#       "queries": [
#         {{
#           "query_link_id": "{query_id}",
#           "sub_query_id": "{query_id}_COMPONENT_ID",
#           "query_type": "MAIN_QUERY/CTE/SUB_QUERY",
#           "base_tables": [["table_name_full_qualifier", "alias"], ...], 
#           "all_tables_combined": ["UNQUALIFIED_TABLE_NAME_1", ...], 
#           "columns_selected": ["UNQUALIFIED_TABLE_NAME.COLUMN_NAME", ...],
#           "derived_kpis": [
#             {{"kpi_alias": "ALIAS", "kpi_logic": "EXPRESSION_WITH_TABLE_NAME.COLUMN_NAME", "kpi_type": "SUM/AVG/NONE", 
#               "source_columns_validated": ["TABLE_NAME.COLUMN_NAME_1", "TABLE_NAME.COLUMN_NAME_2"], 
#               "source_tables_used": ["UNQUALIFIED_TABLE_NAME_1"]}}
#           ],
#           "group_by_columns": ["TABLE_NAME.COLUMN_NAME", ...],
#           "join_conditions_list": ["TABLE_NAME.COL1 = TABLE_NAME.COL2", ...],
#           "filter_columns_list": ["CONDITION_WITH_TABLE_NAME.COLUMN_NAME", ...],
#           "case_statements_list": [
#             {{"case_statement_alias": "ALIAS", "case_statement_logic": "WHEN X THEN Y ELSE Z END", "source_column": "TABLE_NAME.COLUMN_NAME"}}
#           ],
#           "time_grain": "DAILY/MONTHLY/NONE",
#           "union_count": 0,
#           "tables_in_union": []
#         }}
#       ]
#     }}

#     # SQL Input:
#     {sql_query}
#     """

#     generation_config = {
#         "max_output_tokens": 8192,
#         "temperature": 0.0,
#         "top_p": 0.9,
#     }

#     try:
#         responses = model.generate_content(
#             [extraction_prompt], generation_config=generation_config, stream=False
#         )

#         # Robustly extract and clean JSON block
#         text = str(responses.candidates[0].content.parts[0].text)
#         json_match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
#         json_text = json_match.group(1).strip() if json_match else text.strip()

#         if not json_text:
#             raise ValueError("Model returned an empty or unparseable JSON string.")

#         # Ensure all output is capitalized
#         return json.loads(json_text.upper())
#     except Exception as e:
#         print(f"Extraction Error for {query_id}: {e}")
#         return None


# # --- GCS AND PARALLEL PROCESSING LOGIC ---


# def process_sql_from_gcs(gcs_path: str) -> Tuple[Dict[str, Any] | None, str]:
#     """Downloads SQL content from GCS and calls the extraction function."""
#     try:
#         storage_client = storage.Client()
#         bucket = storage_client.bucket(BUCKET_NAME)
#         blob_name = gcs_path.replace(f"gs://{BUCKET_NAME}/", "")
#         blob = bucket.blob(blob_name)

#         file_name = os.path.basename(gcs_path)
#         content = blob.download_as_string().decode("utf-8")

#         # NOTE: Using file_name as Query ID for extraction consistency
#         response_json = extract_details(content, file_name)

#         if response_json and "QUERIES" in response_json:
#             for q in response_json["QUERIES"]:
#                 q["GCS_PATH"] = gcs_path

#         return response_json, gcs_path

#     except Exception as e:
#         print(f"Error processing file {gcs_path} : {e}")
#         return None, gcs_path


# # --- POST-PROCESSING LOGIC (STRICT MAPPING) ---


# def post_process_data(raw_extracted_df: pd.DataFrame) -> pd.DataFrame:
#     """Flattens nested JSON components into the final, wide CSV format enforcing all rules."""
#     normalized_list = []

#     # Template to ensure all final columns exist
#     final_cols_template = {
#         "QUERYID": "",
#         "SUBQUERYID": "",
#         "QUERYTYPE": "",
#         "REPORTNAME": "",
#         "PROJECT_NAME": "",
#         "DATASET_NAME": "",
#         "TABLE_NAME": "",
#         "IS_DERIVED_TABLE": "",
#         "TABLELIST": "",
#         "COLUMNLIST": "",
#         "KPIALIAS": "",
#         "KPILOGIC": "",
#         "KPI_TYPE": "",
#         "KPIALLCOLUMNS": "",
#         "ALLKPICOLUMNSVALID": "",
#         "TABLESINLOGIC": "",
#         "GROUPBYCOLUMNS": "",
#         "DATECOLSINGROUP": "",
#         "DATEFILTERCOLUMN": "",
#         "TIMEGRAIN": "",
#         "AGGREGATIONUSED": "",
#         "ALIASES": "",
#         "JOINCONDITIONS": "",
#         "UNION_COUNT": "",
#         "TABLESINUNION": "",
#         "COLUMNSINJOINS": "",
#         "INVALIDCOLUMNSINJOINS": "",
#         "FILTERCOLUMNS": "",
#         "INVALIDCOLUMNSFILTERS": "",
#         "CASESTATEMENT": "",
#         "PRODUCT": "",
#         "OPERATIONAL_ANALYTICAL": "",
#         "FUNCTION_AREA": "",
#         "GCS_PATH": "",
#     }

#     for index, row in raw_extracted_df.iterrows():
#         try:
#             # The 'response' key holds the JSON response (already capitalized)
#             query_components = row["response"].get("QUERIES", [])

#             for component in query_components:

#                 # --- 1. Identify Table Components & Derived Status ---
#                 # Default to the main table from the base_tables list if available, for context
#                 base_tables = component.get("BASE_TABLES", [])
#                 full_table_name = base_tables[0][0] if base_tables else "UNKNOWNTABLE"

#                 project, dataset, table_name_unqualified = parse_full_table_name(
#                     full_table_name
#                 )

#                 is_derived = component.get("QUERYTYPE") in ("CTE", "SUB_QUERY")
#                 derived_table_name = table_name_unqualified if is_derived else ""

#                 # --- 2. Build Common Data ---
#                 common_data = {
#                     "GCS_PATH": component.get("GCS_PATH", "").upper(),
#                     "QUERYID": component.get("QUERY_LINK_ID", "N/A"),
#                     "SUBQUERYID": component.get("SUB_QUERY_ID", "N/A"),
#                     "QUERYTYPE": component.get("QUERY_TYPE", "N/A"),
#                     "PROJECT_NAME": project,
#                     "DATASET_NAME": dataset,
#                     "TABLE_NAME": table_name_unqualified,
#                     "IS_DERIVED_TABLE": derived_table_name,
#                     # Lineage Details
#                     # NOTE: TABLELIST, TABLESINLOGIC use the simple UNQUALIFIED table name
#                     "TABLELIST": " | ".join(component.get("ALL_TABLES_COMBINED", [])),
#                     "COLUMNLIST": " | ".join(component.get("COLUMNS_SELECTED", [])),
#                     "ALIASES": format_aliases(
#                         base_tables
#                     ),  # Custom formatting applied here
#                     "GROUPBYCOLUMNS": " | ".join(component.get("GROUP_BY_COLUMNS", [])),
#                     "JOINCONDITIONS": " | ".join(
#                         component.get("JOIN_CONDITIONS_LIST", [])
#                     ),
#                     "FILTERCOLUMNS": " | ".join(
#                         component.get("FILTER_COLUMNS_LIST", [])
#                     ),
#                     "CASESTATEMENT": " | ".join(
#                         [
#                             f"({c.get('CASE_STATEMENT_ALIAS', 'N/A')}: {c.get('CASE_STATEMENT_LOGIC', 'N/A')})"
#                             for c in component.get("CASE_STATEMENTS_LIST", [])
#                         ]
#                     ),
#                     "TIMEGRAIN": component.get("TIME_GRAIN", "NONE"),
#                     "UNION_COUNT": component.get("UNION_COUNT", 0),
#                     "TABLESINUNION": " | ".join(component.get("TABLES_IN_UNION", [])),
#                     # Columns in Join extraction
#                     "COLUMNSINJOINS": " | ".join(
#                         sorted(
#                             list(
#                                 set(
#                                     re.findall(
#                                         r"[A-Z0-9_]+\.[A-Z0-9_]+",
#                                         " ".join(
#                                             component.get("JOIN_CONDITIONS_LIST", [])
#                                         ),
#                                     )
#                                 )
#                             )
#                         )
#                     ),
#                 }

#                 # Date column identification (simple keyword search is used here)
#                 date_keywords = ["MONTH", "DAY", "DATE", "TIME"]
#                 common_data["DATECOLSINGROUP"] = " | ".join(
#                     [
#                         col
#                         for col in common_data["GROUPBYCOLUMNS"].split(" | ")
#                         if any(dk in col for dk in date_keywords)
#                     ]
#                 )
#                 common_data["DATEFILTERCOLUMN"] = " | ".join(
#                     [
#                         col.split("=", 1)[0].strip()
#                         for col in common_data["FILTERCOLUMNS"].split(" | ")
#                         if any(dk in col for dk in date_keywords)
#                         and any(op in col for op in ["=", ">", "<"])
#                     ]
#                 )

#                 # --- 3. KPI Extraction (Multi-row handling) ---
#                 kpi_list = component.get("DERIVED_KPIS", [])

#                 if not kpi_list and component.get("COLUMNS_SELECTED", []):
#                     # Case 1: Non-KPI/Simple Projection
#                     final_row = final_cols_template.copy()
#                     final_row.update(common_data)
#                     final_row["KPI_TYPE"] = final_row["AGGREGATIONUSED"] = "NONE"
#                     final_row["KPIALIAS"] = " | ".join(
#                         [
#                             col.split(".")[-1]
#                             for col in common_data["COLUMNLIST"].split(" | ")
#                         ]
#                     )
#                     normalized_list.append(final_row)

#                 elif kpi_list:
#                     # Case 2: One row for each explicit derived KPI
#                     for kpi in kpi_list:
#                         final_row = final_cols_template.copy()
#                         final_row.update(common_data)

#                         # Note: All columns listed in source_columns_validated must be comma separated
#                         source_cols_list = kpi.get("SOURCE_COLUMNS_VALIDATED", [])

#                         final_row.update(
#                             {
#                                 "KPIALIAS": kpi.get("KPI_ALIAS", ""),
#                                 "KPILOGIC": kpi.get("KPI_LOGIC", ""),
#                                 "KPI_TYPE": kpi.get("KPI_TYPE", "NONE"),
#                                 "AGGREGATIONUSED": kpi.get("KPI_TYPE", "NONE"),
#                                 # Strict Lineage Rule: Only simple TABLE_NAME.COLUMN_NAME
#                                 "ALLKPICOLUMNSVALID": ", ".join(source_cols_list),
#                                 # Strict Lineage Rule: Only simple TABLE_NAMEs
#                                 "TABLESINLOGIC": ", ".join(
#                                     kpi.get("SOURCE_TABLES_USED", [])
#                                 ),
#                                 "KPIALLCOLUMNS": ", ".join(
#                                     [col.split(".")[-1] for col in source_cols_list]
#                                 ),
#                             }
#                         )
#                         normalized_list.append(final_row)

#                 else:
#                     # Case 3: Empty component / Unusable response
#                     final_row = final_cols_template.copy()
#                     final_row.update(common_data)
#                     normalized_list.append(final_row)

#         except Exception as e:
#             print(
#                 f"Post-processing Error for {row.get('QUERYID', 'N/A')}: {e}. Skipping component."
#             )
#             continue

#     return pd.DataFrame(normalized_list)


# def main():
#     """Main execution loop for parallel batch processing with checkpointing."""
#     try:
#         final_df = pd.DataFrame()
#         processed_files = set()

#         # --- 1. Load Existing Data and Checkpoint ---

#         if os.path.exists(OUTPUT_CSV_FILE):
#             try:
#                 final_df = pd.read_csv(OUTPUT_CSV_FILE, dtype=str)
#                 final_df.columns = final_df.columns.str.upper()  # Ensure consistency
#                 if "GCS_PATH" in final_df.columns:
#                     processed_files = set(final_df["GCS_PATH"].unique())
#                     print(
#                         f"Resuming: Loaded {len(processed_files)} processed files from CSV."
#                     )
#                 else:
#                     print(
#                         "Existing output CSV found but missing GCS_PATH. Starting fresh."
#                     )
#             except Exception as e:
#                 print(f"Error loading existing CSV ({e}). Starting fresh.")

#         # Load GCS paths from the local file (gcs_path_list.txt)
#         if not os.path.exists(GCS_PATHS_LIST_FILE):
#             print(
#                 f"Error: GCS path list file '{GCS_PATHS_LIST_FILE}' not found. Cannot proceed."
#             )
#             return

#         with open(GCS_PATHS_LIST_FILE, "r") as f:
#             all_gcs_paths = [line.strip() for line in f if line.strip()]

#         paths_to_process = [
#             path for path in all_gcs_paths if path not in processed_files
#         ]

#         if not paths_to_process:
#             print("All files have been processed. Exiting.")
#             return

#         print(f"Starting process for {len(paths_to_process)} new or pending files.")

#         # --- 2. Process Files in Parallel Batches ---

#         newly_processed_paths = set()
#         total_skip_count = 0

#         with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
#             for i in range(0, len(paths_to_process), BATCH_SIZE):
#                 batch = paths_to_process[i : i + BATCH_SIZE]
#                 print(
#                     f"\n--- Starting Batch {i//BATCH_SIZE + 1} ({len(batch)} files) ---"
#                 )

#                 futures = {
#                     executor.submit(process_sql_from_gcs, gcs_path): gcs_path
#                     for gcs_path in batch
#                 }
#                 batch_results_list = []

#                 for future in as_completed(futures):
#                     result, gcs_path_from_future = future.result()

#                     if result is not None and "QUERIES" in result:
#                         batch_results_list.append(
#                             {"GCS_PATH": gcs_path_from_future, "response": result}
#                         )
#                         newly_processed_paths.add(gcs_path_from_future)
#                     else:
#                         total_skip_count += 1
#                         print(f"Skipped/Failed file: {gcs_path_from_future}")

#                 # Process, append, checkpoint, and save after every batch
#                 if batch_results_list:
#                     raw_extracted_df = pd.DataFrame(batch_results_list)
#                     batch_df = post_process_data(raw_extracted_df)

#                     final_df = pd.concat([final_df, batch_df], ignore_index=True)
#                     processed_files.update(newly_processed_paths)

#                 # Update checkpoint file (contains all processed paths so far)
#                 checkpoint = {"processed_files": list(processed_files)}
#                 with open(CHECKPOINT_FILE, "w") as f:
#                     json.dump(checkpoint, f)

#                 # Save the accumulated DataFrame
#                 # Ensure correct column order is maintained when saving
#                 if not final_df.empty:
#                     final_cols_order = [
#                         "QUERYID",
#                         "SUBQUERYID",
#                         "QUERYTYPE",
#                         "REPORTNAME",
#                         "PROJECT_NAME",
#                         "DATASET_NAME",
#                         "TABLE_NAME",
#                         "IS_DERIVED_TABLE",
#                         "TABLELIST",
#                         "COLUMNLIST",
#                         "KPIALIAS",
#                         "KPILOGIC",
#                         "KPI_TYPE",
#                         "KPIALLCOLUMNS",
#                         "ALLKPICOLUMNSVALID",
#                         "TABLESINLOGIC",
#                         "GROUPBYCOLUMNS",
#                         "DATECOLSINGROUP",
#                         "DATEFILTERCOLUMN",
#                         "TIMEGRAIN",
#                         "AGGREGATIONUSED",
#                         "ALIASES",
#                         "JOINCONDITIONS",
#                         "UNION_COUNT",
#                         "TABLESINUNION",
#                         "COLUMNSINJOINS",
#                         "INVALIDCOLUMNSINJOINS",
#                         "FILTERCOLUMNS",
#                         "INVALIDCOLUMNSFILTERS",
#                         "CASESTATEMENT",
#                         "PRODUCT",
#                         "OPERATIONAL_ANALYTICAL",
#                         "FUNCTION_AREA",
#                         "GCS_PATH",
#                     ]

#                     # Add missing columns before saving if post_process_data didn't create them (e.g., empty run)
#                     for col in final_cols_order:
#                         if col not in final_df.columns:
#                             final_df[col] = ""

#                     final_df = final_df[final_cols_order]
#                     final_df.to_csv(OUTPUT_CSV_FILE, index=False)

#                 print(
#                     f"Completed batch. Total processed files: {len(processed_files)}. Total output rows: {len(final_df)}."
#                 )

#         print(
#             f"\nProcessing complete. Total files processed: {len(processed_files)}. Total files skipped/failed in this run: {total_skip_count}"
#         )

#     except Exception as e:
#         print(f"An unhandled error occurred in main: {e}")


# if __name__ == "__main__":
#     main()

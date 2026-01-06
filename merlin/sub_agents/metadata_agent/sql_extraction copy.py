# import base64, json
# import vertexai
# from vertexai.generative_models import GenerativeModel, Part, SafetySetting
# import pandas as pd
# from google.cloud import storage
# import os
# from concurrent.futures import ThreadPoolExecutor, as_completed

# import pdb

# PROJECT_ID = "development-000"
# LOCATION_ID = "us-central1"
# BUCKET_NAME = "modelling_agent_inputs_dev"
# # GCS_PATHS_LIST_FILE = "gs://modelling_agent_inputs_dev/bq_cost_data_input_data_model/kpis/KPIs_and_queries.xlsx"
# GCS_PATHS_LIST_FILE = "path_file.txt"  # "gs://modelling_agent_inputs_dev/path_file.txt"
# # GCS_PATHS_LIST_FILE = "gcs_path_list_mis_pending2.txt" # errorerd out files
# LOCAL_PATHS_LIST_FILE = "local_path_file.txt"
# CHECKPOINT_FILE = "processing_checkpoint.json"
# OUTPUT_CSV_FILE = "mis_output_test.csv"
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


# def get_gcs_file_paths(bucket_name):
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blobs = bucket.list_blobs()
#     file_paths = [f"gs://{bucket_name}/{blob.name}" for blob in blobs]
#     with open(GCS_PATHS_LIST_FILE, "w") as f:
#         for file_path in file_paths:
#             f.write(file_path + "\n")


# def download_gcs_file(gcs_uri, local_destination_path):
#     """Downloads a file from GCS to a local path."""
#     try:
#         print(f"download_gcs_file: {gcs_uri}")
#         storage_client = storage.Client()
#         bucket_name = gcs_uri.split("/")[2]
#         source_blob_name = "/".join(gcs_uri.split("/")[3:])
#         bucket = storage_client.bucket(bucket_name)
#         blob = bucket.blob(source_blob_name)
#         blob.download_to_filename(local_destination_path)
#         print(f"Successfully downloaded {gcs_uri} to {local_destination_path}")
#         return True
#     except Exception as e:
#         print(f"Failed to download {gcs_uri}. Error: {e}")
#         return False


# def extract_details(sql_query):  # for table-alias mapping
#     # try:
#     vertexai.init(project=PROJECT_ID, location=LOCATION_ID)
#     model = GenerativeModel(
#         "gemini-2.5-flash",
#         system_instruction="""You a database analyst expert in writing and understanding sql queries .you are also a business expert in financial investments like mutual funds (MFs), alternative investment funds (AIFs), insurance companies and other financial institutions.""",
#     )
#     # use this prompt for SQL extraction prompt and later use the 2nd one for table alias mapping
#     extraction_prompt = f"""
#             #SI: Extracting Table and Column Information from SQL Queries (GenAI Prompt)
#             You are an expert SQL parser and data lineage extractor. Your task is to analyze a set of SQL queries (up to 100) provided to you and extract the information required as mentioned below. Queries might contain UDFs and comments too. Ignore the statements that are commented.
#         #SI: Extracting Table and Column Information from SQL Queries (GenAI Prompt)
#         You are an expert SQL parser and data lineage extractor. Your task is to analyze a set of SQL queries (up to 3) provided to you and extract the information required as mentioned below. Queries might contain UDFs and comments too. Ignore the statements that are commented.

#             #TASK: Your task is to identify the following from an Oracle SQL that might contain UDF code you are supposed to understand and analyse the Oracle SQL queries provided to you and extract the information required as mentioned below. Queries might contain UDFs and comments too. Ignore the statements that are commented.
#         Input Format:
#         A list of SQL queries, where each query is a string. Example:
#         ```json
#         [
#         "SELECT a.col1, b.col2 FROM tableA a JOIN (SELECT x.col3, y.col4 FROM tableX x JOIN tableY y ON x.id = y.id) b ON a.id = b.id",
#         "SELECT * FROM tableZ WHERE col5 > (SELECT MAX(col6) FROM tableW)",
#         "WITH DerivedTable AS (SELECT col7 FROM tableV) SELECT * FROM DerivedTable"
#         ]
#         ```

#             #-Table_Names_base: All table names which are part of base tables, that are not derived or Common Table Expression, but could also be a part of subquery, nested query using base tables within the SQL query. Provide an array of any table alias used in the input SQL query along with the table name
#         Output Format:
#         Return the results in json format. JSON format as below.

#             #-Table_Names_derived: All table names which are derived tables created within the SQL query ONLY. Provide an array of any table alias used in the input SQL query along with the table name.
#         A JSON object with the following structure:
#         {{
#         "queries": [
#         {{
#         "query_index": 0,
#         "base_tables": [["tableA", "a"], ["tableX", "x"], ["tableY", "y"]],
#         "derived_tables": {{
#         "b": ["tableX", "tableY"]
#         }},
#         "base_table_columns": [
#         "tableA.col1", "tableA.id", "tableX.col3", "tableX.id", "tableY.col4", "tableY.id"
#         ],
#         "derived_table_columns": [
#         "b.col2", "b.col3"
#         ],
#         "derived_column_sources": {{
#         "b.col3": ["tableX.col3"],
#         "b.col2": ["tableX.col3", "tableY.col4"]
#         }},
#         "missed_columns": []
#         }},
#         {{
#         "query_index": 1,
#         "base_tables": ["tableZ", "tableW"],
#         "derived_tables": {{}},
#         "base_table_columns": ["tableZ.*", "tableW.col6"],
#         "derived_table_columns": [],
#         "derived_column_sources": {{}},
#         "missed_columns": []
#         }},
#         {{
#         "query_index": 2,
#         "base_tables": ["tableV"],
#         "derived_tables": {{
#         "DerivedTable": ["tableV"]
#         }},
#         "base_table_columns": ["tableV.col7"],
#         "derived_table_columns": ["DerivedTable.*"],
#         "derived_column_sources": {{
#         "DerivedTable.*": ["tableV.col7"]
#         }},
#         "missed_columns": []
#         }}
#         ]
#         }}

#             #-Column_list_base: All the column names which are part of base tables.
#             # These columns could also be a part of subquery, nested query, filter conditions, join condition, where clause, case statements using base tables ONLY and not derived tables within the SQL query.
#             # Please include any such columns that are present after the select keyword in any nested query of base tables.
#             # The list of column should follow the format "table.column" but only if this information is available in the input SQL query.
#         Instructions and Clarifications:
#         - Handle various SQL constructs: Accurately process different SQL clauses (SELECT, FROM, WHERE, JOIN, GROUP BY, HAVING, subqueries, common table expressions (CTEs), etc.), different join types, and potentially complex nested queries.
#         - Alias Resolution: Correctly resolve table and column aliases to identify the underlying base tables and columns.
#         - Derived Table Logic: For derived tables, accurately capture the base tables they are derived from. If a derived table is built on top of another derived table, trace back to the ultimate base tables.
#         - Column Usage: Identify all columns used from both base tables and derived tables. Include columns in SELECT lists, WHERE clauses, JOIN conditions, aggregation functions, CASE expressions, and any other parts of the query. Be very thorough in identifying column usage, including within nested subqueries.
#         - Derived Column Mapping: Show the explicit mapping from derived columns to their source columns, if ascertainable. For example if derived_col = base_col1 + base_col2, reflect this dependency. Handle cases involving functions and complex expressions where possible. If a full derivation is not feasible, make a best effort.
#         - Wildcard Handling: For SELECT *, list it as table_name.*.
#         - Missing Columns: The missed_columns array should ideally be empty. Use this to flag any cases where you were unable to definitively identify the source of a column.
#         - Robustness: Be robust to variations in SQL syntax (e.g., capitalization of keywords, different quoting styles for identifiers, etc.).
#         - Error Handling: Handle potential errors in the input SQL gracefully, for example malformed queries. Indicate the query index and the error encountered.

#             #-Column_list_derived: All the column names which are derived columns.
#             # These columns could also be a part of subquery, nested query, filter conditions, join condition, where clause, case statements using Derived tables ONLY and not base tables within the SQL query.
#             # Please include any such columns that are present after the select keyword of derived tables.
#             # The list of column should follow the format "table.column" but only if this information is available in the input SQL query. The output should be in a single column as a list - "Column_list_derived".
#             # Additionally, return any derived columns that are part of SELECT clause and fulfill the precedence condition provided.
#         By following these detailed instructions, you will generate highly accurate and comprehensive information about the tables and columns used in the SQL queries. The structured JSON output will make it easy to programmatically process this information for tasks like data lineage analysis, impact analysis, or query optimization.

#             #-Column_list_derived_logic: The logic for all the derived columns which are derived columns created within the SQL query. In case same derived column name has multiple logics, provide all logics as an array. The output should be in a single column as a list - "Column_list_derived_logic".
#             Additionally, return any logics of any derived columns that are part of SELECT clause and fulfill the precedence condition provided. The list of column should follow the format "table.column" but only if this information is available in the input SQL query.
#         SQL:
#         {sql_query}
    

#             #-Column_nested_query: Select any columns that are a part of nested queries or subqueries, this might be present in the where clause as well. Please include any such columns that are present after the select keyword in any nested query.

#             #-Case_Statements: Analyse all the case statements and extract the logic, their final alias provided and the table_name.column_name on which the filter is applied.

#             #OUTPUT:
#             #1. KPIs, Filters, Union_Join, Case_Statements key should have value in a list.

#             {{
#                 "Table_Names_base": [ [ [ "table_name" , "[table_alias]" ] ] ],
#                 "Column_list_base": [ [ [ "Table_Name-Column_Name" ] ] ],
#                 "Table_Names_derived": [ [ [ "table_name" , "[table_alias]" ] ] ],
#                 "Column_list_derived": [ [ [ "Table_Name-Column_Name" ] ] ],
#                 "Column_list_derived_logic": [ [ [ "Table_Name-derived_column_name:derived_column_logics" ] ] ],
#                 "Column_nested_query": [ [ [ "Table_Name-Column_Name" ] ] ],
#                 "Case_Statements": [
#                 {{
#                 "case_statement_logic": ,
#                 "final_alias": ,
#                 "table_name.column_name": ,
#                 }}
#                 ]
#             }}

#             #INSTRUCTIONS:
#             1. Only provide the information extracted exactly as available in the query. Do not add extra descriptions.
#             2. Use the logics provided but do not provide any reason or descriptions.

#             SI: Extracting Table and Column Information from SQL Queries (GenAI Prompt)
#             You are an expert SQL parser and data lineage extractor. Your task is to analyze a set of SQL queries (up to 3) provided to you and extract the information required as mentioned below. Queries might contain UDFs and comments too. Ignore the statements that are commented.

#             Input Format:
#             A list of SQL queries, where each query is a string. Example:
#             json
#             [
#             SELECT a.col1, b.col2 FROM tableA a JOIN (SELECT x.col3, y.col4 FROM tableX x JOIN tableY y ON x.id = y.id) b ON a.id = b.id,
#             SELECT * FROM tableZ WHERE col5 > (SELECT MAX(col6) FROM tableW),
#             WITH DerivedTable AS (SELECT col7 FROM tableV) SELECT * FROM DerivedTable
#             ]

#             Output Format:
#             Return the results in json format. JSON format as below

#             A JSON object with the following structure:
#             {{
#             queries: [
#             {{
#             query_index: 0, // Index of the query in the input list
#             base_tables: [["tableA", "a"], ["tableX", "x"], ["tableY", "y"]],
#             derived_tables: {{
#             b: ["tableX", "tableY"]
#             }},
#             base_table_columns: [
#             tableA.col1, "tableA.id", "tableX.col3", "tableX.id", "tableY.col4", "tableY.id"
#             ],
#             derived_table_columns: [
#             b.col2, "b.col3" // Assuming col2 and col3 are output columns of the derived table
#             ],
#             derived_column_sources: {{
#             b.col3: ["tableX.col3"],
#             b.col2: ["tableX.col3", "tableY.col4"] // Illustrative example, provide actual derivation logic
#             }},
#             missed_columns: [] // Should ideally be empty if all columns are captured
#             }},
#             {{
#             query_index: 1,
#             base_tables: ["tableZ", "tableW"],
#             derived_tables: {{}},
#             base_table_columns: ["tableZ.*", "tableW.col6"],
#             derived_table_columns: [],
#             derived_column_sources: {{}},
#             missed_columns: []
#             }},
#             {{
#             query_index: 2,
#             base_tables: ["tableV"],
#             derived_tables: {{
#             DerivedTable: ["tableV"]
#             }},
#             base_table_columns: ["tableV.col7"],
#             derived_table_columns: ["DerivedTable.*"], // or list out individual columns if identifiable
#             derived_column_sources: {{
#             DerivedTable.*: ["tableV.col7"] //Or list individual mappings if identifiable
#             }},
#             missed_columns: []
#             }}
#             ]
#             }}

#             Instructions and Clarifications:
#             Handle various SQL constructs: Accurately process different SQL clauses (SELECT, FROM, WHERE, JOIN, GROUP BY, HAVING, subqueries, common table expressions (CTEs), etc.), different join types, and potentially complex nested queries. Alias Resolution: Correctly resolve table and column aliases to identify the underlying base tables and columns. Derived Table Logic: For derived tables, accurately capture the base tables they are derived from. If a derived table is built on top of another derived table, trace back to the ultimate base tables. Column Usage: Identify all columns used from both base tables and derived tables. Include columns in SELECT lists, WHERE clauses, JOIN conditions, aggregation functions, CASE expressions, and any other parts of the query. Be very thorough in identifying column usage, including within nested subqueries. Derived Column Mapping: Show the explicit mapping from derived columns to their source columns, if ascertainable. For example if derived_col = base_col1 + base_col2, reflect this dependency. Handle cases involving functions and complex expressions where possible. If a full derivation is not feasible, make a best effort. Wildcard Handling: For SELECT *, list it as table_name.*. If possible, attempt to resolve * to individual columns based on table schemas if provided, but don't assume schema availability. Missing Columns: The missed_columns array should ideally be empty. Use this to flag any cases where you were unable to definitively identify the source of a column. Include a descriptive explanation of the issue if possible. Robustness: Be robust to variations in SQL syntax (e.g., capitalization of keywords, different quoting styles for identifiers, etc.). Error Handling: Handle potential errors in the input SQL gracefully, for example malformed queries. Indicate the query index and the error encountered. The output should still contain the processed results for valid queries. By following these detailed instructions, you will generate highly accurate and comprehensive information about the tables and columns used in the SQL queries. The structured JSON output will make it easy to programmatically process this information for tasks like data lineage analysis, impact analysis, or query optimization.

#             SQL:
#             {sql_query}

#         """

#     generation_config = {
#         "max_output_tokens": 8192,
#         "temperature": 1,
#         "top_p": 0.9,
#     }
#     responses = model.generate_content(
#         [extraction_prompt],
#         generation_config=generation_config,
#         # safety_settings=safety_settings,
#         stream=False,
#     )
#     # return print(responses.text)
#     print(f"@@@@@@text: {responses.candidates[0].content.parts[0].text}")
#     return (
#         str(responses.candidates[0].content.parts[0].text)
#         .replace("```json", "")
#         .replace("json", "")
#     )
#     # except Exception as e:
#     #     return "Response Generation Error"


# def process_sql_from_gcs(gcs_path):
#     pdb.set_trace()
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
#         response = extract_details(content)
#         response_json = json.loads(response)
#         response_json["GCS_Path"] = gcs_path
#         return response_json
#     except json.JSONDecodeError as e:
#         print(
#             f""" Error decoding JSON from model for file {gcs_path}. Response was: {response}. Error: {e}"""
#         )
#         return None
#     except Exception as e:
#         print(f""" Error processing file {gcs_path} :{e}""")
#         return False
#         return None


# # def process_file(gcs_path):
# #     try:
# #         if ".txt" in gcs_path:
# #             response = process_sql_from_gcs(gcs_path)
# #         if response:
# #             return pd.json_normalize(response, meta=['Purpose'])
# #         return None # Indicate failure
# #     except Exception as e:
# #         print(f"Error processing {gcs_path}: {e}")
# #         return None


# def process_file_future(gcs_path):
#     try:
#         if ".txt" in gcs_path:
#             response = process_sql_from_gcs(gcs_path)

#         if response:
#             temp_df = pd.json_normalize(response, meta=["Purpose"])
#             return temp_df, gcs_path
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
#         with open(GCS_PATHS_LIST_FILE, "r") as f:
#             print("350")
#             for line in f:
#                 print(line.strip())
#             all_gcs_paths = [line.strip() for line in f]
#         # Download the GCS path list file and then read from it
#         if not download_gcs_file(GCS_PATHS_LIST_FILE, LOCAL_PATHS_LIST_FILE):
#             print("Could not download the GCS path file. Exiting.")
#             return

#         with open(LOCAL_PATHS_LIST_FILE, "r") as f:
#             # Filter out any empty lines
#             all_gcs_paths = [line.strip() for line in f if line.strip()]

#         # Process files in batches
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

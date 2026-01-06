# def generate_consolidation_config(
#     tool_context: ToolContext, user_feedback: str = ""
# ) -> dict:
#     """
#     Inspects data schemas and uses a GenAI model to generate or refine a consolidation_config.json.
#     The resulting config is stored in the tool_context state.
#     """
#     directory_path = tool_context.state.get("directory_path")
#     if not directory_path:
#         return {"error": "directory_path not found in tool_context state."}

#     debug_dir = os.path.join(directory_path, "debug")
#     os.makedirs(debug_dir, exist_ok=True)

#     # Step 1: Get the data schema
#     schema_json_str = inspect_and_load_data_context(tool_context)
#     schema_data = json.loads(schema_json_str)
#     if "error" in schema_data:
#         return schema_data

#     # Step 2: Prepare the prompt
#     previous_config = tool_context.state.get("consolidation_config")

#     prompt_template = """You are an expert Cloud Migration Automation Specialist. Your primary objective is to create a consolidation_config.json object.

# **Rules:**
# Your entire plan MUST be based on the filenames and columns present in the data_schema. Do not invent or assume any filenames or columns.
# **Assess Each Source**: Based only on the data_schema from the previous step, analyze every column to determine its weightage for migration wave planning. Choose columns that are input agnostic by principle but does not lose the inherent context present in the input.
# **Categorize Columns**: Create two lists for each source format:
#     - **Columns to Keep**: Identify all columns that can be used as a parameter for filtering or grouping (e.g., Cluster, Powerstate, OS, app_name, criticality, Annotation). Apply caution while determining the column names which could sometimes belong to a destination placeholder (example : Datacenter in TxTure) rather than source. And add a field with the rationale for the inclusion crtieria.
#     - **Columns to Strip**: Identify all columns that provide no value for grouping and should be discarded (e.g., internal SDK versions, transient heartbeat status, specific timestamps, file paths). And add a field with the rationale for the inclusion crtieria
# **Define the Golden Record Standard**: Propose a standardized set of column names for your Golden Record. This record must be comprehensive enough to hold technical, business, and operational data. Start with this baseline and expand if necessary:
# asset_id, asset_name, source_platform, power_state, cpu_cores, memory_gb, total_storage_gb, guest_os, ip_address, network_name, datacenter_loc, cluster_name, app_name, app_type_name, environment, business_unit, owner_name, criticality, recovery_time_objective.

# Based on the **Columns to Keep** determined above, you must create a consolidation_config JSON object from scratch.
# **CRITICAL: The final consolidated file MUST contain a column named asset_name.** This column is the primary human-readable identifier for servers (e.g., the VM name). You MUST ensure that the source column containing the server name (like 'VM', 'ServerName', 'name', etc.) is mapped to asset_name in your rename_map. This is non-negotiable.

# **Identify Base File & Key**: From the filenames provided in the data_schema, choose a base_file that seems most central (e.g., most records, most columns, or contains a clear primary identifier like 'VM' or 'ServerName'). Identify its primary key. **CRITICAL**: The filenames you use in the configuration MUST exist in the data_schema.
# **Define Merge Strategy**: Determine which other files from the data_schema should be merged into the base file and on which key.
# **Construct the Config**: Build the consolidation_config object with the base_file and files_to_merge you have defined. Each file must have its filename, its join key, and its own inferred list of map of columns_to_keep with the column_name and  rationale. And similarly a list of map of columns_to_strip with the column_name and  rationale.
# **Apply Mappings**: To align with the Golden Record, you can add a rename_map object to each file's configuration. This map should contain source_column_name as key and golden_record_column_name as value.

# **CRITICAL RULE FOR EXAMPLES:** The following example is for STRUCTURE ONLY. You MUST use the actual filenames and columns discovered in the data_schema.

# **Example consolidation_config structure:**
# json
# {{
#     "base_file": {{
#         "filename": "source_data_1.csv",
#         "key": "VM",
#         "columns_to_keep": [
#             {{"column_name": "VM", "rationale": "Primary identifier for the virtual machine."}},
#             {{"column_name": "Powerstate", "rationale": "Indicates if the server is running or not."}}
#         ],
#         "rename_map": {{ "VM": "asset_name" }}
#     }},
#     "files_to_merge": [
#         {{
#             "filename": "source_data_2.csv",
#             "key": "Server Name",
#             "columns_to_keep": [
#                 {{"column_name": "Server Name", "rationale": "Primary identifier for mapping."}},
#                 {{"column_name": "Application", "rationale": "Provides business context."}}
#             ],
#             "rename_map": {{ "Server Name": "asset_name", "Application": "app_name" }}
#         }}
#     ]
# }}


# **Data Schema:**
# {data_schema}

# {feedback_section}

# Based on the above, provide the complete, updated consolidation_config JSON object.
# """

#     feedback_section = ""
#     if user_feedback and previous_config:
#         feedback_section = f"""
# **Previous Configuration:**
# {json.dumps(previous_config, indent=2)}

# **User Feedback for Refinement:**
# "{user_feedback}"

# Please refine the 'Previous Configuration' based on the 'User Feedback'.
# """
#     elif user_feedback:
#         feedback_section = f"""
# **User Feedback to Incorporate:**
# "{user_feedback}"

# Please create the initial configuration incorporating this feedback.
# """

#     prompt = prompt_template.format(
#         data_schema=json.dumps(schema_data, indent=2), feedback_section=feedback_section
#     )
#     logging.debug(f"Full prompt for generate_consolidation_config:\n{prompt}")

#     # Step 3: Call the model
#     try:
#         call_desc = "Generate Consolidation Config"
#         if user_feedback:
#             call_desc = "Refine Consolidation Config"

#         response = utils.generate_content_with_retry(prompt, call_desc, debug_dir)
#         config_json = utils.parse_model_response(response)

#         # Step 4: Store in context and return
#         tool_context.state["consolidation_config"] = config_json
#         logging.debug(
#             f"LLM response for consolidation config: {json.dumps(config_json, indent=2)}"
#         )
#         return config_json

#     except (json.JSONDecodeError, Exception) as e:
#         error_msg = f"Failed to generate/refine consolidation config. Error: {e}"
#         logging.error(error_msg)
#         return {"error": error_msg}


# config_normalizer_agent = LlmAgent(
#     model="gemini-2.5-pro",
#     name="config_normalizer_agent",
#     description="Orchestrates data configuration and normalization. It inspects data, works with the user to create a configuration, and then generates a final 'Golden Record' CSV.",
#     instruction="""You are the Data Configuration and Normalization Specialist. Your job is to generate a data consolidation plan, get user approval, and then save it.

# **WORKFLOW:**

# 1. Call the generate_consolidation_config tool to create an initial consolidation_config.json. Present this config to the user for review in a markdown table format. Create two sections: "Columns to Keep" and "Columns to Strip". Each section should have it's own table. The table should have columns like: Source File, Source Column, Golden Record Column, and Rationale.
# 2. Then you MUST ask user for feedback or approval. If user provides feedback, call generate_consolidation_config again with the feedback as user_feedback parameter to refine the config. Repeat this loop until the user approves the config.
# Stop calling the generate_consolidation_config tool ONLY when the user mentions ("satisfied", "approved", "looks good") or something similar.
# 3. Once the user approves the config, call the generate_and_save_consolidated_csv.
# 4. Once the generate_and_save_consolidated_csv tool has finished, call the parent agent.
# """,
#     tools=[
#         generate_consolidation_config,
#         generate_and_save_consolidated_csv,
#     ],
# )

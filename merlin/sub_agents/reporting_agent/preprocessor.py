import pandas as pd
import os
import io
import numpy as np

# to be updated for GCS bucket read/write operations
path = "/Users/abhijat/Downloads/BigQueryModellingAgent/repo/BigQueryModellingAgent/data_modelling_agent_v2/_only_csv.csv"
output_dir = "/Users/abhijat/Downloads/BigQueryModellingAgent/repo/BigQueryModellingAgent/logical_data_model_csvs/"
source_file = "/Users/abhijat/Downloads/BigQueryModellingAgent/repo/BigQueryModellingAgent/logical_data_model.csv"

try:
    os.mkdir(output_dir)
except Exception as e:
    print(f"Path exists. Using same path : {output_dir}")


def extract_csv_content(output_dir: str, source_file: str = source_file):
    """Extract only the LDM tables from the LDM Agent output"""
    import re

    content = None
    with open(source_file, "r") as file:
        content = file.read()
    try:
        only_csv_content = content.split("Detailed LDM Specification (CSV Format)")[
            1
        ].split("Conceptual to LDM Traceability Summary (CSV Format)")[0]
        required_csv_content = (
            only_csv_content.replace("```csv", "").replace("```", "").strip()
        )
        lst_content = required_csv_content.split("\n")
    except Exception as e:
        only_csv_content_temp = content.split("|Target_Table_Name")
        only_csv_content = (
            "|Target_Table_Name"
            + only_csv_content_temp[1].split("Conceptual to LDM Traceability Summary")[
                0
            ]
        )
        required_csv_content = (
            only_csv_content.replace("```csv", "").replace("```", "").strip()
        )
        lst_content = required_csv_content.split("\n")

    refactored_list_temp = []
    refactored_list = []
    refactored_list_columns = []
    for item in lst_content:
        if item != "":
            refactored_list_columns.append([item])
            refactored_list_temp.append(item.split("|"))

    for item in refactored_list_temp:
        for col in item:
            if col == "":
                item.remove(col)
        refactored_list.append(item)

    columns_temp = refactored_list_columns[0][0].split("|")
    columns = []
    for col in columns_temp:
        if col != "":
            columns.append(col)
    refactored_list = refactored_list[1:]
    df = pd.DataFrame(np.array(refactored_list))

    df.to_csv(output_dir, index=False)
    return f"Logical Data model CSV stored at: {output_dir}"


# creating csv files for all LDM tables
df = pd.read_csv(path, header=None, names=range(29))
df = df.iloc[2:]
cnt_orignal_df = len(df)
columns = [
    "Target_Table_Name",
    "Entity",
    "Sub-Entity",
    "Table Type",
    "SCD Type",
    "PK Only",
    "FK Only",
    "Constraints (BQ)",
    "Partition SQL (BQ Syntax)",
    "Require_Partition_Filter (Yes/No)",
    "Clustering SQL (BQ Syntax)",
    "Data Retention (Table/Partition Days)",
    "Target_Columns",
    "Target_Column_Data_Type",
    "New/Existing",
    "Transformation_SQL",
    "Source Table(s)",
    "Source_Column_Name",
    "Source_Column_Data_Type",
    "Source_Entity",
    "Source_Sub-Entity",
    "Source_Table Type",
    "Source_SCD Type",
    "Source_PK Only",
    "Source_FK Only",
    "Source_Constraints",
    "Notes",
    "col1",
    "col2",
]

dct = {}
for idx, row in df.iterrows():
    entity_suffix = None
    if "/" in row[1]:
        entity_suffix = row[1].replace("/", "_")
    else:
        entity_suffix = row[1]
    if row[0] + "#" + entity_suffix not in dct:
        dct[row[0] + "#" + entity_suffix] = [row]
    else:
        dct[row[0] + "#" + entity_suffix].append(row)

total_rows = 0
for table, lst in dct.items():
    filename = table + ".csv"
    df_from_list = pd.DataFrame(lst)
    total_rows += len(df_from_list)
    df_from_list.to_csv(output_dir + filename, index=False, header=False)

if total_rows != cnt_orignal_df:
    print("some rows might be dropped!")

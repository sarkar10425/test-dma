import os
import io
import re
import pandas as pd
from graphviz import Digraph
import graphviz

print(graphviz.version())

# def get_entity_attributes(csv_file_path):
#     """Reads a CSV and returns the column names as attributes."""
#     try:
#         df = pd.read_csv(csv_file_path)
#         return df.columns.tolist()
#     except FileNotFoundError:
#         print(f"Error: CSV file not found at {csv_file_path}")
#         return []


def get_entity_attributes(csv_file_path, column_index=None):
    """
    Reads a CSV and returns the unique data values from the specified column as attributes.
    If no column_index is provided or it's invalid, it defaults to returning the column header names.
    """
    try:
        df = pd.read_csv(csv_file_path, header=None)

        # Check if we were asked to use a specific column's data values
        if column_index is not None and 0 <= column_index < len(df.columns):
            # Extract unique values from the data of the specified column (index 12 is the 13th column)
            column_name = df.columns[column_index]
            # Convert to string, drop NaN values, and return unique items as the attributes
            attributes = df[column_name].dropna().astype(str).unique().tolist()
            print(
                f"Extracted {len(attributes)} unique attributes from column '{column_name}' ({column_index})."
            )
            return attributes
        else:
            # Original behavior: returns the header names as attributes
            print("Extracting column header names as attributes.")
            return df.columns.tolist()

    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file_path}")
        return []
    except Exception as e:
        print(f"Error processing CSV {csv_file_path}: {e}")
        return []


def clean_for_match(name):
    """Cleans entity or table names for robust comparison."""
    # Example: 'DIM_ORGANIZATION#ORGANIZATION' -> 'dimorganizationorganization'
    # Example: 'dim_organization' -> 'dimorganization'
    return name.lower().replace("#", "").replace("_", "")


def infer_relationships(all_entity_raw_data, cleaned_entity_map):
    """
    Infers relationships by scanning column 6 (index 6) of the raw CSV data for explicit join or FK reference strings.

    Uses a pre-built 'cleaned_entity_map' to accurately link the table prefix found in Column 6
    (e.g., 'dim_date') to the full entity name (e.g., 'DIM_DATE#REFERENCE').
    """
    relationships = []

    # Regex to capture any table name followed by a dot and a column name: Table.Column
    # Group 1: Table Name (e.g., 'dim_date', 'dim_time')
    table_ref_pattern = re.compile(r"(\w+)\.\w+", re.IGNORECASE)

    print("-" * 50)
    print(f"Cleaned Entity Map (for lookup): {cleaned_entity_map}")
    print("-" * 50)

    # Now, iterate over the raw data for each entity (which is the Source of the FK)
    for source_entity, df in all_entity_raw_data.items():

        # Ensure the DataFrame has the 7th column (index 6) for relationship data
        if len(df.columns) > 6:
            # Column 6 contains the relationship/join information
            # We use .fillna('') to safely handle NaN values before converting to string and taking uniques
            relationship_column_data = df[6].fillna("").astype(str).unique()

            for rel_candidate in relationship_column_data:

                # Find all table references (e.g., dim_date, dim_time)
                table_prefixes = table_ref_pattern.findall(rel_candidate)

                if not table_prefixes:
                    print(
                        f"  > Skip: Column 6 entry contains no 'Table.Column' pattern: '{rel_candidate}'"
                    )
                    continue

                print(
                    f"  > Found references in '{rel_candidate}'. Base table prefixes: {table_prefixes}"
                )

                # We need to create a relationship between the source_entity and all other referenced entities
                referenced_entities = set()

                for prefix in table_prefixes:
                    cleaned_prefix = clean_for_match(prefix)

                    # Direct, unambiguous lookup using the pre-built map
                    target_entity = cleaned_entity_map.get(cleaned_prefix)

                    if target_entity:
                        # Exclude self-references (e.g., 'dim_organization' referencing 'dim_organization')
                        if target_entity != source_entity:
                            referenced_entities.add(target_entity)
                            print(
                                f"  > Matched prefix '{prefix}' to entity '{target_entity}'."
                            )
                        else:
                            print(
                                f"  > Skipped self-reference from '{source_entity}' to '{target_entity}'."
                            )
                    else:
                        print(
                            f"  > FAILED MATCH: Prefix '{prefix}' (cleaned: '{cleaned_prefix}') not found in entity map."
                        )

                # Create relationships from Source to all referenced Target Entities
                for target_entity in referenced_entities:
                    # Use the first part of the column 6 content as the label
                    label_content = rel_candidate.split(",")[0].strip()
                    label = f"Ref: {label_content}"

                    # Ensure we don't add duplicate edges (e.g., if multiple rows refer to the same relationship)
                    # We store the relationship canonically (sorted entity names) to avoid A->B and B->A duplicates
                    canonical_key = tuple(sorted((source_entity, target_entity)))

                    # Check if this relationship (regardless of direction) is already in the list
                    is_duplicate = any(
                        sorted(list(r[:2])) == list(canonical_key)
                        for r in relationships
                    )

                    if not is_duplicate:
                        relationships.append((source_entity, target_entity, label))
                        print(
                            f"  > SUCCESS: Inferred relationship: {source_entity} <-> {target_entity} via {label}"
                        )
                    else:
                        print(
                            f"  > DUPLICATE: Skipping relationship: {source_entity} <-> {target_entity}"
                        )

    print("-" * 50)
    print(f"Total Relationships Inferred for Diagram: {len(relationships)}")
    return relationships


# def infer_relationships(all_entities_attributes):
#     """
#     Infers relationships by checking the 7th column of each entity's attributes.

#     Assumption: If the 7th column's name (index 6) ends in '_id' (e.g., 'customer_id'),
#     it is a foreign key referencing the table named after the prefix (e.g., 'Customers').
#     """
#     relationships = []

#     # List of all entity names for quick lookup
#     all_entity_names = set(all_entities_attributes.keys())

#     for source_entity, attributes in all_entities_attributes.items():
#         # Check if the 7th column (index 6) exists
#         # if len(attributes) >= 7:
#         #     fk_candidate = attributes[6] # The 7th column (index 6)

#         #     # Use regex to find attributes ending in '_id' and extract the entity name
#         #     # Example: 'customer_id' -> 'Customers'
#         #     match = re.match(r'(.+)_id$', fk_candidate)
#         for fk_candidate in attributes:

#         # Use regex to find attributes ending in '_id' and extract the entity name prefix
#         # Example: 'customer_id' -> 'customer'
#             match = re.match(r'(.+)_id$', fk_candidate)
#             if match:
#                 # Target entity name is the matched prefix, capitalized and pluralized (a common pattern)
#                 # We will simplify by just capitalizing the prefix and checking if it exists.
#                 # Example: 'customer' -> 'Customer'
#                 target_entity_base = match.group(1).capitalize()

#                 # Search for a matching entity name (e.g., 'Customers') in our list of tables
#                 # This check ensures we only create a relationship to an existing table.

#                 # Check for direct match (e.g., if target_entity_base is 'Customer' and we have 'Customer')
#                 if target_entity_base in all_entity_names:
#                     target_entity = target_entity_base
#                 # Check for plural match (e.g., if target_entity_base is 'Customer' and we have 'Customers')
#                 elif target_entity_base + 's' in all_entity_names:
#                     target_entity = target_entity_base + 's'
#                 else:
#                     # No target entity found for this FK candidate
#                     continue

#                 # Add the relationship: (Source, Target, Label)
#                 relationships.append((source_entity, target_entity, f"FK: {fk_candidate}"))
#                 print(f"Inferred FK: {source_entity} -> {target_entity} via {fk_candidate}")

#     return relationships


def generate_erd(entities_attributes, relationships=None, output_file="erd.png"):
    """Generates an ERD using Graphviz."""
    dot = Digraph(comment="Entity Relationship Diagram", graph_attr={"rankdir": "TB"})

    # Add entities and their attributes
    for entity_name, attributes in entities_attributes.items():
        # attribute_fields = ' | '.join(attributes)
        # attribute_fields = '\n'.join(attributes)
        # label = f"{{ {entity_name} | {'/n'.join(attributes)} }}"
        clean_attributes = [attr.strip() for attr in attributes]
        attribute_fields = " | ".join(clean_attributes)
        if attribute_fields:
            label = f"{{ {entity_name} | {attribute_fields} }}"
        else:
            label = f"{{ {entity_name} }}"
        # label = f"{{ {entity_name} | {attribute_fields} }}"
        dot.node(
            entity_name,
            label=label,
            shape="record",
            style="filled",
            fillcolor="lightblue",
            fontname="Helvetica",
        )

    # Add relationships (if provided)
    if relationships:
        for rel in relationships:
            source_entity, target_entity, label = rel
            dot.edge(source_entity, target_entity, label=label)
    # data = io.StringIO()
    # data.write(dot.pipe().decode('utf-8',errors='replace'))
    output_base_path, output_format = output_file.rsplit(".", 1)
    dot.render(output_base_path, format=output_format, view=False, cleanup=True)


if __name__ == "__main__":
    COLUMN_INDEX_TO_USE = 12
    all_csvs = "/Users/abhijat/Downloads/BigQueryModellingAgent/repo/BigQueryModellingAgent/logical_data_model_csvs/"

    ## uncomment below if ER Diagram needs to be generated entitywise
    # files_entitywise = {}
    # for root, subdirs, files in os.walk(all_csvs):
    #     for file in files:
    #         print(file)
    #         entity = file.split("#")[1].split(".csv")[0]
    #         print(entity)
    #         if entity not in files_entitywise:
    #             files_entitywise[entity] = [file]
    #         else:
    #             files_entitywise[entity].append(file)

    # for entity,files in files_entitywise.items():
    #     entities_attributes = {}
    #     all_entity_raw_data = {}
    #     cleaned_entity_map = {}
    #     for file in files:
    #         entity_name = file.replace(".csv", "")
    #         entities_attributes[file.replace(".csv", "")] = get_entity_attributes(all_csvs+file)
    #         # relationships = [("Orders", "Products", "contains")]
    #         df = pd.read_csv(all_csvs+file, header=None)
    #         all_entity_raw_data[entity_name] = df
    #         if not df.empty and 0 in df.columns:
    #                 # Use the unique value from the first column, which is the base table name
    #                 base_table_name = str(df.iloc[0, 0]).strip()
    #                 # print(f"base_table_name: {base_table_name}")
    #                 cleaned_base_name = clean_for_match(base_table_name)

    #                 # Map the cleaned short name (e.g., 'dimorganization') to the full entity name (e.g., 'DIM_ORGANIZATION#ORGANIZATION')
    #                 cleaned_entity_map[cleaned_base_name] = entity_name

    #         relationships = infer_relationships(all_entity_raw_data, cleaned_entity_map)
    #         # print(relationships)
    #         generate_erd(entities_attributes,output_file = entity+"_erd.png")

    entities_attributes = {}
    all_entity_raw_data = {}
    cleaned_entity_map = {}
    for root, subdirs, files in os.walk(all_csvs):
        for file in files:
            entity_name = file.replace(".csv", "")
            entities_attributes[entity_name] = get_entity_attributes(
                all_csvs + file, column_index=COLUMN_INDEX_TO_USE
            )

            df = pd.read_csv(all_csvs + file, header=None)
            all_entity_raw_data[entity_name] = df
            if not df.empty and 0 in df.columns:
                # Use the unique value from the first column, which is the base table name
                base_table_name = str(df.iloc[0, 0]).strip()
                # print(f"base_table_name: {base_table_name}")
                cleaned_base_name = clean_for_match(base_table_name)

                # Map the cleaned short name (e.g., 'dimorganization') to the full entity name (e.g., 'DIM_ORGANIZATION#ORGANIZATION')
                cleaned_entity_map[cleaned_base_name] = entity_name

    relationships = infer_relationships(all_entity_raw_data, cleaned_entity_map)
    print(relationships)
    generate_erd(entities_attributes, relationships=relationships)

    # files_entitywise = {}
    # for root, subdirs, files in os.walk(all_csvs):
    #     # print(files)
    #     for file in files:
    #         print(file)
    #         entity = file.split("#")[1].split(".csv")[0]
    #         print(entity)
    #         if entity not in files_entitywise:
    #             files_entitywise[entity] = [file]
    #         else:
    #             files_entitywise[entity].append(file)

    # for entity,files in files_entitywise.items():
    #     output_dir = "/Users/abhijat/Downloads/BigQueryModellingAgent/repo/BigQueryModellingAgent/logical_data_model_csvs/"
    #     entities_attributes = {}
    #     for file in files:
    #         entities_attributes[file.replace(".csv", "")] = get_entity_attributes(output_dir+file)
    #         # relationships = [("Orders", "Products", "contains")]
    #         generate_erd(entities_attributes,output_file = entity+"_erd.png")

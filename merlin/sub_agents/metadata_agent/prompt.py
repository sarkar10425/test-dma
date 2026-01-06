extraction_prompt = f"""
#SI: Extracting Table and Column Information from SQL Queries (GenAI Prompt)																									
You are an expert SQL parser and data lineage extractor. Your task is to analyze a set of SQL queries (up to 100) provided to you and extract the information required as mentioned below. Queries might contain UDFs and comments too. Ignore the statements that are commented.																									
																									
#TASK: Your task is to identify the following from an Oracle SQL that might contain UDF code you are supposed to understand and analyse the Oracle SQL queries provided to you and extract the information required as mentioned below. Queries might contain UDFs and comments too. Ignore the statements that are commented.																									
																									
    #-Table_Names_base: All table names which are part of base tables, that are not derived or Common Table Expression, but could also be a part of subquery, nested query using base tables within the SQL query. Provide an array of any table alias used in the input SQL query along with the table name																									
                                                                                                        
    #-Table_Names_derived: All table names which are derived tables created within the SQL query ONLY. Provide an array of any table alias used in the input SQL query along with the table name.																									
                                                                                                        
    #-Column_list_base: All the column names which are part of base tables.																									
    # These columns could also be a part of subquery, nested query, filter conditions, join condition, where clause, case statements using base tables ONLY and not derived tables within the SQL query.																									
    # Please include any such columns that are present after the select keyword in any nested query of base tables.																									
    # The list of column should follow the format "table.column" but only if this information is available in the input SQL query.																									
                                                                                                        
    #-Column_list_derived: All the column names which are derived columns.																									
    # These columns could also be a part of subquery, nested query, filter conditions, join condition, where clause, case statements using Derived tables ONLY and not base tables within the SQL query.																									
    # Please include any such columns that are present after the select keyword of derived tables.																									
    # The list of column should follow the format "table.column" but only if this information is available in the input SQL query. The output should be in a single column as a list - "Column_list_derived".																									
    # Additionally, return any derived columns that are part of SELECT clause and fulfill the precedence condition provided.																									
                                                                                                        
    #-Column_list_derived_logic: The logic for all the derived columns which are derived columns created within the SQL query. In case same derived column name has multiple logics, provide all logics as an array. The output should be in a single column as a list - "Column_list_derived_logic".																									
    Additionally, return any logics of any derived columns that are part of SELECT clause and fulfill the precedence condition provided. The list of column should follow the format "table.column" but only if this information is available in the input SQL query.																									
                                                                                                        
    #-Column_nested_query: Select any columns that are a part of nested queries or subqueries, this might be present in the where clause as well. Please include any such columns that are present after the select keyword in any nested query.																									
                                                                                                        
    #-Case_Statements: Analyse all the case statements and extract the logic, their final alias provided and the table_name.column_name on which the filter is applied.																									
                                                                                                        
    #OUTPUT:																									
        1. KPIs, Filters, Union_Join, Case_Statements key should have value in a list.																									
                                                                                                            
        # {{																									
        #   "Table_Names_base": [ [ [ "table_name" , "[table_alias]" ] ] ],																									
        #   "Column_list_base": [ [ [ "Table_Name-Column_Name" ] ] ],																									
        #   "Table_Names_derived": [ [ [ "table_name" , "[table_alias]" ] ] ],																									
        #   "Column_list_derived": [ [ [ "Table_Name-Column_Name" ] ] ],																									
        #   "Column_list_derived_logic": [ [ [ "Table_Name-derived_column_name:derived_column_logics" ] ] ],																									
        #   "Column_nested_query": [ [ [ "Table_Name-Column_Name" ] ] ],																									
        #   "Case_Statements": [																									
        #     {{																									
        #       "case_statement_logic": ,																									
        #       "final_alias": ,																									
        #       "table_name.column_name": ,																									
        #     }}																								
        #   ]																									
        # }}																									
                                                                                                        
    #INSTRUCTIONS:																									
        1. Only provide the information extracted exactly as available in the query. Do not add extra descriptions.																									
        2. Use the logics provided but do not provide any reason or descriptions.																									
                                                                                                            
    SI: Extracting Table and Column Information from SQL Queries (GenAI Prompt)																									
    You are an expert SQL parser and data lineage extractor. Your task is to analyze a set of SQL queries (up to 3) provided to you and extract the information required as mentioned below. Queries might contain UDFs and comments too. Ignore the statements that are commented.																									
                                                                                                        
    Input Format:																									
        A list of SQL queries, where each query is a string. Example:																									
        json																									
        [																									
        SELECT a.col1, b.col2 FROM tableA a JOIN (SELECT x.col3, y.col4 FROM tableX x JOIN tableY y ON x.id = y.id) b ON a.id = b.id,																									
        SELECT * FROM tableZ WHERE col5 > (SELECT MAX(col6) FROM tableW),																									
        WITH DerivedTable AS (SELECT col7 FROM tableV) SELECT * FROM DerivedTable																									
        ]																									
                                                                                                        
    Output Format:																									
        Return the results in json format. JSON format as below																									
                                                                                                            
        A JSON object with the following structure:																								
        {{
        query_index: 0, // Index of the query in the input list
        base_tables: [["tableA", "a"], ["tableX", "x"], ["tableY", "y"]],
        derived_tables: {{
        b: ["tableX", "tableY"]
        }},
        base_table_columns: [
        tableA.col1, "tableA.id", "tableX.col3", "tableX.id", "tableY.col4", "tableY.id"
        ],
        derived_table_columns: [
        b.col2, "b.col3" // Assuming col2 and col3 are output columns of the derived table
        ],
        derived_column_sources: {{
        b.col3: ["tableX.col3"],
        b.col2: ["tableX.col3", "tableY.col4"] // Illustrative example, provide actual derivation logic
        }},
        missed_columns: [] // Should ideally be empty if all columns are captured
        }}
                                                                                                 
    Instructions and Clarifications:
        Handle various SQL constructs: Accurately process different SQL clauses (SELECT, FROM, WHERE, JOIN, GROUP BY, HAVING, subqueries, common table expressions (CTEs), etc.), different join types, and potentially complex nested queries. Alias Resolution: Correctly resolve table and column aliases to identify the underlying base tables and columns. Derived Table Logic: For derived tables, accurately capture the base tables they are derived from. If a derived table is built on top of another derived table, trace back to the ultimate base tables. Column Usage: Identify all columns used from both base tables and derived tables. Include columns in SELECT lists, WHERE clauses, JOIN conditions, aggregation functions, CASE expressions, and any other parts of the query. Be very thorough in identifying column usage, including within nested subqueries. Derived Column Mapping: Show the explicit mapping from derived columns to their source columns, if ascertainable. For example if derived_col = base_col1 + base_col2, reflect this dependency. Handle cases involving functions and complex expressions where possible. If a full derivation is not feasible, make a best effort. Wildcard Handling: For SELECT *, list it as table_name.*. If possible, attempt to resolve * to individual columns based on table schemas if provided, but don't assume schema availability. Missing Columns: The missed_columns array should ideally be empty. Use this to flag any cases where you were unable to definitively identify the source of a column. Include a descriptive explanation of the issue if possible. Robustness: Be robust to variations in SQL syntax (e.g., capitalization of keywords, different quoting styles for identifiers, etc.). Error Handling: Handle potential errors in the input SQL gracefully, for example malformed queries. Indicate the query index and the error encountered. The output should still contain the processed results for valid queries. By following these detailed instructions, you will generate highly accurate and comprehensive information about the tables and columns used in the SQL queries. The structured JSON output will make it easy to programmatically process this information for tasks like data lineage analysis, impact analysis, or query optimization.

    SQL:
    """
# extraction_prompt = f"""
# #SI: Extracting Table and Column Information from SQL Queries (GenAI Prompt)
# You are an expert SQL parser and data lineage extractor. Your task is to analyze a set of SQL queries (up to 100) provided to you and extract the information required as mentioned below. Queries might contain UDFs and comments too. Ignore the statements that are commented.

# #TASK: Your task is to identify the following from an Oracle SQL that might contain UDF code you are supposed to understand and analyse the Oracle SQL queries provided to you and extract the information required as mentioned below. Queries might contain UDFs and comments too. Ignore the statements that are commented.

#     #-Table_Names_base: All table names which are part of base tables, that are not derived or Common Table Expression, but could also be a part of subquery, nested query using base tables within the SQL query. Provide an array of any table alias used in the input SQL query along with the table name

#     #-Table_Names_derived: All table names which are derived tables created within the SQL query ONLY. Provide an array of any table alias used in the input SQL query along with the table name.

#     #-Column_list_base: All the column names which are part of base tables.
#     # These columns could also be a part of subquery, nested query, filter conditions, join condition, where clause, case statements using base tables ONLY and not derived tables within the SQL query.
#     # Please include any such columns that are present after the select keyword in any nested query of base tables.
#     # The list of column should follow the format "table.column" but only if this information is available in the input SQL query.

#     #-Column_list_derived: All the column names which are derived columns.
#     # These columns could also be a part of subquery, nested query, filter conditions, join condition, where clause, case statements using Derived tables ONLY and not base tables within the SQL query.
#     # Please include any such columns that are present after the select keyword of derived tables.
#     # The list of column should follow the format "table.column" but only if this information is available in the input SQL query. The output should be in a single column as a list - "Column_list_derived".
#     # Additionally, return any derived columns that are part of SELECT clause and fulfill the precedence condition provided.

#     #-Column_list_derived_logic: The logic for all the derived columns which are derived columns created within the SQL query. In case same derived column name has multiple logics, provide all logics as an array. The output should be in a single column as a list - "Column_list_derived_logic".
#     Additionally, return any logics of any derived columns that are part of SELECT clause and fulfill the precedence condition provided. The list of column should follow the format "table.column" but only if this information is available in the input SQL query.

#     #-Column_nested_query: Select any columns that are a part of nested queries or subqueries, this might be present in the where clause as well. Please include any such columns that are present after the select keyword in any nested query.

#     #-Case_Statements: Analyse all the case statements and extract the logic, their final alias provided and the table_name.column_name on which the filter is applied.

#     #OUTPUT:
#         1. KPIs, Filters, Union_Join, Case_Statements key should have value in a list.

#         # {{
#         #   "Table_Names_base": [ [ [ "table_name" , "[table_alias]" ] ] ],
#         #   "Column_list_base": [ [ [ "Table_Name-Column_Name" ] ] ],
#         #   "Table_Names_derived": [ [ [ "table_name" , "[table_alias]" ] ] ],
#         #   "Column_list_derived": [ [ [ "Table_Name-Column_Name" ] ] ],
#         #   "Column_list_derived_logic": [ [ [ "Table_Name-derived_column_name:derived_column_logics" ] ] ],
#         #   "Column_nested_query": [ [ [ "Table_Name-Column_Name" ] ] ],
#         #   "Case_Statements": [
#         #     {{
#         #       "case_statement_logic": ,
#         #       "final_alias": ,
#         #       "table_name.column_name": ,
#         #     }}
#         #   ]
#         # }}

#     #INSTRUCTIONS:
#         1. Only provide the information extracted exactly as available in the query. Do not add extra descriptions.
#         2. Use the logics provided but do not provide any reason or descriptions.

#     SI: Extracting Table and Column Information from SQL Queries (GenAI Prompt)
#     You are an expert SQL parser and data lineage extractor. Your task is to analyze a set of SQL queries (up to 3) provided to you and extract the information required as mentioned below. Queries might contain UDFs and comments too. Ignore the statements that are commented.

#     Input Format:
#         A list of SQL queries, where each query is a string. Example:
#         json
#         [
#         SELECT a.col1, b.col2 FROM tableA a JOIN (SELECT x.col3, y.col4 FROM tableX x JOIN tableY y ON x.id = y.id) b ON a.id = b.id,
#         SELECT * FROM tableZ WHERE col5 > (SELECT MAX(col6) FROM tableW),
#         WITH DerivedTable AS (SELECT col7 FROM tableV) SELECT * FROM DerivedTable
#         ]

#     Output Format:
#         Return the results in json format. JSON format as below

#         A JSON object with the following structure:
#         {{
#         queries: [
#         {{
#         query_index: 0, // Index of the query in the input list
#         base_tables: [["tableA", "a"], ["tableX", "x"], ["tableY", "y"]],
#         derived_tables: {{
#         b: ["tableX", "tableY"]
#         }},
#         base_table_columns: [
#         tableA.col1, "tableA.id", "tableX.col3", "tableX.id", "tableY.col4", "tableY.id"
#         ],
#         derived_table_columns: [
#         b.col2, "b.col3" // Assuming col2 and col3 are output columns of the derived table
#         ],
#         derived_column_sources: {{
#         b.col3: ["tableX.col3"],
#         b.col2: ["tableX.col3", "tableY.col4"] // Illustrative example, provide actual derivation logic
#         }},
#         missed_columns: [] // Should ideally be empty if all columns are captured
#         }},
#         {{
#         query_index: 1,
#         base_tables: ["tableZ", "tableW"],
#         derived_tables: {{}},
#         base_table_columns: ["tableZ.*", "tableW.col6"],
#         derived_table_columns: [],
#         derived_column_sources: {{}},
#         missed_columns: []
#         }},
#         {{
#         query_index: 2,
#         base_tables: ["tableV"],
#         derived_tables: {{
#         DerivedTable: ["tableV"]
#         }},
#         base_table_columns: ["tableV.col7"],
#         derived_table_columns: ["DerivedTable.*"], // or list out individual columns if identifiable
#         derived_column_sources: {{
#         DerivedTable.*: ["tableV.col7"] //Or list individual mappings if identifiable
#         }},
#         missed_columns: []
#         }}
#         ]
#         }}

#     Instructions and Clarifications:
#         Handle various SQL constructs: Accurately process different SQL clauses (SELECT, FROM, WHERE, JOIN, GROUP BY, HAVING, subqueries, common table expressions (CTEs), etc.), different join types, and potentially complex nested queries. Alias Resolution: Correctly resolve table and column aliases to identify the underlying base tables and columns. Derived Table Logic: For derived tables, accurately capture the base tables they are derived from. If a derived table is built on top of another derived table, trace back to the ultimate base tables. Column Usage: Identify all columns used from both base tables and derived tables. Include columns in SELECT lists, WHERE clauses, JOIN conditions, aggregation functions, CASE expressions, and any other parts of the query. Be very thorough in identifying column usage, including within nested subqueries. Derived Column Mapping: Show the explicit mapping from derived columns to their source columns, if ascertainable. For example if derived_col = base_col1 + base_col2, reflect this dependency. Handle cases involving functions and complex expressions where possible. If a full derivation is not feasible, make a best effort. Wildcard Handling: For SELECT *, list it as table_name.*. If possible, attempt to resolve * to individual columns based on table schemas if provided, but don't assume schema availability. Missing Columns: The missed_columns array should ideally be empty. Use this to flag any cases where you were unable to definitively identify the source of a column. Include a descriptive explanation of the issue if possible. Robustness: Be robust to variations in SQL syntax (e.g., capitalization of keywords, different quoting styles for identifiers, etc.). Error Handling: Handle potential errors in the input SQL gracefully, for example malformed queries. Indicate the query index and the error encountered. The output should still contain the processed results for valid queries. By following these detailed instructions, you will generate highly accurate and comprehensive information about the tables and columns used in the SQL queries. The structured JSON output will make it easy to programmatically process this information for tasks like data lineage analysis, impact analysis, or query optimization.

#     SQL:
#     """

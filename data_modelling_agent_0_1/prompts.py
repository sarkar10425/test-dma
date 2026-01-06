AGENT_INTRODUCTION_MINIFIED = """Welcome! I am your BigQuery Modeling Assistant, a powerful multi-agent system designed to help you with all aspects of data modeling.
I act as an orchestrator for a team of specialist agents. Just tell me what you need to do, and I'll route your request to the right expert.
"""
AGENT_INTRODUCTION = """Welcome! I am your BigQuery Modelling Assistant, a powerful multi-agent system designed to help you with all aspects of data modeling.

I act as an orchestrator for a team of specialist agents. Just tell me what you need to do, and I'll route your request to the right expert.

Here’s a guide to my team and how they can assist you:

**1. `search_agent` - The Information Retriever**
*   **Purpose:** This agent is your go-to for finding information about your existing data. It can retrieve schemas and metadata for both your raw source data and any data models you've already built.
*   **Use Cases & Examples:**
    *   When a user wants to see an existing schema:
        *   *"Find the schema for the source `customers` table."*
        *   *"Show me the metadata for the target `Dim_User` table we created last week."*
    *   When a user wants to retrieve a data model:
        *   *"Can you retrieve the existing data model for sales?"*

**2. `modelling_orchestrator_agent` - The Architect & Designer**
*   **Purpose:** This is the core agent for designing and generating new data models from scratch. It creates all the necessary artifacts for you to review and build upon.
*   **What it creates:** Logical models, physical DDL scripts (`CREATE TABLE ...`), and detailed metadata in JSON format.
*   **Use Cases & Examples:**
    *   When a user wants to create a new data model from scratch:
        *   *"Design a star schema for e-commerce analytics."*
        *   *"Generate the DDL for fact and dimension tables based on the retail KPIs."*
    *   When a user needs specific model artifacts:
        *   *"Create a logical model and provide physical implementation suggestions for our user data."*
        *   *"Generate the BigQuery metadata JSON for the model I just designed."*

**3. `ddl_agent` - The Builder**
*   **Purpose:** Once a data model design is ready (as a DDL script), this agent's job is to build it in BigQuery. It takes the script and executes it to create your tables.
*   **Use Cases & Examples:**
    *   When a user wants to build tables from a script:
        *   *"Execute the DDL to create the tables in the `sales_dm` dataset."*
        *   *"Run the generated DDL scripts."*
        *   *"Apply the table creation script now."*

**4. `synthetic_data_generator_agent` - The Data Populator**
*   **Purpose:** Need to test your new tables? This agent can populate them with realistic, synthetic (mock) data, which is crucial for development and validation.
*   **Use Cases & Examples:**
    *   When a user needs sample data in their new tables:
        *   *"Generate synthetic data for the `Dim_Customer` and `Fact_Sales` tables."*
        *   *"Populate the newly created tables with mock data."*

**5. `reporting_agent` - The Visualizer**
*   **Purpose:** To help you understand your data model's structure, this agent generates visual reports and diagrams, such as Entity-Relationship Diagrams (ERDs).
*   **Use Cases & Examples:**
    *   When a user wants to visualize the data model:
        *   *"Create a Mermaid ER diagram for the current data model."*
        *   *"Generate a report on the table structures."*

**6. `dml_agent` - The Analyst & Querier**
*   **Purpose:** When your tables are built and populated, this agent helps you get insights from your data. It generates and runs SQL queries to answer analytical questions and calculate metrics.
*   **Use Cases & Examples:**
    *   When a user asks an analytical question about the data:
        *   *"What was the total sales amount for last month?"*
        *   *"Show me the top 10 products by sales."*

You can start by telling me what you'd like to accomplish. For example, try asking me to "design a new data model for sales".
"""

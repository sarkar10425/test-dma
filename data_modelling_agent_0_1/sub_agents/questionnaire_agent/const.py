questions = {
    "Business Domain": {
        1: "Please confirm the official name of the organization for which this data model is being developed.",
        2: "What is the primary industry vertical of the customer?",
        3: "What is the classification of the existing source data model (e.g., Application DB, Data Warehouse, Data Lake)?",
        4: "Are there any specific, non-negotiable data modeling preferences or architectural targets that must be incorporated?",
        5: "What are the critical performance metrics (KPIs) that will be used to evaluate the model's effectiveness and end-user experience?",
        6: "Which 3-5 critical business processes or subject areas must be prioritized and included in the initial data model scope (e.g., Order-to-Cash, Customer 360)?",
        7: "What is the lowest required level of reporting granularity for each critical subject area (e.g., individual sales line item, daily record, hourly reading)?",
        8: "Please identify the most important business metrics and Key Performance Indicators (KPIs) that this data model is intended to calculate and analyze (e.g., Gross Margin, CLV)?",
        9: "What is the required volume and time-span of historical data that must be ingested and maintained in the data warehouse?",
    },
    "Data Flow": {
        1: "Can you provide a comprehensive business glossary, including table/column descriptions and defined business usage?",
        2: "What is the definitive origin of the source data (e.g., specific database, API, flat files, third-party systems)?",
        3: "Can you provide a high-level mapping that defines the relationships between core business entities (e.g., one-to-many, many-to-many)?",
        4: "Which dimensional attributes are expected to change over time, and is it a requirement to track the history of those changes for reporting purposes (SCD type)?",
        5: "Which dimensional attributes are expected to change over time, and is it necessary to track the history of these changes for reporting (SCD)",
        6: "Please provide a high-level mapping of the relationships between core entities (e.g., One Customer can have Many Orders, One Order can have Many Line Items)",
    },
    "NFR": {
        1: "What are the primary expected query types for end-users (e.g., aggregate summaries, detailed drill-down, ad-hoc exploration, line-level data extracts)?",
        2: "What is the mandatory data retention period before data can be formally archived or purged?",
        3: "Does the data to be stored or processed contain Personally Identifiable Information (PII) or other forms of sensitive data?",
        4: "What are the critical data quality rules (e.g., mandatory fields, unique keys, valid value constraints) that must be enforced during the data loading process?",
        5: "Are there any specific Row-Level Security (RLS) requirements that need to be implemented within the data model?",
    },
}

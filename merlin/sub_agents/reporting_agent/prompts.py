MERMAID_ERD_PROMPT = """Generate mermaid erDiagram from the given DDLs. One example is below:

    erDiagram
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER {
        name string
        custNumber  string
        sector string
    }
    ORDER ||--|{ LINE-ITEM : contains
    ORDER {
        orderNumber int
        deliveryAddress  string
    }
    LINE-ITEM {
        productCode  string
        quantity int
        pricePerUnit float
    }

**Must Consideration:
 1. references, belongs to, describes - we dont need these many connection descriptors. references should be enough
 2. While generating Entities the order should be:
column name, data type, constraint, descriptions
e.g: 
    CUSTOMER {
        name string "Name of the Customer"
        custNumber  string PK "Unique number for Customer"
        sector string "Sector customer belongs to"
    }
 3. Fact tables must be placed in the center
"""

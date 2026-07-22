# Database Entity-Relationship (ER) Diagram Description
## AI Customer Support Ticket Intelligence Platform

The database model is designed using standard 3rd Normal Form (3NF) relational practices, separating core entities (Customers, SupportAgents, Products, Categories, TicketStatus, and Departments) from transactional tickets to eliminate data redundancies.

---

### Entity-Relationship Diagram (Mermaid Rendering)

```mermaid
erDiagram
    DEPARTMENTS {
        int Department_ID PK
        string Department_Name UK
    }
    
    PRODUCTS {
        int Product_ID PK
        string Product_Name UK
    }
    
    CATEGORIES {
        int Category_ID PK
        string Category_Name UK
    }
    
    TICKETSTATUS {
        int Status_ID PK
        string Status_Name UK
    }
    
    CUSTOMERS {
        int Customer_ID PK
        string Customer_Name
        string Email UK
        int Age
        string Gender
    }
    
    SUPPORTAGENTS {
        int Agent_ID PK
        string Agent_Name
        string Email UK
        int Department_ID FK
    }
    
    SUPPORTTICKETS {
        int Ticket_ID PK
        int Customer_ID FK
        int Product_ID FK
        int Category_ID FK
        int Status_ID FK
        int Agent_ID FK
        string Subject
        string Description
        string Priority
        string Channel
        datetime Created_Date
        datetime Resolved_Date
        double Resolution_Time
        int Satisfaction_Rating
        string Resolution
    }

    DEPARTMENTS ||--o{ SUPPORTAGENTS : "employs"
    SUPPORTAGENTS ||--o{ SUPPORTTICKETS : "resolves"
    CUSTOMERS ||--o{ SUPPORTTICKETS : "submits"
    PRODUCTS ||--o{ SUPPORTTICKETS : "associated_with"
    CATEGORIES ||--o{ SUPPORTTICKETS : "classified_as"
    TICKETSTATUS ||--o{ SUPPORTTICKETS : "tracked_by"
```

---

### Relationship Rules

1. **Departments to SupportAgents (1:N)**:
   * A support department employs many support agents.
   * An agent belongs to exactly one department (or NULL if unassigned).
2. **SupportAgents to SupportTickets (1:N)**:
   * A support agent can be assigned to resolve multiple support tickets.
   * A ticket has at most one active support agent assigned.
3. **Customers to SupportTickets (1:N)**:
   * A customer can log/submit multiple support tickets over time.
   * A support ticket belongs to exactly one customer.
4. **Products to SupportTickets (1:N)**:
   * A tech product can have multiple related support tickets.
   * A ticket belongs to exactly one product.
5. **Categories to SupportTickets (1:N)**:
   * A ticket category can classify multiple tickets.
   * A ticket has exactly one category.
6. **TicketStatus to SupportTickets (1:N)**:
   * A status label (e.g. Open) tracks multiple tickets simultaneously.
   * A ticket resides in exactly one state status.

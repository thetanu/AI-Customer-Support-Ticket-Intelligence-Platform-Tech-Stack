# Database Data Dictionary
## AI Customer Support Ticket Intelligence Platform

This document describes the schema structure of the normalized 3NF MySQL relational database designed for the support platform.

---

### Table 1: Departments
Contains details of the internal customer support divisions.

| Column Name | Data Type | Key / Constraint | Description |
| :--- | :--- | :--- | :--- |
| **Department_ID** | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each department. |
| **Department_Name** | VARCHAR(100) | NOT NULL, UNIQUE | Name of the support department (e.g. Technical Support). |

---

### Table 2: Products
Contains the list of products supported by the organization.

| Column Name | Data Type | Key / Constraint | Description |
| :--- | :--- | :--- | :--- |
| **Product_ID** | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each product. |
| **Product_Name** | VARCHAR(150) | NOT NULL, UNIQUE | Commercial name of the tech product. |

---

### Table 3: Categories
Classifications for customer issues.

| Column Name | Data Type | Key / Constraint | Description |
| :--- | :--- | :--- | :--- |
| **Category_ID** | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each category. |
| **Category_Name** | VARCHAR(100) | NOT NULL, UNIQUE | Name of the ticket category (e.g., Refund, Billing). |

---

### Table 4: TicketStatus
State machine phases for support tickets.

| Column Name | Data Type | Key / Constraint | Description |
| :--- | :--- | :--- | :--- |
| **Status_ID** | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each status. |
| **Status_Name** | VARCHAR(50) | NOT NULL, UNIQUE | Label of the ticket status (Open, Pending, Closed). |

---

### Table 5: Customers
Profiles of customers registered in the support registry.

| Column Name | Data Type | Key / Constraint | Description |
| :--- | :--- | :--- | :--- |
| **Customer_ID** | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each customer. |
| **Customer_Name** | VARCHAR(150) | NOT NULL | Customer's full name. |
| **Email** | VARCHAR(150) | NOT NULL, UNIQUE | Customer's email address. |
| **Age** | INT | | Age of the customer. |
| **Gender** | VARCHAR(20) | | Registered gender (e.g., Male, Female, Other). |

---

### Table 6: SupportAgents
Operational support personnel assignment registry.

| Column Name | Data Type | Key / Constraint | Description |
| :--- | :--- | :--- | :--- |
| **Agent_ID** | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each agent. |
| **Agent_Name** | VARCHAR(150) | NOT NULL | Full name of the agent. |
| **Email** | VARCHAR(150) | NOT NULL, UNIQUE | Corporate email address. |
| **Department_ID** | INT | FOREIGN KEY | Department the agent belongs to. |

---

### Table 7: SupportTickets
The core transactional table linking customer issues, agents, products, and operational logs.

| Column Name | Data Type | Key / Constraint | Description |
| :--- | :--- | :--- | :--- |
| **Ticket_ID** | INT | PRIMARY KEY | Unique identifier for each support ticket. |
| **Customer_ID** | INT | FOREIGN KEY | Customer who logged the ticket. |
| **Product_ID** | INT | FOREIGN KEY | Product associated with the issue. |
| **Category_ID** | INT | FOREIGN KEY | Category of the issue. |
| **Status_ID** | INT | FOREIGN KEY | Current status of the ticket. |
| **Agent_ID** | INT | FOREIGN KEY | Support agent assigned to resolve it. |
| **Subject** | VARCHAR(255) | NOT NULL | Summary line of the issue. |
| **Description** | TEXT | | Detailed descriptive log of the issue. |
| **Priority** | VARCHAR(50) | NOT NULL | Priority level (Low, Medium, High). |
| **Channel** | VARCHAR(50) | NOT NULL | Intake channel (Email, Phone, Chat, Social media). |
| **Created_Date** | DATETIME | NOT NULL | Timestamp when the ticket was generated. |
| **Resolved_Date** | DATETIME | NULLABLE | Timestamp when the ticket was marked Closed. |
| **Resolution_Time**| DOUBLE | NULLABLE | Resolution time computed in hours. |
| **Satisfaction_Rating**| INT | NULLABLE | CSAT score rating (1-5 stars). |
| **Resolution** | TEXT | NULLABLE | Technical description of the final resolution. |

USE support_intelligence;

-- View 1: Detailed Ticket Summary
CREATE OR REPLACE VIEW v_detailed_tickets AS
SELECT 
    t.Ticket_ID,
    c.Customer_Name,
    c.Email AS Customer_Email,
    c.Age AS Customer_Age,
    c.Gender AS Customer_Gender,
    p.Product_Name,
    cat.Category_Name AS Ticket_Category,
    t.Subject,
    t.Description,
    t.Priority,
    s.Status_Name AS Ticket_Status,
    t.Channel,
    t.Created_Date,
    t.Resolved_Date,
    t.Resolution_Time,
    t.Satisfaction_Rating,
    a.Agent_Name,
    d.Department_Name
FROM SupportTickets t
LEFT JOIN Customers c ON t.Customer_ID = c.Customer_ID
LEFT JOIN Products p ON t.Product_ID = p.Product_ID
LEFT JOIN Categories cat ON t.Category_ID = cat.Category_ID
LEFT JOIN TicketStatus s ON t.Status_ID = s.Status_ID
LEFT JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
LEFT JOIN Departments d ON a.Department_ID = d.Department_ID;

-- View 2: Agent Performance Metrics
CREATE OR REPLACE VIEW v_agent_kpi AS
SELECT 
    a.Agent_ID,
    a.Agent_Name,
    d.Department_Name,
    COUNT(t.Ticket_ID) AS Total_Tickets_Assigned,
    SUM(CASE WHEN s.Status_Name = 'Closed' THEN 1 ELSE 0 END) AS Resolved_Tickets,
    SUM(CASE WHEN s.Status_Name = 'Open' THEN 1 ELSE 0 END) AS Open_Tickets,
    ROUND(AVG(t.Resolution_Time), 2) AS Avg_Resolution_Time_Hours,
    ROUND(AVG(t.Satisfaction_Rating), 2) AS Avg_Satisfaction_Rating
FROM SupportAgents a
LEFT JOIN Departments d ON a.Department_ID = d.Department_ID
LEFT JOIN SupportTickets t ON a.Agent_ID = t.Agent_ID
LEFT JOIN TicketStatus s ON t.Status_ID = s.Status_ID
GROUP BY a.Agent_ID, a.Agent_Name, d.Department_Name;

-- View 3: Executive Daily Summary KPIs
CREATE OR REPLACE VIEW v_executive_kpis AS
SELECT
    COUNT(Ticket_ID) AS Total_Tickets,
    SUM(CASE WHEN Status_ID = (SELECT Status_ID FROM TicketStatus WHERE Status_Name='Open') THEN 1 ELSE 0 END) AS Open_Tickets,
    SUM(CASE WHEN Status_ID = (SELECT Status_ID FROM TicketStatus WHERE Status_Name='Closed') THEN 1 ELSE 0 END) AS Closed_Tickets,
    ROUND(AVG(Resolution_Time), 2) AS Overall_Avg_Resolution_Hours,
    ROUND(AVG(Satisfaction_Rating), 2) AS Overall_Satisfaction_Rating,
    SUM(CASE WHEN Priority='High' AND Status_ID != (SELECT Status_ID FROM TicketStatus WHERE Status_Name='Closed') THEN 1 ELSE 0 END) AS Open_High_Priority_Tickets
FROM SupportTickets;

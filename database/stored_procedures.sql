USE support_intelligence;

DROP PROCEDURE IF EXISTS sp_get_agent_workload;
DROP PROCEDURE IF EXISTS sp_close_ticket;
DROP PROCEDURE IF EXISTS sp_get_tickets_by_customer;

DELIMITER $$

-- Procedure 1: Agent Workload Report
CREATE PROCEDURE sp_get_agent_workload()
BEGIN
    SELECT 
        a.Agent_ID,
        a.Agent_Name,
        COUNT(t.Ticket_ID) AS Active_Tickets
    FROM SupportAgents a
    LEFT JOIN SupportTickets t ON a.Agent_ID = t.Agent_ID
    LEFT JOIN TicketStatus s ON t.Status_ID = s.Status_ID
    WHERE s.Status_Name != 'Closed' OR s.Status_Name IS NULL
    GROUP BY a.Agent_ID, a.Agent_Name
    ORDER BY Active_Tickets DESC;
END$$

-- Procedure 2: Resolution closure handler
CREATE PROCEDURE sp_close_ticket(
    IN p_ticket_id INT,
    IN p_resolution TEXT,
    IN p_satisfaction INT
)
BEGIN
    DECLARE v_status_closed_id INT;
    SELECT Status_ID INTO v_status_closed_id FROM TicketStatus WHERE Status_Name = 'Closed';
    
    UPDATE SupportTickets
    SET 
        Status_ID = v_status_closed_id,
        Resolution = p_resolution,
        Satisfaction_Rating = p_satisfaction,
        Resolved_Date = NOW(),
        Resolution_Time = ROUND(TIMESTAMPDIFF(MINUTE, Created_Date, NOW()) / 60.0, 2)
    WHERE Ticket_ID = p_ticket_id;
END$$

-- Procedure 3: Get tickets by Customer ID or Email
CREATE PROCEDURE sp_get_tickets_by_customer(
    IN p_cust_identifier VARCHAR(150)
)
BEGIN
    SELECT 
        t.Ticket_ID,
        t.Subject,
        t.Priority,
        s.Status_Name AS Status,
        t.Created_Date
    FROM SupportTickets t
    JOIN Customers c ON t.Customer_ID = c.Customer_ID
    JOIN TicketStatus s ON t.Status_ID = s.Status_ID
    WHERE c.Email = p_cust_identifier OR c.Customer_Name LIKE CONCAT('%', p_cust_identifier, '%')
    ORDER BY t.Created_Date DESC;
END$$

DELIMITER ;

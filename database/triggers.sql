USE support_intelligence;

DROP TABLE IF EXISTS TicketAuditLog;
CREATE TABLE TicketAuditLog (
    Audit_ID INT PRIMARY KEY AUTO_INCREMENT,
    Ticket_ID INT,
    Old_Status_ID INT,
    New_Status_ID INT,
    Changed_By VARCHAR(100),
    Changed_At DATETIME
);

DROP TRIGGER IF EXISTS trg_audit_ticket_status;
DROP TRIGGER IF EXISTS trg_check_agent_assignment;

DELIMITER $$

-- Trigger 1: Status Change Audit Tracker
CREATE TRIGGER trg_audit_ticket_status
AFTER UPDATE ON SupportTickets
FOR EACH ROW
BEGIN
    IF OLD.Status_ID <> NEW.Status_ID THEN
        INSERT INTO TicketAuditLog (Ticket_ID, Old_Status_ID, New_Status_ID, Changed_By, Changed_At)
        VALUES (NEW.Ticket_ID, OLD.Status_ID, NEW.Status_ID, USER(), NOW());
    END IF;
END$$

-- Trigger 2: Prevent assigning tickets to Agents not belonging to Departments if no Department
CREATE TRIGGER trg_check_agent_assignment
BEFORE INSERT ON SupportTickets
FOR EACH ROW
BEGIN
    DECLARE v_agent_dept INT;
    IF NEW.Agent_ID IS NOT NULL THEN
        SELECT Department_ID INTO v_agent_dept FROM SupportAgents WHERE Agent_ID = NEW.Agent_ID;
        IF v_agent_dept IS NULL THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot assign ticket: Support Agent must belong to an active Department.';
        END IF;
    END IF;
END$$

DELIMITER ;

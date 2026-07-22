USE support_intelligence;

DROP FUNCTION IF EXISTS fn_get_sla_status;
DROP FUNCTION IF EXISTS fn_get_satisfaction_label;

DELIMITER $$

-- Function 1: SLA status evaluation (returns Breached or Met)
CREATE FUNCTION fn_get_sla_status(priority VARCHAR(50), resolution_time DOUBLE)
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
    DECLARE sla_status VARCHAR(20);
    IF resolution_time IS NULL THEN
        SET sla_status = 'Pending';
    ELSEIF priority = 'High' AND resolution_time > 24.0 THEN
        SET sla_status = 'SLA Breached';
    ELSEIF priority = 'Medium' AND resolution_time > 72.0 THEN
        SET sla_status = 'SLA Breached';
    ELSEIF priority = 'Low' AND resolution_time > 120.0 THEN
        SET sla_status = 'SLA Breached';
    ELSE
        SET sla_status = 'SLA Met';
    END IF;
    RETURN sla_status;
END$$

-- Function 2: Satisfaction score text mapping
CREATE FUNCTION fn_get_satisfaction_label(rating INT)
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
    DECLARE label VARCHAR(20);
    CASE rating
        WHEN 1 THEN SET label = 'Very Dissatisfied';
        WHEN 2 THEN SET label = 'Dissatisfied';
        WHEN 3 THEN SET label = 'Neutral';
        WHEN 4 THEN SET label = 'Satisfied';
        WHEN 5 THEN SET label = 'Very Satisfied';
        ELSE SET label = 'Not Rated';
    END CASE;
    RETURN label;
END$$

DELIMITER ;

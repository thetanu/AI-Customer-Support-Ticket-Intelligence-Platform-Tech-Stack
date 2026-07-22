-- AI Customer Support Ticket Intelligence Platform
-- 65 Business KPI & Analytical Queries for MySQL Workbench
-- ==============================================================================

USE support_intelligence;

-- ------------------------------------------------------------------------------
-- PART 1: TICKET VOLUME & STATUS ANALYSIS (10 Queries)
-- ------------------------------------------------------------------------------

-- Query 1: Total Support Tickets count
SELECT COUNT(*) AS total_tickets FROM SupportTickets;

-- Query 2: Ticket counts grouped by Status
SELECT ts.Status_Name, COUNT(st.Ticket_ID) AS ticket_count 
FROM SupportTickets st
JOIN TicketStatus ts ON st.Status_ID = ts.Status_ID
GROUP BY ts.Status_Name;

-- Query 3: Ticket counts by Priority Level
SELECT Priority, COUNT(*) AS ticket_count 
FROM SupportTickets 
GROUP BY Priority 
ORDER BY ticket_count DESC;

-- Query 4: Open and Pending Tickets
SELECT COUNT(*) AS open_pending_tickets 
FROM SupportTickets 
WHERE Status_ID IN (SELECT Status_ID FROM TicketStatus WHERE Status_Name IN ('Open', 'Pending Customer Response'));

-- Query 5: Closed Ticket Volume
SELECT COUNT(*) AS closed_tickets 
FROM SupportTickets 
WHERE Status_ID = (SELECT Status_ID FROM TicketStatus WHERE Status_Name = 'Closed');

-- Query 6: Tickets by Submission Channel
SELECT Channel, COUNT(*) AS channel_volume
FROM SupportTickets 
GROUP BY Channel 
ORDER BY channel_volume DESC;

-- Query 7: Percentage Distribution of Channels
SELECT Channel, COUNT(*) AS volume,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM SupportTickets), 2) AS percentage
FROM SupportTickets 
GROUP BY Channel;

-- Query 8: High Priority Tickets submitted through Email
SELECT COUNT(*) AS high_priority_email_tickets 
FROM SupportTickets 
WHERE Priority = 'High' AND Channel = 'Email';

-- Query 9: Tickets Created per Calendar Year
SELECT YEAR(Created_Date) AS ticket_year, COUNT(*) AS volume 
FROM SupportTickets 
GROUP BY YEAR(Created_Date);

-- Query 10: Tickets by Month and Year
SELECT YEAR(Created_Date) AS ticket_year, MONTH(Created_Date) AS ticket_month, COUNT(*) AS volume 
FROM SupportTickets 
GROUP BY YEAR(Created_Date), MONTH(Created_Date)
ORDER BY ticket_year DESC, ticket_month DESC;


-- ------------------------------------------------------------------------------
-- PART 2: CATEGORY & PRODUCT ANGLE (10 Queries)
-- ------------------------------------------------------------------------------

-- Query 11: Tickets by Ticket Category
SELECT c.Category_Name, COUNT(t.Ticket_ID) AS volume 
FROM SupportTickets t
JOIN Categories c ON t.Category_ID = c.Category_ID
GROUP BY c.Category_Name
ORDER BY volume DESC;

-- Query 12: Ticket Category breakdown by Priority
SELECT c.Category_Name, t.Priority, COUNT(t.Ticket_ID) AS volume 
FROM SupportTickets t
JOIN Categories c ON t.Category_ID = c.Category_ID
GROUP BY c.Category_Name, t.Priority
ORDER BY c.Category_Name, volume DESC;

-- Query 13: Top 10 Products generating highest ticket volume
SELECT p.Product_Name, COUNT(t.Ticket_ID) AS ticket_count
FROM SupportTickets t
JOIN Products p ON t.Product_ID = p.Product_ID
GROUP BY p.Product_Name
ORDER BY ticket_count DESC
LIMIT 10;

-- Query 14: Ticket Category distribution for GoPro Hero
SELECT c.Category_Name, COUNT(t.Ticket_ID) AS ticket_count
FROM SupportTickets t
JOIN Products p ON t.Product_ID = p.Product_ID
JOIN Categories c ON t.Category_ID = c.Category_ID
WHERE p.Product_Name = 'GoPro Hero'
GROUP BY c.Category_Name
ORDER BY ticket_count DESC;

-- Query 15: Products with the highest proportion of High Priority Tickets
SELECT p.Product_Name, 
       SUM(CASE WHEN t.Priority = 'High' THEN 1 ELSE 0 END) AS high_priority_count,
       COUNT(t.Ticket_ID) AS total_count,
       ROUND(SUM(CASE WHEN t.Priority = 'High' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.Ticket_ID), 2) AS high_priority_pct
FROM SupportTickets t
JOIN Products p ON t.Product_ID = p.Product_ID
GROUP BY p.Product_Name
HAVING total_count > 50
ORDER BY high_priority_pct DESC
LIMIT 10;

-- Query 16: Satisfaction rating by Ticket Category
SELECT c.Category_Name, ROUND(AVG(t.Satisfaction_Rating), 2) AS avg_csat
FROM SupportTickets t
JOIN Categories c ON t.Category_ID = c.Category_ID
WHERE t.Satisfaction_Rating IS NOT NULL
GROUP BY c.Category_Name;

-- Query 17: Average resolution time (hours) by Category
SELECT c.Category_Name, ROUND(AVG(t.Resolution_Time), 2) AS avg_resolution_hours
FROM SupportTickets t
JOIN Categories c ON t.Category_ID = c.Category_ID
WHERE t.Resolution_Time IS NOT NULL
GROUP BY c.Category_Name;

-- Query 18: Channels generating the most Refund tickets
SELECT t.Channel, COUNT(t.Ticket_ID) AS refund_tickets
FROM SupportTickets t
JOIN Categories c ON t.Category_ID = c.Category_ID
WHERE c.Category_Name = 'Refund'
GROUP BY t.Channel
ORDER BY refund_tickets DESC;

-- Query 19: Bottom 5 Products by average Customer Satisfaction (CSAT)
SELECT p.Product_Name, ROUND(AVG(t.Satisfaction_Rating), 2) AS avg_csat, COUNT(t.Ticket_ID) AS total_tickets
FROM SupportTickets t
JOIN Products p ON t.Product_ID = p.Product_ID
WHERE t.Satisfaction_Rating IS NOT NULL
GROUP BY p.Product_Name
HAVING total_tickets >= 10
ORDER BY avg_csat ASC
LIMIT 5;

-- Query 20: Monthly trend of Technical issues
SELECT YEAR(t.Created_Date) AS yr, MONTH(t.Created_Date) AS mth, COUNT(t.Ticket_ID) AS tech_tickets
FROM SupportTickets t
JOIN Categories c ON t.Category_ID = c.Category_ID
WHERE c.Category_Name = 'Technical'
GROUP BY YEAR(t.Created_Date), MONTH(t.Created_Date)
ORDER BY yr DESC, mth DESC;


-- ------------------------------------------------------------------------------
-- PART 3: AGENT & DEPARTMENT PERFORMANCE KPIs (15 Queries)
-- ------------------------------------------------------------------------------

-- Query 21: Support Agents count per Department
SELECT d.Department_Name, COUNT(a.Agent_ID) AS agent_count
FROM SupportAgents a
JOIN Departments d ON a.Department_ID = d.Department_ID
GROUP BY d.Department_Name;

-- Query 22: Top 5 Agents with the most resolved tickets
SELECT a.Agent_Name, COUNT(t.Ticket_ID) AS resolved_count
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
JOIN TicketStatus s ON t.Status_ID = s.Status_ID
WHERE s.Status_Name = 'Closed'
GROUP BY a.Agent_Name
ORDER BY resolved_count DESC
LIMIT 5;

-- Query 23: Average CSAT rating of each Support Department
SELECT d.Department_Name, ROUND(AVG(t.Satisfaction_Rating), 2) AS avg_csat
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
JOIN Departments d ON a.Department_ID = d.Department_ID
WHERE t.Satisfaction_Rating IS NOT NULL
GROUP BY d.Department_Name;

-- Query 24: Average Resolution Time (Hours) by Department
SELECT d.Department_Name, ROUND(AVG(t.Resolution_Time), 2) AS avg_resolution_time
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
JOIN Departments d ON a.Department_ID = d.Department_ID
WHERE t.Resolution_Time IS NOT NULL
GROUP BY d.Department_Name;

-- Query 25: Active ticket workload per agent
SELECT a.Agent_Name, COUNT(t.Ticket_ID) AS active_workload
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
JOIN TicketStatus s ON t.Status_ID = s.Status_ID
WHERE s.Status_Name IN ('Open', 'Pending Customer Response')
GROUP BY a.Agent_Name
ORDER BY active_workload DESC;

-- Query 26: Bottom 5 agents with lowest CSAT ratings (minimum 30 ratings)
SELECT a.Agent_Name, ROUND(AVG(t.Satisfaction_Rating), 2) AS avg_csat, COUNT(t.Satisfaction_Rating) AS rating_count
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
WHERE t.Satisfaction_Rating IS NOT NULL
GROUP BY a.Agent_Name
HAVING rating_count >= 30
ORDER BY avg_csat ASC
LIMIT 5;

-- Query 27: Top 5 agents with highest CSAT ratings (minimum 30 ratings)
SELECT a.Agent_Name, ROUND(AVG(t.Satisfaction_Rating), 2) AS avg_csat, COUNT(t.Satisfaction_Rating) AS rating_count
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
WHERE t.Satisfaction_Rating IS NOT NULL
GROUP BY a.Agent_Name
HAVING rating_count >= 30
ORDER BY avg_csat DESC
LIMIT 5;

-- Query 28: Agent ticket distribution by priority levels
SELECT a.Agent_Name, t.Priority, COUNT(t.Ticket_ID) AS count
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
GROUP BY a.Agent_Name, t.Priority
ORDER BY a.Agent_Name, count DESC;

-- Query 29: Resolution efficiency: Tickets resolved within 24 hours by Agent
SELECT a.Agent_Name, COUNT(t.Ticket_ID) AS quick_resolutions
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
WHERE t.Resolution_Time <= 24.0 AND t.Status_ID = (SELECT Status_ID FROM TicketStatus WHERE Status_Name='Closed')
GROUP BY a.Agent_Name
ORDER BY quick_resolutions DESC;

-- Query 30: Total unresolved tickets older than 5 days
SELECT COUNT(*) AS aged_unresolved_tickets
FROM SupportTickets t
JOIN TicketStatus s ON t.Status_ID = s.Status_ID
WHERE s.Status_Name <> 'Closed' AND t.Created_Date < DATE_SUB(NOW(), INTERVAL 5 DAY);

-- Query 31: Department SLA compliance rate (High Priority Target < 24 Hours)
SELECT d.Department_Name, 
       SUM(CASE WHEN t.Priority = 'High' AND t.Resolution_Time <= 24.0 THEN 1 
                WHEN t.Priority = 'High' AND t.Resolution_Time > 24.0 THEN 0 ELSE NULL END) AS sla_met,
       SUM(CASE WHEN t.Priority = 'High' THEN 1 ELSE 0 END) AS total_high_priority,
       ROUND(SUM(CASE WHEN t.Priority = 'High' AND t.Resolution_Time <= 24.0 THEN 1 ELSE 0 END) * 100.0 / 
             SUM(CASE WHEN t.Priority = 'High' THEN 1 ELSE 0 END), 2) AS sla_compliance_pct
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
JOIN Departments d ON a.Department_ID = d.Department_ID
GROUP BY d.Department_Name;

-- Query 32: Agents with no tickets assigned
SELECT Agent_Name, Email 
FROM SupportAgents 
WHERE Agent_ID NOT IN (SELECT DISTINCT Agent_ID FROM SupportTickets WHERE Agent_ID IS NOT NULL);

-- Query 33: Agent with the fastest average resolution time for Billing issues
SELECT a.Agent_Name, ROUND(AVG(t.Resolution_Time), 2) AS avg_res_time
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
JOIN Categories c ON t.Category_ID = c.Category_ID
WHERE c.Category_Name = 'Billing' AND t.Resolution_Time IS NOT NULL
GROUP BY a.Agent_Name
ORDER BY avg_res_time ASC
LIMIT 1;

-- Query 34: CSAT score distribution by Support Agent (1-5)
SELECT a.Agent_Name,
       SUM(CASE WHEN t.Satisfaction_Rating = 1 THEN 1 ELSE 0 END) AS score_1,
       SUM(CASE WHEN t.Satisfaction_Rating = 2 THEN 1 ELSE 0 END) AS score_2,
       SUM(CASE WHEN t.Satisfaction_Rating = 3 THEN 1 ELSE 0 END) AS score_3,
       SUM(CASE WHEN t.Satisfaction_Rating = 4 THEN 1 ELSE 0 END) AS score_4,
       SUM(CASE WHEN t.Satisfaction_Rating = 5 THEN 1 ELSE 0 END) AS score_5
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
GROUP BY a.Agent_Name;

-- Query 35: Agent efficiency ratio (Total closed tickets divided by average resolution time)
SELECT a.Agent_Name,
       COUNT(CASE WHEN s.Status_Name='Closed' THEN 1 END) AS closed_tickets,
       ROUND(AVG(t.Resolution_Time), 2) AS avg_time,
       ROUND(COUNT(CASE WHEN s.Status_Name='Closed' THEN 1 END) / AVG(t.Resolution_Time), 2) AS efficiency_index
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
JOIN TicketStatus s ON t.Status_ID = s.Status_ID
WHERE t.Resolution_Time > 0
GROUP BY a.Agent_Name
ORDER BY efficiency_index DESC;


-- ------------------------------------------------------------------------------
-- PART 4: CUSTOMER PROFILES & BEHAVIOUR (10 Queries)
-- ------------------------------------------------------------------------------

-- Query 36: Top 5 Customers who submitted the most tickets
SELECT c.Customer_Name, c.Email, COUNT(t.Ticket_ID) AS ticket_count
FROM SupportTickets t
JOIN Customers c ON t.Customer_ID = c.Customer_ID
GROUP BY c.Customer_ID, c.Customer_Name, c.Email
ORDER BY ticket_count DESC
LIMIT 5;

-- Query 37: Customer demographics: ticket volume by Gender
SELECT c.Gender, COUNT(t.Ticket_ID) AS ticket_count
FROM SupportTickets t
JOIN Customers c ON t.Customer_ID = c.Customer_ID
GROUP BY c.Gender;

-- Query 38: Customer demographics: average satisfaction rating by Gender
SELECT c.Gender, ROUND(AVG(t.Satisfaction_Rating), 2) AS avg_csat
FROM SupportTickets t
JOIN Customers c ON t.Customer_ID = c.Customer_ID
WHERE t.Satisfaction_Rating IS NOT NULL
GROUP BY c.Gender;

-- Query 39: Ticket volume by Customer Age Groups
SELECT 
    CASE 
        WHEN c.Age < 25 THEN 'Under 25'
        WHEN c.Age BETWEEN 25 AND 40 THEN '25-40'
        WHEN c.Age BETWEEN 41 AND 60 THEN '41-60'
        ELSE 'Over 60'
    END AS age_group,
    COUNT(t.Ticket_ID) AS ticket_count
FROM SupportTickets t
JOIN Customers c ON t.Customer_ID = c.Customer_ID
GROUP BY age_group
ORDER BY ticket_count DESC;

-- Query 40: Customer Satisfaction Rating (CSAT) by Age Group
SELECT 
    CASE 
        WHEN c.Age < 25 THEN 'Under 25'
        WHEN c.Age BETWEEN 25 AND 40 THEN '25-40'
        WHEN c.Age BETWEEN 41 AND 60 THEN '41-60'
        ELSE 'Over 60'
    END AS age_group,
    ROUND(AVG(t.Satisfaction_Rating), 2) AS avg_csat
FROM SupportTickets t
JOIN Customers c ON t.Customer_ID = c.Customer_ID
WHERE t.Satisfaction_Rating IS NOT NULL
GROUP BY age_group;

-- Query 41: Top 5 customers with lowest average satisfaction rating (minimum 2 tickets)
SELECT c.Customer_Name, c.Email, ROUND(AVG(t.Satisfaction_Rating), 2) AS avg_csat, COUNT(t.Ticket_ID) AS total_tickets
FROM SupportTickets t
JOIN Customers c ON t.Customer_ID = c.Customer_ID
WHERE t.Satisfaction_Rating IS NOT NULL
GROUP BY c.Customer_ID, c.Customer_Name, c.Email
HAVING total_tickets >= 2
ORDER BY avg_csat ASC
LIMIT 5;

-- Query 42: Channel preference based on Customer Age Group
SELECT 
    CASE 
        WHEN c.Age < 25 THEN 'Under 25'
        WHEN c.Age BETWEEN 25 AND 40 THEN '25-40'
        WHEN c.Age BETWEEN 41 AND 60 THEN '41-60'
        ELSE 'Over 60'
    END AS age_group,
    t.Channel,
    COUNT(t.Ticket_ID) AS ticket_count
FROM SupportTickets t
JOIN Customers c ON t.Customer_ID = c.Customer_ID
GROUP BY age_group, t.Channel
ORDER BY age_group, ticket_count DESC;

-- Query 43: Average satisfaction score for tickets resolved in less than 12 hours
SELECT ROUND(AVG(Satisfaction_Rating), 2) AS avg_csat_fast_res 
FROM SupportTickets 
WHERE Resolution_Time <= 12.0 AND Satisfaction_Rating IS NOT NULL;

-- Query 44: Average satisfaction score for tickets resolved in more than 72 hours
SELECT ROUND(AVG(Satisfaction_Rating), 2) AS avg_csat_slow_res 
FROM SupportTickets 
WHERE Resolution_Time >= 72.0 AND Satisfaction_Rating IS NOT NULL;

-- Query 45: Customers who had a negative experience (CSAT <= 2) and their tickets details
SELECT c.Customer_Name, t.Ticket_ID, t.Subject, t.Satisfaction_Rating, t.Resolution
FROM SupportTickets t
JOIN Customers c ON t.Customer_ID = c.Customer_ID
WHERE t.Satisfaction_Rating <= 2
ORDER BY t.Satisfaction_Rating ASC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- PART 5: ADVANCED ANALYTICS, CTEs, WINDOW FUNCTIONS (20 Queries)
-- ------------------------------------------------------------------------------

-- Query 46: Rank products by customer satisfaction score using DENSE_RANK()
WITH ProductCSAT AS (
    SELECT p.Product_Name, 
           AVG(t.Satisfaction_Rating) AS avg_rating,
           COUNT(t.Ticket_ID) AS ticket_count
    FROM SupportTickets t
    JOIN Products p ON t.Product_ID = p.Product_ID
    WHERE t.Satisfaction_Rating IS NOT NULL
    GROUP BY p.Product_Name
)
SELECT Product_Name, ROUND(avg_rating, 2) AS avg_rating, ticket_count,
       DENSE_RANK() OVER (ORDER BY avg_rating DESC) AS rating_rank
FROM ProductCSAT
LIMIT 10;

-- Query 47: Running cumulative total of tickets submitted monthly over time
WITH MonthlyVolume AS (
    SELECT YEAR(Created_Date) AS yr, MONTH(Created_Date) AS mth, COUNT(Ticket_ID) AS mth_count
    FROM SupportTickets
    GROUP BY YEAR(Created_Date), MONTH(Created_Date)
)
SELECT yr, mth, mth_count,
       SUM(mth_count) OVER (ORDER BY yr, mth) AS running_total
FROM MonthlyVolume;

-- Query 48: First ticket submitted in each year using ROW_NUMBER()
WITH YearRankedTickets AS (
    SELECT Ticket_ID, Subject, Created_Date, YEAR(Created_Date) AS yr,
           ROW_NUMBER() OVER (PARTITION BY YEAR(Created_Date) ORDER BY Created_Date ASC) AS rn
    FROM SupportTickets
)
SELECT yr, Ticket_ID, Subject, Created_Date 
FROM YearRankedTickets
WHERE rn = 1;

-- Query 49: Difference in resolution time compared to department average using Window Functions
SELECT t.Ticket_ID, d.Department_Name, t.Resolution_Time,
       ROUND(AVG(t.Resolution_Time) OVER (PARTITION BY d.Department_ID), 2) AS dept_avg,
       ROUND(t.Resolution_Time - AVG(t.Resolution_Time) OVER (PARTITION BY d.Department_ID), 2) AS diff_from_avg
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
JOIN Departments d ON a.Department_ID = d.Department_ID
WHERE t.Resolution_Time IS NOT NULL
LIMIT 10;

-- Query 50: Finding the percentage difference in ticket volume month-over-month
WITH MonthlyTickets AS (
    SELECT DATE_FORMAT(Created_Date, '%Y-%m') AS year_month, COUNT(*) AS ticket_count
    FROM SupportTickets
    GROUP BY year_month
    ORDER BY year_month
),
MoMCompare AS (
    SELECT year_month, ticket_count,
           LAG(ticket_count, 1) OVER (ORDER BY year_month) AS prev_month_count
    FROM MonthlyTickets
)
SELECT year_month, ticket_count, prev_month_count,
       ROUND((ticket_count - prev_month_count) * 100.0 / prev_month_count, 2) AS pct_change
FROM MoMCompare;

-- Query 51: Finding customers with above-average number of tickets submitted
WITH CustomerCounts AS (
    SELECT Customer_ID, COUNT(Ticket_ID) AS count
    FROM SupportTickets
    GROUP BY Customer_ID
)
SELECT c.Customer_Name, cc.count
FROM CustomerCounts cc
JOIN Customers c ON cc.Customer_ID = c.Customer_ID
WHERE cc.count > (SELECT AVG(count) FROM CustomerCounts)
ORDER BY cc.count DESC
LIMIT 10;

-- Query 52: Identify SLA breaches per Agent using the User Defined Function fn_get_sla_status()
SELECT t.Ticket_ID, a.Agent_Name, t.Priority, t.Resolution_Time,
       fn_get_sla_status(t.Priority, t.Resolution_Time) AS SLA_Status
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
WHERE t.Resolution_Time IS NOT NULL
LIMIT 15;

-- Query 53: Total tickets and SLA compliance rate for each Support Agent
WITH AgentSLAs AS (
    SELECT Agent_ID, Priority, Resolution_Time,
           fn_get_sla_status(Priority, Resolution_Time) AS status
    FROM SupportTickets
    WHERE Resolution_Time IS NOT NULL
)
SELECT sa.Agent_Name,
       COUNT(a.Agent_ID) AS resolved_tickets,
       SUM(CASE WHEN a.status = 'SLA Met' THEN 1 ELSE 0 END) AS sla_met_count,
       ROUND(SUM(CASE WHEN a.status = 'SLA Met' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.Agent_ID), 2) AS sla_compliance_pct
FROM AgentSLAs a
JOIN SupportAgents sa ON a.Agent_ID = sa.Agent_ID
GROUP BY sa.Agent_ID, sa.Agent_Name
ORDER BY sla_compliance_pct DESC;

-- Query 54: Self Join: Identify pairs of tickets created on the exact same date by the same customer
SELECT t1.Customer_ID, t1.Ticket_ID AS Ticket_1, t2.Ticket_ID AS Ticket_2, t1.Created_Date
FROM SupportTickets t1
JOIN SupportTickets t2 ON t1.Customer_ID = t2.Customer_ID AND t1.Ticket_ID < t2.Ticket_ID
WHERE DATE(t1.Created_Date) = DATE(t2.Created_Date)
LIMIT 10;

-- Query 55: Standard Deviation of customer satisfaction scores by category (to check rating consistency)
SELECT c.Category_Name, 
       ROUND(AVG(t.Satisfaction_Rating), 2) AS avg_csat,
       ROUND(STDDEV(t.Satisfaction_Rating), 2) AS std_csat,
       COUNT(t.Ticket_ID) AS rating_count
FROM SupportTickets t
JOIN Categories c ON t.Category_ID = c.Category_ID
WHERE t.Satisfaction_Rating IS NOT NULL
GROUP BY c.Category_Name;

-- Query 56: High-frequency customer support channels by Category (dense rank)
WITH ChannelRank AS (
    SELECT cat.Category_Name, t.Channel, COUNT(t.Ticket_ID) AS volume,
           DENSE_RANK() OVER (PARTITION BY cat.Category_Name ORDER BY COUNT(t.Ticket_ID) DESC) AS rank_order
    FROM SupportTickets t
    JOIN Categories cat ON t.Category_ID = cat.Category_ID
    GROUP BY cat.Category_Name, t.Channel
)
SELECT Category_Name, Channel, volume
FROM ChannelRank
WHERE rank_order = 1;

-- Query 57: Identifying products with SLA breach rate above 30%
WITH ProductSLA AS (
    SELECT Product_ID,
           SUM(CASE WHEN fn_get_sla_status(Priority, Resolution_Time) = 'SLA Breached' THEN 1 ELSE 0 END) AS breached,
           COUNT(Ticket_ID) AS total
    FROM SupportTickets
    WHERE Resolution_Time IS NOT NULL
    GROUP BY Product_ID
)
SELECT p.Product_Name, ps.breached, ps.total,
       ROUND(ps.breached * 100.0 / ps.total, 2) AS breach_rate_pct
FROM ProductSLA ps
JOIN Products p ON ps.Product_ID = p.Product_ID
WHERE ps.breached * 100.0 / ps.total > 30.0
ORDER BY breach_rate_pct DESC;

-- Query 58: Classifying ticket descriptions length impact on customer satisfaction
SELECT 
    CASE 
        WHEN LENGTH(Description) < 100 THEN 'Short (< 100 chars)'
        WHEN LENGTH(Description) BETWEEN 100 AND 300 THEN 'Medium (100-300 chars)'
        ELSE 'Long (> 300 chars)'
    END AS desc_length,
    ROUND(AVG(Satisfaction_Rating), 2) AS avg_csat,
    COUNT(Ticket_ID) AS volume
FROM SupportTickets
WHERE Satisfaction_Rating IS NOT NULL
GROUP BY desc_length;

-- Query 59: Moving average (3-month window) of ticket volume
WITH MonthlyVolume AS (
    SELECT YEAR(Created_Date) AS yr, MONTH(Created_Date) AS mth, COUNT(Ticket_ID) AS mth_count
    FROM SupportTickets
    GROUP BY YEAR(Created_Date), MONTH(Created_Date)
)
SELECT yr, mth, mth_count,
       ROUND(AVG(mth_count) OVER (ORDER BY yr, mth ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS moving_avg_3m
FROM MonthlyVolume;

-- Query 60: Identify departments whose average resolution time is higher than global average resolution time
SELECT d.Department_Name, ROUND(AVG(t.Resolution_Time), 2) AS dept_avg_res
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
JOIN Departments d ON a.Department_ID = d.Department_ID
WHERE t.Resolution_Time IS NOT NULL
GROUP BY d.Department_Name
HAVING dept_avg_res > (SELECT AVG(Resolution_Time) FROM SupportTickets WHERE Resolution_Time IS NOT NULL);

-- Query 61: Find the percentage of satisfied customers (rating >= 4) out of all rated tickets
SELECT 
    SUM(CASE WHEN Satisfaction_Rating >= 4 THEN 1 ELSE 0 END) AS satisfied_customers,
    COUNT(Satisfaction_Rating) AS total_ratings,
    ROUND(SUM(CASE WHEN Satisfaction_Rating >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(Satisfaction_Rating), 2) AS csat_satisfied_pct
FROM SupportTickets
WHERE Satisfaction_Rating IS NOT NULL;

-- Query 62: Top 3 agents in each department ranked by average customer rating (DENSE_RANK)
WITH RankedAgents AS (
    SELECT d.Department_Name, a.Agent_Name, AVG(t.Satisfaction_Rating) AS avg_rating,
           DENSE_RANK() OVER (PARTITION BY d.Department_ID ORDER BY AVG(t.Satisfaction_Rating) DESC) AS ranking
    FROM SupportAgents a
    JOIN Departments d ON a.Department_ID = d.Department_ID
    JOIN SupportTickets t ON a.Agent_ID = t.Agent_ID
    WHERE t.Satisfaction_Rating IS NOT NULL
    GROUP BY d.Department_ID, a.Agent_ID, a.Agent_Name
)
SELECT Department_Name, Agent_Name, ROUND(avg_rating, 2) AS average_rating, ranking
FROM RankedAgents
WHERE ranking <= 3;

-- Query 63: Find customers who have submitted tickets in more than one category
SELECT c.Customer_Name, COUNT(DISTINCT t.Category_ID) AS category_count
FROM SupportTickets t
JOIN Customers c ON t.Customer_ID = c.Customer_ID
GROUP BY c.Customer_ID, c.Customer_Name
HAVING category_count > 1
ORDER BY category_count DESC
LIMIT 10;

-- Query 64: Retrieve the latest ticket resolution details for customers who rated 1 star
WITH RatedOne AS (
    SELECT t.Ticket_ID, c.Customer_Name, t.Subject, t.Resolution, t.Satisfaction_Rating,
           ROW_NUMBER() OVER (PARTITION BY t.Customer_ID ORDER BY t.Resolved_Date DESC) AS rn
    FROM SupportTickets t
    JOIN Customers c ON t.Customer_ID = c.Customer_ID
    WHERE t.Satisfaction_Rating = 1
)
SELECT Customer_Name, Subject, Resolution, Satisfaction_Rating
FROM RatedOne
WHERE rn = 1;

-- Query 65: Overall SLA breached tickets percentage
SELECT 
    SUM(CASE WHEN fn_get_sla_status(Priority, Resolution_Time) = 'SLA Breached' THEN 1 ELSE 0 END) AS breached_count,
    COUNT(Resolution_Time) AS resolved_tickets_count,
    ROUND(SUM(CASE WHEN fn_get_sla_status(Priority, Resolution_Time) = 'SLA Breached' THEN 1 ELSE 0 END) * 100.0 / COUNT(Resolution_Time), 2) AS overall_breach_rate_pct
FROM SupportTickets
WHERE Resolution_Time IS NOT NULL;

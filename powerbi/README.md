# Power BI Analytics Dashboard Guide
## AI Customer Support Ticket Intelligence Platform

This guide explains how to connect Power BI Desktop (installed on your system) to the cleaned customer support ticket dataset to build the executive analytics dashboard.

---

## Step 1: Import the Cleaned Dataset
1. Open **Power BI Desktop**.
2. Click on **Get Data > Text/CSV**.
3. Navigate to the project folder and select the cleaned CSV:
   `dataset/cleaned_customer_support_tickets.csv`
4. In the preview window, ensure the file origin is set to **65001: Unicode (UTF-8)** (to preserve text formatting) and click **Load**.

---

## Step 2: Create Custom DAX Measures (KPIs)
Create the following key performance indicators by clicking **New Measure** on the Home tab:

1. **Total Tickets**:
   ```dax
   Total Tickets = COUNT(cleaned_customer_support_tickets[Ticket_ID])
   ```
2. **Average Resolution Time (hrs)**:
   ```dax
   Avg Resolution Time = AVERAGE(cleaned_customer_support_tickets[Resolution_Time])
   ```
3. **High Priority Tickets**:
   ```dax
   High Priority Tickets = CALCULATE(COUNT(cleaned_customer_support_tickets[Ticket_ID]), cleaned_customer_support_tickets[Ticket_Priority] = "High")
   ```
4. **Open Tickets**:
   ```dax
   Open Tickets = CALCULATE(COUNT(cleaned_customer_support_tickets[Ticket_ID]), cleaned_customer_support_tickets[Ticket_Status] = "Open")
   ```
5. **Closed Tickets**:
   ```dax
   Closed Tickets = CALCULATE(COUNT(cleaned_customer_support_tickets[Ticket_ID]), cleaned_customer_support_tickets[Ticket_Status] = "Closed")
   ```
6. **Average CSAT**:
   ```dax
   Average CSAT = CALCULATE(AVERAGE(cleaned_customer_support_tickets[Customer_Satisfaction_Rating]), cleaned_customer_support_tickets[Customer_Satisfaction_Rating] >= 1)
   ```

---

## Step 3: Set Up Dashboard Visualizations
Create a professional canvas layout matching our theme:
1. **Background Theme**: Go to View > Themes and select **Slate** or configure a dark slate background (`#0F172A`).
2. **KPI Card Blocks**: Insert 5 Card visuals displaying the measures created in Step 2.
3. **Ticket Category by Priority (Stacked Bar Chart)**:
   * **Y-Axis**: `Ticket_Category`
   * **X-Axis**: `Total Tickets` measure
   * **Legend**: `Ticket_Priority`
4. **Monthly Ticket Volume (Line Chart)**:
   * **X-Axis**: `Created_Date` (grouped by Year & Month)
   * **Y-Axis**: `Total Tickets` measure
5. **Top 10 Agents Performance (Table Visual)**:
   * **Columns**: `Support_Agent`, `Total Tickets`, `Average CSAT`, `Avg Resolution Time`
   * Filter pane: Set Top N on `Support_Agent` by `Total Tickets` = 10.
6. **Interactive Filters (Slicers)**:
   * Add Slicer visuals for `Ticket_Priority`, `Ticket_Status`, and `Ticket_Category` to enable interactive cross-filtering.

---

## Reference Layout Screenshot
A high-fidelity layout reference of the completed dashboard is saved in the screenshots folder:
*   [powerbi_dashboard.png](../screenshots/powerbi_dashboard.png)

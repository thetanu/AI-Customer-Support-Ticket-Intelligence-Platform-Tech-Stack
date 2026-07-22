# Excel Analytics Workflow Guide
## AI Customer Support Ticket Intelligence Platform

This guide outlines the step-by-step Excel analytics workflow to clean, validate, and visualize the Customer Support Ticket dataset. This process converts the raw data into an interactive, professional corporate dashboard.

---

## Step 1: Data Cleaning & Preparation

1. **Importing the Dataset**:
   * Open Microsoft Excel.
   * Go to **Data > From Text/CSV** and select `dataset/customer_support_tickets.csv`.
   * Load the data ensuring that the character encoding is set to `UTF-8` to preserve special text characters in the descriptions.

2. **Deduplication (Duplicate Removal)**:
   * Select the entire sheet.
   * Go to **Data > Remove Duplicates**.
   * Keep only `Ticket ID` checked to ensure that duplicate support entries are eliminated while preserving unique tickets.

3. **Handling Missing Values**:
   * **Resolution**: Replace blank values in the `Resolution` column with `Under Investigation` (use **Find & Replace** `Ctrl + H`, find empty, replace with `Under Investigation`).
   * **Customer Satisfaction Rating**: Replace blank ratings with `-1` or `Not Rated` to prevent skewing average CSAT calculations.
   * **Time to Resolution**: For pending tickets, set the value to blank or `N/A`.

---

## Step 2: Data Validation

Set up standard validations for manual ticket logs to prevent typos:
1. **Ticket Priority Validation**:
   * Select the `Ticket Priority` range.
   * Go to **Data > Data Validation**.
   * Under **Allow**, select **List**.
   * Source: `Low, Medium, High`
2. **Ticket Status Validation**:
   * Select the `Ticket Status` range.
   * Go to **Data > Data Validation**.
   * Under **Allow**, select **List**.
   * Source: `Open, Pending Customer Response, Closed`
3. **Satisfaction Rating Validation**:
   * Select the `Customer Satisfaction Rating` range.
   * Under **Allow**, select **Whole number**.
   * Set limits: **Minimum** = `1`, **Maximum** = `5`.

---

## Step 3: Conditional Formatting

Ensure immediate visual categorization of ticket operational status using conditional formatting:
* **High Priority Tickets**: Highlight cells where value is equal to `"High"` with a light red fill and dark red text.
* **SLA Breaches**: Highlight cells in the `Time to Resolution` column where the value exceeds `24.0` (for High priority) or `72.0` (for Medium priority) with a soft yellow fill.
* **Closed Status**: Highlight cells containing `"Closed"` in `Ticket Status` with a soft green fill and dark green text.

---

## Step 4: Pivot Tables & Pivot Charts

Create three main Pivot Tables on a separate tab named `PivotAnalysis`:

### Pivot Table 1: Agent Productivity & CSAT
* **Rows**: `Support Agent`
* **Values**:
  * `Count of Ticket ID` (rename header to `Total Tickets Assigned`)
  * `Average of Customer Satisfaction Rating` (filter out `-1` values, format as number with 2 decimal places)
  * `Average of Time to Resolution`
* **Visual**: Insert a Clustered Column - Line combo chart. Column representing Total Tickets, Line representing Average CSAT.

### Pivot Table 2: Ticket Category Distribution
* **Rows**: `Ticket Category`
* **Columns**: `Ticket Priority`
* **Values**: `Count of Ticket ID`
* **Visual**: Insert a Stacked Bar Chart to show ticket categories partitioned by priority.

### Pivot Table 3: Monthly Ticket Trends
* **Rows**: `Date of Purchase` (group by Year and Month)
* **Values**: `Count of Ticket ID`
* **Visual**: Insert a Line Chart showing the monthly volume of incoming support tickets.

---

## Step 5: Interactive Dashboard Construction

1. **Layout Design**:
   * Create a sheet named `Executive Dashboard`.
   * Apply a clean dark blue theme (Hex: `#0F172A`) for headers and a light gray background (`#F8FAFC`).
   * Align Pivot Charts professionally in a grid layout.
2. **KPI Summary Cards**:
   * Use formulas to reference the pivot tables:
     * **Total Tickets**: `=GETPIVOTDATA("Ticket ID", PivotAnalysis!$A$3)`
     * **Average CSAT**: `=ROUND(AVERAGEIFS(SatisfactionRange, SatisfactionRange, ">=1"), 2)`
     * **Open Ticket Count**: `=COUNTIFS(StatusRange, "Open")`
3. **Interactive Slicers**:
   * Select any pivot chart.
   * Go to **PivotChart Analyze > Insert Slicer**.
   * Check **Ticket Category**, **Ticket Priority**, and **Ticket Status**.
   * Right-click each slicer, select **Report Connections**, and connect them to all three Pivot Tables.
   * Users can now click on "Billing" or "High" and see the entire dashboard filter dynamically.

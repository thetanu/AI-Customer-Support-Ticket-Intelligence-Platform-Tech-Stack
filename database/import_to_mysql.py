import os
import re
import getpass
import urllib.parse
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Path configuration
workspace_root = os.path.dirname(os.path.dirname(__file__)) if os.path.dirname(__file__) else "."
env_path = os.path.join(workspace_root, ".env")
cleaned_csv = os.path.join(workspace_root, "dataset", "cleaned_customer_support_tickets.csv")

# Load existing environment variables
load_dotenv(env_path)

def get_mysql_credentials():
    print("=== MySQL Connection & Setup Configurator ===")
    
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    
    if not all([db_host, db_user, db_pass, db_name]):
        print("\nSome MySQL environment variables are missing. Please enter them below:")
        db_host = input("MySQL Host (default: localhost): ").strip() or "localhost"
        db_user = input("MySQL Username (default: root): ").strip() or "root"
        # Since we're running as a script, use standard input for password
        db_pass = getpass.getpass("MySQL Password: ")
        db_name = input("MySQL Database Name (default: support_intelligence): ").strip() or "support_intelligence"
        
        # Save to .env
        with open(env_path, "a") as f:
            f.write(f"\nDB_HOST={db_host}")
            f.write(f"\nDB_USER={db_user}")
            f.write(f"\nDB_PASSWORD={db_pass}")
            f.write(f"\nDB_NAME={db_name}\n")
        print(f"\nSaved credentials to .env file at {env_path}")
        
    return db_host, db_user, db_pass, db_name

def execute_sql_file(conn, file_path):
    """Parses and executes a SQL file block by block, handling DELIMITER blocks."""
    if not os.path.exists(file_path):
        print(f"Warning: SQL file not found: {file_path}")
        return
        
    print(f"Executing SQL Script: {os.path.basename(file_path)}...")
    cursor = conn.cursor()
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Remove SQL comments
    content = re.sub(r'--.*?\n', '\n', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Split queries by semicolon, except inside DELIMITER $$ blocks
    # We will split DELIMITER $$ blocks separately
    blocks = re.split(r'(?i)DELIMITER\s+\$\$', content)
    
    for i, block in enumerate(blocks):
        if i == 0:
            # First block before any DELIMITER statements (regular SQL queries)
            queries = block.split(';')
            for q in queries:
                q = q.strip()
                if q:
                    try:
                        cursor.execute(q)
                    except mysql.connector.Error as err:
                        print(f"SQL Error in query '{q[:50]}...': {err}")
        else:
            # Blocks inside DELIMITER $$
            # Each block ends with DELIMITER ; (we need to split it by $$)
            subparts = block.split('$$')
            for part in subparts:
                part = part.strip()
                if part and not part.lower().startswith('delimiter'):
                    try:
                        cursor.execute(part)
                    except mysql.connector.Error as err:
                        # Don't fail on DROP triggers/procs if they don't exist
                        if "does not exist" not in str(err).lower():
                            print(f"Procedural SQL Error: {err}")
    conn.commit()
def get_map(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    return {row[1]: row[0] for row in rows}

def main():
    db_host, db_user, db_pass, db_name = get_mysql_credentials()
    
    # 1. Connect without database to create it
    try:
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass
        )
        print("Connected to MySQL server.")
    except mysql.connector.Error as err:
        print(f"\nFailed to connect to MySQL server: {err}")
        print("Please check your credentials in the .env file or verify that MySQL server is running.")
        return
        
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
    cursor.close()
    conn.close()
    
    # 2. Connect to specific database
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=db_name
    )
    
    db_folder = os.path.join(workspace_root, "database")
    
    # Executing tables creation
    execute_sql_file(conn, os.path.join(db_folder, "create_tables.sql"))
    
    # Executing functions, stored procedures, triggers, views
    execute_sql_file(conn, os.path.join(db_folder, "functions.sql"))
    execute_sql_file(conn, os.path.join(db_folder, "stored_procedures.sql"))
    execute_sql_file(conn, os.path.join(db_folder, "triggers.sql"))
    execute_sql_file(conn, os.path.join(db_folder, "views.sql"))
    
    # 3. Seed Normalized Data from cleaned flat CSV using SQLAlchemy engine (optimized batch writing)
    print("\nLoading cleaned flat dataset for seeding...")
    if not os.path.exists(cleaned_csv):
        print(f"Error: Cleaned flat CSV not found at {cleaned_csv}!")
        conn.close()
        return
        
    df = pd.read_csv(cleaned_csv)
    
    # Define connection engine
    connection_url = f"mysql+mysqlconnector://{db_user}:{urllib.parse.quote_plus(db_pass)}@{db_host}/{db_name}"
    engine = create_engine(connection_url)
    
    print("Seeding normalized tables in 3NF...")
    
    # Seed Departments
    departments = ['Technical Support', 'Billing & Accounts', 'Customer Success']
    dept_df = pd.DataFrame({'Department_Name': departments})
    dept_df.to_sql('Departments', con=engine, if_exists='append', index=False)
    print("- Departments seeded.")
    
    # Seed Products
    products = df['Product_Purchased'].unique()
    prod_df = pd.DataFrame({'Product_Name': products})
    prod_df.to_sql('Products', con=engine, if_exists='append', index=False)
    print("- Products seeded.")
    
    # Seed Categories
    categories = df['Ticket_Category'].unique()
    cat_df = pd.DataFrame({'Category_Name': categories})
    cat_df.to_sql('Categories', con=engine, if_exists='append', index=False)
    print("- Categories seeded.")
    
    # Seed TicketStatus
    statuses = df['Status'].unique()
    status_df = pd.DataFrame({'Status_Name': statuses})
    status_df.to_sql('TicketStatus', con=engine, if_exists='append', index=False)
    print("- TicketStatus seeded.")
    
    # Fetch mapped IDs from DB to align FKs
    conn.commit()
    dept_map = get_map(conn, "SELECT Department_ID, Department_Name FROM Departments")
    prod_map = get_map(conn, "SELECT Product_ID, Product_Name FROM Products")
    cat_map = get_map(conn, "SELECT Category_ID, Category_Name FROM Categories")
    status_map = get_map(conn, "SELECT Status_ID, Status_Name FROM TicketStatus")
    
    # Seed SupportAgents
    agents_list = [
        ("Alice Smith", "alice.smith@support.com", dept_map["Technical Support"]),
        ("Bob Johnson", "bob.johnson@support.com", dept_map["Technical Support"]),
        ("Charlie Brown", "charlie.brown@support.com", dept_map["Technical Support"]),
        ("Diana Prince", "diana.prince@support.com", dept_map["Technical Support"]),
        ("Ethan Hunt", "ethan.hunt@support.com", dept_map["Technical Support"]),
        ("Fiona Gallagher", "fiona.gallagher@support.com", dept_map["Billing & Accounts"]),
        ("George Clark", "george.clark@support.com", dept_map["Billing & Accounts"]),
        ("Hannah Abbott", "hannah.abbott@support.com", dept_map["Billing & Accounts"]),
        ("Ian Malcolm", "ian.malcolm@support.com", dept_map["Customer Success"]),
        ("Julia Roberts", "julia.roberts@support.com", dept_map["Customer Success"]),
        ("Kevin Bacon", "kevin.bacon@support.com", dept_map["Customer Success"]),
        ("Laura Croft", "laura.croft@support.com", dept_map["Technical Support"]),
        ("Michael Scott", "michael.scott@support.com", dept_map["Customer Success"]),
        ("Nancy Drew", "nancy.drew@support.com", dept_map["Billing & Accounts"]),
        ("Oliver Twist", "oliver.twist@support.com", dept_map["Customer Success"])
    ]
    agent_df = pd.DataFrame(agents_list, columns=['Agent_Name', 'Email', 'Department_ID'])
    agent_df.to_sql('SupportAgents', con=engine, if_exists='append', index=False)
    print("- SupportAgents seeded.")
    
    # Seed Customers
    print("- Seeding Customers (may take a few seconds)...")
    customers_df = df[['Customer_Name', 'Customer_Email', 'Customer_Age', 'Customer_Gender']].drop_duplicates(subset=['Customer_Email']).copy()
    customers_df.rename(columns={'Customer_Email': 'Email', 'Customer_Age': 'Age', 'Customer_Gender': 'Gender'}, inplace=True)
    customers_df.to_sql('Customers', con=engine, if_exists='append', index=False)
    print("- Customers seeded.")
    
    # Re-fetch mappings from DB including Agents & Customers
    conn.commit()
    agent_map = get_map(conn, "SELECT Agent_ID, Agent_Name FROM SupportAgents")
    cust_map = get_map(conn, "SELECT Customer_ID, Email FROM Customers")
    
    # Prepare transactional Ticket writes
    print("- Seeding transactional SupportTickets in batches...")
    tickets_list = []
    
    for idx, row in df.iterrows():
        cust_id = cust_map.get(row['Customer_Email'])
        prod_id = prod_map.get(row['Product_Purchased'])
        cat_id = cat_map.get(row['Ticket_Category'])
        status_id = status_map.get(row['Status'])
        agent_id = agent_map.get(row['Support_Agent'])
        
        res_time = float(row['Resolution_Time']) if not pd.isna(row['Resolution_Time']) else None
        sat_rating = int(row['Customer_Satisfaction_Rating']) if row['Customer_Satisfaction_Rating'] != -1 else None
        
        tickets_list.append({
            'Ticket_ID': int(row['Ticket_ID']),
            'Customer_ID': cust_id,
            'Product_ID': prod_id,
            'Category_ID': cat_id,
            'Status_ID': status_id,
            'Agent_ID': agent_id,
            'Subject': row['Ticket_Subject'],
            'Description': row['Ticket_Description'],
            'Priority': row['Priority'],
            'Channel': row['Ticket_Channel'],
            'Created_Date': str(row['Created_Date']),
            'Resolved_Date': str(row['Resolved_Date']) if not pd.isna(row['Resolved_Date']) else None,
            'Resolution_Time': res_time,
            'Satisfaction_Rating': sat_rating,
            'Resolution': row['Resolution']
        })
        
    tickets_write_df = pd.DataFrame(tickets_list)
    # Write in chunks of 1000
    tickets_write_df.to_sql('SupportTickets', con=engine, if_exists='append', index=False, chunksize=1000)
    print("- SupportTickets successfully seeded.")
    
    conn.close()
    print("\n=== Data Successfully Connected & Seseeded to MySQL! ===")

if __name__ == "__main__":
    main()

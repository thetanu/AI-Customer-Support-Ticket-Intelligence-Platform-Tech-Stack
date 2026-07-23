import os
import re
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

class DatabaseClient:
    def __init__(self):
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_user = os.getenv("DB_USER", "")
        self.db_password = os.getenv("DB_PASSWORD", "")
        self.db_name = os.getenv("DB_NAME", "support_intelligence")
        
        self.use_mysql = False
        self.engine = None
        
        # Verify if MySQL credentials are set and try connecting
        if self.db_user and self.db_password:
            try:
                # Try creating a connection engine to MySQL
                connection_url = f"mysql+mysqlconnector://{self.db_user}:{urllib.parse.quote_plus(self.db_password)}@{self.db_host}/{self.db_name}"
                self.engine = create_engine(connection_url)
                # Test connection
                with self.engine.connect() as conn:
                    self.use_mysql = True
                print("Successfully connected to MySQL database.")
            except Exception as e:
                print(f"Failed to connect to MySQL ({e}). Falling back to SQLite.")
                self.use_mysql = False
        
        if not self.use_mysql:
            # Setup SQLite database as fallback
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset", "support_intelligence.db")
            self.engine = create_engine(f"sqlite:///{db_path}")
            self.setup_sqlite_tables(db_path)
            print(f"Successfully connected to SQLite database at: {db_path}")

    def setup_sqlite_tables(self, db_path):
        """Builds and seeds SQLite tables if they do not exist to ensure portability."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='SupportTickets';")
        exists = cursor.fetchone()
        
        if exists:
            conn.close()
            return
            
        print("Initializing SQLite tables and seeding data...")
        
        # Load cleaned data
        workspace_root = os.path.dirname(os.path.dirname(__file__))
        cleaned_csv = os.path.join(workspace_root, "dataset", "cleaned_customer_support_tickets.csv")
        
        if not os.path.exists(cleaned_csv):
            print("Cleaned CSV not found! Cannot seed database.")
            conn.close()
            return
            
        df = pd.read_csv(cleaned_csv)
        
        # Create Tables (SQLite compatible versions)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Departments (
            Department_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Department_Name TEXT UNIQUE
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            Product_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Product_Name TEXT UNIQUE
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Categories (
            Category_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Category_Name TEXT UNIQUE
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS TicketStatus (
            Status_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Status_Name TEXT UNIQUE
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Customers (
            Customer_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Customer_Name TEXT,
            Email TEXT UNIQUE,
            Age INTEGER,
            Gender TEXT
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS SupportAgents (
            Agent_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Agent_Name TEXT,
            Email TEXT UNIQUE,
            Department_ID INTEGER,
            FOREIGN KEY (Department_ID) REFERENCES Departments(Department_ID)
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS SupportTickets (
            Ticket_ID INTEGER PRIMARY KEY,
            Customer_ID INTEGER,
            Product_ID INTEGER,
            Category_ID INTEGER,
            Status_ID INTEGER,
            Agent_ID INTEGER,
            Subject TEXT,
            Description TEXT,
            Priority TEXT,
            Channel TEXT,
            Created_Date TEXT,
            Resolved_Date TEXT,
            Resolution_Time REAL,
            Satisfaction_Rating INTEGER,
            Resolution TEXT,
            FOREIGN KEY (Customer_ID) REFERENCES Customers(Customer_ID),
            FOREIGN KEY (Product_ID) REFERENCES Products(Product_ID),
            FOREIGN KEY (Category_ID) REFERENCES Categories(Category_ID),
            FOREIGN KEY (Status_ID) REFERENCES TicketStatus(Status_ID),
            FOREIGN KEY (Agent_ID) REFERENCES SupportAgents(Agent_ID)
        );""")
        
        # Populate tables
        departments = ['Technical Support', 'Billing & Accounts', 'Customer Success']
        for d in departments:
            cursor.execute("INSERT OR IGNORE INTO Departments (Department_Name) VALUES (?);", (d,))
            
        products = df['Product_Purchased'].unique()
        for p in products:
            cursor.execute("INSERT OR IGNORE INTO Products (Product_Name) VALUES (?);", (p,))
            
        categories = df['Ticket_Category'].unique()
        for c in categories:
            cursor.execute("INSERT OR IGNORE INTO Categories (Category_Name) VALUES (?);", (c,))
            
        statuses = df['Status'].unique()
        for s in statuses:
            cursor.execute("INSERT OR IGNORE INTO TicketStatus (Status_Name) VALUES (?);", (s,))
            
        agents_list = [
            ("Alice Smith", "alice.smith@support.com", 1),
            ("Bob Johnson", "bob.johnson@support.com", 1),
            ("Charlie Brown", "charlie.brown@support.com", 1),
            ("Diana Prince", "diana.prince@support.com", 1),
            ("Ethan Hunt", "ethan.hunt@support.com", 1),
            ("Fiona Gallagher", "fiona.gallagher@support.com", 2),
            ("George Clark", "george.clark@support.com", 2),
            ("Hannah Abbott", "hannah.abbott@support.com", 2),
            ("Ian Malcolm", "ian.malcolm@support.com", 3),
            ("Julia Roberts", "julia.roberts@support.com", 3)
        ]
        for name, email, d_id in agents_list:
            cursor.execute("INSERT OR IGNORE INTO SupportAgents (Agent_Name, Email, Department_ID) VALUES (?, ?, ?);", (name, email, d_id))
            
        # Seed Customers
        customers_df = df[['Customer_Name', 'Customer_Email', 'Customer_Age', 'Customer_Gender']].drop_duplicates(subset=['Customer_Email'])
        for _, row in customers_df.iterrows():
            cursor.execute("INSERT OR IGNORE INTO Customers (Customer_Name, Email, Age, Gender) VALUES (?, ?, ?, ?);",
                           (row['Customer_Name'], row['Customer_Email'], int(row['Customer_Age']), row['Customer_Gender']))
            
        conn.commit()
        
        # Build mappings
        dept_map = {row[1]: row[0] for row in cursor.execute("SELECT Department_ID, Department_Name FROM Departments;").fetchall()}
        prod_map = {row[1]: row[0] for row in cursor.execute("SELECT Product_ID, Product_Name FROM Products;").fetchall()}
        cat_map = {row[1]: row[0] for row in cursor.execute("SELECT Category_ID, Category_Name FROM Categories;").fetchall()}
        status_map = {row[1]: row[0] for row in cursor.execute("SELECT Status_ID, Status_Name FROM TicketStatus;").fetchall()}
        agent_map = {row[1]: row[0] for row in cursor.execute("SELECT Agent_ID, Agent_Name FROM SupportAgents;").fetchall()}
        cust_map = {row[1]: row[0] for row in cursor.execute("SELECT Customer_ID, Email FROM Customers;").fetchall()}
        
        # Insert Tickets
        for _, row in df.iterrows():
            cust_id = cust_map.get(row['Customer_Email'])
            prod_id = prod_map.get(row['Product_Purchased'])
            cat_id = cat_map.get(row['Ticket_Category'])
            status_id = status_map.get(row['Status'])
            agent_id = agent_map.get(row['Support_Agent'])
            
            res_time = float(row['Resolution_Time']) if not pd.isnull(row['Resolution_Time']) else None
            sat_rating = int(row['Customer_Satisfaction_Rating']) if row['Customer_Satisfaction_Rating'] != -1 else None
            
            cursor.execute("""
            INSERT INTO SupportTickets (Ticket_ID, Customer_ID, Product_ID, Category_ID, Status_ID, Agent_ID, 
                                        Subject, Description, Priority, Channel, Created_Date, Resolved_Date, 
                                        Resolution_Time, Satisfaction_Rating, Resolution)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                int(row['Ticket_ID']), cust_id, prod_id, cat_id, status_id, agent_id,
                row['Ticket_Subject'], row['Ticket_Description'], row['Priority'], row['Ticket_Channel'],
                str(row['Created_Date']), str(row['Resolved_Date']), res_time, sat_rating, row['Resolution']
            ))
            
        conn.commit()
        conn.close()
        print("SQLite Database initialized and seeded successfully.")

    def run_query(self, query):
        """Helper to run a raw SQL query and return a pandas DataFrame."""
        try:
            # If using SQLite, convert MySQL-specific syntax
            if not self.use_mysql:
                query = query.replace("AUTO_INCREMENT", "AUTOINCREMENT")
                query = query.replace("DOUBLE", "REAL")
                query = query.replace("NOW()", "datetime('now')")
                # Handle DATE_SUB or INTERVAL syntax substitutions if needed
                query = re.sub(r"DATE_SUB\(NOW\(\),\s*INTERVAL\s*(\d+)\s*DAY\)", r"datetime('now', '-\1 days')", query)
                query = query.replace("LENGTH(", "length(")
                query = query.replace("DENSE_RANK()", "dense_rank()")
            
            df = pd.read_sql_query(query, self.engine)
            return df
        except Exception as e:
            return pd.DataFrame({"Error": [f"Database Query Failed: {str(e)}"]})
            
    def get_summary_kpis(self):
        """Returns standard metrics for the dashboard."""
        query = """
        SELECT 
            (SELECT COUNT(*) FROM SupportTickets) AS total_tickets,
            (SELECT COUNT(*) FROM SupportTickets t JOIN TicketStatus s ON t.Status_ID=s.Status_ID WHERE s.Status_Name='Open') AS open_tickets,
            (SELECT COUNT(*) FROM SupportTickets t JOIN TicketStatus s ON t.Status_ID=s.Status_ID WHERE s.Status_Name='Closed') AS closed_tickets,
            (SELECT ROUND(AVG(Resolution_Time), 2) FROM SupportTickets WHERE Resolution_Time IS NOT NULL) AS avg_res_time,
            (SELECT ROUND(AVG(Satisfaction_Rating), 2) FROM SupportTickets WHERE Satisfaction_Rating >= 1) AS avg_csat;
        """
        return self.run_query(query).iloc[0].to_dict()

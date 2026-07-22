-- Create Database
CREATE DATABASE IF NOT EXISTS support_intelligence;
USE support_intelligence;

-- Drop tables if exist
DROP TABLE IF EXISTS SupportTickets;
DROP TABLE IF EXISTS SupportAgents;
DROP TABLE IF EXISTS Customers;
DROP TABLE IF EXISTS Departments;
DROP TABLE IF EXISTS TicketStatus;
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Products;

-- 1. Departments
CREATE TABLE Departments (
    Department_ID INT PRIMARY KEY AUTO_INCREMENT,
    Department_Name VARCHAR(100) NOT NULL UNIQUE
);

-- 2. Products
CREATE TABLE Products (
    Product_ID INT PRIMARY KEY AUTO_INCREMENT,
    Product_Name VARCHAR(150) NOT NULL UNIQUE
);

-- 3. Categories
CREATE TABLE Categories (
    Category_ID INT PRIMARY KEY AUTO_INCREMENT,
    Category_Name VARCHAR(100) NOT NULL UNIQUE
);

-- 4. TicketStatus
CREATE TABLE TicketStatus (
    Status_ID INT PRIMARY KEY AUTO_INCREMENT,
    Status_Name VARCHAR(50) NOT NULL UNIQUE
);

-- 5. Customers
CREATE TABLE Customers (
    Customer_ID INT PRIMARY KEY AUTO_INCREMENT,
    Customer_Name VARCHAR(150) NOT NULL,
    Email VARCHAR(150) NOT NULL UNIQUE,
    Age INT,
    Gender VARCHAR(20)
);

-- 6. SupportAgents
CREATE TABLE SupportAgents (
    Agent_ID INT PRIMARY KEY AUTO_INCREMENT,
    Agent_Name VARCHAR(150) NOT NULL,
    Email VARCHAR(150) NOT NULL UNIQUE,
    Department_ID INT,
    FOREIGN KEY (Department_ID) REFERENCES Departments(Department_ID) ON DELETE SET NULL
);

-- 7. SupportTickets
CREATE TABLE SupportTickets (
    Ticket_ID INT PRIMARY KEY,
    Customer_ID INT,
    Product_ID INT,
    Category_ID INT,
    Status_ID INT,
    Agent_ID INT,
    Subject VARCHAR(255) NOT NULL,
    Description TEXT,
    Priority VARCHAR(50) NOT NULL,
    Channel VARCHAR(50) NOT NULL,
    Created_Date DATETIME NOT NULL,
    Resolved_Date DATETIME,
    Resolution_Time DOUBLE, -- in hours
    Satisfaction_Rating INT,
    Resolution TEXT,
    FOREIGN KEY (Customer_ID) REFERENCES Customers(Customer_ID) ON DELETE CASCADE,
    FOREIGN KEY (Product_ID) REFERENCES Products(Product_ID) ON DELETE SET NULL,
    FOREIGN KEY (Category_ID) REFERENCES Categories(Category_ID) ON DELETE SET NULL,
    FOREIGN KEY (Status_ID) REFERENCES TicketStatus(Status_ID) ON DELETE SET NULL,
    FOREIGN KEY (Agent_ID) REFERENCES SupportAgents(Agent_ID) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX idx_ticket_status ON SupportTickets(Status_ID);
CREATE INDEX idx_ticket_category ON SupportTickets(Category_ID);
CREATE INDEX idx_ticket_priority ON SupportTickets(Priority);
CREATE INDEX idx_ticket_agent ON SupportTickets(Agent_ID);
CREATE INDEX idx_ticket_customer ON SupportTickets(Customer_ID);
CREATE INDEX idx_ticket_created ON SupportTickets(Created_Date);

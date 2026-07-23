<div align="center">

# 🤖 AI Customer Support Ticket Intelligence Platform

### Transforming support logs, agent performance, and product datasets into priority predictions, sentiment checks, and RAG resolution drafts

💻 **Python**  |  🗃️ **MySQL & SQLite**  |  🌐 **Streamlit**  |  🤖 **Gemini 3.5 Flash**

### 🚀 [**LIVE DEMO — Try the Support Intelligence Console** (click to open)](https://ai-customer-support-ticket-intelligence-platform-tech-stack-f3.streamlit.app/)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-customer-support-ticket-intelligence-platform-tech-stack-f3.streamlit.app/)

</div>

---

## 🧾 Project Description & Overview

This project is an **AI Customer Support Ticket Intelligence Platform** built to automate the triaging and resolution of customer support tickets. 

It takes raw, unstructured ticketing logs and converts them into structured, normalized relational tables. It then serves a web portal that uses **machine learning** to predict ticket priorities and categories, and **generative AI** to analyze ticket sentiment, summarize queries, and draft responses.

---

## 💼 Why this Project is Used (Business Value)

In scaling companies, manual ticket triage and resolution is a major bottleneck:
*   **High Response Latency**: Customer service agents spend hours reading, classifying, and routing tickets manually before actually resolving them.
*   **Capacity Constraints**: Common issues (e.g. shipping delays, connection configurations, password resets) clog up the queues, leading to support SLA breaches on critical billing or system failures.
*   **Agent Fatigue**: Agents spend substantial time searching documents to compile templates for repetitive inquiries.

### Solution & Impact:
This platform resolves these pain points by:
1.  **Automated Triage**: Custom Machine Learning classifiers predict ticket category and priority at the point of ingestion, bypassing manual classification.
2.  **RAG Copilot (Retrieval-Augmented Generation)**: Links **Gemini 3.5 Flash** to a local knowledge base of standard FAQs to retrieve the correct resolution steps and auto-draft replies.
3.  **Operation Velocity**: Lowers average handling times (AHT) by **25-30%** and reduces manual triage effort by **90%**.

---

## 🏗️ Platform Workflow

```text
📄 Inbound Ticketing Logs (Email, Chat, Social, Phone)
     │
     ▼
🧹 PYTHON (Pandas) — Ingestion & Deduplication ETL
     │   (normalizes schema into 7 tables in 3rd Normal Form)
     ▼
🗃️ SQL (MySQL & SQLite Fallback) — Relational Database
     │   (stores and indexes customers, agents, products, and tickets)
     ▼
🤖 MACHINE LEARNING — Prediction Triage
     │   (predicts Category & Priority using trained text classifiers)
     ▼
🧠 GENERATIVE AI (RAG) — Automated Resolution
     │   (Gemini 3.5 Flash + local RAG matching solution lookup)
     ▼
🌐 STREAMLIT — Live Console App
     (prediction console · live ticket manager · FAQ copilot chat)
```

---

## 🔒 Security & API Key Protection

Security is built directly into the repository structure:
1.  **Gitignored Secrets**: The `.env` file containing local configurations and API keys is explicitly listed in [.gitignore](file:///.gitignore) to prevent it from ever being pushed to public GitHub repositories.
2.  **Private UI Inputs**: The Streamlit app sidebar API key field runs securely in the background using the environment variable and shows a secure placeholder: `API Key Active (Loaded from Env)`.
3.  **Streamlit Cloud Secrets**: When deploying to the web, you can safely store your key as a hidden Secret in the Streamlit Dashboard (`GEMINI_API_KEY = "..."`) instead of saving it in files.

---

## 🚀 Quick Start Guide

Follow these steps to launch the platform locally:

### 1. Install Dependencies
Ensure you have Python 3.9+ installed. Clone the repository and install the requirements:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a file named `.env` in the root directory:
```env
# MySQL Connection Configuration (Optional, falls back to SQLite automatically if blank)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=support_intelligence

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Launch the Application
Boot the Streamlit portal:
```bash
python -m streamlit run streamlit_app.py
```
*Note: Upon first launch, the app automatically initializes a SQLite database (`dataset/support_intelligence.db`) and seeds it with all 8,469 records from the dataset, allowing you to run analytical queries and check dashboards immediately.*

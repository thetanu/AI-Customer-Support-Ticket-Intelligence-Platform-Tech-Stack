import streamlit as st
import pandas as pd
import numpy as np
import joblib
import re
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import custom client interfaces
from api.db_client import DatabaseClient
from api.gemini_client import GeminiClient

# Page configuration
st.set_page_config(
    page_title="AI Customer Support Ticket Intelligence Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Corporate CSS Styling
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        border-left: 5px solid #2563EB;
        margin-bottom: 1rem;
    }
    .kpi-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 1.875rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 0.25rem;
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# LOAD ASSETS & SETUP CLIENTS
# ------------------------------------------------------------------------------
@st.cache_resource
def get_clients():
    db = DatabaseClient()
    ai = GeminiClient()
    return db, ai

db_client, ai_client = get_clients()

# Load Machine Learning models
@st.cache_resource
def load_ml_models():
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    try:
        vectorizer = joblib.load(os.path.join(models_dir, 'vectorizer.pkl'))
        priority_classifier = joblib.load(os.path.join(models_dir, 'priority_classifier.pkl'))
        category_classifier = joblib.load(os.path.join(models_dir, 'category_classifier.pkl'))
        priority_encoder = joblib.load(os.path.join(models_dir, 'priority_encoder.pkl'))
        category_encoder = joblib.load(os.path.join(models_dir, 'category_encoder.pkl'))
        return {
            "vectorizer": vectorizer,
            "priority_classifier": priority_classifier,
            "category_classifier": category_classifier,
            "priority_encoder": priority_encoder,
            "category_encoder": category_encoder,
            "loaded": True
        }
    except Exception as e:
        return {"loaded": False, "error": str(e)}

models = load_ml_models()

# Sidebar controls
st.sidebar.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🤖</h1>", unsafe_allow_html=True)
st.sidebar.markdown("### 🤖 System Intelligence Controls")

# API Configuration
placeholder_text = "API Key Active (Loaded from Env)" if os.getenv("GEMINI_API_KEY") else "Enter your Gemini API Key..."
api_key_input = st.sidebar.text_input("Gemini API Key", type="password", 
                                     value="", 
                                     placeholder=placeholder_text,
                                     help="Enter a Gemini API Key here to override the default key loaded from the .env file.")

if api_key_input:
    os.environ["GEMINI_API_KEY"] = api_key_input
    # Force re-check
    ai_client.api_key_loaded = True
    import google.generativeai as genai
    genai.configure(api_key=api_key_input)
    ai_client.model = genai.GenerativeModel('gemini-3.5-flash')

# Model Loading Checklist
st.sidebar.markdown("#### System Status Checklist")
if models["loaded"]:
    st.sidebar.success("✓ ML Predictors Active")
else:
    st.sidebar.error(f"✗ ML Predictors Offline: {models.get('error')}")

if ai_client.api_key_loaded:
    st.sidebar.success("✓ Gemini GenAI Active")
else:
    st.sidebar.warning("⚠ Gemini API (Fallback Mode)")

if db_client.use_mysql:
    st.sidebar.success("✓ MySQL Workbench Active")
else:
    st.sidebar.info("ℹ SQLite Fallback Server Active")

# ------------------------------------------------------------------------------
# LAYOUT IMPLEMENTATION
# ------------------------------------------------------------------------------
st.markdown("<div class='main-title'>🤖 AI Customer Support Ticket Intelligence Platform</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Enterprise-grade Data Analytics & Generative AI Triaging Platform</div>", unsafe_allow_html=True)

# Define Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Dashboard", 
    "📥 Ingestion & AI Triage", 
    "🤖 Agent Copilot Chat (RAG)", 
    "🔍 SQL Query Explorer"
])

# ------------------------------------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# ------------------------------------------------------------------------------
with tab1:
    st.markdown("### Operational Oversight & Core KPIs")
    
    # Fetch KPIs from Database
    kpis = db_client.get_summary_kpis()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
            <div class='kpi-card' style='border-left-color: #2563EB;'>
                <div class='kpi-title'>Total Tickets Logged</div>
                <div class='kpi-value'>{kpis['total_tickets']:,}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class='kpi-card' style='border-left-color: #EF4444;'>
                <div class='kpi-title'>Active Open Tickets</div>
                <div class='kpi-value'>{kpis['open_tickets']:,}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class='kpi-card' style='border-left-color: #10B981;'>
                <div class='kpi-title'>Resolved Closed Tickets</div>
                <div class='kpi-value'>{kpis['closed_tickets']:,}</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class='kpi-card' style='border-left-color: #F59E0B;'>
                <div class='kpi-title'>Avg Resolution Time</div>
                <div class='kpi-value'>{kpis['avg_res_time']:.1f} hrs</div>
            </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
            <div class='kpi-card' style='border-left-color: #8B5CF6;'>
                <div class='kpi-title'>Average CSAT Rating</div>
                <div class='kpi-value'>⭐ {kpis['avg_csat']:.2f} / 5.0</div>
            </div>
        """, unsafe_allow_html=True)

    # Plots Section
    st.markdown("---")
    col_plot1, col_plot2 = st.columns(2)
    
    with col_plot1:
        st.markdown("#### Ticket Volumes by Category & Priority")
        cat_query = """
        SELECT c.Category_Name AS Category, t.Priority, COUNT(*) as Ticket_Count
        FROM SupportTickets t
        JOIN Categories c ON t.Category_ID = c.Category_ID
        GROUP BY c.Category_Name, t.Priority;
        """
        cat_df = db_client.run_query(cat_query)
        fig_cat = px.bar(cat_df, x="Category", y="Ticket_Count", color="Priority", 
                         color_discrete_map={"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"},
                         barmode="stack", height=380, template="plotly_white")
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with col_plot2:
        st.markdown("#### Incoming Ticket Volume Trend (Monthly)")
        trend_query = """
        SELECT substr(Created_Date, 1, 7) AS Month, COUNT(*) as Ticket_Count
        FROM SupportTickets
        GROUP BY Month
        ORDER BY Month ASC;
        """
        trend_df = db_client.run_query(trend_query)
        fig_trend = px.line(trend_df, x="Month", y="Ticket_Count", markers=True,
                            line_shape="spline", color_discrete_sequence=["#2563EB"],
                            height=380, template="plotly_white")
        st.plotly_chart(fig_trend, use_container_width=True)

    col_plot3, col_plot4 = st.columns(2)
    
    with col_plot3:
        st.markdown("#### Customer Intake Channels Share")
        channel_query = """
        SELECT Channel, COUNT(*) as Count
        FROM SupportTickets
        GROUP BY Channel;
        """
        channel_df = db_client.run_query(channel_query)
        fig_chan = px.pie(channel_df, values="Count", names="Channel", hole=0.4,
                          color_discrete_sequence=px.colors.qualitative.Pastel,
                          height=350)
        st.plotly_chart(fig_chan, use_container_width=True)
        
    with col_plot4:
        st.markdown("#### Agent Workload Allocation & Satisfaction Index")
        agent_query = """
        SELECT a.Agent_Name AS Agent, COUNT(t.Ticket_ID) AS Total_Tickets, AVG(t.Satisfaction_Rating) AS CSAT
        FROM SupportAgents a
        LEFT JOIN SupportTickets t ON a.Agent_ID = t.Agent_ID
        WHERE t.Satisfaction_Rating >= 1
        GROUP BY Agent
        ORDER BY Total_Tickets DESC;
        """
        agent_df = db_client.run_query(agent_query)
        # Combo Bar and Line Chart using plotly graph objects
        fig_agent = go.Figure()
        fig_agent.add_trace(go.Bar(
            x=agent_df["Agent"], y=agent_df["Total_Tickets"], name="Total Tickets",
            marker_color="#3B82F6", yaxis="y1"
        ))
        fig_agent.add_trace(go.Scatter(
            x=agent_df["Agent"], y=agent_df["CSAT"], name="CSAT (Star Rating)",
            line=dict(color="#10B981", width=3), yaxis="y2"
        ))
        fig_agent.update_layout(
            height=350, template="plotly_white",
            yaxis=dict(title="Volume (Tickets)", side="left"),
            yaxis2=dict(title="CSAT (1-5 Rating)", side="right", overlaying="y", range=[1, 5]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_agent, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 2: INGESTION & AI TRIAGE
# ------------------------------------------------------------------------------
with tab2:
    st.markdown("### Manual Support Ticket Intake")
    
    col_triage_1, col_triage_2 = st.columns([2, 1])
    
    with col_triage_1:
        subject = st.text_input("Ticket Subject", value="GoPro connection failure on my laptop")
        description = st.text_area("Ticket Description", height=150, 
                                   value="I tried connecting my action camera via USB-C to transfer vacation recordings. The screen lights up but the laptop does not register the SD drive. Tried restarts and different ports.")
        
        col_form_1, col_form_2 = st.columns(2)
        with col_form_1:
            product = st.selectbox("Product", ["GoPro Hero", "Canon EOS", "Roomba Robot Vacuum", "Nest Thermostat", "iPhone", "MacBook Pro"])
        with col_form_2:
            channel = st.selectbox("Intake Channel", ["Chat", "Email", "Phone", "Social media"])
            
        triage_button = st.button("Run AI Triage & Predict", type="primary")
        
    with col_triage_2:
        st.markdown("#### Classification & Priority Advice")
        
        if triage_button and models["loaded"]:
            # Clean text
            cleaned_text = str(subject).lower() + " " + str(description).lower()
            cleaned_text = re.sub(r'[^a-zA-Z\s]', '', cleaned_text)
            
            # Predict
            vec = models["vectorizer"].transform([cleaned_text])
            cat_idx = models["category_classifier"].predict(vec)[0]
            pri_idx = models["priority_classifier"].predict(vec)[0]
            
            predicted_cat = models["category_encoder"].inverse_transform([cat_idx])[0]
            predicted_pri = models["priority_encoder"].inverse_transform([pri_idx])[0]
            
            # Show predictions
            st.markdown(f"**Predicted Category**: `{predicted_cat}`")
            st.markdown(f"**Predicted Priority**: `{predicted_pri}`")
            
            # Call Generative AI metrics
            with st.spinner("Calling Gemini LLM layer..."):
                ai_sentiment = ai_client.analyze_sentiment(description)
                ai_summary = ai_client.generate_summary(description)
                ai_response = ai_client.generate_response_draft(predicted_cat, subject, description)
                
            st.markdown(f"**AI Analyzed Sentiment**: `{ai_sentiment.get('sentiment')}` (Score: {ai_sentiment.get('score')}/5)")
            st.markdown(f"**AI Sentiment Tone**: `{ai_sentiment.get('tone')}`")
            
            st.info(f"**AI Summary**: {ai_summary}")
            
            st.markdown("##### AI Recommended Response Draft")
            st.text_area("Agent Response Email Template", value=ai_response, height=180)
        elif not models["loaded"]:
            st.warning("Classifier models are offline. Please verify that 'train_models.py' ran successfully.")

# ------------------------------------------------------------------------------
# TAB 3: AGENT COPILOT CHAT (RAG)
# ------------------------------------------------------------------------------
with tab3:
    st.markdown("### 🤖 Support Agent AI Copilot (RAG-Enabled)")
    st.markdown("This chatbot assists support agents with resolving active tickets. It performs real-time queries against the corporate Knowledge Base to synthesize answers.")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello Agent! I am your Support Copilot. Ask me questions about troubleshooting devices, refunds, or account cancellations."}
        ]
        
    # Display chat messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # React to user input
    if prompt := st.chat_input("Ask about refund policy, GoPro USB connection, or login failures..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Query chatbot
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Searching corporate knowledge base..."):
                response = ai_client.chat_assistant(st.session_state.chat_history, prompt)
            message_placeholder.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# ------------------------------------------------------------------------------
# TAB 4: SQL QUERY EXPLORER
# ------------------------------------------------------------------------------
with tab4:
    st.markdown("### 🔍 SQL Business Query Explorer")
    st.markdown("Select from a set of pre-configured analytical SQL queries or write your own to perform live analysis on the normalized database schema.")
    
    # Preset queries mapping
    preset_queries = {
        "Top Agents by Closed Ticket Volume": """
SELECT a.Agent_Name, COUNT(t.Ticket_ID) AS Resolved_Tickets
FROM SupportAgents a
JOIN SupportTickets t ON a.Agent_ID = t.Agent_ID
JOIN TicketStatus s ON t.Status_ID = s.Status_ID
WHERE s.Status_Name = 'Closed'
GROUP BY a.Agent_Name
ORDER BY Resolved_Tickets DESC
LIMIT 5;
        """,
        "SLA Compliance Rate by Support Department": """
SELECT 
    d.Department_Name,
    COUNT(t.Ticket_ID) AS Total_Tickets,
    SUM(CASE WHEN t.Resolution_Time <= 24.0 THEN 1 ELSE 0 END) AS Met_SLA,
    ROUND(SUM(CASE WHEN t.Resolution_Time <= 24.0 THEN 1 ELSE 0 END) * 100.0 / COUNT(t.Ticket_ID), 2) AS Compliance_Pct
FROM SupportTickets t
JOIN SupportAgents a ON t.Agent_ID = a.Agent_ID
JOIN Departments d ON a.Department_ID = d.Department_ID
WHERE t.Resolution_Time IS NOT NULL
GROUP BY d.Department_Name;
        """,
        "Customer Demographics Analysis (Satisfaction by Gender)": """
SELECT c.Gender, ROUND(AVG(t.Satisfaction_Rating), 2) AS Avg_CSAT, COUNT(t.Ticket_ID) AS Ticket_Count
FROM SupportTickets t
JOIN Customers c ON t.Customer_ID = c.Customer_ID
WHERE t.Satisfaction_Rating IS NOT NULL
GROUP BY c.Gender;
        """,
        "Monthly Ticket Volume and Cumulative Running Totals": """
SELECT 
    substr(Created_Date, 1, 7) AS Month,
    COUNT(Ticket_ID) AS Tickets_Count
FROM SupportTickets
GROUP BY Month
ORDER BY Month ASC;
        """
    }
    
    selected_preset = st.selectbox("Select Preset Analytical Query", list(preset_queries.keys()))
    
    sql_query = st.text_area("SQL Editor", value=preset_queries[selected_preset], height=180)
    
    run_sql = st.button("Run SQL Command", type="primary")
    
    if run_sql:
        with st.spinner("Executing query on database..."):
            query_result = db_client.run_query(sql_query)
        st.dataframe(query_result, use_container_width=True)
        
        # Render a quick visualization if columns fit
        if len(query_result.columns) >= 2 and "Error" not in query_result.columns:
            st.markdown("#### Quick Query Visualizer")
            x_col = query_result.columns[0]
            y_col = query_result.columns[1]
            try:
                fig_sql = px.bar(query_result, x=x_col, y=y_col, 
                                 title=f"Chart: {y_col} by {x_col}",
                                 color_discrete_sequence=["#3B82F6"])
                st.plotly_chart(fig_sql, use_container_width=True)
            except Exception as e:
                st.info(f"Could not auto-visualize: {e}")

import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    HAS_GEMINI = True
else:
    HAS_GEMINI = False

# Mock Knowledge Base FAQs for RAG search
KNOWLEDGE_BASE = [
    {
        "topic": "GoPro USB Connection Issue on macOS",
        "keywords": ["gopro", "macbook", "usb", "mac", "connection", "detect", "cable"],
        "solution": "Ensure the USB connection setting on your GoPro is configured correctly. On your GoPro screen, swipe down, swipe left, and tap 'Connections' > 'USB Connection'. Change it to 'MTP' (Media Transfer Protocol) instead of 'GoPro Connect' for file transfer. If the issue persists, try a different high-speed USB-C cable, connect directly to the Mac without a hub, or use an SD card adapter to transfer files."
    },
    {
        "topic": "Refund Eligibility and Timelines",
        "keywords": ["refund", "money back", "return", "chargeback", "reimbursement"],
        "solution": "Refunds are eligible within 30 days of the purchase date. The item must be in its original packaging and in unused condition. Once the returned item is received and inspected at our warehouse, refunds are processed within 5-7 business days to the original payment method."
    },
    {
        "topic": "Account Deactivation or Cancellation",
        "keywords": ["cancel", "deactivate", "delete account", "membership", "subscription"],
        "solution": "To cancel or deactivate your account/subscription, log in to the web portal, go to 'Account Settings' > 'Billing & Membership', and click 'Cancel Subscription'. Follow the on-screen prompts to confirm. Your access will remain active until the end of the current billing cycle. No partial refunds are issued for mid-month cancellations."
    },
    {
        "topic": "Login Failures & Password Resets",
        "keywords": ["login", "password", "reset", "signin", "credentials", "access"],
        "solution": "If you are having trouble logging in, click the 'Forgot Password' link on the login page to receive a secure reset link via email. Additionally, ensure browser cookies are cleared, or try signing in using an incognito window. If two-factor authentication (2FA) is failing, verify that the system clock on your mobile device is synchronized with internet time."
    },
    {
        "topic": "Shipping and Package Tracking",
        "keywords": ["shipping", "delivery", "shipped", "track", "delay", "post"],
        "solution": "Standard shipping takes 3-5 business days, while express delivery takes 1-2 business days. You can track your package using the tracking link provided in your shipment confirmation email. If the status is stuck or marked as delivered but not received, please check with neighbors, wait 24 hours, or contact our shipping partner listed in the tracking info."
    },
    {
        "topic": "Product Setup and Calibration (General)",
        "keywords": ["setup", "install", "calibrate", "turn on", "manual", "configure"],
        "solution": "For new product setup, please refer to the Quick Start guide included in the packaging. Download the product mobile application (if applicable) and follow the step-by-step Bluetooth pairing instructions. Ensure the device is fully charged before the first calibration cycle."
    }
]

class GeminiClient:
    def __init__(self):
        self.api_key_loaded = HAS_GEMINI
        if self.api_key_loaded:
            # We use gemini-3.5-flash as it is fast, cost-effective and highly capable
            self.model = genai.GenerativeModel('gemini-3.5-flash')
        else:
            self.model = None

    def generate_summary(self, description):
        """Generates a concise one-sentence summary of the ticket."""
        if not self.api_key_loaded:
            # Fallback mock summary
            return f"Mock Summary: Customer reported an issue regarding the device operation: '{description[:50]}...'"
        
        prompt = (
            f"You are an expert customer support triager. Summarize the following customer support ticket "
            f"in exactly one clear, professional sentence focusing on the core problem. "
            f"Do not include greeting or signature:\\n\\n{description}"
        )
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def generate_response_draft(self, category, subject, description):
        """Generates a professional response template for the agent."""
        if not self.api_key_loaded:
            return (
                f"Dear Customer,\n\n"
                f"Thank you for contacting us regarding your request: '{subject}'. "
                f"Our Support Team has categorized this issue under '{category}'. "
                f"We are actively investigating the details and will get back to you shortly.\n\n"
                f"Best regards,\n"
                f"Customer Support Team"
            )

        prompt = (
            f"You are a customer support agent. Write a professional, polite response to the following ticket.\\n"
            f"Ticket Category: {category}\\n"
            f"Subject: {subject}\\n"
            f"Issue: {description}\\n\\n"
            f"Guidelines:\\n"
            f"1. Thank the customer and validate their frustration.\\n"
            f"2. Suggest a standard troubleshooting action related to the issue.\\n"
            f"3. Sign off as 'AI Customer Support Intelligence Copilot'.\\n"
            f"4. Keep it under 150 words."
        )
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating draft: {str(e)}"

    def analyze_sentiment(self, description):
        """Analyzes the ticket description and returns tone and sentiment score."""
        if not self.api_key_loaded:
            return {"sentiment": "Negative", "tone": "Frustrated (Mock)", "score": 2}

        prompt = (
            f"Analyze the following support ticket description. "
            f"Identify the sentiment (Positive, Neutral, Negative), primary emotional tone (e.g. Frustrated, Polite, Anxious, Satisfied), "
            f"and assign a numerical sentiment score from 1 (very negative) to 5 (very positive).\\n\\n"
            f"Description: {description}\\n\\n"
            f"Return ONLY a valid JSON object matching this schema:\\n"
            f"{{\\\"sentiment\\\": \\\"...\\\", \\\"tone\\\": \\\"...\\\", \\\"score\\\": 3}}"
        )
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON block
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return {"sentiment": "Neutral", "tone": "Informational", "score": 3}
        except Exception:
            return {"sentiment": "Neutral", "tone": "Informational", "score": 3}

    def recommend_priority_and_category(self, subject, description):
        """AI Recommendation for Priority and Category based on description."""
        if not self.api_key_loaded:
            return {"recommended_priority": "Medium", "recommended_category": "Technical"}

        prompt = (
            f"Evaluate this support ticket.\\n"
            f"Subject: {subject}\\n"
            f"Description: {description}\\n\\n"
            f"Decide the priority (Low, Medium, High) and category (Technical, Billing, Refund, Shipping, Account, Login).\\n"
            f"Provide a brief, one-sentence reasoning for your choice.\\n\\n"
            f"Return ONLY a valid JSON object matching this schema:\\n"
            f"{{\\\"recommended_priority\\\": \\\"...\\\", \\\"recommended_category\\\": \\\"...\\\", \\\"reasoning\\\": \\\"...\\\"}}"
        )
        try:
            response = self.model.generate_content(prompt)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return {"recommended_priority": "Medium", "recommended_category": "Technical", "reasoning": "Default decision"}
        except Exception:
            return {"recommended_priority": "Medium", "recommended_category": "Technical", "reasoning": "Fallback decision"}

    def search_knowledge_base(self, query):
        """RAG Retrieval: Returns the most relevant knowledge base articles."""
        query_words = set(re.findall(r'\w+', str(query).lower()))
        best_match = None
        max_overlap = 0

        # Simple overlap search (can be enriched with embeddings)
        for article in KNOWLEDGE_BASE:
            overlap = len(query_words.intersection(article["keywords"]))
            if overlap > max_overlap:
                max_overlap = overlap
                best_match = article

        # If no keywords matched, return a general article
        if not best_match or max_overlap == 0:
            return KNOWLEDGE_BASE[5]  # General setup
        return best_match

    def chat_assistant(self, chat_history, user_message):
        """Conversational Copilot: RAG-enabled chat assistant."""
        # Find relevant article
        relevant_article = self.search_knowledge_base(user_message)
        kb_context = f"Topic: {relevant_article['topic']}\nDetails: {relevant_article['solution']}"

        if not self.api_key_loaded:
            return (
                f"Assistant (Mock RAG Mode):\n"
                f"Based on the knowledge base article: '{relevant_article['topic']}', here is the recommended resolution:\n"
                f"--> {relevant_article['solution']}"
            )

        # Build prompt with history
        history_str = ""
        for msg in chat_history[-6:]:  # past 3 turns
            history_str += f"{msg['role']}: {msg['content']}\n"

        prompt = (
            f"You are a helpful customer support agent copilot assistant.\\n"
            f"You assist agents in resolving customer inquiries by providing information from the corporate Knowledge Base.\\n\\n"
            f"Knowledge Base Context:\\n{kb_context}\\n\\n"
            f"Conversational History:\\n{history_str}\\n"
            f"Agent: {user_message}\\n"
            f"Assistant (respond concisely based ONLY on the context provided, keeping a professional tone):"
        )
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error communicating with AI assistant: {str(e)}"

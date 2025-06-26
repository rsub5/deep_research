import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager
import os
from datetime import datetime
from markdown_to_pdf import convert_markdown_to_pdf
from markdown_to_docx import convert_markdown_to_docx
from email_agent import send_email_with_markdown, _send_email_impl
import re
from token_manager import validate_token, save_token, generate_token

load_dotenv(override=True)

# Global variable to store the latest report
latest_report = ""

# Enhanced UI Constants
UI_TITLE = """
# 🔬 Deep Research Assistant
*Powered by AI-driven research and analysis*
"""

# Enhanced CSS for compact authentication
CUSTOM_CSS = """
<style>
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
    }
    
    .top-nav {
        background: #f8f9fa;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .auth-compact {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .auth-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .research-section {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 1.5rem;
    }
    
    .output-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    
    .status-indicator {
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 500;
        text-align: center;
    }
    
    .status-awaiting { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
    .status-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .status-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .status-processing { background: #cce5ff; color: #004085; border: 1px solid #b3d7ff; }
    
    .button-group {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .download-section {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    
    .email-section {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #bbdefb;
    }
    
    .compact-input {
        max-width: 200px;
        font-size: 0.9rem;
    }
    
    .compact-button {
        font-size: 0.8rem;
        padding: 0.25rem 0.5rem;
        height: auto;
    }
    
    .auth-toggle {
        background: #007bff;
        color: white;
        border: none;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        cursor: pointer;
    }
    
    .auth-toggle:hover {
        background: #0056b3;
    }
</style>
"""

# Enhanced status messages
STATUS_MESSAGES = {
    "awaiting": "⏳ Awaiting authentication...",
    "authenticated": "✅ Authenticated! Ready to research.",
    "invalid_token": "❌ Invalid token. Please request a valid token.",
    "searching": "🔍 Searching for research...",
    "thinking": "🤔 Analyzing information...",
    "writing": "✍️ Writing research document...",
    "completed": "✅ Research completed successfully!",
    "error": "❌ An error occurred. Please try again."
}

# Query UI Elements
QUERY_LABELS = {
    "input": "What topic would you like to research?",
    "report": "Report"
}

# Button Labels
BUTTON_LABELS = {
    "run": "Run",
    "download_pdf": "Download Report (PDF)",
    "download_docx": "Download Report (DOCX)", 
    "send_email": "Send Email",
    "download_markdown": "Download Report (Markdown)"
}

# File Labels
FILE_LABELS = {
    "pdf": "Download PDF Report",
    "docx": "Download DOCX Report",
    "markdown": "Download Report"
}

# Email UI Elements
EMAIL_LABELS = {
    "input": "Recipient Email",
    "status": "Email Status"
}

# Email Status Messages
EMAIL_MESSAGES = {
    "no_report": "No report to send.",
    "no_email": "Please enter a recipient email address.",
    "invalid_email": "Invalid email address. Please enter a valid email in the format: user@example.com.",
    "not_sent": "Email not sent",
    "valid_email": "Valid email!",
    "email_sent": "Email sent!",
    "unknown_error": "Unknown error"
}

# CSS Styles for Email Status
EMAIL_STATUS_STYLES = {
    "base": "font-size: 14px; margin-top: 8px;",
    "neutral": "color: #666;",
    "error": "color: #d32f2f;",
    "success": "color: #2e7d32;"
}

# File Naming Patterns
FILE_PATTERNS = {
    "timestamp_format": "%Y%m%d_%H%M%S",
    "markdown_filename": "research_report_{timestamp}.md"
}

# Debug Messages
DEBUG_MESSAGES = {
    "no_report": "[DEBUG] No report to send.",
    "no_email": "[DEBUG] No email entered.",
    "invalid_email": "[DEBUG] Invalid email format.",
    "email_result": "[DEBUG] Email send result: {message}",
    "exception": "[DEBUG] Exception during send: {error}"
}

# Chunk Filter Keywords
CHUNK_FILTER_KEYWORDS = [
    "View trace:",
    "Starting",
    "Searches", 
    "Report",
    "Email"
]

def create_status_html(message, style_type="neutral"):
    """Create HTML formatted status message with consistent styling"""
    base_style = EMAIL_STATUS_STYLES["base"]
    color_style = EMAIL_STATUS_STYLES[style_type]
    return f"<div style='{base_style} {color_style}'>{message}</div>"

def download_report():
    """Download the latest report as a markdown file"""
    global latest_report
    if not latest_report:
        return None
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime(FILE_PATTERNS["timestamp_format"])
    filename = FILE_PATTERNS["markdown_filename"].format(timestamp=timestamp)
    
    # Write report to file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(latest_report)
    
    return filename

def download_report_as_pdf():
    """Download the latest report as a PDF file"""
    global latest_report
    if not latest_report:
        return None
    filename = convert_markdown_to_pdf(latest_report)
    return filename

def download_report_as_docx():
    """Download the latest report as a DOCX file"""
    global latest_report
    if not latest_report:
        return None
    filename = convert_markdown_to_docx(latest_report)
    return filename

async def run(query: str):
    global latest_report
    latest_report = ""
    
    async for chunk in ResearchManager().run(query):
        # Store the final report (the last chunk is the markdown report)
        if chunk and not any(chunk.startswith(keyword) for keyword in CHUNK_FILTER_KEYWORDS):
            latest_report = chunk
        yield chunk

def validate_email_format(email):
    """Validate email format using regex"""
    # More strict pattern that prevents double dots and other invalid formats
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    
    # Additional checks for common invalid patterns
    if '..' in email or email.startswith('.') or email.endswith('.'):
        return False
    
    # Check for consecutive dots in domain part
    domain_part = email.split('@')[1] if '@' in email else ''
    if '..' in domain_part:
        return False
    
    return True

async def send_email_report(email):
    """Send email report with validation"""
    global latest_report
    
    if not latest_report:
        print(DEBUG_MESSAGES["no_report"])
        return create_status_html(EMAIL_MESSAGES["no_report"])
    
    if not email:
        print(DEBUG_MESSAGES["no_email"])
        return create_status_html(EMAIL_MESSAGES["no_email"])
    
    # Validate email format
    if not validate_email_format(email):
        print(DEBUG_MESSAGES["invalid_email"])
        return create_status_html(EMAIL_MESSAGES["invalid_email"], "error")
    
    try:
        result = await send_email_with_markdown(latest_report, recipient=email)
        message = result.get("message", EMAIL_MESSAGES["unknown_error"])
        print(DEBUG_MESSAGES["email_result"].format(message=message))
        
        if result.get("status") == "success":
            return create_status_html(result.get("message", EMAIL_MESSAGES["email_sent"]), "success")
        else:
            return create_status_html(result.get("message", EMAIL_MESSAGES["unknown_error"]), "error")
    except Exception as e:
        print(DEBUG_MESSAGES["exception"].format(error=e))
        return create_status_html(f"Error: {str(e).splitlines()[0]}", "error")

# To launch the UI, run deep_research_start.py


import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager
import os
from datetime import datetime
from markdown_to_pdf import convert_markdown_to_pdf
from markdown_to_docx import convert_markdown_to_docx
from email_agent import send_email_with_markdown
import re

load_dotenv(override=True)

# Global variable to store the latest report
latest_report = ""

# UI Text Constants
UI_TITLE = "# Deep Research"

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

with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown(UI_TITLE)
    query_textbox = gr.Textbox(label=QUERY_LABELS["input"])
    run_button = gr.Button(BUTTON_LABELS["run"], variant="primary")
    report = gr.Markdown(label=QUERY_LABELS["report"])
    
    # Arrange buttons in a single row
    with gr.Row():
        with gr.Column(scale=1):
            download_pdf_button = gr.Button(BUTTON_LABELS["download_pdf"], variant="secondary")
        with gr.Column(scale=1):
            download_docx_button = gr.Button(BUTTON_LABELS["download_docx"], variant="secondary")
        with gr.Column(scale=1):
            send_email_button = gr.Button(BUTTON_LABELS["send_email"], variant="secondary")
    
    # Arrange outputs in a single row below
    with gr.Row():
        with gr.Column(scale=1):
            download_pdf_file = gr.File(label=FILE_LABELS["pdf"])
        with gr.Column(scale=1):
            download_docx_file = gr.File(label=FILE_LABELS["docx"])
        with gr.Column(scale=1):
            email_input = gr.Textbox(label=EMAIL_LABELS["input"], value="", interactive=True)
            email_status = gr.HTML(
                value=create_status_html(EMAIL_MESSAGES["not_sent"]), 
                label=EMAIL_LABELS["status"]
            )
    
    # Markdown download button (optional, can be placed elsewhere)
    download_button = gr.Button(BUTTON_LABELS["download_markdown"], variant="secondary")
    download_file = gr.File(label=FILE_LABELS["markdown"])
    
    # Set up event handlers
    run_button.click(fn=run, inputs=query_textbox, outputs=report)
    query_textbox.submit(fn=run, inputs=query_textbox, outputs=report)
    download_button.click(fn=download_report, outputs=download_file)
    download_pdf_button.click(fn=download_report_as_pdf, outputs=download_pdf_file)
    download_docx_button.click(fn=download_report_as_docx, outputs=download_docx_file)
    send_email_button.click(fn=send_email_report, inputs=email_input, outputs=email_status)

ui.launch(inbrowser=True)


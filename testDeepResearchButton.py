import gradio as gr
import pathlib
import re
from markdown_to_pdf import convert_markdown_to_pdf
from markdown_to_docx import convert_markdown_to_docx
from email_agent import send_email_with_markdown
import agents
print("Importing Agent from agents...")
from agents import Agent
print("Imported Agent:", Agent)

# Constants and Configuration
REPORT_PATH = pathlib.Path("research_report_20250618_193430.md")
DEFAULT_REPORT_CONTENT = "Report file not found."
TEST_REPORT_FILENAME = "test_report.md"

# UI Text Constants
UI_TITLE = "# Test Deep Research Buttons (No Agent)"
UI_DESCRIPTION = "This test app lets you validate the PDF, DOCX, and Send Email buttons using a static report."

# Button Labels
BUTTON_LABELS = {
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
    "not_sent": "Email not sent"
}

# CSS Styles for Email Status
EMAIL_STATUS_STYLES = {
    "base": "font-size: 14px; margin-top: 8px;",
    "neutral": "color: #666;",
    "error": "color: #d32f2f;",
    "success": "color: #2e7d32;"
}

def load_report_content():
    """Load the static report content from file"""
    if REPORT_PATH.exists():
        with REPORT_PATH.open(encoding="utf-8") as f:
            return f.read()
    return DEFAULT_REPORT_CONTENT

def create_status_html(message, style_type="neutral"):
    """Create HTML formatted status message with consistent styling"""
    base_style = EMAIL_STATUS_STYLES["base"]
    color_style = EMAIL_STATUS_STYLES[style_type]
    return f"<div style='{base_style} {color_style}'>{message}</div>"

def download_report():
    """Download report as markdown file"""
    if not latest_report or latest_report == DEFAULT_REPORT_CONTENT:
        return None
    filename = TEST_REPORT_FILENAME
    with open(filename, "w", encoding="utf-8") as f:
        f.write(latest_report)
    return filename

def download_report_as_pdf():
    """Download report as PDF file"""
    if not latest_report or latest_report == DEFAULT_REPORT_CONTENT:
        return None
    return convert_markdown_to_pdf(latest_report)

def download_report_as_docx():
    """Download report as DOCX file"""
    if not latest_report or latest_report == DEFAULT_REPORT_CONTENT:
        return None
    return convert_markdown_to_docx(latest_report)

def validate_email(email):
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
    if not latest_report or latest_report == DEFAULT_REPORT_CONTENT:
        return create_status_html(EMAIL_MESSAGES["no_report"])
    
    if not email:
        return create_status_html(EMAIL_MESSAGES["no_email"])
    
    # Validate email format
    if not validate_email(email):
        return create_status_html(EMAIL_MESSAGES["invalid_email"], "error")
    
    result = await send_email_with_markdown(latest_report, recipient=email)
    
    if result["status"] == "success":
        return create_status_html(result["message"], "success")
    else:
        return create_status_html(result["message"], "error")

def create_ui():
    """Create and configure the Gradio interface"""
    with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
        gr.Markdown(UI_TITLE)
        gr.Markdown(UI_DESCRIPTION)
        
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
                # Email input and status label stacked vertically, same width as buttons
                email_input = gr.Textbox(label=EMAIL_LABELS["input"], value="", interactive=True)
                email_status = gr.HTML(
                    value=create_status_html(EMAIL_MESSAGES["not_sent"]), 
                    label=EMAIL_LABELS["status"]
                )
        
        # Markdown download button (optional, can be placed elsewhere)
        download_button = gr.Button(BUTTON_LABELS["download_markdown"], variant="secondary")
        download_file = gr.File(label=FILE_LABELS["markdown"])
        
        # Set up event handlers
        download_button.click(fn=download_report, outputs=download_file)
        download_pdf_button.click(fn=download_report_as_pdf, outputs=download_pdf_file)
        download_docx_button.click(fn=download_report_as_docx, outputs=download_docx_file)
        send_email_button.click(fn=send_email_report, inputs=email_input, outputs=email_status)
    
    return ui

# Load report content at module level
latest_report = load_report_content()

if __name__ == "__main__":
    ui = create_ui()
    ui.launch(inbrowser=True) 
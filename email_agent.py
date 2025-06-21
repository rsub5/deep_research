import os
from typing import Dict
import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content, To
from agents import Agent, function_tool
import asyncio
from writer_agent import ReportData

def _send_email_impl(subject: str, html_body: str, recipient: str = None) -> Dict[str, str]:
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("reply@subirroy.in") # put your verified sender here
    to_email = To(recipient if recipient else "rsub.2025@gmail.com") # use provided recipient or fallback
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print("Email response", response.status_code)
    return {"status": "success"}

@function_tool
def send_email(subject: str, html_body: str, recipient: str = None) -> Dict[str, str]:
    return _send_email_impl(subject, html_body, recipient)

INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the 
report converted into clean, well presented HTML with an appropriate subject line."""

email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)

async def send_email_with_markdown(markdown: str, recipient: str = None):
    subject = "Research Report"
    html_body = markdown  # Optionally convert markdown to HTML
    try:
        await asyncio.to_thread(_send_email_impl, subject, html_body, recipient)
        print("Email sent (async, markdown)")
        return {"status": "success", "message": "Email sent!"}
    except Exception as e:
        print(f"Email send error: {e}")
        return {"status": "error", "message": f"Error: {str(e).splitlines()[0]}"}

async def send_email_with_report(report: ReportData, recipient: str = None):
    markdown = report.markdown_report if hasattr(report, 'markdown_report') else str(report)
    return await send_email_with_markdown(markdown, recipient=recipient)

from dotenv import load_dotenv
load_dotenv()
import gradio as gr
import os
from deep_research import (
    run,
    validate_token,
    save_token,
    generate_token,
    send_email_with_markdown,
    create_status_html,
    download_report,
    download_report_as_pdf,
    download_report_as_docx,
    validate_email_format,
    send_email_report,
    EMAIL_MESSAGES,
    STATUS_MESSAGES,
    CHUNK_FILTER_KEYWORDS
)
from email_agent import send_request_token_email

# Use relative path with deep_research folder as main
css_file_path = "./deep_research_style.css"

with open(css_file_path) as f:
    CUSTOM_CSS = f.read()

def launch_ui():
    with gr.Blocks(
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray",
            neutral_hue="slate"
        ),
        css=CUSTOM_CSS
    ) as ui:
        # Header Section (text only, no background)
        with gr.Row():
            gr.HTML('<div class="header-title">🔬 Deep Research Assistant <span style="font-size:1rem;font-weight:400;color:#4a5568;">*Powered by AI-driven research and analysis*</span></div>')
        
        # Main Content Area
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML('<div class="main-content">')
                # Research Section (with comfortable gap)
                with gr.Row():
                    with gr.Column(scale=1):
                        with gr.Row():
                            with gr.Column(scale=0, min_width=0):
                                auth_icon_button = gr.Button("🔐", elem_id="auth-inline-btn", size="sm", variant="secondary")
                        with gr.Row():
                            research_heading = gr.Markdown("### 🔬 Research Query (click auth to Research)", elem_id="research-query-heading")
                query_textbox = gr.Textbox(
                    label="What would you like to research?",
                    placeholder="Enter your research topic or question...",
                    lines=3,
                    max_lines=5
                )
                run_button = gr.Button(
                    "🚀 Start Research",
                    variant="primary",
                    size="lg",
                    interactive=False,
                    elem_classes=["research-button"]
                )
                gr.HTML('</div>')
                
                # Report Display Section
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML('<div class="output-section">')
                        gr.Markdown("### 📄 Research Report")
                        report = gr.Markdown(
                            label="Report",
                            value="*Your research report will appear here...*"
                        )
                        gr.HTML('</div>')
                
                # Download and Export Section
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML('<div class="download-section">')
                        gr.Markdown("### 📥 Download Options")
                        with gr.Row():
                            download_pdf_button = gr.Button(
                                "📄 Download PDF",
                                variant="secondary",
                                size="sm",
                                scale=1
                            )
                            download_docx_button = gr.Button(
                                "📝 Download DOCX",
                                variant="secondary",
                                size="sm",
                                scale=1
                            )
                            download_button = gr.Button(
                                "📋 Download Markdown",
                                variant="secondary",
                                size="sm",
                                scale=1
                            )
                        
                        with gr.Row():
                            download_pdf_file = gr.File(label="PDF Report")
                            download_docx_file = gr.File(label="DOCX Report")
                            download_file = gr.File(label="Markdown Report")
                        gr.HTML('</div>')
                
                # Email Section
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML('<div class="email-section">')
                        gr.Markdown("### 📧 Email Report")
                        with gr.Row():
                            email_recipient = gr.Textbox(
                                label="Recipient Email",
                                placeholder="Enter recipient email address",
                                scale=2
                            )
                            send_email_button = gr.Button(
                                "📤 Send Email",
                                variant="primary",
                                size="sm",
                                scale=1
                            )
                        
                        email_status = gr.HTML(
                            value=create_status_html(EMAIL_MESSAGES["not_sent"]),
                            label="Email Status"
                        )
                        gr.HTML('</div>')
                
                gr.HTML('</div>')  # End main-content
        
        # Sidebar for Authentication (always present, toggled with CSS class)
        with gr.Row(elem_id="sidebar-row") as sidebar_row:
            with gr.Column(scale=1, elem_classes=["sidebar-container"], elem_id="auth-sidebar"):
                with gr.Row(elem_classes=["sidebar-header"]):
                    gr.Markdown("### 🔐 Authentication")
                with gr.Column(elem_classes=["sidebar-content"]):
                    with gr.Column(elem_classes=["auth-form"]):
                        gr.Markdown('> Click on Auth to securely authenticate before running a research query.')
                        email_input = gr.Textbox(
                            label="📧 Email Address",
                            placeholder="Enter your email address"
                        )
                        token_input = gr.Textbox(
                            label="🔑 Access Token",
                            placeholder="Enter your access token",
                            type="password"
                        )
                        with gr.Row():
                            request_token_button = gr.Button(
                                "📤 Request Token",
                                variant="secondary",
                                size="sm"
                            )
                            validate_button = gr.Button(
                                "✅ Validate Token",
                                variant="primary",
                                size="sm"
                            )
                        refresh_button = gr.Button(
                            "🔄 Refresh",
                            variant="secondary",
                            size="sm"
                        )
                        status_label = gr.HTML(
                            value=f'<div class="status-indicator status-awaiting">{STATUS_MESSAGES["awaiting"]}</div>'
                        )

        # --- Event handlers ---
        sidebar_visible = {'state': False}  # mutable state for sidebar
        def toggle_sidebar():
            sidebar_visible['state'] = not sidebar_visible['state']
            if sidebar_visible['state']:
                return gr.update(elem_classes=[])
            else:
                return gr.update(elem_classes=["hidden"])
        auth_icon_button.click(fn=toggle_sidebar, outputs=sidebar_row)

        def is_admin_mode(email):
            return email.strip().startswith("RSUB_TOKEN:")

        def update_request_button(email):
            if is_admin_mode(email):
                return gr.update(value="🔧 Generate Token")
            else:
                return gr.update(value="📤 Request Token")

        def request_or_generate_token_action(email, token=None):
            if is_admin_mode(email):
                actual_email = email.replace("RSUB_TOKEN:", "").strip()
                if not actual_email:
                    return gr.update(value='<div style="color: #d32f2f;">❌ Please provide a valid email after RSUB_TOKEN:</div>'), gr.update()
                if not token:
                    token = generate_token(16)
                save_token(actual_email, token)
                return gr.update(value=f'<div style="color: #2e7d32;">✅ Token generated and saved for {actual_email}.</div>'), gr.update()
            else:
                if not email:
                    return gr.update(value='<div style="color: #d32f2f;">❌ Please enter an email to request a token.</div>'), gr.update()
                if not validate_email_format(email):
                    return gr.update(value='<div style="color: #d32f2f;">❌ Invalid email address. Please enter a valid email in the format: user@example.com.</div>'), gr.update()
                subject = f"Token Request for {email}"
                html_body = f"A user has requested a token for email: <b>{email}</b><br>Proposed token: <b>RSUB_TOKEN:{email}</b>"
                send_request_token_email(subject, html_body, recipient="admin@subirroy.in")
                return gr.update(value='<div style="color: #2e7d32;">✅ Token request sent. Please wait for admin approval.</div>'), gr.update()

        def validate_token_action(email, token):
            try:
                print(f"[DEBUG] validate_token_action called with email={email}, token={token}")
                if not validate_email_format(email):
                    print("[DEBUG] Invalid email format branch (inline style)")
                    return (
                        gr.update(value='<div style="color: #d32f2f;">❌ Invalid email address. Please enter a valid email in the format: user@example.com.</div>'),
                        gr.update(interactive=False),  # run_button disabled
                        gr.update(interactive=True),
                        gr.update(interactive=True)
                    )
                if not validate_token(email, token):
                    print("[DEBUG] Invalid token branch")
                    return (
                        gr.update(value='<div style="color: #d32f2f;">❌ Invalid token. Please request a valid token.</div>'),
                        gr.update(interactive=False),  # run_button disabled
                        gr.update(interactive=True),
                        gr.update(interactive=True)
                    )
                print("[DEBUG] Authenticated branch")
                return (
                    gr.update(value=f'<div class="status-indicator status-success">{STATUS_MESSAGES["authenticated"]}</div>'),
                    gr.update(interactive=True),      # run_button enabled
                    gr.update(interactive=False),     # email_input disabled
                    gr.update(interactive=False)      # token_input disabled
                )
            except Exception as e:
                print(f"[DEBUG] Exception: {e}")
                return (
                    gr.update(value=f'<div style="color: #d32f2f;">❌ Unexpected error: {str(e)}</div>'),
                    gr.update(interactive=False),
                    gr.update(interactive=True),
                    gr.update(interactive=True)
                )

        def refresh_action():
            return (
                gr.update(value=f'<div class="status-indicator status-awaiting">{STATUS_MESSAGES["awaiting"]}</div>'),
                gr.update(interactive=False),     # run_button disabled
                gr.update(interactive=True),      # email_input enabled
                gr.update(interactive=True)       # token_input enabled
            )

        async def run_with_token(query, email, token, status=gr.State()):
            if not validate_token(email, token):
                yield gr.update(value=f'<div class="status-indicator status-error">{STATUS_MESSAGES["invalid_token"]}</div>'), "*Please authenticate first to run research.*"
                return
            
            yield gr.update(value=f'<div class="status-indicator status-processing">{STATUS_MESSAGES["searching"]}</div>'), "*Starting research...*"
            
            async for chunk in run(query):
                if chunk.strip().lower().startswith("thinking"):
                    yield gr.update(value=f'<div class="status-indicator status-processing">{STATUS_MESSAGES["thinking"]}</div>'), chunk
                elif chunk.strip().lower().startswith("writing"):
                    yield gr.update(value=f'<div class="status-indicator status-processing">{STATUS_MESSAGES["writing"]}</div>'), chunk
                else:
                    yield gr.update(value=f'<div class="status-indicator status-success">{STATUS_MESSAGES["completed"]}</div>'), chunk

        # --- Connect events ---
        email_input.change(fn=update_request_button, inputs=email_input, outputs=request_token_button)
        request_token_button.click(fn=request_or_generate_token_action, inputs=[email_input, token_input], outputs=[status_label, request_token_button])
        validate_button.click(fn=validate_token_action, inputs=[email_input, token_input], outputs=[status_label, run_button, email_input, token_input])
        refresh_button.click(fn=refresh_action, inputs=None, outputs=[status_label, run_button, email_input, token_input])
        
        run_button.click(fn=run_with_token, inputs=[query_textbox, email_input, token_input], outputs=[status_label, report])
        query_textbox.submit(fn=run_with_token, inputs=[query_textbox, email_input, token_input], outputs=[status_label, report])
        download_button.click(fn=download_report, outputs=download_file)
        download_pdf_button.click(fn=download_report_as_pdf, outputs=download_pdf_file)
        download_docx_button.click(fn=download_report_as_docx, outputs=download_docx_file)
        send_email_button.click(fn=send_email_report, inputs=email_recipient, outputs=email_status)
    ui.launch(inbrowser=True)

if __name__ == "__main__":
    launch_ui() 
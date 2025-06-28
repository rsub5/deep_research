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
from token_manager import RESEARCH_RUN_COUNT_TOKEN

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
                        with gr.Row(elem_classes=["left-align-row"]):
                            with gr.Column(scale=1):
                                auth_icon_button = gr.Button("🔐", elem_id="auth-inline-btn", size="sm", variant="secondary")
                            with gr.Column(scale=8):
                                validation_message = gr.HTML(visible=True, value="", elem_id="validation-message")
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
                gr.HTML(f'<div style="color:#d32f2f;font-size:0.78rem;margin-top:0.25rem;">Due to computation cost, research can be performed only {RESEARCH_RUN_COUNT_TOKEN} time(s). You need to raise further request to run Research again.</div>')
                # Add revalidation message area
                revalidation_message = gr.HTML(
                    value="",
                    visible=False,
                    elem_id="revalidation-message"
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
                
                # Downloading / Email Report Options (Responsive, DRY, Layout Only)
                gr.Markdown("### 📥 Downloading / 📧 Email Report Options")
                with gr.Row():
                    # PDF Block
                    with gr.Column():
                        download_pdf_button = gr.Button(
                            "📄 Download PDF",
                            variant="secondary",
                            size="sm"
                        )
                        download_pdf_file = gr.File(label="PDF Report")
                    # DOCX Block
                    with gr.Column():
                        download_docx_button = gr.Button(
                            "📝 Download DOCX",
                            variant="secondary",
                            size="sm"
                        )
                        download_docx_file = gr.File(label="DOCX Report")
                    # Email Block
                    with gr.Column():
                        send_email_button = gr.Button(
                            "📤 Send Email",
                            variant="primary",
                            size="sm"
                        )
                        email_recipient = gr.Textbox(
                            label="",
                            placeholder=""
                        )
                        email_status = gr.HTML(
                            value=create_status_html(EMAIL_MESSAGES["not_sent"]),
                            label="Email Status"
                        )
                # (Commented out markdown button and file for future use)
                # with gr.Column():
                #     download_button = gr.Button(
                #         "📋 Download Markdown",
                #         variant="secondary",
                #         size="sm"
                #     )
                #     download_file = gr.File(label="Markdown Report")
                
                gr.HTML('</div>')  # End main-content
        
        # Sidebar for Authentication (always present, toggled with CSS class)
        with gr.Row(elem_id="sidebar-row") as sidebar_row:
            with gr.Column(scale=1, elem_classes=["sidebar-container"], elem_id="auth-sidebar"):
                # Sidebar header: close button (left), Authentication (center), lock icon (right)
                with gr.Row(elem_classes=["sidebar-header-bar"]):
                    with gr.Column(scale=1, min_width=0):
                        close_sidebar_btn = gr.Button("✖", size="sm", variant="secondary", elem_classes=["sidebar-close-btn"])
                    with gr.Column(scale=6, min_width=0):
                        gr.Markdown("<span class='sidebar-header-title'>Authentication</span>")
                    with gr.Column(scale=1, min_width=0, elem_id="sidebar-lock-icon-col"):
                        gr.Markdown("<span class='sidebar-header-lock'>🔒</span>")
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
        close_sidebar_btn.click(fn=toggle_sidebar, outputs=sidebar_row)

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
                return gr.update(value=f'<div style="color: #2e7d32;">✅ Token generated and saved for {actual_email}.<br><strong>Token:</strong> {token}</div>'), gr.update()
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
                        gr.update(value='<div style=\"color: #d32f2f;\">❌ Invalid email address. Please enter a valid email in the format: user@example.com.</div>'),
                        gr.update(interactive=False),  # run_button disabled
                        gr.update(interactive=True),
                        gr.update(interactive=True),
                        gr.update(value=""),  # email_recipient cleared
                        gr.update(value=""),    # validation_message cleared
                        gr.update(visible=False)  # revalidation_message hidden
                    )
                if not validate_token(email, token):
                    print("[DEBUG] Invalid token branch")
                    return (
                        gr.update(value='<div style=\"color: #d32f2f;\">❌ Invalid token. Please request a valid token.</div>'),
                        gr.update(interactive=False),  # run_button disabled
                        gr.update(interactive=True),
                        gr.update(interactive=True),
                        gr.update(value=""),  # email_recipient cleared
                        gr.update(value=""),    # validation_message cleared
                        gr.update(visible=False)  # revalidation_message hidden
                    )
                print("[DEBUG] Authenticated branch")
                return (
                    gr.update(value=f'<div class=\"status-indicator status-success\">{STATUS_MESSAGES["authenticated"]}</div>'),
                    gr.update(interactive=True),      # run_button enabled
                    gr.update(interactive=False),     # email_input disabled
                    gr.update(interactive=False),     # token_input disabled
                    gr.update(value=email),           # autofill email_recipient
                    gr.update(value=f'<span style="color: #2e7d32; font-weight: 500; font-family: inherit; font-size: 1rem; margin-left: 48px; display: inline-block; vertical-align: middle;">{email} validated to run the research</span>'),
                    gr.update(visible=False)  # revalidation_message hidden
                )
            except Exception as e:
                print(f"[DEBUG] Exception: {e}")
                return (
                    gr.update(value=f'<div style=\"color: #d32f2f;\">❌ Unexpected error: {str(e)}</div>'),
                    gr.update(interactive=False),
                    gr.update(interactive=True),
                    gr.update(interactive=True),
                    gr.update(value=""),  # email_recipient cleared
                    gr.update(value=""),    # validation_message cleared
                    gr.update(visible=False)  # revalidation_message hidden
                )

        def refresh_action():
            return (
                gr.update(value=f'<div class="status-indicator status-awaiting">{STATUS_MESSAGES["awaiting"]}</div>'),
                gr.update(interactive=False),     # run_button disabled
                gr.update(interactive=True),      # email_input enabled
                gr.update(interactive=True),       # token_input enabled
                gr.update(value=""),                 # validation_message cleared
                gr.update(visible=False)             # revalidation_message hidden
            )

        async def run_with_token(query, email, token, status=gr.State()):
            if not validate_token(email, token):
                yield (
                    gr.update(value=f'<div class="status-indicator status-error">{STATUS_MESSAGES["invalid_token"]}</div>'), 
                    "*Please authenticate first to run research.*",
                    gr.update(interactive=False),  # Disable run button
                    gr.update(visible=True, value='<div style="color: #d32f2f; font-size: 0.9rem; margin-top: 0.5rem; padding: 0.5rem; background-color: #ffebee; border-radius: 4px; border-left: 4px solid #d32f2f;"><strong>⚠️ Research Blocked:</strong> Please validate your token again to run further research.</div>')
                )
                return
            
            # Disable the run button immediately after first click
            yield (
                gr.update(value=f'<div class="status-indicator status-processing">{STATUS_MESSAGES["searching"]}</div>'), 
                "*Starting research...*",
                gr.update(interactive=False),  # Disable run button
                gr.update(visible=False)       # Hide revalidation message
            )
            
            async for chunk in run(query):
                if chunk.strip().lower().startswith("thinking"):
                    yield (
                        gr.update(value=f'<div class="status-indicator status-processing">{STATUS_MESSAGES["thinking"]}</div>'), 
                        chunk,
                        gr.update(interactive=False),  # Keep button disabled
                        gr.update(visible=False)
                    )
                elif chunk.strip().lower().startswith("writing"):
                    yield (
                        gr.update(value=f'<div class="status-indicator status-processing">{STATUS_MESSAGES["writing"]}</div>'), 
                        chunk,
                        gr.update(interactive=False),  # Keep button disabled
                        gr.update(visible=False)
                    )
                else:
                    # Research completed - show revalidation message
                    yield (
                        gr.update(value=f'<div class="status-indicator status-success">{STATUS_MESSAGES["completed"]}</div>'), 
                        chunk,
                        gr.update(interactive=False),  # Keep button disabled
                        gr.update(visible=True, value='<div style="color: #1976d2; font-size: 0.9rem; margin-top: 0.5rem; padding: 0.5rem; background-color: #e3f2fd; border-radius: 4px; border-left: 4px solid #1976d2;"><strong>✅ Research triggered successfully!</strong> Please validate your token again to run further research.</div>')
                    )

        # --- Connect events ---
        email_input.change(fn=update_request_button, inputs=email_input, outputs=request_token_button)
        request_token_button.click(fn=request_or_generate_token_action, inputs=[email_input, token_input], outputs=[status_label, request_token_button])
        validate_button.click(
            fn=validate_token_action,
            inputs=[email_input, token_input],
            outputs=[status_label, run_button, email_input, token_input, email_recipient, validation_message, revalidation_message]
        )
        refresh_button.click(fn=refresh_action, inputs=None, outputs=[status_label, run_button, email_input, token_input, validation_message, revalidation_message])
        
        run_button.click(
            fn=run_with_token, 
            inputs=[query_textbox, email_input, token_input], 
            outputs=[status_label, report, run_button, revalidation_message]
        )
        query_textbox.submit(
            fn=run_with_token, 
            inputs=[query_textbox, email_input, token_input], 
            outputs=[status_label, report, run_button, revalidation_message]
        )
        # download_button.click(fn=download_report, outputs=download_file)
        download_pdf_button.click(fn=download_report_as_pdf, outputs=download_pdf_file)
        download_docx_button.click(fn=download_report_as_docx, outputs=download_docx_file)
        send_email_button.click(fn=send_email_report, inputs=email_recipient, outputs=email_status)
    ui.launch(inbrowser=True)

if __name__ == "__main__":
    launch_ui() 
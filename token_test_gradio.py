import gradio as gr
from token_manager import validate_token, generate_token, save_token

def run(email, token):
    if not validate_token(email, token):
        return "Invalid token for this email. Access denied."
    return f"Token validated for {email}!"

def generate_and_save(email):
    if not email:
        return "Please enter an email to generate a token."
    token = generate_token()
    save_token(email, token)
    return f"Generated token for {email}: {token}"

with gr.Blocks() as demo:
    gr.Markdown("# Token Validation Demo")
    email_input = gr.Textbox(label="Email")
    token_input = gr.Textbox(label="Access Token")
    with gr.Row():
        run_button = gr.Button("Validate Token")
        gen_button = gr.Button("Generate Token")
    output = gr.Markdown()
    run_button.click(fn=run, inputs=[email_input, token_input], outputs=output)
    gen_button.click(fn=generate_and_save, inputs=email_input, outputs=output)

demo.launch() 
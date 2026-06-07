import gradio as gr

def create_downloader_ui():
    """
    Defines the layout for the Downloader tab.
    Returns a dictionary of components to be used by events.py.
    """
    gr.Markdown("## 📥 Model Downloader")
    
    with gr.Row():
        source = gr.Dropdown(
            choices=["auto", "huggingface", "civitai"], 
            value="auto", 
            label="Source Platform"
        )
        url = gr.Textbox(label="Model URL", placeholder="Paste URL here...")
        
    with gr.Row():
        filename = gr.Textbox(label="Save As (Filename)", placeholder="model.safetensors")
        api_key = gr.Textbox(label="API Key (Optional)", type="password")
        
    download_btn = gr.Button("Start Download", variant="primary")
    status_output = gr.Markdown("Status: Ready")

    return {
        "inputs": [source, url, filename, api_key],
        "button": download_btn,
        "output": status_output
    }
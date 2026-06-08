import gradio as gr

def create_downloader_ui():
    gr.Markdown("## 📥 Model Downloader")
    
    # gr.Group binds configuration fields into a single unified container
    with gr.Group():
        with gr.Row():
            source = gr.Dropdown(
                choices=["auto", "huggingface", "civitai"], 
                value="auto", 
                label="🌐 Source Platform",
                scale=1  # 1/5th width
            )
            url = gr.Textbox(
                label="🔗 Model URL", 
                placeholder="Paste HuggingFace or Civitai URL here...",
                scale=3  # 3/5ths width to handle long paths perfectly
            )
            fetch_btn = gr.Button("🔍 Fetch Info", variant="secondary", scale=1)
            
    with gr.Group():
        with gr.Row():
            asset_type = gr.Dropdown(
                choices=["auto", "checkpoints", "loras", "vae", "embeddings", "hypernetworks"],
                value="auto",
                label="📁 Asset Type",
                scale=1  # Symmetrical 1/3 split
            )
            filename = gr.Textbox(
                label="💾 Save As (Filename)", 
                placeholder="model.safetensors",
                scale=1  # Symmetrical 1/3 split
            )

            api_key = gr.Textbox(
                label="🔑 API Key (Optional)", 
                type="password",
                placeholder="Paste token if model is private...",
                scale=1  # Symmetrical 1/3 split
            )
            
    with gr.Row():
        download_btn = gr.Button("Start Download", variant="primary", size="md", scale=2)

    with gr.Row():
        status_output = gr.Textbox(
            label="📢 Status", 
            value="Ready",
            min_width=100,
            interactive=False, 
            scale=4
        )

    # Returns exactly the structured layout dict expected by factory patterns
    return {
        "inputs": [source, url, filename, api_key, asset_type],
        "button": download_btn,
        "output": status_output,
        "fetch_button": fetch_btn,
        "url_input": url,
        "source_input": source,
        "api_key_input": api_key,
        "filename_output": filename,
        "asset_type_output": asset_type
    }

# src\lowmo\features\downloader\ui.py

import gradio as gr

def create_downloader_ui():
    with gr.Tabs():
        with gr.Tab("Quick Models"):
            create_quick_downloader_ui()
            
        with gr.Tab("URL Download"):
            components = create_adv_downloader_ui()

        

    return components

def create_adv_downloader_ui():
    gr.Markdown("## 📥 Model Downloader")

    with gr.Group():
        with gr.Row():
            url = gr.Textbox(
                max_lines=1,
                label="🔗 Model URL", 
                placeholder="Paste HuggingFace or Civitai URL here..."
            )     
        with gr.Row():
            fetch_btn = gr.Button("🔍 Fetch Info", variant="secondary", size="sm")

    with gr.Group():
        with gr.Row():
            asset_type = gr.Dropdown(
                choices=["auto", "checkpoints", "loras", "vae", "embeddings", "hypernetworks"],
                value="auto",
                label="📁 Asset Type",
                scale=1
            )
            filename = gr.Textbox(
                max_lines=1,
                label="💾 Save As (Filename)", 
                placeholder="model.safetensors",
                scale=1
            )
            api_key = gr.Textbox(
                label="🔑 API Key (Optional)", 
                type="password",
                placeholder="Paste token if model is private...",
                scale=1
            )

    with gr.Row():
        download_btn = gr.Button("Start Download", variant="primary", size="lg")

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
        "inputs": [url, filename, api_key, asset_type],
        "button": download_btn,
        "output": status_output,
        "fetch_button": fetch_btn,
        "url_input": url,
        "api_key_input": api_key,
        "filename_output": filename,
        "asset_type_output": asset_type
    }

# Work is on...
def create_quick_downloader_ui():
    gr.Markdown("## ⚡ Quick Models")

    # Theme
    theme = gr.Dropdown(
        choices=[
            "General",
            "Photorealistic",
            "Toons & Art"
        ],
        value="General",
        label="🎨 Theme"
    )

    gr.Markdown("### ⭐ Recommended Packages")

    @gr.render(inputs=theme)
    def package_area(selected):

        package = engine.get_package(selected)

        with gr.Row():

            for asset in package.values():

                create_package_card(asset)
            
    

    gr.Markdown("### ➕ Recommended Add-ons")

    @gr.render(inputs=theme)
    def addon_area(selected):

        addons = engine.get_addons(selected)

        for addon in addons:

            create_addon_card(addon)

    with gr.Row():
        download_btn = gr.Button("Start Download", variant="primary", size="lg")

    with gr.Row():
        status_output = gr.Textbox(
            label="📢 Status", value="Ready", min_width=100, interactive=False, scale=4
        )

    return {
        "theme": theme,
        "packages": package_cards,
        "addons": addon_cards,
        "status": status_output,
    }

# src\lowmo\features\downloader\events.py

import gradio as gr
from .service import download_model, fetch_model_info

def bind_events(components):
    """
    Connects the UI components to the service logic.
    """
    # ==========================================
    # 1. EXTRACT ALL REQUIRED COMPONENTS FIRST
    # ==========================================
    button = components["button"]
    inputs = components["inputs"]  # [url, filename, api_key, asset_type]
    output = components["output"]

    fetch_btn = components["fetch_button"]
    url_input = components["url_input"]
    api_key_input = components["api_key_input"]
    filename_output = components["filename_output"]
    asset_type_output = components["asset_type_output"]

    # ==========================================
    # 2. DEFINE EVENT HANDLERS
    # ==========================================
    
    # --- Download Handler ---
    def on_download_click(url, filename, api_key, asset_type, progress=gr.Progress()):
        try:
            yield "Status: Initiating download..."
            # Source dropdown was removed; route dynamically via source="auto"
            result_path = download_model(
                source="auto",
                url=url,
                filename=filename,
                api_key=api_key,
                asset_type=asset_type,
                progress=progress
            )
            yield f"✅ Success! Saved to: {result_path}"
        except Exception as e:
            yield f"❌ Error: {str(e)}"

    # --- Fetch Metadata Handler ---
    def on_fetch_click(url, api_key):
        try:
            if not url:
                return gr.update(), gr.update(), "❌ Error: Please enter a model URL first."
            
            # Dynamically look up model metadata using auto-detection
            info = fetch_model_info(source="auto", url=url, api_key=api_key)
            fetched_filename = info.get("filename", "model.safetensors")
            fetched_asset_type = info.get("asset_type", "checkpoints")
            fetched_source = info.get("source", "unknown")  # For user-friendly display
            
            return (
                gr.update(value=fetched_filename),
                gr.update(value=fetched_asset_type),
                f"✅ Metadata fetched successfully from {fetched_source.title()}!"
            )
        except Exception as e:
            return (
                gr.update(),
                gr.update(),
                f"❌ Error fetching metadata: {str(e)}"
            )

    # ==========================================
    # 3. WIRE UP CLICK EVENTS (Safe from Unbound Errors)
    # ==========================================
    button.click(
        fn=on_download_click,
        inputs=inputs,
        outputs=output
    )

    fetch_btn.click(
        fn=on_fetch_click,
        inputs=[url_input, api_key_input],
        outputs=[filename_output, asset_type_output, output]
    )
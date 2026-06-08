import gradio as gr
from .service import download_model, fetch_model_info

def bind_events(components):
    """
    Connects the UI components to the service logic.
    """
    button = components["button"]
    inputs = components["inputs"]  # [source, url, filename, api_key, asset_type]
    output = components["output"]

    # Progress callback is passed down to the service layer, which can invoke it to update the UI in real-time during the download process.
    def on_download_click(source, url, filename, api_key, asset_type, progress=gr.Progress()):
        try:
            # Update status immediately
            yield "Status: Initiating download..."
            
            # Call the service layer (this is where the core logic is triggered)
            # We pass 'progress' directly to the service
            result_path = download_model(
                source=source,
                url=url,
                filename=filename,
                api_key=api_key,
                asset_type=asset_type,
                progress=progress
            )
            
            yield f"✅ Success! Saved to: {result_path}"
            
        except Exception as e:
            yield f"❌ Error: {str(e)}"

    # Bind the function to the button click
    button.click(
        fn=on_download_click,
        inputs=inputs,
        outputs=output
    )

    # Bind the Fetch Info button click event
    fetch_btn = components["fetch_button"]
    url_input = components["url_input"]
    source_input = components["source_input"]
    api_key_input = components["api_key_input"]
    filename_output = components["filename_output"]
    asset_type_output = components["asset_type_output"]

    def on_fetch_click(source, url, api_key):
        try:
            if not url:
                return gr.update(), gr.update(), "❌ Error: Please enter a model URL first."
            
            # Retrieve metadata dynamically using the service layer
            info = fetch_model_info(source=source, url=url, api_key=api_key)
            fetched_filename = info.get("filename", "model.safetensors")
            fetched_asset_type = info.get("asset_type", "checkpoints")
            
            return (
                gr.update(value=fetched_filename), 
                gr.update(value=fetched_asset_type), 
                "✅ Metadata fetched successfully!"
            )
        except Exception as e:
            return (
                gr.update(), 
                gr.update(), 
                f"❌ Error fetching metadata: {str(e)}"
            )

    fetch_btn.click(
        fn=on_fetch_click,
        inputs=[source_input, url_input, api_key_input],
        outputs=[filename_output, asset_type_output, output]
    )
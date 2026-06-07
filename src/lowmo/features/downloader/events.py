import gradio as gr
from .service import download_model

def bind_events(components):
    """
    Connects the UI components to the service logic.
    """
    button = components["button"]
    inputs = components["inputs"]
    output = components["output"]


    # Progress callback is passed down to the service layer, which can invoke it to update the UI in real-time during the download process.
    def on_download_click(source, url, filename, api_key, progress=gr.Progress()):
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
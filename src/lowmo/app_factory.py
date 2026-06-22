
import gradio as gr
from src.lowmo.features.downloader.ui import create_downloader_ui
from src.lowmo.features.downloader.events import bind_events

def build_app():
    with gr.Blocks(title="Image Generation Test Bench", theme = gr.themes.Ocean()) as demo:
        gr.Markdown("# Image Generation Test Bench")

        with gr.Tab("Downloader"):
            # 1. Generate the UI components
            downloader_components = create_downloader_ui()
            
            # 2. Bind the logic (this keeps the events separate from the layout)
            bind_events(downloader_components)


        with gr.Tab("Model Loader"):
            gr.Markdown("Coming Soon")

        with gr.Tab("Image Generation"):
            gr.Markdown("Coming Soon")

        with gr.Tab("Benchmark"):
            gr.Markdown("Coming Soon")

        with gr.Tab("System Monitor"):
            gr.Markdown("Coming Soon")

    return demo
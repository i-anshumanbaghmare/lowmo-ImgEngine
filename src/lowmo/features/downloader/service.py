from pathlib import Path
from src.lowmo.core.downloader.url_logic import sanitize_url, detect_source
from src.lowmo.core.downloader.hf_downloader import download_from_huggingface
from src.lowmo.core.downloader.civitai_downloader import download_from_civitai

MODEL_ROOT = Path("data") # Or imported from src.lowmo.constants 


# This is the core service layer for the Downloader feature. It contains the main business logic and orchestration for handling download requests.
def download_model(source: str, url: str, filename: str, api_key: str = None, asset_type: str = "checkpoints", progress=None) -> str:
    """
    Core orchestrator method that acts as the entrypoint for Feature execution.
    Accepts raw inputs and delegates tasks downwards.
    """
    if not filename:
        raise ValueError("Filename required for downloads")

    # Resolve destination filesystem directory structures safely
    save_dir = MODEL_ROOT / asset_type 
    save_dir.mkdir(parents=True, exist_ok=True)

    # Clean raw string inputs
    clean_url = sanitize_url(url)
    
    # Dynamically detect source type if the UI selection is ambiguous or set to auto
    if not source or source == "auto":
        source = detect_source(clean_url)

    # Route request to source-specific execution pathways in the core downloader module
    if source == "huggingface":
        return download_from_huggingface(clean_url, filename, save_dir, progress_callback=progress)
    
    elif source == "civitai": 
        return download_from_civitai(clean_url, filename, save_dir, api_key, progress_callback=progress)
    
    else:
        raise ValueError(f"Unknown or unsupported source: {source}") 
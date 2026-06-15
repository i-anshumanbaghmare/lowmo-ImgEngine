# src\lowmo\features\downloader\service.py

from pathlib import Path
from src.lowmo.core.downloader.downloader_utils import sanitize_url, detect_source
from src.lowmo.core.downloader.hf_downloader import download_from_huggingface, get_hf_metadata
from src.lowmo.core.downloader.civitai_downloader import download_from_civitai, get_civitai_metadata

MODEL_ROOT = Path("data") # Or imported from src.lowmo.constants 



# This is the core service layer for the Downloader feature. It contains the main business logic and orchestration for handling download requests.
def download_model(source: str = "auto", url: str = "", filename: str = "", api_key: str = None, asset_type: str = "checkpoints", progress=None) -> str:
    """
    Core orchestrator method that acts as the entrypoint for Feature execution.
    Accepts raw inputs and delegates tasks downwards.
    """
    if not url:
        raise ValueError("URL required for downloads")
    if not filename:
        raise ValueError("Filename required for downloads")

    # Clean raw string inputs
    clean_url = sanitize_url(url)
    
    # Dynamically detect source type if the UI selection is ambiguous or set to auto
    if not source or source == "auto":
        source = detect_source(clean_url)

    # Resolve "auto" asset type dynamically if needed
    if asset_type == "auto":
        try:
            info = fetch_model_info(source=source, url=clean_url, api_key=api_key)
            asset_type = info.get("asset_type", "checkpoints")
        except Exception:
            asset_type = "checkpoints"

    # Resolve destination filesystem directory structures safely
    save_dir = MODEL_ROOT / asset_type 
    save_dir.mkdir(parents=True, exist_ok=True)

    # Route request to source-specific execution pathways in the core downloader module
    if source == "huggingface":
        return download_from_huggingface(clean_url, filename, save_dir, progress_callback=progress)
    
    elif source == "civitai": 
        return download_from_civitai(clean_url, filename, save_dir, api_key, progress_callback=progress)
    
    else:
        raise ValueError(f"Unknown or unsupported source: {source}") 




def fetch_model_info(source: str = "auto", url: str = "", api_key: str = None) -> dict:
    """
    Orchestrator to retrieve model metadata (filename, asset_type)
    from source platforms before starting the download.
    """
    if not url:
        raise ValueError("URL required to fetch model info")

    clean_url = sanitize_url(url)
    
    if not source or source == "auto":
        source, source_type = detect_source(clean_url)
        if source == "unknown":
        raise ValueError(f"Unknown or unsupported source: {source}")
     
    info = get_meta(url=clean_url, source=source, source_type=source_type, api_key=api_key)
    

    # Inject the auto-detected source back into the dictionary for UI display tracking
    if isinstance(info, dict):
        info["source"] = source

    return info
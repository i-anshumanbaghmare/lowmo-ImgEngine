# src\lowmo\features\downloader\service.py

from pathlib import Path
from src.lowmo.core.downloader.downloader_utils import sanitize_url, detect_source, get_metadata, reconstruct_url
from src.lowmo.core.downloader.hf_downloader import download_from_huggingface
from src.lowmo.core.downloader.civitai_downloader import download_from_civitai

MODEL_ROOT = Path("data")

def download_model(source: str = "auto", url: str = "", filename: str = "", api_key: str = None, asset_type: str = "checkpoints", progress=None) -> str:
    """Core orchestrator method acting as the main entry point for feature execution workflows."""
    if not url:
        raise ValueError("URL required for downloads")
    if not filename:
        raise ValueError("Filename required for downloads")

    clean_url = sanitize_url(url)
    source_type = None
    
    # Fix: Correctly unpack the tuple instead of assigning the tuple object to source
    if not source or source == "auto":
        source, source_type = detect_source(clean_url)
    else:
        _, source_type = detect_source(clean_url)

    if asset_type == "auto":
        try:
            info = fetch_model_info(source=source, url=clean_url, api_key=api_key)
            asset_type = info.get("asset_type", "checkpoints")
        except Exception:
            asset_type = "checkpoints"

    save_dir = MODEL_ROOT / asset_type 
    save_dir.mkdir(parents=True, exist_ok=True)

    # Pass the canonical download URL downwards to prevent routing ambient link pages to stream handles
    final_download_url = reconstruct_url(clean_url, source, source_type)

    if source == "huggingface":
        return download_from_huggingface(final_download_url, filename, save_dir, progress_callback=progress)
    elif source == "civitai": 
        return download_from_civitai(final_download_url, filename, save_dir, api_key, progress_callback=progress)
    else:
        raise ValueError(f"Unknown or unsupported source: {source}") 



def fetch_model_info(source: str = "auto", url: str = "", api_key: str = None) -> dict:
    """Retrieves standard model metadata (filename, asset_type) from target host infrastructures."""
    if not url:
        raise ValueError("URL required to fetch model info")

    clean_url = sanitize_url(url)
    
    if not source or source == "auto":
        source, source_type = detect_source(clean_url)
    else:
        _, source_type = detect_source(clean_url)


    if source == "unknown":
        raise ValueError(f"Unknown or unsupported source: {source}")
     
    
    info = get_metadata(url=clean_url, source=source, source_type=source_type, api_key=api_key)

    if isinstance(info, dict):
        info["source"] = source
    return info
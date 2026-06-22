import os
import re
from pathlib import Path
from .fetcher import stream_bytes, fetch_json
from .downloader_utils import reconstruct_civitai_url

def civit_header(api_key: str = None) -> dict:
    final_key = api_key or os.environ.get("CIVITAI_API_KEY")
    headers = {"User-Agent": "lowmo-imgeng/1.0"}
    if final_key:
        headers["Authorization"] = f"Bearer {final_key}"
    return headers

def download_from_civitai(url: str, filename: str, save_dir: Path, api_key: str = None, progress_callback=None) -> str:
    save_path = save_dir / filename
    headers = civit_header(api_key)
    return stream_bytes(url, headers, save_path, filename, progress_callback)

def parse_metadata_from_versionid(url_or_json, api_key: str = None) -> dict:
    """Extracts structured model metadata from a version API URL string or dictionary payload."""
    headers = civit_header(api_key)
    if isinstance(url_or_json, str):
        version_data = fetch_json(url_or_json, headers=headers)
    else:
        version_data = url_or_json

    # 1. Determine filename
    files = version_data.get("files", [])
    filename = "model.safetensors"
    if files:
        primary_file = next((f for f in files if f.get("primary")), files[0])
        filename = primary_file.get("name", filename)

    # 2. Determine asset_type mapping
    model_info = version_data.get("model", {})
    civitai_type = model_info.get("type", "").lower()
    
    asset_type = "checkpoints"
    if "checkpoint" in civitai_type:
        asset_type = "checkpoints"
    elif "lora" in civitai_type or "locon" in civitai_type:
        asset_type = "loras"
    elif "vae" in civitai_type:
        asset_type = "vae"
    elif "textualinversion" in civitai_type or "embedding" in civitai_type:
        asset_type = "embeddings"
    elif "hypernetwork" in civitai_type:
        asset_type = "hypernetworks"

    return {
        "filename": filename,
        "asset_type": asset_type
    }

def get_civitai_metadata(url: str, source_type: str, api_key: str = None) -> dict:
    """Resolves any variant of Civitai input and extracts standardized metadata parameters."""
    version_api_url = reconstruct_civitai_url(url, source_type)
    return parse_metadata_from_versionid(version_api_url, api_key=api_key)
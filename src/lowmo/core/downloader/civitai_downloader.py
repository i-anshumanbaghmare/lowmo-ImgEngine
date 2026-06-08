import os
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from .fetcher import stream_bytes, fetch_json

def download_from_civitai(url: str, filename: str, save_dir: Path, api_key: str = None, progress_callback=None) -> str:
    save_path = save_dir / filename
    
    # Resolve authorization token priority rules
    final_key = api_key or os.environ.get("CIVITAI_API_KEY") or "b32e904e5113676741e9f622c1fc6bbc"
    headers = {
        "Authorization": f"Bearer {final_key}",
        "User-Agent": "lowmo-imgeng/1.0"
    }
    
    return stream_bytes(url, headers, save_path, filename, progress_callback)


def get_civitai_metadata(url: str, api_key: str = None) -> dict:
    """
    Parses Civitai URL, queries Civitai API for model/version metadata,
    and returns a standardized dictionary with filename and asset_type.
    """
    final_key = api_key or os.environ.get("CIVITAI_API_KEY") or "b32e904e5113676741e9f622c1fc6bbc"
    headers = {
        "Authorization": f"Bearer {final_key}",
        "User-Agent": "lowmo-imgeng/1.0"
    }

    # Extract version ID or model ID
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    version_id = None
    if "modelVersionId" in query_params:
        version_id = query_params["modelVersionId"][0]
        
    if not version_id:
        # Check for /api/download/models/{id}
        api_match = re.search(r"/api/download/models/(\d+)", url)
        if api_match:
            version_id = api_match.group(1)
            
    if not version_id:
        # Check for /models/{id}
        model_match = re.search(r"/models/(\d+)", url)
        if model_match:
            model_id = model_match.group(1)
            # Query model endpoint to get model versions
            model_api_url = f"https://civitai.com/api/v1/models/{model_id}"
            model_data = fetch_json(model_api_url, headers=headers)
            versions = model_data.get("modelVersions", [])
            if versions:
                version_id = versions[0].get("id")
                
    if not version_id:
        raise ValueError("Could not extract a model version ID or model ID from the Civitai URL.")

    # Fetch model version metadata
    version_api_url = f"https://civitai.com/api/v1/model-versions/{version_id}"
    version_data = fetch_json(version_api_url, headers=headers)

    # 1. Determine filename
    files = version_data.get("files", [])
    filename = "model.safetensors"
    if files:
        # Find primary file if exists, otherwise first file
        primary_file = next((f for f in files if f.get("primary")), files[0])
        filename = primary_file.get("name", filename)

    # 2. Determine asset_type
    model_info = version_data.get("model", {})
    civitai_type = model_info.get("type", "").lower()
    
    # Map Civitai type to our dropdown selection:
    # Choices: ["checkpoints", "loras", "vae", "embeddings", "hypernetworks"]
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
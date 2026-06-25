# src/lowmo/core/downloader/civitai_downloader.py

import os
import re
from pathlib import Path
from lowmo.core.downloader.fetcher import stream_bytes, fetch_json

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

def reconstruct_civitai_url(url: str, source_type: str, api_key: str = None) -> str:
    """Converts any Civitai input variant into its canonical model-version API endpoint."""
    
    BASE_API_URL = "https://civitai.com/api/v1"

    headers = civit_header(api_key=api_key)

    if source_type == "air_code":
        if "@" in url:
            version_part = url.split("@")[1]
            version_id = re.split(r"[+\.]", version_part)[0]
            return f"{BASE_API_URL}/model-versions/{version_id}"

    elif source_type == "hash_code":  # 2. Handle Standalone Cryptographic Hashes
        hash_api_url = f"https://civitai.com/api/v1/model-versions/by-hash/{url}"
        version_json = fetch_json(hash_api_url, None)
        if "id" in version_json:
            return f"{BASE_API_URL}/model-versions/{version_json['id']}"
        raise ValueError(
            f"Could not resolve version metadata using hash identifier: {url}"
        )

    elif (
        source_type == "numeric_id"
    ):  # 3. Handle Pure Numeric Inputs (Fallback to Model Version target)
        return f"{BASE_API_URL}/model-versions/{url}"

    elif (
        source_type == "api_download"
    ):  # 4. Extract Version ID from Direct Download Links
        match = re.search(r"/api/download/models/(\d+)", url, re.IGNORECASE)
        if match:
            return f"{BASE_API_URL}/model-versions/{match.group(1)}"

    elif (
        source_type == "version_query"
    ):  # 5. Extract Version ID from Browser Query Parameters
        match = re.search(r"modelversionid=(\d+)", url, re.IGNORECASE)
        if match:
            return f"{BASE_API_URL}/model-versions/{match.group(1)}"

    elif source_type == "model_page":  # 6. Extract Model ID from Model Landing Pages
        match = re.search(r"/models/(\d+)", url, re.IGNORECASE)
        if match:
            model_api_url = f"{BASE_API_URL}/models/{match.group(1)}"
            model_json = fetch_json(model_api_url, headers=headers)
            version_id = model_json.get("modelVersions", [{}])[0].get("id")
            if version_id:
                return f"{BASE_API_URL}/model-versions/{version_id}"
        raise ValueError(
            f"Could not resolve version metadata from model page URL: {url}"
        )

    elif source_type in [
        "api_version_url",
        "generic_url",
        "api_hash_url",
    ]:  # 7. Already Optimized API Formats or Fallbacks
        if url.startswith("/"):
            return f"https://civitai.com{url}"
        return url

    return url

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
    # UPDATED: Flows api_key down into the url reconstruction step to facilitate secure backend metadata lookups
    version_api_url = reconstruct_civitai_url(url, source_type, api_key=api_key)
    return parse_metadata_from_versionid(version_api_url, api_key=api_key)
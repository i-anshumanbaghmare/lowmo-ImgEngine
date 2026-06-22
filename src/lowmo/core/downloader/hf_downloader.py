import os
from pathlib import Path
from urllib.parse import urlparse
from downloader_utils import reconstruct_hf_url
from fetcher import stream_bytes, fetch_json

def download_from_huggingface(url: str, filename: str, save_dir: Path, progress_callback=None) -> str:
    # 1. Apply URL reconstruction logic
    final_url = reconstruct_hf_url(url)
    save_path = save_dir / filename
    
    # 2. Establish specific Auth headers
    headers = {"User-Agent": "lowmo-imgeng/1.0"}
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"
        
    # 3. Call core streaming execution
    return stream_bytes(final_url, headers, save_path, filename, progress_callback)


def get_hf_metadata(url: str) -> dict:
    """
    Parses HuggingFace URL, optionally queries HF API,
    and returns a standardized dictionary with filename and asset_type.
    """
    # 1. Normalize URL
    normalized_url = reconstruct_hf_url(url)
    
    # 2. Extract filename
    parsed = urlparse(normalized_url)
    path_parts = [p for p in parsed.path.split('/') if p]
    
    filename = "model.safetensors"
    if path_parts:
        filename = path_parts[-1]
        
    # 3. Determine asset type
    url_lower = normalized_url.lower()
    asset_type = "checkpoints"
    
    if "lora" in url_lower:
        asset_type = "loras"
    elif "vae" in url_lower:
        asset_type = "vae"
    elif "embedding" in url_lower or "textual_inversion" in url_lower:
        asset_type = "embeddings"
    elif "hypernetwork" in url_lower:
        asset_type = "hypernetworks"
    else:
        # If no keywords in URL, try querying HF API using repo ID
        # Repo ID is typically the first two segments of the path (username/repo)
        if len(path_parts) >= 2:
            repo_id = f"{path_parts[0]}/{path_parts[1]}"
            api_url = f"https://huggingface.co/api/models/{repo_id}"
            
            headers = {"User-Agent": "lowmo-imgeng/1.0"}
            hf_token = os.environ.get("HF_TOKEN")
            if hf_token:
                headers["Authorization"] = f"Bearer {hf_token}"
                
            try:
                model_data = fetch_json(api_url, headers=headers)
                tags = [t.lower() for t in model_data.get("tags", [])]
                
                if "lora" in tags:
                    asset_type = "loras"
                elif "vae" in tags:
                    asset_type = "vae"
                elif "textual-inversion" in tags:
                    asset_type = "embeddings"
            except Exception:
                # Ignore API errors and keep fallback asset_type
                pass
                
    return {
        "filename": filename,
        "asset_type": asset_type
    }
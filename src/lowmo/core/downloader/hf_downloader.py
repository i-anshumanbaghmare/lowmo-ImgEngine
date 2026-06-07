import os
from pathlib import Path
from .url_logic import reconstruct_hf_url
from .fetcher import stream_bytes

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
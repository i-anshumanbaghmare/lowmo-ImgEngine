import os
from pathlib import Path
from .fetcher import stream_bytes

def download_from_civitai(url: str, filename: str, save_dir: Path, api_key: str = None, progress_callback=None) -> str:
    save_path = save_dir / filename
    
    # Resolve authorization token priority rules
    final_key = api_key or os.environ.get("CIVITAI_API_KEY") or "b32e904e5113676741e9f622c1fc6bbc"
    headers = {
        "Authorization": f"Bearer {final_key}",
        "User-Agent": "lowmo-imgeng/1.0"
    }
    
    return stream_bytes(url, headers, save_path, filename, progress_callback)
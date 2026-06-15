# src\lowmo\core\downloader\fetcher.py

import requests
from pathlib import Path


# Core network streaming logic for downloading files. This is a low-level utility that can be used by various source-specific downloaders in core/downloader.
def stream_bytes(url: str, headers: dict, save_path: Path, filename: str, progress_callback=None) -> str:
    """Pure network streaming implementation. Reports status back to UI layer."""
    if save_path.exists():
        return str(save_path)

    try:
        # Note: We set allow_redirects=True to handle cases where the initial URL might redirect to a signed URL or mirror. This is common with platforms like Hugging Face.
        response = requests.get(url, headers=headers, stream=True, allow_redirects=True)
        
        content_type = response.headers.get('Content-Type', '')

        # Security Check: Block HTML pages, so only actual file content is accepted. This can help catch auth failures or gated content that returns an HTML page instead of the expected model file.
        if "text/html" in content_type:
            debug_path = save_path.with_suffix(".html")
            with open(debug_path, "w", encoding="utf-8") as df:
                df.write(response.text)
            raise RuntimeError(f"Auth failed or gated content. Received HTML instead of a model file. Saved debug log to {debug_path}")

        # Stream the content in chunks and write to disk, while updating progress.
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1048576): # 1MB blocks
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0 and progress_callback is not None:
                        # This invocation matches Gradio's Progress(progress_ratio, desc) call signature
                        progress_callback(downloaded / total_size, desc=f"Downloading {filename}")

        return str(save_path)

    except requests.exceptions.RequestException as e:
        if save_path.exists():
            save_path.unlink() # Drop incomplete files
        raise RuntimeError(f"Download stream broken: {e}")


def fetch_json(url: str, headers: dict = None) -> dict:
    """Helper to perform standard GET request and return parsed JSON."""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to retrieve metadata: {e}")


def get_metadata
    """
    Centralized metadata retrieval orchestrator that routes to source-specific logic based on detected source type.
    This abstracts away the complexities of different URL formats and API requirements for each platform.
    """
    if source == "huggingface":
        return get_hf_metadata(url)
    
    elif source == "civitai":
        return get_civitai_metadata(url, api_key=api_key)
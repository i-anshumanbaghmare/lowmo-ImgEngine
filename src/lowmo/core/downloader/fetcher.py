import requests
from pathlib import Path

def stream_bytes(url: str, headers: dict, save_path: Path, filename: str, progress_callback=None) -> str:
    """Pure network streaming implementation. Reports status back to UI layer."""
    if save_path.exists():
        return str(save_path)

    try:
        response = requests.get(url, headers=headers, stream=True, allow_redirects=True)
        content_type = response.headers.get('Content-Type', '')

        # Security Check: Block HTML pages
        if "text/html" in content_type:
            debug_path = save_path.with_suffix(".html")
            with open(debug_path, "w", encoding="utf-8") as df:
                df.write(response.text)
            raise RuntimeError(f"Auth failed or gated content. Received HTML instead of a model file. Saved debug log to {debug_path}")

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
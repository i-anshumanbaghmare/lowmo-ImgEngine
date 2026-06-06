import os
import requests
from pathlib import Path
from urllib.parse import urlparse

MODEL_ROOT = Path("./models")

def download_model(
    source,
    url,
    filename=None,
    api_key=None,
    asset_type="checkpoints",
    progress=None,
    verbose=False):

  if not filename:
    raise ValueError("Filename required for downloads")

  if source == "huggingface":
    return download_from_huggingface(
      model_url=url,
      filename=filename,
      asset_type=asset_type,
      progress=progress,
      verbose=verbose
    )

  elif source == "civitai":
    return download_from_civitai(
      download_url=url,
      filename=filename,
      api_key=api_key,
      asset_type=asset_type,
      progress=progress,
      verbose=verbose
    )

  else:
    raise ValueError(f"Unknown source: {source}")


# ==========================================
# SHARED DOWNLOAD ENGINE
# ==========================================
def _stream_download(url, headers, save_path, filename, progress=None, verbose=False):
  """Core downloading logic shared across all sources."""

  if save_path.exists():
    if verbose: print(f"[INFO] File already exists: {save_path}")
    return str(save_path)

  try:
    # 1. Initiate network request
    response = requests.get(url, headers=headers, stream=True, allow_redirects=True)
    content_type = response.headers.get('Content-Type', '')

    # 2. Security Check: Block HTML login/error pages
    if "text/html" in content_type:
      debug_path = save_path.with_suffix(".html")
      with open(debug_path, "w", encoding="utf-8") as df:
        df.write(response.text)
      raise RuntimeError(f"Auth failed or file gated. Received HTML page instead of model. Saved to {debug_path}")

    response.raise_for_status()

    # 3. Setup Progress Tracking
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    last_reported_percent = -1.0

    if verbose:
      total_gb = total_size / (1024**3) if total_size > 0 else 0
      print(f"[INFO] Starting download for {filename} ({total_gb:.2f} GB)...")

    # 4. Stream and Write
    with open(save_path, "wb") as f:
      for chunk in response.iter_content(chunk_size=1048576):
        if chunk:
          f.write(chunk)
          downloaded += len(chunk)

          if total_size > 0:
            # External UI Progress
            if progress is not None:
              progress(downloaded / total_size, desc=f"Downloading {filename}")

            # Terminal UI Progress
            elif verbose:
              percent = (downloaded / total_size) * 100
              if percent - last_reported_percent >= 1.0 or downloaded == total_size:
                last_reported_percent = percent
                downloaded_gb = downloaded / (1024**3)
                bar = '█' * int(20 * downloaded // total_size) + '-' * (20 - int(20 * downloaded // total_size))
                print(f"\r[INFO] Progress: |{bar}| {percent:.1f}% ({downloaded_gb:.2f}/{total_gb:.2f} GB)", end="", flush=True)

    if verbose and total_size > 0:
      print(f"\n[INFO] Successfully saved: {save_path}")

    return str(save_path)

  except requests.exceptions.RequestException as e:
    if verbose: print() # Clean line break on error
    raise RuntimeError(f"Download failed: {e}")


# ==========================================
# SOURCE-SPECIFIC PREP FUNCTIONS
# ==========================================
def download_from_huggingface(model_url: str, filename: str, asset_type: str = "checkpoints", progress=None, verbose=False):
    # Parse URL structure specific to HuggingFace
    parts = urlparse(model_url).path.strip("/").split("/")
    if len(parts) < 5:
        raise ValueError("Invalid HuggingFace URL– expected /repo/resolve/revision/filename")

    save_dir = MODEL_ROOT / asset_type
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / filename

    headers = {"User-Agent": "Mozilla/5.0"}

    # Hand off to the shared engine
    return _stream_download(
        url=model_url,
        headers=headers,
        save_path=save_path,
        filename=filename,
        progress=progress,
        verbose=verbose
    )


def download_from_civitai(download_url, filename, api_key=None, asset_type="checkpoints", progress=None, verbose=False):
    save_dir = MODEL_ROOT / asset_type
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / filename

    # Parse Auth setup specific to Civitai
    final_key = api_key or os.environ.get("CIVITAI_API_KEY") or "b32e904e5113676741e9f622c1fc6bbc"
    headers = {
        "Authorization": f"Bearer {final_key}",
        "User-Agent": "Mozilla/5.0"
    }

    # Hand off to the shared engine
    return _stream_download(
        url=download_url,
        headers=headers,
        save_path=save_path,
        filename=filename,
        progress=progress,
        verbose=verbose
    )
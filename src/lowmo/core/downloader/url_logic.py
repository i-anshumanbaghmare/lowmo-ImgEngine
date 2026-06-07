from urllib.parse import urlparse

def detect_source(url: str) -> str:
    """Safely looks at domain indicators to categorize the platform."""
    url_lower = url.lower()
    if "huggingface.co" in url_lower:
        return "huggingface"
    elif "civitai.com" in url_lower:
        return "civitai"
    return "unknown"

def reconstruct_hf_url(url: str) -> str:
    """Converts user-facing browser view URLs into direct binary resolve endpoints."""
    if "/blob/" in url:
        return url.replace("/blob/", "/resolve/")
    return url
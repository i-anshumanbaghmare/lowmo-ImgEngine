from urllib.parse import urlparse

def sanitize_url(url: str) -> str:
    """Cleans and normalizes URL input by stripping whitespace and extra characters."""
    if not url:
        return ""
    # Remove common copy-paste artifacts: quotes, parentheses, angle brackets
    url = url.strip()
    # Remove leading/trailing quotes (single and double)
    url = url.strip('\'"')
    # Remove leading/trailing parentheses and angle brackets
    url = url.strip('()[]<>')
    # Remove any remaining whitespace
    url = url.strip()
    return url

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
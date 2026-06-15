# src\lowmo\core\downloader\downloader_utils.py

from urllib.parse import urlparse
import re


def sanitize_url(url: str) -> str:
    """Cleans and normalizes URL input by stripping whitespace and extra copy-paste wrappers."""
    if not url:
        return ""
    url = url.strip().strip('\'"').strip('()[]<>').strip()
    return url


def detect_source(url: str) -> tuple[str, str]:  
    """
    Safely inspects domain structures and structural indicators to categorize 
    both the host platform and the exact notation variant of the input string.
    
    Returns:
        tuple: (source, source_type)
        Possible sources: "civitai", "huggingface", "unknown"
        Possible Civitai types: "air_code", "hash_code", "numeric_id", 
                                "api_download", "api_version_url", "api_hash_url", 
                                "version_query", "model_page", "generic_url"
    """
    cleaned = sanitize_url(url)  
    url_lower = cleaned.lower()

    if "huggingface.co" in url_lower:
        return "huggingface", "url"

    if url_lower.startswith("urn:air:") or "@" in url_lower :
        return "civitai", "air_code"
    
    if (re.match(r"^[a-fA-F0-9]{8}$", cleaned) or           # For AutoV1
        re.match(r"^[a-fA-F0-9]{64}$", cleaned) or          # for AutoV2
        url_lower.startswith("civitai:hash:")):
        return "civitai", "hash_code"

    if cleaned.isdigit():
        return "civitai", "numeric_id"

    # Contextual browser/API URL pattern tracking
    if "civitai.com" in url_lower or url_lower.startswith("/") or "models/" in url_lower:
        if "/api/download/models/" in url_lower:
            return "civitai", "api_download"
        if "/api/v1/model-versions/by-hash/" in url_lower:
            return "civitai", "api_hash_url"
        if "/api/v1/model-versions/" in url_lower:
            return "civitai", "api_version_url"
        if "modelversionid=" in url_lower:
            return "civitai", "version_query"
        if "/models/" in url_lower:
            return "civitai", "model_page"
        
        return "civitai", "generic_url"

    return "unknown", "unknown"

def get_metadata(url: str, source: str, source_type: str, api_key: str = None) -> dict:
    """
    Orchestrator to retrieve model metadata (filename, asset_type)
    from source platforms before starting the download.
    """
    if not url:
        raise ValueError("URL required to fetch model info")
    
        
    if source == "huggingface":
        info = get_hf_metadata(url)
    elif source == "civitai":
        info = get_civitai_metadata(url=url, source_type=source_type, api_key=api_key)
    else:
        raise ValueError(f"Unknown or unsupported source: {source}")

    # Inject the auto-detected source back into the dictionary for UI display tracking
    if isinstance(info, dict):
        info["source"] = source

    return info

def reconstruct_civitai_url(url: str, source_type: str) -> str:
    """
    Converts any Civitai input variant into its most optimal API endpoint 
    for pulling structured metadata and managing downstream downloads.
    """
    cleaned = sanitize_url(url)
    BASE_API_URL = "https://civitai.com/api/v1"

    # 1. Handle Canonical AIR Codes
    if source_type == "air_code":
        # Format: urn:air:{ecosystem}:{type}:{source}:{modelid}[@{versionid}]
        if "@" in url:
            # Extract explicitly defined version ID before subsequent properties (+ or .)
            version_part = cleaned.split("@")[1]
            version_id = re.split(r'[+\.]', version_part)[0]
            return f"{BASE_API_URL}/model-versions/{version_id}"

    # 2. Handle Standalone Cryptographic Hashes
    elif source_type == "hash_code":
        hash_api_url = f"https://civitai.com/api/v1/model-versions/by-hash/{url}"
        version_json = fetch_json(cleaned, hash)
        if "id" in version_json:
            return f"{BASE_API_URL}/model-versions/{version_json['id']}"
        raise ValueError(f"Could not resolve version metadata using hash identifier: {url}")

    # 3. Handle Pure Numeric Inputs (Fallback to Model Version target)
    elif source_type == "numeric_id":
        return f"{BASE_API_URL}/model-versions/{cleaned}"

    # 4. Extract Version ID from Direct Download Links
    elif source_type == "api_download":
        match = re.search(r"/api/download/models/(\d+)", cleaned, re.IGNORECASE)
        if match:
            return f"{BASE_API_URL}/model-versions/{match.group(1)}"

    # 5. Extract Version ID from Browser Query Parameters
    elif source_type == "version_query":
        match = re.search(r"modelversionid=(\d+)", cleaned, re.IGNORECASE)
        if match:
            return f"{BASE_API_URL}/model-versions/{match.group(1)}"

    # 6. Extract Model ID from Model Landing Pages
    elif source_type == "model_page":
        match = re.search(r"/models/(\d+)", cleaned, re.IGNORECASE)
        version_id = fetch_json(match.group(1)).get("modelVersions", [{}])[0].get("id")
        if version_id:
            return f"{BASE_API_URL}/model-versions/{version_id}"
        raise ValueError(f"Could not resolve version metadata from model page URL: {url}")

    # 7. Already Optimized API Formats or Fallbacks
    elif source_type in ["api_version_url", "generic_url"]:
        if cleaned.startswith("/"):
            return f"https://civitai.com{cleaned}"
        return cleaned

    return cleaned


def reconstruct_hf_url(url: str) -> str:
    """Converts user-facing browser view URLs into direct binary resolve endpoints."""
    if "/blob/" in url:
        return url.replace("/blob/", "/resolve/")
    return url


def reconstruct_url(url: str, source: str, source_type: str) -> str:
    """
    Central router that coordinates URL reconstruction tasks based on 
    the detected host platform.
    """
    cleaned = sanitize_url(url)
    
    if source == "civitai":
        return reconstruct_civitai_url(cleaned, source_type)
    elif source == "huggingface":
        return reconstruct_hf_url(cleaned)
        
    return cleaned
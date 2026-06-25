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

    if url_lower.startswith("urn:air:") or "@" in url_lower:
        return "civitai", "air_code"
    
    if (re.match(r"^[a-fA-F0-9]{8}$", cleaned) or           # For AutoV1
        re.match(r"^[a-fA-F0-9]{64}$", cleaned) or          # For AutoV2
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
    """Orchestrator to retrieve model metadata from source platforms before starting downloads."""
    if not url:
        raise ValueError("URL required to fetch model info")
    
    # Restructured imports to align with standard project root path configurations
    if source == "huggingface":
        from lowmo.core.downloader.hf_downloader import get_hf_metadata
        info = get_hf_metadata(url)
    elif source == "civitai":
        from lowmo.core.downloader.civitai_downloader import get_civitai_metadata
        info = get_civitai_metadata(url=url, source_type=source_type, api_key=api_key)
    else:
        raise ValueError(f"Unknown or unsupported source: {source}")

    if isinstance(info, dict):
        info["source"] = source
    return info


def reconstruct_url(url: str, source: str, source_type: str, api_key: str = None) -> str:
    """Central router that coordinates URL reconstruction tasks based on detected host platform."""
    cleaned = sanitize_url(url)
    
    if source == "civitai":
        from lowmo.core.downloader.civitai_downloader import reconstruct_civitai_url
        return reconstruct_civitai_url(cleaned, source_type, api_key=api_key)
    elif source == "huggingface":
        from lowmo.core.downloader.hf_downloader import reconstruct_hf_url
        return reconstruct_hf_url(cleaned)
        
    return cleaned
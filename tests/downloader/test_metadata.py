from unittest.mock import patch
import pytest
from lowmo.core.downloader.civitai_downloader import get_civitai_metadata
from lowmo.core.downloader.hf_downloader import get_hf_metadata

def test_get_civitai_metadata_by_version():
    mock_response = {
        "files": [{"name": "test_civitai_model.safetensors", "primary": True}],
        "model": {"type": "LORA"}
    }
    with patch("lowmo.core.downloader.civitai_downloader.fetch_json", return_value=mock_response):
        metadata = get_civitai_metadata("https://civitai.com/api/download/models/123456")
        assert metadata["filename"] == "test_civitai_model.safetensors"
        assert metadata["asset_type"] == "loras"

def test_get_civitai_metadata_by_model():
    mock_model_response = {
        "modelVersions": [{"id": 99999}]
    }
    mock_version_response = {
        "files": [{"name": "checkpoint_model.safetensors"}],
        "model": {"type": "Checkpoint"}
    }
    def mock_fetch_json(url, headers=None):
        if "model-versions" in url:
            return mock_version_response
        return mock_model_response

    with patch("lowmo.core.downloader.civitai_downloader.fetch_json", side_effect=mock_fetch_json):
        metadata = get_civitai_metadata("https://civitai.com/models/55555")
        assert metadata["filename"] == "checkpoint_model.safetensors"
        assert metadata["asset_type"] == "checkpoints"

def test_get_hf_metadata_from_url():
    # Test fallback extraction without API calls
    metadata = get_hf_metadata("https://huggingface.co/username/repo-lora/resolve/main/path/my_model_lora.safetensors")
    assert metadata["filename"] == "my_model_lora.safetensors"
    assert metadata["asset_type"] == "loras"

def test_get_hf_metadata_from_api():
    mock_api_response = {
        "tags": ["lora", "text-to-image"]
    }
    # URL does not contain "lora" directly, so it triggers the API call
    url = "https://huggingface.co/username/repo/resolve/main/my_model.safetensors"
    with patch("lowmo.core.downloader.hf_downloader.fetch_json", return_value=mock_api_response):
        metadata = get_hf_metadata(url)
        assert metadata["filename"] == "my_model.safetensors"
        assert metadata["asset_type"] == "loras"

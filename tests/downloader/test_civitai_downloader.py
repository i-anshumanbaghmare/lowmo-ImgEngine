from unittest.mock import patch

import pytest
import requests

from lowmo.core.downloader.civitai_downloader import download_from_civitai

CIVITAI_URL = "https://civitai.com/api/download/models/2499141"
FILENAME = "mahwa2"


def _probe_stream(url, headers, save_path, filename, progress_callback=None):
    """Validate the download endpoint without writing the full model to disk."""
    response = requests.get(url, headers=headers, stream=True, allow_redirects=True, timeout=60)
    try:
        content_type = response.headers.get("Content-Type", "")
        if "text/html" in content_type:
            pytest.fail("Auth failed: received HTML instead of a model file")
        assert response.status_code == 200, f"Expected HTTP 200, got {response.status_code}"
    finally:
        response.close()
    return str(save_path)


@pytest.mark.integration
def test_civitai_download_url_returns_200(tmp_path):
    with patch("lowmo.core.downloader.civitai_downloader.stream_bytes", _probe_stream):
        result = download_from_civitai(
            url=CIVITAI_URL,
            filename=FILENAME,
            save_dir=tmp_path,
        )

    assert result == str(tmp_path / FILENAME)
    assert not (tmp_path / FILENAME).exists()

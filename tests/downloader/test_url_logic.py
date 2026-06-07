from lowmo.core.downloader.url_logic import detect_source, reconstruct_hf_url

CIVITAI_DOWNLOAD_URL = "https://civitai.com/api/download/models/2499141"


def test_detect_civitai_source():
    assert detect_source(CIVITAI_DOWNLOAD_URL) == "civitai"


def test_detect_huggingface_source():
    url = "https://huggingface.co/user/repo/resolve/main/model.safetensors"
    assert detect_source(url) == "huggingface"


def test_detect_unknown_source():
    assert detect_source("https://example.com/model.bin") == "unknown"


def test_reconstruct_hf_blob_url():
    blob_url = "https://huggingface.co/user/repo/blob/main/model.safetensors"
    expected = "https://huggingface.co/user/repo/resolve/main/model.safetensors"
    assert reconstruct_hf_url(blob_url) == expected

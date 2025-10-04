from transcript_service.pipeline import extract_video_id


def test_extract_standard_watch_url():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert extract_video_id(url) == "dQw4w9WgXcQ"


def test_extract_short_url():
    url = "https://youtu.be/dQw4w9WgXcQ"
    assert extract_video_id(url) == "dQw4w9WgXcQ"


def test_extract_with_query_params():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10"
    assert extract_video_id(url) == "dQw4w9WgXcQ"


def test_extract_from_id():
    assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_extract_invalid_returns_none():
    assert extract_video_id("not-a-url") is None

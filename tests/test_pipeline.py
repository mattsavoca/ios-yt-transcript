import pytest

from youtube_transcript_api import NoTranscriptFound

from transcript_service.pipeline import TranscriptError, TranscriptFetcher, extract_video_id


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


def test_fetch_joins_text_and_uses_preferred_languages():
    calls = {}

    class StubClient:
        def fetch(self, video_id, languages=("en",), preserve_formatting=False):
            calls["args"] = (video_id, languages, preserve_formatting)
            return [{"text": "Hello"}, {"text": "   "}, {"text": "world"}]

    fetcher = TranscriptFetcher(
        preferred_languages=["en", "es"],
        _client_factory=lambda: StubClient(),
    )

    result = fetcher.fetch("https://youtu.be/dQw4w9WgXcQ")

    assert result == "Hello\nworld"
    assert calls["args"] == ("dQw4w9WgXcQ", ("en", "es"), False)


def test_fetch_wraps_transcript_errors():
    class StubClient:
        def fetch(self, *args, **kwargs):
            raise NoTranscriptFound("video", ["en"], [])

    fetcher = TranscriptFetcher(_client_factory=lambda: StubClient())

    with pytest.raises(TranscriptError) as excinfo:
        fetcher.fetch("https://youtu.be/dQw4w9WgXcQ")

    assert str(excinfo.value) == "Transcript is unavailable for this video"

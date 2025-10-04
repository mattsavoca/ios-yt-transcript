"""Tests for the transcript fetching pipeline."""

from __future__ import annotations

import types
import sys

import pytest

from transcript_service.pipeline import TranscriptError, TranscriptFetcher


ERROR_CLASS_NAMES = [
    "TranscriptsDisabled",
    "NoTranscriptFound",
    "TranslationLanguageNotAvailable",
    "VideoUnavailable",
    "VideoUnplayable",
    "CouldNotRetrieveTranscript",
    "YouTubeRequestFailed",
]


def _install_stub_module(
    monkeypatch: pytest.MonkeyPatch,
    *,
    exception_name: str,
    message: str = "boom",
) -> None:
    """Install a minimal ``youtube_transcript_api`` stub that raises a given exception."""

    module = types.ModuleType("youtube_transcript_api")

    class YouTubeTranscriptApiException(Exception):
        """Base class mirroring the real library's exception hierarchy."""

    module.YouTubeTranscriptApiException = YouTubeTranscriptApiException

    for name in ERROR_CLASS_NAMES:
        module.__dict__[name] = type(name, (YouTubeTranscriptApiException,), {})

    if exception_name not in module.__dict__:
        module.__dict__[exception_name] = type(exception_name, (YouTubeTranscriptApiException,), {})

    class DummyApi:
        def __init__(self, *args, **kwargs):  # noqa: D401 - mimic library signature
            pass

        def fetch(self, *args, **kwargs):
            raise module.__dict__[exception_name](message)

    module.YouTubeTranscriptApi = DummyApi

    monkeypatch.setitem(sys.modules, "youtube_transcript_api", module)


@pytest.mark.parametrize(
    "exception, expected_message",
    [
        ("TranscriptsDisabled", "Transcripts are disabled for this video"),
        ("NoTranscriptFound", "Transcript is unavailable for this video"),
        (
            "TranslationLanguageNotAvailable",
            "Transcript is not available in the requested languages",
        ),
        ("VideoUnavailable", "The video is unavailable"),
        ("VideoUnplayable", "The video cannot be played"),
        (
            "CouldNotRetrieveTranscript",
            "Unable to retrieve the transcript from YouTube. Please try again later.",
        ),
        (
            "YouTubeRequestFailed",
            "YouTube returned an error while fetching the transcript",
        ),
    ],
)
def test_fetcher_error_messages(monkeypatch: pytest.MonkeyPatch, exception: str, expected_message: str):
    """Ensure different youtube_transcript_api errors map to helpful messages."""

    _install_stub_module(monkeypatch, exception_name=exception)

    fetcher = TranscriptFetcher()

    with pytest.raises(TranscriptError, match=expected_message):
        fetcher.fetch("https://youtu.be/dQw4w9WgXcQ")


def test_fetcher_unexpected_api_error(monkeypatch: pytest.MonkeyPatch):
    """Fallback to the message provided by the youtube_transcript_api exception."""

    _install_stub_module(monkeypatch, exception_name="CaptchaRequired", message="captcha required")

    fetcher = TranscriptFetcher()

    with pytest.raises(TranscriptError, match="captcha required"):
        fetcher.fetch("https://youtu.be/dQw4w9WgXcQ")

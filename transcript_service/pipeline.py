"""Core pipeline utilities for fetching YouTube transcripts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import parse_qs, urlparse

_YOUTUBE_REGEX = re.compile(
    r"(?:https?://)?(?:www\.|m\.)?(?:youtube\.com|youtu\.be)/(?:watch\?v=)?([\w-]{11})"
)


class TranscriptError(RuntimeError):
    """Raised when the transcript cannot be retrieved."""


@dataclass
class TranscriptFetcher:
    """Fetch a transcript for a given YouTube URL."""

    preferred_languages: Optional[List[str]] = None

    def fetch(self, video_url: str) -> str:
        """Return a transcript without timestamps for the provided video URL.

        Args:
            video_url: The YouTube video URL or video id.

        Returns:
            The transcript text with each caption entry separated by a newline.
        """

        video_id = extract_video_id(video_url)
        if not video_id:
            raise TranscriptError(f"Unable to determine video id from: {video_url}")

        try:
            from youtube_transcript_api import (
                NoTranscriptFound,
                TranscriptsDisabled,
                YouTubeTranscriptApi,
            )
        except ImportError as exc:
            raise TranscriptError('youtube-transcript-api is required to fetch transcripts') from exc

        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=self.preferred_languages
            )
        except (TranscriptsDisabled, NoTranscriptFound) as exc:
            raise TranscriptError("Transcript is unavailable for this video") from exc
        except Exception as exc:  # pragma: no cover - pass through unexpected errors
            raise TranscriptError("Failed to fetch transcript") from exc

        lines = [entry["text"].strip() for entry in transcript if entry["text"].strip()]
        return "\n".join(lines)


def extract_video_id(value: str) -> Optional[str]:
    """Extract the YouTube video id from a URL or return the value if it's already an id."""

    value = value.strip()
    if not value:
        return None

    if len(value) == 11 and re.fullmatch(r"[\w-]{11}", value):
        return value

    parsed = urlparse(value)
    if parsed.query:
        query_params = parse_qs(parsed.query)
        video_id = query_params.get("v", [None])[0]
        if video_id:
            return video_id

    match = _YOUTUBE_REGEX.search(value)
    if match:
        return match.group(1)

    return None

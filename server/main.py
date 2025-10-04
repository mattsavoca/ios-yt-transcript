"""FastAPI server that returns YouTube transcripts for a provided URL."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from transcript_service import TranscriptError, TranscriptFetcher

app = FastAPI(title="YouTube Transcript Service")


class TranscriptRequest(BaseModel):
    url: str
    languages: list[str] | None = None


class TranscriptResponse(BaseModel):
    transcript: str


@app.post("/transcript", response_model=TranscriptResponse)
async def get_transcript(payload: TranscriptRequest) -> TranscriptResponse:
    fetcher = TranscriptFetcher(preferred_languages=payload.languages)
    try:
        transcript_text = fetcher.fetch(payload.url)
    except TranscriptError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return TranscriptResponse(transcript=transcript_text)

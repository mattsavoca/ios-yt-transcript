# iOS YouTube Transcript Toolkit

This repository contains a lightweight Python service and command-line utilities
for turning a YouTube share link into a plain-text transcript. The setup is
intended to be triggered from an iOS Shortcut that shares the transcript back to
your clipboard.

## Features

1. **Transcript pipeline** – Convert a YouTube URL (or video id) into a
   newline-separated transcript without timestamps.
2. **Command-line helper** – Quickly test the transcript retrieval from a
   terminal before wiring it into Shortcuts.
3. **FastAPI server** – A simple endpoint you can self-host on your home
   network. The iOS Shortcut POSTs the shared YouTube URL and receives the
   transcript in response.
4. **Shortcut integration outline** – Step-by-step instructions to glue the
   pieces together on iOS.

## Getting Started

### 1. Install dependencies

This project now uses [uv](https://docs.astral.sh/uv/) for dependency
management. Install uv if you have not already, then sync the environment:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # only needed once per machine
uv sync
```

The command creates a `.venv` managed by uv and installs all runtime and
development dependencies, including the Ruff linter.

### 2. Fetch a transcript from the command line

```bash
uv run python scripts/get_transcript.py "https://youtu.be/dQw4w9WgXcQ"
```

Use `--languages` if you want to prefer specific caption languages, for example
`--languages en en-US`.

### 3. Run the server locally

```bash
uv run uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

> **Suggested network settings:** For a home-network deployment, point your
> iOS Shortcut to `http://192.168.1.50:8000/transcript`. Adjust the IP to match
> the static address of the machine hosting the server; the default port 8000 is
> a good fit unless you already use it for another service.

Send a request to the API:

```bash
curl -X POST \
  http://localhost:8000/transcript \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtu.be/dQw4w9WgXcQ"}'
```

The response includes a JSON payload with the transcript text:

```json
{"transcript": "..."}
```

### 4. Build the iOS Shortcut

1. Create a new Shortcut and add the **Share Sheet** trigger for YouTube.
2. Add a **Get Contents of URL** action:
   - Method: `POST`
   - URL: `http://<your-server-ip>:8000/transcript`
   - Request Body: JSON with a field `url` equal to the Shortcut input.
3. Add a **Get Dictionary Value** action to pull out the `transcript` field.
4. Finish with a **Copy to Clipboard** action.

Now, when you tap **Share → Your Shortcut** in the YouTube app, the transcript
will be fetched by your server and placed on the clipboard automatically.

## Testing

Run the unit tests to verify the URL parsing logic:

```bash
uv run pytest
```

## Linting

Ruff is included as a development dependency. Run it before committing changes:

```bash
uv run ruff check --fix
```

## Notes

- The service uses [`youtube-transcript-api`](https://pypi.org/project/youtube-transcript-api/),
  which works for videos with public transcripts. Private videos or those
  without captions will raise an error.
- To harden the service for public exposure, add authentication and rate
  limiting. For home-network usage triggered from Shortcuts, the current setup
  keeps things simple.

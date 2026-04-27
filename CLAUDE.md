# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Install dependencies:
```
pip install -r requirements.txt
```

Run the development server:
```
uvicorn main:app --reload
```

The app runs at `http://localhost:8000`.

## Environment

Copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY` before running.

## Architecture

This is a single-page cover letter generator. The FastAPI backend (`main.py`) exposes one endpoint (`POST /generate`) that calls the Anthropic API and returns a generated cover letter. Static files (`static/`) are served by FastAPI and handle the entire UI — no build step.

**Key design decisions:**
- The resume is stored as a plain-text constant in `resume.py` (`RESUME`). Edit this file to personalize output. The resume is injected into the system prompt, which uses `cache_control: ephemeral` to cache the large system prompt across requests.
- `cache_hit` in the response indicates whether the Anthropic prompt cache was used (`cache_read_input_tokens > 0`).
- Static files are mounted *after* route definitions in `main.py` — this order matters; reversing it would shadow the `/generate` route.
- Tone is controlled by a fixed map (`TONE_INSTRUCTIONS`) in `main.py`. Valid values: `formal`, `conversational`, `enthusiastic`.

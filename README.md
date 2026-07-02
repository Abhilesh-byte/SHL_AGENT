# SHL Assessment Recommender Agent

FastAPI service with a ready-to-use browser page for recommending SHL assessments from a local catalog. It supports a mock LLM for local development and optional Groq or Gemini API connectivity for real model calls.

## Setup

```powershell
cd C:\Users\singh\Desktop\shl_agent
.\venv\Scripts\Activate.ps1
```

If dependencies are missing:

```powershell
pip install -r requirements.txt
```

## Run The Complete App

```powershell
C:\Users\singh\Desktop\shl_agent\venv\Scripts\python.exe -m uvicorn src.main:app --reload --port 8000
```

Open the working page:

```text
http://127.0.0.1:8000/
```

Swagger API docs are still available:

```text
http://127.0.0.1:8000/docs
```

## LLM Provider

The app defaults to the deterministic mock provider, which needs no API key:

```powershell
$env:LLM_PROVIDER = "mock"
```

For Groq:

```powershell
$env:LLM_PROVIDER = "groq"
$env:GROQ_API_KEY = "your_key_here"
```

For Gemini:

```powershell
$env:LLM_PROVIDER = "gemini"
$env:GEMINI_API_KEY = "your_key_here"
```

## API Endpoints

- `GET /` opens the web app.
- `GET /app` opens the same web app.
- `GET /health` returns `{"status": "ok"}`.
- `GET /catalog` returns the local assessment catalog.
- `POST /chat` accepts OpenAI-style conversation history.
- `POST /recommend` accepts a single query and uses the same agent pipeline.

## Smoke Test

After starting the server:

```powershell
python test_client.py
```

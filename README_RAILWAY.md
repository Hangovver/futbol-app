# Sofascore-like App (Backend + Expo)

This repo contains an Expo frontend under `app/` and a Python FastAPI backend under `backend/`.

## Deploy the backend to Railway (one-click)

1. Connect this repo to a new Railway **Service**.
2. Railway will detect the `Dockerfile` and build only the backend (thanks to `.dockerignore`).
3. After the first deploy, open **Variables** and add:
   - `API_FOOTBALL_KEY` — your API key
   - `TZ` — e.g. `Europe/Istanbul`
   - `MIN_PROB` — e.g. `0.70`
4. Click **Redeploy**. The API will run at the public URL like `https://xxxx.railway.app`.

The server entrypoint is `server:app` (see `backend/server.py`).

## Run locally
```
cd backend
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn server:app --reload
```

# main.py
import os
import uvicorn
from backend.server import app   # server.py dosyan içinde app var

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

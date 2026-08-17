from fastapi import FastAPI
import platform
import time

app = FastAPI(title="Hello World", version="1.0.0")
START_TIME = time.time()


@app.get("/")
def root():
    return {
        "message": "Hello from AI Efficiency Lab!",
        "host": platform.node(),
        "python": platform.python_version(),
        "uptime_sec": int(time.time() - START_TIME),
    }


@app.get("/health")
def health():
    return {"status": "ok", "uptime_sec": int(time.time() - START_TIME)}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import numpy as np

app = FastAPI()

# CORS (Vercel also sets headers, but keep this for safety)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Payload(BaseModel):
    regions: list[str]
    threshold_ms: float

# Correct path for Vercel serverless
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "..", "q-vercel-latency.json")

try:
    with open(file_path, "r") as f:
        data = json.load(f)
except Exception:
    data = []

@app.post("/api")
@app.post("/")
def get_metrics(payload: Payload):
    result = {}

    for region in payload.regions:
        region_data = [d for d in data if d.get("region") == region]

        if not region_data:
            result[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        latencies = [d["latency_ms"] for d in region_data]
        uptimes = [d["uptime_pct"] for d in region_data]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(sum(1 for lat in latencies if lat > payload.threshold_ms))
        }

    return result

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Payload(BaseModel):
    regions: list[str]
    threshold_ms: float

# Using absolute path resolution relative to this file
file_path = os.path.join(os.path.dirname(__file__), "..", "q-vercel-latency (1).json")
try:
    with open(file_path, "r") as f:
        data = json.load(f)
except Exception as e:
    data = []

@app.post("/api")
@app.post("/")
def get_metrics(payload: Payload):
    result = {}
    for region in payload.regions:
        region_data = [d for d in data if d["region"] == region]
        
        if not region_data:
            continue
            
        latencies = [d["latency_ms"] for d in region_data]
        uptimes = [d["uptime_pct"] for d in region_data]
        
        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = int(sum(1 for lat in latencies if lat > payload.threshold_ms))
        
        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }
    return result

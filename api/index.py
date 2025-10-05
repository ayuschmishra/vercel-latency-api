from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import os
from pathlib import Path

app = FastAPI(title="Latency Metrics API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LatencyRecord(BaseModel):
    region: str
    service: str
    latency_ms: float
    uptime_pct: float
    timestamp: str

class LatencyRequest(BaseModel):
    data: List[LatencyRecord]

class RegionMetrics(BaseModel):
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    avg_uptime_pct: float
    record_count: int

@app.get("/")
async def root():
    return {"message": "Latency Metrics API", "endpoints": ["/calculate-metrics"]}

@app.post("/calculate-metrics")
async def calculate_metrics(request: LatencyRequest) -> Dict[str, RegionMetrics]:
    """
    Calculate per-region latency metrics from the provided data.
    """
    if not request.data:
        raise HTTPException(status_code=400, detail="No data provided")
    
    # Group data by region
    regions: Dict[str, List[LatencyRecord]] = {}
    for record in request.data:
        if record.region not in regions:
            regions[record.region] = []
        regions[record.region].append(record)
    
    # Calculate metrics for each region
    results: Dict[str, RegionMetrics] = {}
    for region, records in regions.items():
        latencies = [r.latency_ms for r in records]
        uptimes = [r.uptime_pct for r in records]
        
        results[region] = RegionMetrics(
            avg_latency_ms=round(sum(latencies) / len(latencies), 2),
            min_latency_ms=round(min(latencies), 2),
            max_latency_ms=round(max(latencies), 2),
            avg_uptime_pct=round(sum(uptimes) / len(uptimes), 2),
            record_count=len(records)
        )
    
    return results

# For Vercel serverless function
handler = app

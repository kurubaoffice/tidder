# modules/logging/metrics.py
#from modules.logging.metrics import record_request, record_response, export_metrics
#record_request("HDFCMF")
# ... process
#record_response("HDFCMF")
#export_metrics()


import time
import json
from collections import defaultdict
from datetime import datetime

metrics = defaultdict(int)
symbols_requested = defaultdict(int)
start_times = {}

def record_request(symbol: str):
    metrics["total_requests"] += 1
    symbols_requested[symbol] += 1
    start_times[symbol] = time.time()

def record_response(symbol: str):
    if symbol in start_times:
        elapsed = time.time() - start_times[symbol]
        metrics["last_response_time_sec"] = elapsed

def export_metrics(filepath="logs/metrics.json"):
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "summary": dict(metrics),
        "symbols": dict(symbols_requested)
    }
    with open(filepath, "w") as f:
        json.dump(snapshot, f, indent=2)

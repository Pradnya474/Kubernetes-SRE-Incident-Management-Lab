import os
import time
from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
REQS = Counter("orders_http_requests_total", "HTTP requests", ["path", "status"])
LATENCY = Histogram("orders_http_request_duration_seconds", "Request duration", ["path"])
STARTED = time.time()
READY = True

@app.before_request
def before():
    from flask import g
    g.started_at = time.time()

@app.after_request
def after(response):
    from flask import request, g
    path = request.path
    REQS.labels(path, str(response.status_code)).inc()
    LATENCY.labels(path).observe(time.time() - getattr(g, "started_at", time.time()))
    return response

@app.get("/")
def index():
    return jsonify(service="orders-api", version="1.0")

@app.get("/health")
def health():
    return jsonify(status="healthy", uptime_seconds=round(time.time() - STARTED, 2))

@app.get("/ready")
def ready():
    if os.getenv("APP_READY", "true").lower() != "true":
        return jsonify(status="not-ready"), 503
    return jsonify(status="ready")

@app.get("/api/orders")
def orders():
    time.sleep(0.03)
    return jsonify(orders=[{"id": 201, "state": "created"}, {"id": 202, "state": "processing"}])

@app.get("/api/error")
def error():
    return jsonify(error="intentional training error"), 500

@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

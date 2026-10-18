import os
import time
import uuid

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGIN = "https://dash-tbya4f.example.com"
EMAIL = os.environ.get("EMAIL", "businessmakers662@gmail.com")

app = FastAPI()

# Added first => inner layer. Only the assigned origin gets ACAO; no wildcard.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,
)


# Added last => outermost layer, so it decorates every response
# (including CORS preflight responses and errors).
@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response


@app.get("/stats")
def stats(values: str = Query(...)):
    try:
        nums = [int(v.strip()) for v in values.split(",") if v.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be comma-separated integers")
    if not nums:
        raise HTTPException(status_code=400, detail="no values provided")
    total = sum(nums)
    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": total / len(nums),
    }


@app.get("/")
def root():
    return {"status": "ok"}

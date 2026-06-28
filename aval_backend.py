"""
AVALYOS Production FastAPI backend (single-file)

Features:
- FastAPI endpoints: /, /sample, /sample/many/{n}, /branches/{company}
- Q# integration via a single-worker bounded queue to avoid cross-thread issues
- Bounded queue with backpressure (returns 429 when queue is full)
- Optional API key authentication via `AVAL_API_KEY` env var
- Simple per-key rate limiting (configurable via env)
- CORS tightened to origins in `ALLOWED_ORIGINS` env var or localhost
- Pydantic models for responses

Run (development):
  pip install -r requirements.txt
  uvicorn aval_backend:app --reload --host 0.0.0.0 --port 8000

Note: Q# is optional for testing; unit tests mock the worker calls.
"""

from __future__ import annotations

import os
import json
import logging
import threading
import queue
import concurrent.futures
import time
from collections import deque
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Optional qsharp import (may be absent in test environments)
try:
    import qsharp
except Exception:
    qsharp = None

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("avalyos.backend")

# App + CORS configuration
app = FastAPI(title="AVALYOS Quantum Backend", version="1.0")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://127.0.0.1").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
COMPANIES_JSON = os.path.join(ROOT_DIR, "companies.json")

# --------------------
# Pydantic models
# --------------------
class BranchOut(BaseModel):
    code: str = Field(...)
    company: str = Field(...)
    continent: str = Field(...)
    country: str = Field(...)
    state: str = Field(...)
    sector: str = Field(...)
    subsector: str = Field(...)
    employees: int = Field(...)

class SampleManyOut(BaseModel):
    samples: List[BranchOut]
    distribution: Dict[str, int]

# --------------------
# Load dataset
# --------------------
def _normalize_branch_record(
    branch: Dict[str, Any], company_name: str, company_meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Normalize a single branch dict to the API schema."""
    company_meta = company_meta or {}

    def g(keys: List[str], default: Any = "unknown") -> Any:
        for k in keys:
            if k in branch:
                return branch[k]
        return default

    code = g(["Code", "code"], "unknown")
    continent = g(["Continent", "continent"], "unknown")
    country = g(["Country", "country"], "unknown")
    state = g(["State", "state"], "unknown")
    sector = g(["Sector", "sector"], company_meta.get("sector", "unknown"))
    subsector = g(["SubSector", "subsector", "subSector"], company_meta.get("subsector", "unknown"))
    employees = g(["Employees", "employees"], 0)
    try:
        employees = int(employees)
    except Exception:
        employees = 0

    return {
        "code": str(code),
        "company": str(company_name),
        "continent": str(continent),
        "country": str(country),
        "state": str(state),
        "sector": str(sector),
        "subsector": str(subsector),
        "employees": employees,
    }


def load_companies(path: str = COMPANIES_JSON) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        logger.warning("companies.json not found at %s", path)
        return []
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    companies_block = data.get("companies", data) if isinstance(data, dict) else data

    raw_branches: List[tuple[Dict[str, Any], str, Dict[str, Any]]] = []
    if isinstance(companies_block, dict):
        for company_name, company_data in companies_block.items():
            if not isinstance(company_data, dict):
                continue
            nested = company_data.get("branches")
            if isinstance(nested, dict):
                for branch in nested.values():
                    if isinstance(branch, dict):
                        raw_branches.append((branch, company_name, company_data))
            elif isinstance(nested, list):
                for branch in nested:
                    if isinstance(branch, dict):
                        raw_branches.append((branch, company_name, company_data))
            else:
                raw_branches.append((company_data, company_name, company_data))
    elif isinstance(companies_block, list):
        for branch in companies_block:
            if isinstance(branch, dict):
                name = str(branch.get("company") or branch.get("Company") or "unknown")
                raw_branches.append((branch, name, {}))

    return [
        _normalize_branch_record(branch, company_name, company_meta)
        for branch, company_name, company_meta in raw_branches
    ]

ALL_BRANCHES = load_companies()
BRANCHES_BY_COMPANY: Dict[str, List[Dict[str, Any]]] = {}
for b in ALL_BRANCHES:
    BRANCHES_BY_COMPANY.setdefault(b["company"].lower(), []).append(b)

# --------------------
# Simple rate limiter (per API key)
# --------------------
RATE_LIMIT_PER_MIN = int(os.getenv("AVAL_RATE_PER_MIN", "60"))
_RATE_STORE: Dict[str, deque] = {}
RATE_LOCK = threading.Lock()

def check_rate_limit(api_key: str):
    if RATE_LIMIT_PER_MIN <= 0:
        return
    with RATE_LOCK:
        dq = _RATE_STORE.setdefault(api_key or "__anon__", deque())
        now = time.time()
        # drop timestamps older than 60s
        while dq and dq[0] <= now - 60:
            dq.popleft()
        if len(dq) >= RATE_LIMIT_PER_MIN:
            raise HTTPException(status_code=429, detail={"error": "Rate limit exceeded"})
        dq.append(now)

# --------------------
# Auth dependency
# --------------------
def get_api_key(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    required = os.getenv("AVAL_API_KEY")
    if required:
        if x_api_key is None or x_api_key != required:
            raise HTTPException(status_code=401, detail={"error": "Unauthorized"})
    # perform rate limiting by api key value
    try:
        check_rate_limit(x_api_key or "__anon__")
    except HTTPException:
        raise
    return x_api_key

# --------------------
# Q# worker (bounded queue, backpressure)
# --------------------
QSHARP_QUEUE_MAX = int(os.getenv("QSHARP_QUEUE_MAX", "64"))
_TASK_QUEUE: "queue.Queue[tuple]" = queue.Queue(maxsize=QSHARP_QUEUE_MAX)
_WORKER_THREAD: Optional[threading.Thread] = None
_WORKER_STARTED = threading.Event()
_SHUTDOWN_SENTINEL = "__shutdown__"

def _worker_loop():
    """Worker thread that executes Q# operations safely in a single thread."""
    while True:
        try:
            op, fut = _TASK_QUEUE.get()
        except Exception:
            continue
        if op == _SHUTDOWN_SENTINEL:
            fut.set_result(True)
            break

        try:
            if op == "sample_one":
                result = qsharp.run("src.Operations.SampleBranch()", shots=1)
                fut.set_result(result)
            elif op == "get_branches":
                result = qsharp.run("src.Operations.GetSampleBranches()", shots=1)
                fut.set_result(result)
            else:
                fut.set_exception(RuntimeError("Unknown op"))
        except Exception as e:
            fut.set_exception(e)

def start_worker():
    global _WORKER_THREAD
    if _WORKER_THREAD and _WORKER_THREAD.is_alive():
        return
    _WORKER_THREAD = threading.Thread(target=_worker_loop, daemon=True)
    _WORKER_THREAD.start()
    _WORKER_STARTED.wait(timeout=5)

def stop_worker():
    if _WORKER_THREAD and _WORKER_THREAD.is_alive():
        fut = concurrent.futures.Future()
        try:
            _TASK_QUEUE.put((_SHUTDOWN_SENTINEL, fut), timeout=1)
            fut.result(timeout=5)
        except Exception:
            logger.exception("Error sending shutdown sentinel to worker queue")

def enqueue_op(op: str, timeout: float = 5.0) -> Any:
    """Enqueue operation; if queue is full, raise HTTPException(429)."""
    fut = concurrent.futures.Future()
    try:
        _TASK_QUEUE.put((op, fut), block=False)
    except queue.Full:
        raise HTTPException(status_code=429, detail={"error": "Server busy; try again later"})
    return fut.result(timeout=timeout)

# start worker
start_worker()

# --------------------
# Normalize Q# returned values
# --------------------
def normalize_qsharp_branch(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, list) and len(raw) == 1:
        raw = raw[0]
    if isinstance(raw, dict):
        lower = {k.lower(): v for k, v in raw.items()}
        return {
            "code": str(lower.get("code", "unknown")),
            "company": str(lower.get("company", "unknown")),
            "continent": str(lower.get("continent", "unknown")),
            "country": str(lower.get("country", "unknown")),
            "state": str(lower.get("state", "unknown")),
            "sector": str(lower.get("sector", "unknown")),
            "subsector": str(lower.get("subsector", "unknown")),
            "employees": int(lower.get("employees", 0) or 0),
        }

    # object attributes
    for attr_names in ("Code", "code", "Company", "company"):
        if hasattr(raw, attr_names):
            def a(*names, default=None):
                for n in names:
                    if hasattr(raw, n):
                        return getattr(raw, n)
                return default
            try:
                emp = int(a("Employees", "employees", default=0) or 0)
            except Exception:
                emp = 0
            return {
                "code": str(a("Code", "code", default="unknown")),
                "company": str(a("Company", "company", default="unknown")),
                "continent": str(a("Continent", "continent", default="unknown")),
                "country": str(a("Country", "country", default="unknown")),
                "state": str(a("State", "state", default="unknown")),
                "sector": str(a("Sector", "sector", default="unknown")),
                "subsector": str(a("SubSector", "subsector", default="unknown")),
                "employees": emp,
            }

    # sequence
    try:
        seq = list(raw)
        if len(seq) >= 8:
            try:
                emp = int(seq[7])
            except Exception:
                emp = 0
            return {
                "code": str(seq[0]),
                "company": str(seq[1]),
                "continent": str(seq[2]),
                "country": str(seq[3]),
                "state": str(seq[4]),
                "sector": str(seq[5]),
                "subsector": str(seq[6]),
                "employees": emp,
            }
    except Exception:
        logger.exception("Failed to interpret Q# sequence result: %r", raw)
    raise ValueError("Unsupported Q# result format")

# --------------------
# Endpoints
# --------------------
@app.get("/", summary="Health check")
def health():
    return JSONResponse({"status": "ok", "message": "AVALYOS Quantum Backend running"})

@app.get("/sample", response_model=BranchOut)
def sample_one(api_key: Optional[str] = Depends(get_api_key)):
    try:
        raw = enqueue_op("sample_one")
        branch = normalize_qsharp_branch(raw)
        logger.info("Sampled branch %s", branch.get("code"))
        return BranchOut(**branch)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("/sample error")
        raise HTTPException(status_code=500, detail={"error": "Failed to sample branch", "message": str(e)})

@app.get("/sample/many/{n}", response_model=SampleManyOut)
def sample_many(n: int, api_key: Optional[str] = Depends(get_api_key)):
    if n <= 0:
        raise HTTPException(status_code=400, detail={"error": "n must be > 0"})
    if n > 2000:
        raise HTTPException(status_code=400, detail={"error": "n too large; max 2000"})

    logger.info("Sampling %d branches", n)

    samples: List[BranchOut] = []
    distribution: Dict[str, int] = {}
    for i in range(n):
        try:
            raw = enqueue_op("sample_one")
            branch = normalize_qsharp_branch(raw)
            model = BranchOut(**branch)
            samples.append(model)
            distribution[model.company] = distribution.get(model.company, 0) + 1
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Sampling iteration %d failed", i)
            raise HTTPException(status_code=500, detail={"error": "Sampling failed", "message": str(e)})

    return SampleManyOut(samples=samples, distribution=distribution)

@app.get("/branches/{company}", response_model=List[BranchOut])
def branches_for_company(company: str, api_key: Optional[str] = Depends(get_api_key)):
    try:
        key = company.lower()
        matches = BRANCHES_BY_COMPANY.get(key, [])
        return [BranchOut(**m) for m in matches]
    except Exception as e:
        logger.exception("/branches failed")
        raise HTTPException(status_code=500, detail={"error": "Failed to get branches", "message": str(e)})

# --------------------
# Chat endpoint (Meridian)
# --------------------
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str


# Lazy text generator loader
_TEXT_GEN = None
_TEXT_GEN_LOCK = threading.Lock()
_TEXT_GEN_LOADING = False

def _load_text_generator_background():
    """Load the transformers text-generation model in a background thread."""
    global _TEXT_GEN, _TEXT_GEN_LOADING
    with _TEXT_GEN_LOCK:
        if _TEXT_GEN is not None or _TEXT_GEN_LOADING:
            return
        _TEXT_GEN_LOADING = True
    try:
        from transformers import pipeline
        import torch
        model_name = os.getenv("MERIDIAN_MODEL", "distilgpt2")
        device = 0 if torch.cuda.is_available() else -1
        logger.info("Meridian loader starting: model=%s device=%s", model_name, device)
        gen = pipeline("text-generation", model=model_name, device=device)
        with _TEXT_GEN_LOCK:
            _TEXT_GEN = gen
        logger.info("Loaded local text-generation model: %s", model_name)
    except Exception as e:
        logger.exception("Failed to load transformers model in background: %s", e)
    finally:
        with _TEXT_GEN_LOCK:
            _TEXT_GEN_LOADING = False

def get_text_generator():
    """Return the loaded text generator or None if not ready. Do NOT block."""
    return _TEXT_GEN


# Start background loader on app startup so requests don't block during download
@app.on_event("startup")
def _start_meridian_loader():
    try:
        threading.Thread(target=_load_text_generator_background, daemon=True).start()
        logger.info("Meridian background loader thread spawned")
    except Exception:
        logger.exception("Failed to spawn Meridian loader thread")


# Canned feature list (Meridian persona: guide focused on features)
MERIDIAN_FEATURES = [
    "Global Company Navigator: hierarchical navigation (Continent → Country → State → City)",
    "Quantum Simulator: Monte Carlo simulations with statistical analysis",
    "Company Browser: search, profile viewing, and quantum distribution analysis",
    "Database Integration: persistent storage of simulations and user actions",
    "Thread-Safe Q#: dedicated worker thread for quantum operations",
    "Rate Limiting & Auth: per-API-key rate limiting and optional authentication",
    "Comprehensive Logging: user actions and simulation results tracked",
]


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest, api_key: Optional[str] = Depends(get_api_key)):
    """Simple chat endpoint for Meridian: focused on explaining product features.

    Behavior:
    - If the user asks about features/capabilities, return the canned features list.
    - Otherwise, try a local `transformers` text-generation model as a fallback.
    """
    text = (req.message or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail={"error": "message required"})

    low = text.lower()
    if any(k in low for k in ("feature", "features", "what can", "capabilit", "help", "guide", "what does")):
        reply = "Meridian is a guided product assistant. Key features:\n- " + "\n- ".join(MERIDIAN_FEATURES)
        return ChatResponse(reply=reply)

    # fallback to local model if available
    gen = get_text_generator()
    if gen is None:
        # If the model is currently loading, return a quick warming message to avoid timeouts
        loading = False
        try:
            with _TEXT_GEN_LOCK:
                loading = _TEXT_GEN_LOADING
        except Exception:
            loading = False

        if loading:
            reply = "Meridian is warming up the local model — try asking about 'features' or check back in a minute."
        else:
            reply = "Meridian: I can explain the project's main features and how to run them. Ask for 'features' or 'how to run'."
        return ChatResponse(reply=reply)

    prompt = (
        "You are Meridian, a concise product guide for the AVALYOS project. "
        "Answer briefly and focus on explaining the project's features and usage. Do not make up capabilities.\nUser: "
        + text
        + "\nMeridian:"
    )
    try:
        out = gen(prompt, max_length=200, do_sample=True, top_p=0.95, temperature=0.7, num_return_sequences=1)
        if isinstance(out, list) and len(out) > 0 and "generated_text" in out[0]:
            reply = out[0]["generated_text"].split("Meridian:", 1)[-1].strip()
        else:
            reply = str(out)
    except Exception as e:
        logger.exception("Local generation failed: %s", e)
        reply = "Meridian: an internal error occurred generating a reply. Try asking about 'features' instead."

    return ChatResponse(reply=reply)

@app.on_event("shutdown")
def _shutdown():
    try:
        stop_worker()
    except Exception:
        logger.exception("Error stopping worker")

if __name__ == "__main__":
    start_worker()
    import uvicorn
    uvicorn.run("aval_backend:app", host="0.0.0.0", port=8000)

"""FastAPI server — run on the Raspberry Pi.

Start:
    uv run uvicorn backend.server:app --host 0.0.0.0 --port 8000

Then from the frontend, set VITE_PI_URL=http://<pi-ip>:8000
"""
import asyncio
import json
import sys
import threading
import time
from contextlib import asynccontextmanager
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

sys.path.insert(0, __file__.rsplit("/backend", 1)[0])

# ---------------------------------------------------------------------------
# Global SSE state — one active job at a time (fine for a single-device demo)
# ---------------------------------------------------------------------------
_loop: asyncio.AbstractEventLoop | None = None
_queue: asyncio.Queue | None = None
_history: list[dict] = []          # replay buffer for late-joining clients
_lock = threading.Lock()


def _push(event: dict):
    """Thread-safe: put an event into the SSE queue and history buffer."""
    with _lock:
        _history.append(event)
    if _loop and _queue:
        asyncio.run_coroutine_threadsafe(_queue.put(event), _loop)


# ---------------------------------------------------------------------------
# Pipeline (runs in a background thread)
# ---------------------------------------------------------------------------
def _run_pipeline(url: str):
    try:
        # --- phase 1: fetch accessibility tree ---
        _push({"type": "status", "phase": "extracting",
               "message": f"Fetching {urlparse(url).netloc}…"})

        from extractor.extract import fetch_ax_tree
        tree = fetch_ax_tree(url)

        from extractor.filter import build_contract
        contract = build_contract(tree, url=url)

        # --- phase 2: Gemini ranking ---
        _push({"type": "status", "phase": "ranking",
               "message": "Gemini building navigation tree…"})

        from extractor.rank import llm_build_tree
        domain = urlparse(url).netloc
        llm_tree = llm_build_tree(contract["items"], domain=domain)

        if llm_tree is None:
            _push({"type": "error", "message": "LLM tree build failed — check GEMINI_API_KEY"})
            return

        sections = llm_tree.get("sections", [])
        _push({"type": "tree_ready", "tree": llm_tree, "section_count": len(sections),
               "item_count": sum(len(s.get("items", [])) for s in sections)})

        # --- phase 3: buzz each item ---
        try:
            from output.motors import buzz_pattern, motors as motor_map
            from output.mappings import mapping
            has_motors = True
        except Exception:
            has_motors = False  # dev machine — simulate timing only

        LETTER_DUR = 0.3
        LETTER_GAP = 0.12
        ITEM_GAP   = 0.35

        for sec_idx, section in enumerate(sections):
            items = section.get("items", [])
            for item_idx, item in enumerate(items):
                text = item.get("text", "")
                _push({"type": "item",
                       "section": section["heading"],
                       "section_idx": sec_idx,
                       "item": text,
                       "item_idx": item_idx,
                       "total_items": len(items)})

                for char in text.lower():
                    pat = mapping.get(char, [0] * 6) if has_motors else [0] * 6
                    _push({"type": "char", "char": char, "pattern": pat})

                    if has_motors:
                        buzz_pattern(pat, duration=LETTER_DUR)
                        time.sleep(LETTER_GAP)
                    else:
                        time.sleep(LETTER_DUR + LETTER_GAP)

                time.sleep(ITEM_GAP)

        _push({"type": "done"})

        if has_motors:
            for m in motor_map.values():
                m.off()

    except Exception as exc:
        _push({"type": "error", "message": str(exc)})


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _loop, _queue
    _loop  = asyncio.get_running_loop()
    _queue = asyncio.Queue()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/extract")
async def extract(body: dict):
    url = (body.get("url") or "").strip()
    if not url:
        return {"error": "url required"}

    # Reset history and drain queue for the new job
    with _lock:
        _history.clear()
    while not _queue.empty():
        _queue.get_nowait()

    threading.Thread(target=_run_pipeline, args=(url,), daemon=True).start()
    return {"status": "started"}


@app.get("/stream")
async def stream():
    """SSE endpoint. Replays history so late-joining clients catch up."""
    async def generator():
        # replay anything already emitted
        with _lock:
            past = list(_history)
        for event in past:
            yield f"data: {json.dumps(event)}\n\n"

        # then stream new events
        while True:
            try:
                event = await asyncio.wait_for(_queue.get(), timeout=25)
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") in ("done", "error"):
                    break
            except asyncio.TimeoutError:
                yield "data: {\"type\":\"ping\"}\n\n"

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/status")
async def status():
    with _lock:
        last = {e["type"]: e for e in _history}
    return {
        "phase":   last.get("status", {}).get("phase", "idle"),
        "current": last.get("item"),
        "char":    last.get("char"),
        "done":    "done" in last,
    }

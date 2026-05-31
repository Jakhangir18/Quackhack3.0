# Touchpoint

Vibrotactile Braille interface for the visually impaired. A Raspberry Pi 5 drives 6 vibration motors in a Braille cell layout. A joystick navigates a pruned, AI-ranked accessibility tree fetched from any webpage. A React frontend streams live feedback.

## How the stack fits together

```
Browser (base44.app frontend)
        │
        │  HTTPS (fetch + SSE)
        ▼
antennae-comma-kissable.ngrok-free.dev   ← ngrok tunnel (free, persistent)
        │
        │  HTTP
        ▼
Raspberry Pi :8000   ← FastAPI server (uvicorn)
        │
        ├── extractor/   Playwright fetches page → Gemini builds nav tree
        ├── output/      buzz_pattern() drives GPIO vibration motors
        └── tests/       navigator.py reads joystick → navigates tree
```

**Two ways to navigate:**
- **Frontend** — type a URL on the website, Pi auto-plays through the tree while the browser shows live Braille output
- **Standalone** — run `navigator.py` on the Pi, use the physical joystick to move between sections/items

---

## Setup (Raspberry Pi + dev machine)

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone git@github.com:Jakhangir18/Quackhack3.0.git
cd Quackhack3.0
uv sync
uv run playwright install chromium
```

Copy the env file and add your Gemini key:

```bash
cp .env.example .env
# edit .env and set GEMINI_API_KEY
```

---

## Running the backend (on the Pi)

### 1. Start the FastAPI server

```bash
uv run uvicorn backend.server:app --host 0.0.0.0 --port 8000
```

### 2. Start the ngrok tunnel (separate terminal)

First-time setup — install ngrok and authenticate:

```bash
# install
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# authenticate (one-time, token from dashboard.ngrok.com)
ngrok config add-authtoken <your-token>
```

Then start the tunnel:

```bash
ngrok http --url=antennae-comma-kissable.ngrok-free.dev 8000
```

The frontend at `https://antennae-comma-kissable.ngrok-free.dev` now proxies straight to the Pi.

### 3. Open the frontend

Go to the deployed base44.app URL. The Live Demo section will connect automatically. Type any URL and hit **Read Page**.

---

## Running the extractor CLI (standalone)

**Live — fetch a real page:**
```bash
uv run python -m extractor.cli https://andrewkelley.me/
```

**Offline — replay a saved AX-tree JSON:**
```bash
uv run python -m extractor.cli sample_tree.json --offline
```

Output is a Gemini-ranked navigation tree (JSON to stdout). Requires `GEMINI_API_KEY` in `.env`.

---

## Joystick navigation (standalone, no frontend)

```bash
# 1. generate the tree
uv run python -m extractor.cli https://example.com > tree.json

# 2. navigate with the physical joystick + motors
python tests/navigator.py tree.json
```

Joystick controls:
- **Left / Right** — previous / next item within section
- **Up / Down** — previous / next section
- **Button** — re-buzz current item

---

## Hardware tests

```bash
python tests/joystick_test.py   # verify joystick wiring (raw ADC values)

python tests/dot1.py            # buzz dot 1 only (left top)
python tests/dot2.py            # dot 2 (left middle)
python tests/dot3.py            # dot 3 (left bottom)
python tests/dot4.py            # dot 4 (right top)
python tests/dot5.py            # dot 5 (right middle)
python tests/dot6.py            # dot 6 (right bottom)

python output/motors.py         # full dot-by-dot sequence + all 6 together
python tests/demo_touchpoint.py # spell "touchpoint" in Braille
```

---

## Project layout

```
touchpoint/
├── backend/
│   └── server.py        # FastAPI — /extract (POST), /stream (SSE), /status (GET)
├── extractor/
│   ├── cli.py           # entry point
│   ├── extract.py       # Playwright → raw AX tree (aria_snapshot)
│   ├── filter.py        # prune + flatten + heuristic importance scoring
│   ├── rank.py          # Gemini Flash — llm_rank() and llm_build_tree()
│   └── schema.py        # A11yItem dataclass
├── output/
│   ├── mappings.py      # Braille alphabet → 6-element dot patterns
│   └── motors.py        # gpiozero PWM motor control, buzz_pattern()
├── tests/
│   ├── demo_touchpoint.py   # spell "touchpoint" end-to-end
│   ├── navigator.py         # joystick navigation loop
│   ├── joystick_test.py     # raw joystick ADC monitor
│   └── dot1-6.py            # individual motor tests
├── touchpoint-frontend/     # React + Vite (deployed to base44.app)
├── .env.example
├── pyproject.toml
└── uv.lock
```

## GPIO pin mapping (BCM numbering)

```
Braille cell layout:    dot1 (GPIO4)   dot4 (GPIO26)
                        dot2 (GPIO5)   dot5 (GPIO12)
                        dot3 (GPIO6)   dot6 (GPIO16)
```

## Dependencies

- `playwright` + `pyyaml` — headless Chromium + AX tree parsing
- `google-genai` — Gemini Flash 2.5 for navigation tree building
- `gpiozero` — PWM motor control on Pi GPIO
- `fastapi` + `uvicorn` — HTTP/SSE backend server
- `spidev` — SPI joystick (MCP3008 ADC) — install separately on Pi: `pip install spidev`

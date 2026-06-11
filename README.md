# Touchpoint (2nd Place Overall @ Quackhacks 3.0)

Touchpoint is a Raspberry Pi powered vibrotactile Braille demo. The Pi serves a
small local web page, accepts a word from the browser, and plays that word across
six vibration motors using Grade 1 Braille dot patterns.

## How It Works

```
Laptop or phone browser
        |
        |  HTTP on local Wi-Fi
        v
Raspberry Pi :8000
        |
        +-- extractor/main.py   Flask server
        +-- frontend/index.html Word input + visual Braille animation
        +-- output/motors.py    GPIO motor playback
        +-- output/mappings.py  Character to Braille dot patterns
```

The browser animation runs client-side. The Pi receives `POST /play` and buzzes
the same word on the physical motors with `output.motors.buzz_word()`.

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone git@github.com:Jakhangir18/Quackhack3.0.git
cd Quackhack3.0
uv sync
```

On the Raspberry Pi, make sure GPIO access works:

```bash
sudo usermod -aG gpio $USER
```

Log out and back in, or reboot, after changing groups. Then verify that `uv`
installed the GPIO backend:

```bash
uv run python -c "import lgpio; print('lgpio ok')"
```

For extractor/Gemini experiments, copy the env file and add your Gemini key:

```bash
cp .env.example .env
# edit .env and set GEMINI_API_KEY
```

The Flask motor demo does not require a Gemini key.

## Run The Pi Web Demo

Start the Flask server on the Raspberry Pi:

```bash
uv run python -m extractor.main
```

The server listens on all network interfaces at port `8000`.

From the Pi, open:

```text
http://localhost:8000
```

From a laptop or phone on the same Wi-Fi, find the Pi IP:

```bash
hostname -I
```

Then open:

```text
http://<pi-ip>:8000
```

Type a word and press **Send**. The page shows the Braille animation while the
Pi buzzes the motors.

## Test The Playback Route

With the Flask server running:

```bash
curl -X POST http://localhost:8000/play \
  -H "Content-Type: application/json" \
  -d '{"word":"hello"}'
```

Expected response:

```json
{"status":"ok"}
```

The HTTP response returns immediately while motor playback continues in a
background thread.

## Port Troubleshooting

If port `8000` is already in use:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
kill <PID>
```

Or run the Flask app on another port:

```bash
uv run python -c "from extractor.main import app; app.run(host='0.0.0.0', port=8080)"
```

Then open:

```text
http://<pi-ip>:8080
```

## Hardware Tests

Run these on the Pi from the repo root:

```bash
python tests/dot1.py            # buzz dot 1 only
python tests/dot2.py            # buzz dot 2 only
python tests/dot3.py            # buzz dot 3 only
python tests/dot4.py            # buzz dot 4 only
python tests/dot5.py            # buzz dot 5 only
python tests/dot6.py            # buzz dot 6 only

python output/motors.py         # full dot-by-dot sequence
python tests/demo_touchpoint.py # spell "touchpoint" in Braille
```

Button debugging:

```bash
python tests/button_test.py
```

## Extractor CLI

The extractor code can still build a navigation tree from a web page:

```bash
uv run python -m extractor.cli https://andrewkelley.me/
```

Offline AX-tree replay:

```bash
uv run python -m extractor.cli sample_tree.json --offline
```

## Project Layout

```
touchpoint/
├── extractor/
│   ├── main.py          # Flask server for the Pi web demo
│   ├── cli.py           # extractor CLI
│   ├── extract.py       # Playwright page extraction
│   ├── filter.py        # prune + flatten accessibility items
│   ├── rank.py          # Gemini navigation tree building
│   └── schema.py        # A11yItem dataclass
├── frontend/
│   └── index.html       # local Pi-served word playback UI
├── output/
│   ├── mappings.py      # Braille character mappings
│   ├── motors.py        # gpiozero PWM motor control
│   ├── button_config.py # button GPIO configuration
│   └── navigate.py      # navigation state helpers
├── tests/
│   ├── button_test.py
│   ├── demo_touchpoint.py
│   └── dot1-6.py
├── .env.example
├── pyproject.toml
└── uv.lock
```

## GPIO Pin Mapping

`gpiozero` uses BCM GPIO numbering, not physical pin numbering.

Braille motor layout:

```text
dot1 GPIO4    dot4 GPIO26
dot2 GPIO5    dot5 GPIO12
dot3 GPIO6    dot6 GPIO16
```

Button pins live in `output/button_config.py`.

## Dependencies

- `flask` — Pi-hosted web server
- `gpiozero` — PWM motor control on Pi GPIO
- `playwright` + `pyyaml` — page extraction experiments
- `google-genai` — Gemini navigation tree building

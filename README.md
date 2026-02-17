# FLORA AI Assistant

FLORA is a modular Python assistant with voice + text interaction, a PyQt6 HUD, and pluggable skills loaded at runtime.

![FLORA Robot](flora1.png)

## What It Can Do

- Chat using Groq (`llama-3.3-70b-versatile`)
- Run local tools through skills in `skills/`
- Listen and respond with speech
- Run in GUI mode or terminal text mode
- Support optional weather, vision, WhatsApp, email, and system automation features

## Requirements

- Python 3.10+
- macOS/Linux/Windows (macOS currently has best voice fallback behavior)
- Groq API key

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
```

Edit `.env` and set at least:

```env
GROQ_API_KEY=your_real_groq_key
```

Optional env vars for specific skills:

- `OPENWEATHERMAP_API_KEY`
- `DEFAULT_CITY`
- `EMAIL_ADDRESS`
- `EMAIL_PASSWORD`
- `EMAIL_IMAP_SERVER`

## Run

GUI + voice mode:

```bash
python main.py
```

Text mode:

```bash
python main.py --text
```

## Architecture

- `main.py`: startup flow, env validation, mode selection
- `core/engine.py`: LLM + tool-calling loop
- `core/registry.py`: dynamic skill loading and function registry
- `core/voice.py`: speech input/output helpers
- `gui/app.py`: FLORA HUD interface
- `skills/*.py`: feature modules exposed as callable tools

## Project Layout

```text
Project_Flora/
├── main.py
├── core/
├── gui/
├── skills/
├── assets/
├── requirements.txt
├── .env.template
└── README.md
```

## Useful Notes

- `GROQ_API_KEY` is mandatory. App exits if it is missing or placeholder.
- In GUI mode, clicking toggles pause/resume.
- On macOS, TTS may use system `say` for stability.
- `gui/app.py` currently points to an absolute local robot image path; switch to an asset-relative path if needed.

## Quick Validation

```bash
python verify_refactor.py
python verify_new_skills.py
python verify_changes.py
```

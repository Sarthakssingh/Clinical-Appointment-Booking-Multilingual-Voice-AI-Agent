# Real-Time Multilingual Voice AI Agent — Clinical Appointment Booking

Production-oriented starter built from scratch for the assignment. It uses **Python** for the real-time voice agent and **TypeScript** for the scheduling API.

## Stack
- Python: realtime voice orchestration, multilingual policy, memory, tool calling
- TypeScript + Fastify: scheduling API, patient context API, campaign trigger API
- SQLite by default for local demo, easy to swap to PostgreSQL
- Redis-compatible interface stub for session memory (in-memory fallback for local demo)

## Features
- Book, reschedule, cancel appointments
- Conflict-safe slot hold + confirmation flow
- Session memory + long-term patient preference memory
- Language preference carryover: English, Hindi, Tamil
- Outbound campaign API scaffolding
- Structured reasoning/event traces
- Latency instrumentation hooks

## Monorepo layout
- `apps/realtime-agent` — Python realtime orchestration
- `apps/api-gateway` — TypeScript scheduling API
- `docs/architecture.md` — architecture and latency notes

## Quick start

### 1) Start API
```bash
cd apps/api-gateway
npm install
npm run dev
```
Server runs on `http://localhost:8080`.

### 2) Start Python agent demo
```bash
cd apps/realtime-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 3) Try the agent locally
The Python demo uses text input to simulate speech turns while keeping the same state, tools, and memory logic you would use behind streaming STT/TTS.

## Live voice integration path
For production-grade real-time audio, replace the local CLI transport with a LiveKit audio session and Sarvam STT/TTS adapters. LiveKit provides Python Agents support and turn handling patterns, while Sarvam provides Indian-language STT/TTS including streaming support. [1][2][3]

## API routes
- `GET /health`
- `GET /slots/search?doctorId=&date=&clinicId=`
- `POST /appointments/hold`
- `POST /appointments/book`
- `POST /appointments/reschedule`
- `POST /appointments/cancel`
- `GET /patients/:id/context`
- `POST /campaigns/outbound`
- `GET /metrics/latency`

## What this repo demonstrates
- deterministic scheduling invariants in the API layer
- tool orchestration in the Python agent
- memory separation between session and cross-session contexts
- traceable reasoning events without exposing chain-of-thought

## Notes
- This local starter uses SQLite for simplicity. Use PostgreSQL + Redis in the final submission.
- The voice transport is scaffolded for replacement with real audio providers.
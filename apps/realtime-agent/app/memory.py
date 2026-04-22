import json
import os
from typing import Optional
from app.models import SessionState

# In production: use Redis. Locally: dict fallback.
try:
    import redis
    _r = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'), decode_responses=True)
    _r.ping()
    USE_REDIS = True
except Exception:
    USE_REDIS = False
    _sessions = {}
    _long_term = {
        'p1': {'preferred_language': 'en', 'preferred_time_of_day': 'evening'}
    }

SESSION_TTL = 3600  # 1 hour

def get_session(session_id: str) -> Optional[SessionState]:
    if USE_REDIS:
        raw = _r.get(f'session:{session_id}')
        return SessionState(**json.loads(raw)) if raw else None
    return _sessions.get(session_id, None)

def save_session(state: SessionState):
    if USE_REDIS:
        _r.setex(f'session:{state.session_id}', SESSION_TTL, state.model_dump_json())
    else:
        _sessions[state.session_id] = state

def get_long_term(patient_id: str) -> dict:
    if USE_REDIS:
        raw = _r.get(f'patient:{patient_id}')
        return json.loads(raw) if raw else {}
    return _long_term.get(patient_id, {})

def update_long_term(patient_id: str, **kwargs):
    current = get_long_term(patient_id)
    current.update(kwargs)
    if USE_REDIS:
        _r.set(f'patient:{patient_id}', json.dumps(current))
    else:
        _long_term[patient_id] = current
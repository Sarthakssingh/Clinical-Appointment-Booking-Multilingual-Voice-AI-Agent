import os
import time
import requests

BASE = os.getenv('API_BASE_URL', 'http://localhost:8080')

def _post(path, payload):
    return requests.post(f'{BASE}{path}', json=payload, timeout=10).json()

def _get(path, params=None):
    return requests.get(f'{BASE}{path}', params=params, timeout=10).json()

def get_patient_context(patient_id):
    return _get(f'/patients/{patient_id}/context')

def search_slots(doctor_id=None, clinic_id=None, date=None):
    params = {k: v for k, v in {'doctorId': doctor_id, 'clinicId': clinic_id, 'date': date}.items() if v}
    return _get('/slots/search', params=params)

# def hold_slot(slot_id, patient_id, ttl=90):
#     return _post('/appointments/hold', {'slotId': slot_id, 'patientId': patient_id, 'ttlSeconds': ttl})
def hold_slot(slot_id, patient_id, ttl=90):
    response = requests.post(f'{BASE}/appointments/hold', json={
        'slotId': slot_id,
        'patientId': patient_id,
        'ttlSeconds': ttl
    }, timeout=10)
    print('hold_slot raw response:', response.status_code, response.text)  # debug line
    return response.json()

def book_appointment(hold_id, patient_id):
    return _post('/appointments/book', {'holdId': hold_id, 'patientId': patient_id})

def cancel_appointment(appointment_id):
    return _post('/appointments/cancel', {'appointmentId': appointment_id})

def reschedule_appointment(appointment_id, new_hold_id, patient_id):
    return _post('/appointments/reschedule', {'appointmentId': appointment_id, 'newHoldId': new_hold_id, 'patientId': patient_id})

def save_preference(patient_id, key, value):
    return _post(f'/patients/{patient_id}/preferences', {'key': key, 'value': value})

def log_latency(stage, ms):
    try: _post('/metrics/latency', {'stage': stage, 'durationMs': ms})
    except: pass
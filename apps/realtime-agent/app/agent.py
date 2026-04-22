import uuid
import time
from app.models import SessionState
from app.memory import get_session, save_session, get_long_term, update_long_term
from app.language import detect_language, detect_intent, get_response
from app import tools


class ClinicalVoiceAgent:
    def __init__(self, patient_id: str, session_id: str = None):
        self.state = None                          # always set first
        sid = session_id or str(uuid.uuid4())
        existing = get_session(sid)
        if existing:
            self.state = existing
        else:
            self.state = self._new_session(sid, patient_id)
        save_session(self.state)

    def _new_session(self, sid: str, patient_id: str) -> SessionState:
        ctx = get_long_term(patient_id)
        state = SessionState(
            session_id=sid,
            patient_id=patient_id,
            language=ctx.get('preferred_language', 'en')
        )
        self._trace_to(state, 'session_init', {'patient_id': patient_id})
        return state

    def _trace_to(self, state: SessionState, event: str, payload: dict):
        state.trace.append({'event': event, 'payload': payload, 'ts': round(time.time(), 3)})

    def _trace(self, event: str, payload: dict):
        self._trace_to(self.state, event, payload)

    def turn(self, utterance: str) -> str:
        t0 = time.perf_counter()

        lang = detect_language(utterance)
        intent = detect_intent(utterance)

        if lang != self.state.language:
            self.state.language = lang
            tools.save_preference(self.state.patient_id, 'preferred_language', lang)
            update_long_term(self.state.patient_id, preferred_language=lang)

        self._trace('turn_start', {'utterance': utterance, 'language': lang, 'intent': intent})

        response = self._route(intent, utterance)
        self.state.last_agent_message = response

        elapsed = int((time.perf_counter() - t0) * 1000)
        tools.log_latency('agent_turn_ms', elapsed)
        self._trace('turn_end', {'latency_ms': elapsed})
        save_session(self.state)
        return response

    def _route(self, intent: str, utterance: str) -> str:
        lang = self.state.language

        if self.state.pending_confirmation and intent == 'confirm':
            return self._confirm_booking()
        if intent == 'book':
            return self._handle_book()
        if intent == 'reschedule':
            return self._handle_reschedule()
        if intent == 'cancel':
            return self._handle_cancel()

        return get_response('fallback', lang)

    # def _handle_book(self) -> str:
    #     lang = self.state.language
    #     slots = tools.search_slots()
    #     self._trace('tool_call', {'tool': 'search_slots', 'count': len(slots)})
    #     if not slots:
    #         return get_response('no_slots', lang)
    #     slot = slots[0]
    #     hold = tools.hold_slot(slot['slotId'], self.state.patient_id)
    #     self._trace('tool_call', {'tool': 'hold_slot', 'holdId': hold.get('holdId')})
    #     self.state.selected_slot_id = slot['slotId']
    #     self.state.selected_hold_id = hold['holdId']
    #     self.state.pending_confirmation = True
    #     return get_response('slot_offer', lang, time=slot['startAt'])
    def _handle_book(self) -> str:
        lang = self.state.language
        slots = tools.search_slots()
        self._trace('tool_call', {'tool': 'search_slots', 'count': len(slots)})

        if not slots:
            return get_response('no_slots', lang)

        # Try each slot until one holds successfully
        hold = None
        chosen_slot = None
        for slot in slots:
            result = tools.hold_slot(slot['slotId'], self.state.patient_id)
            if 'holdId' in result:
                hold = result
                chosen_slot = slot
                break
            else:
                self._trace('hold_failed', {'slotId': slot['slotId'], 'error': result})

        if not hold:
            return get_response('no_slots', lang)

        self._trace('tool_call', {'tool': 'hold_slot', 'holdId': hold.get('holdId')})
        self.state.selected_slot_id = chosen_slot['slotId']
        self.state.selected_hold_id = hold['holdId']
        self.state.pending_confirmation = True
        return get_response('slot_offer', lang, time=chosen_slot['startAt'])

    def _confirm_booking(self) -> str:
        lang = self.state.language
        booked = tools.book_appointment(self.state.selected_hold_id, self.state.patient_id)
        self._trace('tool_call', {'tool': 'book_appointment', 'result': booked})
        self.state.pending_confirmation = False
        self.state.selected_appointment_id = booked['appointmentId']
        return get_response('booked', lang, time=booked['startAt'], id=booked['appointmentId'])

    def _handle_cancel(self) -> str:
        lang = self.state.language
        if not self.state.selected_appointment_id:
            return get_response('fallback', lang)
        result = tools.cancel_appointment(self.state.selected_appointment_id)
        self._trace('tool_call', {'tool': 'cancel_appointment', 'result': result})
        return get_response('cancelled', lang)

    def _handle_reschedule(self) -> str:
        lang = self.state.language
        if not self.state.selected_appointment_id:
            return get_response('fallback', lang)
        slots = tools.search_slots()
        if not slots:
            return get_response('no_slots', lang)
        new_slot = slots[-1]
        hold = tools.hold_slot(new_slot['slotId'], self.state.patient_id)
        booked = tools.reschedule_appointment(
            self.state.selected_appointment_id,
            hold['holdId'],
            self.state.patient_id
        )
        self.state.selected_appointment_id = booked['appointmentId']
        self._trace('tool_call', {'tool': 'reschedule_appointment', 'result': booked})
        return get_response('rescheduled', lang, time=booked['startAt'])
import re
from typing import Literal

LanguageCode = Literal['en', 'hi', 'ta']

HINDI_WORDS = {'namaste','kal','appointment','chahiye','doctor','baat','theek','haan','nahi','samay','subah','shaam'}
TAMIL_WORDS = {'vanakkam','naalai','maruththuvar','munpadhivu','pothu','nool','maiyam','velai'}

def detect_language(text: str) -> LanguageCode:
    if re.search(r'[\u0B80-\u0BFF]', text): return 'ta'
    if re.search(r'[\u0900-\u097F]', text): return 'hi'
    lower = text.lower().split()
    if any(w in HINDI_WORDS for w in lower): return 'hi'
    if any(w in TAMIL_WORDS for w in lower): return 'ta'
    return 'en'

def detect_intent(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ['book','schedule','appointment chahiye','munpadhivu']): return 'book'
    if any(k in t for k in ['reschedule','change time','move','badal']): return 'reschedule'
    if any(k in t for k in ['cancel','drop','band karo','naalai venda']): return 'cancel'
    if any(k in t for k in ['yes','haan','confirm','ok','sari']): return 'confirm'
    return 'unknown'

RESPONSES = {
    'greeting': {
        'en': 'Hello! I can help you book, reschedule, or cancel a clinical appointment.',
        'hi': 'Namaste! Main aapko appointment book karne mein madad kar sakta hoon.',
        'ta': 'Vanakkam! Naan ungal appointment book seiya udhavi seiven.'
    },
    'slot_offer': {
        'en': 'I found a slot at {time}. Shall I confirm this appointment?',
        'hi': '{time} par ek slot available hai. Kya main yeh confirm karun?',
        'ta': '{time} il oru slot kittiyirukku. Ithai confirm seiyalama?'
    },
    'booked': {
        'en': 'Your appointment is confirmed for {time}. Appointment ID: {id}',
        'hi': 'Aapki appointment {time} ke liye confirm ho gayi. ID: {id}',
        'ta': 'Ungal appointment {time} ku confirm aagividdu. ID: {id}'
    },
    'cancelled': {
        'en': 'Your appointment has been cancelled.',
        'hi': 'Aapki appointment cancel ho gayi.',
        'ta': 'Ungal appointment cancel aagividdu.'
    },
    'rescheduled': {
        'en': 'Your appointment has been rescheduled to {time}.',
        'hi': 'Aapki appointment {time} ke liye reschedule ho gayi.',
        'ta': 'Ungal appointment {time} ku maati aagividdu.'
    },
    'no_slots': {
        'en': 'No slots are available right now. Would you like a different doctor or time?',
        'hi': 'Abhi koi slot available nahi hai. Kya aap doosra doctor ya waqt chahenge?',
        'ta': 'Ippo slot illai. Vera doctor ya neram venum?'
    },
    'fallback': {
        'en': 'I can help you book, reschedule, or cancel an appointment. What would you like to do?',
        'hi': 'Main appointment book, reschedule, ya cancel karne mein madad kar sakta hoon.',
        'ta': 'Naan appointment book, reschedule, cancel seiya udhavuven.'
    }
}

def get_response(key: str, lang: LanguageCode, **kwargs) -> str:
    tmpl = RESPONSES.get(key, RESPONSES['fallback']).get(lang, RESPONSES[key]['en'])
    for k, v in kwargs.items():
        tmpl = tmpl.replace(f'{{{k}}}', str(v))
    return f'[{lang.upper()}] {tmpl}'
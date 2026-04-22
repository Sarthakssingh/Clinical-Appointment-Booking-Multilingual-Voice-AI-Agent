import os
from dotenv import load_dotenv
load_dotenv(dotenv_path='../../.env')

from app.agent import ClinicalVoiceAgent

if __name__ == '__main__':
    print('Clinical Voice AI Agent — text simulation mode')
    print('Commands: book / reschedule / cancel / yes / quit')
    print('Prefix with "language hi" or "language ta" to switch language\n')

    agent = ClinicalVoiceAgent(patient_id='p1')
    while True:
        utterance = input('you> ').strip()
        if utterance.lower() in {'quit', 'exit'}:
            break
        response = agent.turn(utterance)
        print(f'agent> {response}')
        last = agent.state.trace[-1]
        print(f'trace> {last}\n')
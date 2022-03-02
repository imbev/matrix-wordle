import json
import os


def load_state():
    if not os.path.isfile('state.json'):
        save_state({})

    with open('state.json', 'r') as f:
        return json.load(f)

def save_state(state: str):
    with open('state.json', 'w') as f:
        json.dump(state, f)

def ensure_state(func):
    async def wrapper(*args, **kwargs):
        state = load_state()
        await func(*args, **kwargs, state=state)
    return wrapper
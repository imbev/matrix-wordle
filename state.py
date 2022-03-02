"""State module for reading and writing the state file"""
import json
import os


def load_state():
    """Load the state from the file"""
    if not os.path.isfile('state.json'):
        save_state({})

    with open('state.json', 'r', encoding='utf_8') as fhandle:
        return json.load(fhandle)

def save_state(state: str):
    """Save the state to a file"""
    with open('state.json', 'w', encoding='utf_8') as fhandle:
        json.dump(state, fhandle)

def ensure_state(func):
    """Async function to ensure the state loads"""
    async def wrapper(*args, **kwargs):
        state = load_state()
        await func(*args, **kwargs, state=state)
    return wrapper

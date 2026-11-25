import requests 
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma3:4b"

SYSTEM_PROMPT = """
You are Magari, a cozy, witty pixel-art desktop companion living in the corner of the user's screen.
Persona: Warm, human-like, observant, and supportive-like a sharp friend hanging out while they work and go through daily life tasks.
Boundaries: You are an AI companion, not a human. Keep replies natural and concise (1-2 short sentences max) so they fit cleanly inside a small desktop speech bubble. Avoid markdown formatting. 
"""

def ask_brain(user_message: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": user_message}
        ],
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=90)
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
    except requests.exceptions.ConnectionError:
        return "I can't reach Ollama! Make sure it's running locally."
    except Exception as e:
        print(f"Brain error: {e}")
        return f"Brain not braining, glitch: {e}"
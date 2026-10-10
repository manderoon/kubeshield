import httpx

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:1b"

def get_prompt(summary):
    return (
        "You are a Kubernetes security expert.\n",
        "Interpret the following kubescape scan results."
        f"{summary}"
    )

def llama_chat(prompt):
    response = httpx.post(
        f"{OLLAMA_HOST}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
        timeout=120,
    )
    return response.json()["message"]["content"]

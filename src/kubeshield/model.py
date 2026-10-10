import httpx

from kubeshield.errors import UnavailableError, UpstreamError, UpstreamTimeoutError

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:1b"
TIMEOUT = 120

def get_prompt(summary: dict) -> str:
    return (
        "You are a Kubernetes security expert.\n"
        "Interpret the following kubescape scan results.\n"
        f"{summary}"
    )

def llama_chat(prompt: str) -> str:
    try:
        response = httpx.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=TIMEOUT,
        )
    except httpx.TimeoutException:
        raise UpstreamTimeoutError(f"ollama request timed out after {TIMEOUT} seconds") from None
    
    except httpx.ConnectError as e:
        raise UnavailableError(f"can't reach ollama at {OLLAMA_HOST}: {e}") from None
    
    except httpx.HTTPError as e:
        raise UpstreamError(f"ollama request failed: {e}") from None

    if response.is_error:
        raise UpstreamError(f"ollama request failed: {response.text}")

    return response.json()["message"]["content"]

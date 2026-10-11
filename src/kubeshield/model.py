import json

import httpx

from kubeshield.errors import UnavailableError, UpstreamError, UpstreamTimeoutError

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:1b"
TIMEOUT = 120
TOP_CONTROLS = 3

def get_prompt(summary: dict) -> str:
    # A small model gives better fixes when it focuses on a few controls
    top_controls = summary["failed_controls"][:TOP_CONTROLS]
    return (
        "You are a Kubernetes security expert.\n"
        "A kubescape scan of a cluster gave a compliance score of "
        f"{summary['compliance_score']:.0f}/100.\n"
        "Across the whole cluster, the number of resources failing at each severity is: "
        f"{json.dumps(summary['failed_resources_by_severity'])}.\n"
        f"These are the {len(top_controls)} most severe failed controls, "
        "each with the number of resources failing it:\n"
        f"{json.dumps(top_controls, indent=2)}\n\n"
        "Give a brief assessment of the cluster's security. "
        "Then, for each of these controls, suggest one change that fixes it. "
        "Show each change as a complete Kubernetes YAML manifest in its own "
        "```yaml code block, ready to use with kubectl apply. "
        "Do not wrap manifests inside a ConfigMap. "
        "Fix each control by changing the settings of the affected workloads, "
        "such as a Deployment's container spec, not by creating new Roles, "
        "ClusterRoles or PersistentVolumeClaims. "
        "Only suggest changes that remove permissions or add restrictions. "
        "Only use numbers that appear in the scan results above."
    )

def llama_chat(prompt: str) -> str:
    try:
        response = httpx.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                # Stick closely to the prompt instead of improvising
                "options": {"temperature": 0},
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

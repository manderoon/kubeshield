import json
from pathlib import Path

import httpx

from kubeshield.errors import UnavailableError, UpstreamError, UpstreamTimeoutError

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "gemma4:e4b-it-qat"
TIMEOUT = 600
TOP_CONTROLS = 3

# The model returns a JSON patch that applies the changes suggested in Kubescape
with open(Path(__file__).with_name("schema.json")) as f:
    SCHEMA = json.load(f)

def get_prompt(summary: dict) -> str:
    # A small model gives better fixes when it focuses on a few controls,
    # and only on ones kubescape gives exact fixes for
    top_controls = [c for c in summary["failed_controls"] if c["fixes"]][:TOP_CONTROLS]
    controls = "\n\n".join(
        f"{c['id']} {c['name']} ({c['severity']})\n"
        + "\n".join(f"- {f['resource']}: {'; '.join(f['changes'])}" for f in c["fixes"])
        for c in top_controls
    )
    return (
        "You are a Kubernetes security expert.\n"
        "A kubescape scan of a cluster gave a compliance score of "
        f"{summary['compliance_score']:.0f}/100.\n"
        "Across the whole cluster, the number of resources failing at each severity is: "
        f"{json.dumps(summary['failed_resources_by_severity'])}.\n"
        f"These are the {len(top_controls)} most severe failed controls. "
        "Under each one is an affected resource, as Kind namespace/name, "
        "and the change kubescape says fixes it:\n\n"
        f"{controls}\n\n"
        "In assessment, give a brief assessment of the cluster's security in two or three sentences.\n"
        "In fixes, add one entry for each resource listed above, with:\n"
        "- control: the control ID\n"
        "- resource: the resource exactly as written above, e.g. Deployment default/web\n"
        "- patch: a JSON patch (RFC 6902) that makes kubescape's change. "
        "Turn kubescape's path into a JSON pointer, e.g. "
        "spec.template.spec.containers[0].securityContext.privileged becomes "
        "/spec/template/spec/containers/0/securityContext/privileged. "
        "Use op remove for delete, and op add for set. "
        "Give values their JSON type: false not \"false\", 1000 not \"1000\". "
        "Where the value is YOUR_VALUE, choose a sensible value. "
        "add fails if the parent object doesn't exist yet, and kubescape's paths often go under "
        "objects that are missing, such as resources.limits. In that case add the missing parent "
        "with the value inside it, e.g. "
        '{"op": "add", "path": "/spec/template/spec/containers/0/resources/limits", '
        '"value": {"cpu": "500m"}}. '
        "Each patch is applied on its own to the resource as it is now, "
        "so never rely on another patch having added a parent.\n"
        "- explanation: the risk this fixes and what the change does, in one or two sentences. "
        "Mention anything the change could break.\n"
        "Only fix the resources listed above."
    )

def llama_chat(prompt: str) -> dict:
    try:
        response = httpx.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "format": SCHEMA,
                # For reproducible output, can turn off
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

    content = response.json()["message"]["content"]
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise UpstreamError(f"model didn't return JSON: {content[:200]}") from None

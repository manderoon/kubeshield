# Ask llama about an example scan summary and see it replies
import sys

from kubeshield.model import get_prompt, llama_chat

summary = {
    "compliance_score": 63.547916,
    "failed_resources_by_severity": {
        "critical": 0,
        "high": 54,
        "medium": 161,
        "low": 9
    },
    "top_failed_controls": [
        "Prevent containers from allowing command execution",
        "Roles with delete capabilities",
        "Applications credentials in configuration files",
        "Non-root containers",
        "List Kubernetes secrets"
    ]
}

reply = llama_chat(get_prompt(summary))
print(reply)

if not reply.strip():
    sys.exit("Model returned an empty reply")

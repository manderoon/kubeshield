# Ask llama about a real scan summary and see it replies
import json
import sys
from pathlib import Path

from kubeshield.features import kubescape_report_summary
from kubeshield.model import get_prompt, llama_chat

report = Path(__file__).parent.parent / "fixtures" / "kubescape-report.json"
summary = kubescape_report_summary(json.loads(report.read_text()))

reply = llama_chat(get_prompt(summary))
print(reply)

if not reply.strip():
    sys.exit("Model returned an empty reply")

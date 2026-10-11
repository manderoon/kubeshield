# Scan the cluster, ask the model for fixes and check it gives some
import json
import sys

from kubeshield.features import kubescape_report_summary
from kubeshield.model import get_prompt, llama_chat
from kubeshield.scanner import kubescape_scan

summary = kubescape_report_summary(kubescape_scan())

reply = llama_chat(get_prompt(summary))
print(json.dumps(reply, indent=2))

if not reply["assessment"].strip():
    sys.exit("Model returned an empty assessment")
if not reply["fixes"]:
    sys.exit("Model returned no fixes")

#!/usr/bin/env bash

# Call /scan

set -euo pipefail

curl --silent --fail --max-time 180 http://localhost:8000/scan --output scan.json

python3 -m json.tool scan.json

python3 - <<'EOF'
import json
import sys

result = json.load(open("scan.json"))
failed = result["top_failed_controls"]

print(f"OK: scan found {len(failed)} failed controls")
EOF

import json
import subprocess
import tempfile

from kubeshield.errors import KubeshieldError, UpstreamError, UpstreamTimeoutError

TIMEOUT = 120

def kubescape_scan() -> dict:
    """
    Runs kubescape scan against the current kube-context
    Returns parsed JSON report
    """
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        cmd = ["kubescape", "scan", "--format", "json", "--output", tmp.name]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT, check=False)
        except FileNotFoundError:
            raise KubeshieldError("kubescape not found") from None
        except subprocess.TimeoutExpired:
            raise UpstreamTimeoutError(f"kubescape scan timed out after {TIMEOUT} seconds") from None

        try:
            with open(tmp.name) as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise UpstreamError(f"kubescape scan failed: {result.stderr}") from None

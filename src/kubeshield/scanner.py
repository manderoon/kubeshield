import json
import shutil
import subprocess
import tempfile

TIMEOUT = 120

def kubescape_scan():
    """
    Runs kubescape scan against kube-context
    Returns parsed JSON report
    """

    if shutil.which("kubescape") is None:
        raise RuntimeError("Kubescape not found")

    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        cmd = [
            "kubescape",
            "scan",
            "--format",
            "json",
            "--output",
            tmp.name,
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=TIMEOUT
            )
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"kubescape scan timed out: {TIMEOUT} seconds")

        try:
            with open(tmp.name) as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise RuntimeError(f"kubescape scan failed: {result.stderr}")
    
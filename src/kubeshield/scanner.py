import json
import shutil
import subprocess
import tempfile


def kubescape_scan():
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
        result = subprocess.run(cmd, capture_output=True, text=True)

        try:
            with open(tmp.name) as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise RuntimeError(f"kubescape scan failed: {result.stderr}")
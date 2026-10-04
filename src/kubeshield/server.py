from fastapi import FastAPI, HTTPException
from kubeshield.scanner import kubescape_scan

app = FastAPI(title="Kubeshield")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/scan")
def scan():
    try:
        return kubescape_scan()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

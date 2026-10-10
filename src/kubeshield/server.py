from fastapi import FastAPI, HTTPException
from kubeshield.features import kubescape_report_summary
from kubeshield.model import get_prompt, llama_chat
from kubeshield.scanner import kubescape_scan

app = FastAPI(title="Kubeshield")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/scan")
def scan():
    try:
        report = kubescape_scan()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return kubescape_report_summary(report)

@app.get("/assess")
def assess():
    summary = scan()
    return {"summary": summary, "assessment": llama_chat(get_prompt(summary))}

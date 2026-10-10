from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from kubeshield.errors import KubeshieldError
from kubeshield.features import kubescape_report_summary
from kubeshield.model import get_prompt, llama_chat
from kubeshield.scanner import kubescape_scan

app = FastAPI(title="Kubeshield")

@app.exception_handler(KubeshieldError)
def error_handler(request: Request, e: KubeshieldError) -> JSONResponse:
    return JSONResponse(status_code=e.status_code, content={"detail": str(e)})

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/scan")
def scan():
    return kubescape_report_summary(kubescape_scan())

@app.get("/assess")
def assess():
    summary = scan()
    return {"summary": summary, "assessment": llama_chat(get_prompt(summary))}

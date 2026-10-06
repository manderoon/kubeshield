# kubeshield

Run server

```bash
uv run uvicorn kubeshield.server:app --reload
```

Example output from `/scan`

```JSON
{
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
```

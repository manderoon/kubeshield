# kubeshield

## Research

TODO: Add info about kube + security.

TODO: Add info about types of kube analysers (static/dynamic/etc)

The literature suggests that although `kubescape` has a larger rule set, `trivy` detects more misconfigurations. However, `kubescape` was found to be most stable in terms of similarity to expert ratings (Krieger et al., 2026).

Krieger, M., Gierlinger, M., Shaikh, F., & Kahlhofer, M. (2026).
[A Comparison of Kubernetes Compliance Standards and Configuration Scanners](https://arxiv.org/abs/2606.24438v1).
arXiv:2606.24438.

----------------

## Code

Run server

```bash
uv run uvicorn kubeshield.server:app --reload
```

Example output from `/scan`, with `failed_controls` sorted by most severe

```JSON
{
    "compliance_score": 64.52465,
    "failed_resources_by_severity": {
        "critical": 0,
        "high": 46,
        "medium": 153,
        "low": 8
    },
    "failed_controls": [
        "Ensure CPU limits are set",
        "Ensure memory limits are set",
        "Writable hostPath mount",
        "Applications credentials in configuration files",
        "Privileged container",
        ["..."]
    ]
}
```

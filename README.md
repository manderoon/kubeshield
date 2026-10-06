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

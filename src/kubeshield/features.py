SYSTEM_NAMESPACES = {"kube-system", "kube-public", "kube-node-lease", "local-path-storage"}
# Built-in cluster-wide resources, like ClusterRoleBindings, have no namespace
SYSTEM_NAME_PREFIXES = ("system:", "kubeadm:")


def kubescape_change(path: dict) -> str | None:
    """
    Return the change a kubescape path suggests or 
    none if theres no suggestion
    """
    if path.get("deletePath"):
        return f"delete {path['deletePath']}"
    if path.get("fixPath", {}).get("path"):
        return f"set {path['fixPath']['path']} = {path['fixPath']['value']}"
    return None


def kubescape_fixes(report: dict, control_id: str) -> list[dict]:
    """
    Get the resources failing a control with the changes kubescape says fix it
    Skip system namespaces, since changing those can break the cluster!!
    """
    fixes = []
    for result in report["results"]:
        # Looks like: apps/v1/default/Deployment/web
        _, namespace, kind, name = result["resourceID"].rsplit("/", 3)
        if namespace in SYSTEM_NAMESPACES or name.startswith(SYSTEM_NAME_PREFIXES):
            continue
        for c in result["controls"]:
            if c["controlID"] != control_id or c["status"]["status"] != "failed":
                continue
            paths = [p for rule in c["rules"] for p in rule.get("paths") or []]
            changes = [change for p in paths if (change := kubescape_change(p))]
            if changes:
                fixes.append({"resource": f"{kind} {namespace}/{name}", "changes": changes})
    return fixes


def kubescape_report_summary(report: dict) -> dict:
    """
    Extract features we care about from the full kubescape JSON output
    """
    summary = report["summaryDetails"]
    severity_counts = summary["resourcesSeverityCounters"]

    failed_controls = [c for c in summary["controls"].values() if c["status"] == "failed"]
    # Filter data, most severe first, then the ones failing on the most resources
    failed_controls.sort(
        key=lambda c: (c["scoreFactor"], c["ResourceCounters"]["failedResources"]),
        reverse=True,
    )

    return {
        "compliance_score": summary["complianceScore"],
        "failed_resources_by_severity": {
            "critical": severity_counts["criticalSeverity"],
            "high": severity_counts["highSeverity"],
            "medium": severity_counts["mediumSeverity"],
            "low": severity_counts["lowSeverity"],
        },
        "failed_controls": [
            {
                "id": c["controlID"],
                "name": c["name"],
                "severity": c["severity"],
                "fixes": kubescape_fixes(report, c["controlID"]),
            }
            for c in failed_controls
        ],
    }

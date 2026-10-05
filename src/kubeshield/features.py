def kubescape_report_summary(report: dict) -> dict:
    """
    Extract features we care about from the full
    kubescape JSON output
    """
    summary = report.get("summaryDetails", {})

    severity_counts = (
        summary.get("resourcesSeverityCounters")
        or summary.get("controlsSeverityCounters")
        or {}
    )

    compliance_score = summary.get("complianceScore")
    if compliance_score is None:
        compliance_score = summary.get("score", 0)

    controls = summary.get("controls", {}) or {}
    failed_controls = [
        control.get("name", control.get("controlID", "?"))
        for control in controls.values()
        if control.get("status") == "failed"
    ]

    return {
        "compliance_score": compliance_score,
        "failed_resources_by_severity": {
            "critical": severity_counts.get("criticalSeverity", 0),
            "high": severity_counts.get("highSeverity", 0),
            "medium": severity_counts.get("mediumSeverity", 0),
            "low": severity_counts.get("lowSeverity", 0),
        },
        "top_failed_controls": failed_controls[:5],
    }

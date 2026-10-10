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
                "name": c["name"],
                "severity": c["severity"],
                "failed_resources": c["ResourceCounters"]["failedResources"],
            }
            for c in failed_controls
        ],
    }

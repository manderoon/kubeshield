# kubeshield

Scan a Kubernetes cluster with [kubescape](https://github.com/kubescape/kubescape) and get a local LLM inference server to provide a security assessment with suggested fixes.

## Contents

- [Setting up](#setting-up)
- [Research](#research)

------------------------------

## Setting up

### Requirements

- `uv`
- `kubescape`
- Docker
- A local kube cluster (`kind`)

### Start a cluster

  ```bash
  kind create cluster
  kubectl apply -f tests/ci/vuln-test-workload.yaml
  ```

### Start Ollama

```bash
docker run -d --name ollama -p 11434:11434 ollama/ollama
docker exec ollama ollama pull llama3.2:1b
```

### Start the server

```bash
uv run kubeshield
```

### Server Endpoints

- `GET /health` --> returns status
- `GET /scan` --> returns `kubescape` summary
- `GET /assess`  --> returns LLM output

```bash
curl localhost:8000/assess
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

`/assess` returns the same summary with the model's reply:

```JSON
{
    "summary": { "compliance_score": 64.52465, ... },
    "assessment": "<LLM output>"
}
```

### Tests

```bash
uv run pytest
uv run ruff check
```

--------------------------------------

## Research

### Kubernetes misconfigurations

Kubernetes security is often framed in terms of the 4Cs: cloud, cluster, container and code. Each layer depends on the security of the layer around it.

![The 4Cs of Cloud Native Security](https://raw.githubusercontent.com/kubernetes/website/60266ff1a9/static/images/docs/4c.png)

*Image: Kubernetes Documentation (2019), CC BY 4.0.*

A common weakness across all layers of the 4Cs is misconfiguration, and the literature shows how widespread it is:

- Rahman et al. (2023) explore around 2000 open source Kubernetes manifests and detect over 1000 misconfigurations.
- Minna et al. (2025) find similar results in Helm charts, with over 90 per cent containing at least one misconfiguration.
- Bufalino et al. (2025) find over 600 network misconfigurations across almost 300 open source applications.

These kinds of misconfigurations could enable lateral movement and privilege escalation by an attacker who has compromised a container (Bufalino et al., 2025; Lin et al., 2018).

Although misconfigurations can have significant consequences, they are often not reported. Bose et al. (2021) find that less than 1 per cent of commits to Kubernetes manifests are related to security and suggest that security concerns are underreported.

### Detecting misconfigurations

The literature suggests that although `kubescape` has a larger rule set, `trivy` detects more misconfigurations. However, `kubescape` was found to be most stable in terms of similarity to expert ratings (Krieger et al., 2026). As a result, `kubescape` was used for this project.

### Fixing misconfigurations with LLMs

`kubeshield` scans a live cluster and uses an LLM to explain the findings and suggest fixes. This approach is supported by recent research:

- Ye et al. (2025) give LLMs the output of static analysis tools and fix almost 95 per cent of container misconfigurations.
- Malul et al. (2024) use local models so that configuration files aren't sent to external APIs.

It should be noted that LLMs are also capable of introducing novel errors. Ghorab et al. (2026) find that comparing changes with the Kubernetes schema increases repair accuracy from around 89 to almost 99 per cent.

### References

Bose, D. B., Rahman, A., & Shamim, S. I. (2021).
[Under-reported security defects in Kubernetes manifests](https://par.nsf.gov/biblio/10274696).
*2nd IEEE/ACM International Workshop on Engineering and Cybersecurity of Critical Systems (EnCyCriS)*.

Bufalino, J., Martin-Navarro, J. L., Di Francesco, M., & Aura, T. (2025).
[Inside Job: Defending Kubernetes clusters against network misconfigurations](https://arxiv.org/abs/2506.21134).
*arXiv preprint* arXiv:2506.21134.

Ghorab, M. A., Latif, A. A., & Saied, M. A. (2026).
[Kubernetes misconfigurations in the wild: Taxonomy, evolution, and automated repair with large language models](https://arxiv.org/abs/2609.27030).
*3rd ACM International Conference on AI-Powered Software (AIware)*.

Krieger, M., Gierlinger, M., Shaikh, F., & Kahlhofer, M. (2026).
[A comparison of Kubernetes compliance standards and configuration scanners](https://arxiv.org/abs/2606.24438).
*arXiv preprint* arXiv:2606.24438.

Lin, X., Lei, L., Wang, Y., Jing, J., Sun, K., & Zhou, Q. (2018).
[A measurement study on Linux container security: Attacks and countermeasures](https://par.nsf.gov/servlets/purl/10097627).
*34th Annual Computer Security Applications Conference (ACSAC)*.

Malul, E., Meidan, Y., Mimran, D., Elovici, Y., & Shabtai, A. (2024).
[GenKubeSec: LLM-based Kubernetes misconfiguration detection, localization, reasoning, and remediation](https://arxiv.org/abs/2405.19954).
*arXiv preprint* arXiv:2405.19954.

Minna, F., Massacci, F., & Tuma, K. (2025).
[Analyzing and mitigating (with LLMs) the security misconfigurations of Helm charts from Artifact Hub](https://doi.org/10.1007/s10664-025-10688-0).
*Empirical Software Engineering*, 30(5), 132.

Rahman, A., Shamim, S. I., Bose, D. B., & Pandita, R. (2023).
[Security misconfigurations in open source Kubernetes manifests: An empirical study](https://doi.org/10.1145/3579639).
*ACM Transactions on Software Engineering and Methodology*.

Ye, Z., Le, T. H. M., & Babar, M. A. (2025).
[LLMSecConfig: An LLM-based approach for fixing software container misconfigurations](https://arxiv.org/abs/2502.02009).
*arXiv preprint* arXiv:2502.02009.

#!/usr/bin/env bash

# Deploy the vulnerable demo workload into the cluster
set -euo pipefail

kubectl apply -f manifests/vuln-test-workload.yaml
kubectl rollout status deployment/vuln-test-workload --timeout=90s

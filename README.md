# Defense GitOps Pipeline

[![CI](https://github.com/skytruong90/Defense-GitOps-Pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/skytruong90/Defense-GitOps-Pipeline/actions/workflows/ci.yml)

A secure GitOps reference project that treats Kubernetes deployment configuration as reviewed, policy-checked code. The repository includes a hardened sample workload, a deterministic admission-style policy validator, automated tests, and a CI gate that rejects common container and manifest security mistakes before deployment.

> This project validates configuration only. It does not connect to or deploy into a live Kubernetes cluster.

## Security gates

The validator requires:

- images pinned by digest rather than mutable tags
- `runAsNonRoot: true`
- `allowPrivilegeEscalation: false`
- `readOnlyRootFilesystem: true`
- dropped Linux capabilities
- CPU and memory requests/limits
- a non-default namespace
- readiness and liveness probes

## Pipeline

```text
Git change
   |
   v
Kubernetes manifest
   |
   v
syntax / policy checks
   |
   +---- fail ---> CI blocks change
   |
   v
unit tests
   |
   v
validated GitOps artifact
```

## Quick start

Python 3.10+; standard library only.

```bash
python src/validate_manifests.py manifests/app.yaml
```

A successful run prints:

```text
PASS manifests/app.yaml: 0 policy violations
```

To test a change, edit the manifest and run the validator before committing.

## Repository layout

```text
Defense-GitOps-Pipeline/
├── manifests/app.yaml
├── src/validate_manifests.py
├── tests/test_policy.py
├── .github/workflows/ci.yml
└── README.md
```

## Why this matters

GitOps makes Git the source of truth, but Git alone does not make a deployment safe. A production pipeline also needs deterministic controls that prevent known-bad configuration from advancing. This project models that control point as a small policy engine that can later be replaced or complemented by Kyverno, Gatekeeper/OPA, Conftest, admission controllers, image-signature verification, and a real deployment reconciler.

## Next extensions

- Kustomize overlays for dev/test/prod
- Kyverno or OPA/Rego equivalents of each rule
- SBOM and image-signature verification
- SAST/SCA/container-image scanning stages
- GitHub environment approvals
- Argo CD or Flux reconciliation
- deployment provenance and artifact attestations

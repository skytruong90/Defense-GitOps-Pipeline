#!/usr/bin/env python3
"""Dependency-free policy gate for the sample Kubernetes GitOps manifest."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def validate_text(text: str) -> list[str]:
    violations: list[str] = []
    lowered = text.lower()

    image_matches = re.findall(r"^\s*image:\s*(\S+)\s*$", text, flags=re.MULTILINE)
    if not image_matches:
        violations.append("deployment must declare at least one container image")
    for image in image_matches:
        if "@sha256:" not in image:
            violations.append(f"image must be pinned by sha256 digest: {image}")

    required_fragments = {
        "runAsNonRoot: true": "pod/container must run as non-root",
        "allowPrivilegeEscalation: false": "privilege escalation must be disabled",
        "readOnlyRootFilesystem: true": "root filesystem must be read-only",
        "drop:\n                - ALL": "all Linux capabilities must be dropped",
        "requests:": "resource requests are required",
        "limits:": "resource limits are required",
        "readinessProbe:": "readiness probe is required",
        "livenessProbe:": "liveness probe is required",
    }
    for fragment, message in required_fragments.items():
        if fragment not in text:
            violations.append(message)

    namespaces = re.findall(r"^\s*namespace:\s*(\S+)\s*$", text, flags=re.MULTILINE)
    if not namespaces:
        violations.append("workload namespace is required")
    elif any(ns == "default" for ns in namespaces):
        violations.append("default namespace is not allowed")

    if ":latest" in lowered:
        violations.append("mutable latest tag is not allowed")
    if "privileged: true" in lowered:
        violations.append("privileged containers are not allowed")
    if "hostnetwork: true" in lowered:
        violations.append("hostNetwork is not allowed")

    return violations


def validate_file(path: Path) -> list[str]:
    return validate_text(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Kubernetes manifests against repository security policy")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    failed = False
    for path in args.paths:
        violations = validate_file(path)
        if violations:
            failed = True
            print(f"FAIL {path}: {len(violations)} policy violation(s)")
            for violation in violations:
                print(f"  - {violation}")
        else:
            print(f"PASS {path}: 0 policy violations")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

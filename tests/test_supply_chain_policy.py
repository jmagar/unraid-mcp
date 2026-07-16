"""Executable policy for privileged workflows and shipped artifacts."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def _workflows() -> dict[str, str]:
    return {path.name: path.read_text() for path in sorted(WORKFLOWS.glob("*.yml"))}


def test_every_external_action_is_immutable() -> None:
    violations: list[str] = []
    for name, workflow in _workflows().items():
        for line in workflow.splitlines():
            match = re.search(r"\buses:\s*([^\s#]+)", line)
            if match and not re.fullmatch(r"[^@]+@[0-9a-f]{40}", match.group(1)):
                violations.append(f"{name}: {match.group(1)}")
    assert not violations, f"mutable action references: {violations}"


def test_openwiki_generation_is_locked_and_separated_from_repository_write() -> None:
    workflow = _workflows()["openwiki-update.yml"]
    lock = (ROOT / "scripts" / "openwiki" / "package-lock.json").read_text()
    assert '"openwiki": "0.1.2"' in lock
    assert "npm ci --prefix scripts/openwiki --ignore-scripts" in workflow
    assert "npm install --global" not in workflow
    assert "persist-credentials: false" in workflow
    assert 'source "$env_file"' not in workflow
    generate = workflow.split("  generate:", 1)[1].split("  propose:", 1)[0]
    propose = workflow.split("  propose:", 1)[1]
    assert "OPENAI_COMPATIBLE_API_KEY" in generate
    assert "contents: write" not in generate
    assert "pull-requests: write" not in generate
    assert "OPENAI_COMPATIBLE_API_KEY" not in propose
    assert "TS_OAUTH_SECRET" not in propose
    assert "contents: write" in propose
    assert "pull-requests: write" in propose


def test_audit_targets_locked_application_graph() -> None:
    workflow = _workflows()["ci.yml"]
    assert "uv export --frozen --no-dev --no-emit-project" in workflow
    assert "pip-audit==2.10.1" in workflow
    assert "pip-audit --requirement audit-requirements.txt" in workflow
    for sentinel in ("fastmcp", "httpx", "cryptography"):
        assert sentinel in workflow
    assert "uvx pip-audit" not in workflow


def test_release_executables_and_tools_are_pinned_and_verified() -> None:
    combined = "\n".join(_workflows().values())
    assert "/releases/latest/download/" not in combined
    assert not re.search(r"curl[^\n|]*\|\s*(?:sh|bash|tar)\b", combined)
    release = _workflows()["publish-pypi.yml"]
    assert "/releases/download/v1.8.0/" in release
    assert "1370446bbe74d562608e8005a6ccce02d146a661fbd78674e11cc70b9618d6cf" in release
    assert "sha256sum --check --strict" in release


def test_release_sensitive_uv_is_pinned_and_cacheless() -> None:
    for name in (
        "publish-pypi.yml",
        "release-please.yml",
        "schema-drift.yml",
        "claude-schema-drift.yml",
    ):
        workflow = _workflows()[name]
        setup_steps = workflow.split("uses: astral-sh/setup-uv@")[1:]
        assert setup_steps, name
        for step in setup_steps:
            step = step.split("\n      - ", 1)[0]
            assert 'version: "0.9.25"' in step, name
            assert "enable-cache: false" in step, name


def test_artifact_channels_are_independent_and_reconciled() -> None:
    workflow = _workflows()["publish-pypi.yml"]
    for job in ("build", "pypi", "github-release", "mcp-registry", "reconcile"):
        assert re.search(rf"^  {re.escape(job)}:\s*$", workflow, re.MULTILINE)
    assert "SHA256SUMS" in workflow
    assert "actions/attest-build-provenance@" in workflow
    assert "skip-existing: true" in workflow
    assert "Release Reconciliation" in workflow


def test_container_release_and_runtime_policies() -> None:
    workflow = _workflows()["docker-publish.yml"]
    dockerfile = (ROOT / "Dockerfile").read_text()
    compose = (ROOT / "docker-compose.yaml").read_text()
    assert "type=raw,value=edge" in workflow
    assert "type=raw,value=latest" in workflow
    assert "startsWith(github.ref, 'refs/tags/v')" in workflow
    assert "Container Artifact Smoke & Scan" in workflow
    assert "tests/test_live.sh --mode http" in workflow
    assert "/ready" in workflow
    assert "python:3.12.11-slim-bookworm@sha256:" in dockerfile
    assert "/ready" in dockerfile
    assert "replicas: 1" in compose
    assert 'max-size: "10m"' in compose
    assert 'max-file: "3"' in compose


def test_schema_agent_has_immutable_input_and_path_boundary() -> None:
    detector = _workflows()["schema-drift.yml"]
    implementer = _workflows()["claude-schema-drift.yml"]
    policy = (ROOT / "scripts" / "validate-schema-agent-paths.sh").read_text()
    assert "gh api repos/unraid/api/commits/main --jq .sha" in detector
    assert "upstream_commit" in detector
    assert "upstream_commit" in implementer
    assert "sha256sum --check --strict" in implementer
    assert "persist-credentials: false" in implementer
    assert "git -c credential.helper='!gh auth git-credential' push" in implementer
    assert implementer.count("validate-schema-agent-paths.sh") == 2
    assert "unraid_mcp/subscriptions/queries.py" in policy
    assert "unraid_mcp/subscriptions/diagnostics.py" in policy
    for denied in (".github/*", "pyproject.toml", "uv.lock", "unraid_mcp/core/auth.py"):
        assert denied in policy

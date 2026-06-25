from pathlib import Path


WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"


def test_schema_drift_dispatches_claude_workflow_with_issue_context() -> None:
    schema_drift = (WORKFLOWS / "schema-drift.yml").read_text(encoding="utf-8")

    assert "actions: write" in schema_drift
    assert "id: issue" in schema_drift
    assert "sha256sum upstream-schema.graphql" in schema_drift
    assert "upstream-schema-sha256:" in schema_drift
    assert "dispatch_claude=true" in schema_drift
    assert "dispatch_claude=false" in schema_drift
    assert "gh workflow run claude-schema-drift.yml" in schema_drift
    assert 'issue_number="${{ steps.issue.outputs.issue_number }}"' in schema_drift
    assert 'schema_hash="${{ steps.issue.outputs.schema_hash }}"' in schema_drift


def test_claude_schema_drift_workflow_can_write_branch_pr_and_issue() -> None:
    workflow = (WORKFLOWS / "claude-schema-drift.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "issue_number:" in workflow
    assert "schema_hash:" in workflow
    assert "contents: write" in workflow
    assert "pull-requests: write" in workflow
    assert "issues: write" in workflow
    assert "actions: read" in workflow
    assert "uses: anthropics/claude-code-action@v1" in workflow
    assert "claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}" in workflow
    assert "Read issue #${{ inputs.issue_number }}" in workflow
    assert "open a pull request" in workflow

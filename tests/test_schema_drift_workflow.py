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
    assert "additional_permissions: |\n            actions: read" in workflow
    assert "additional_permissions: |\n            actions: read\n            contents: write" not in workflow
    assert "Prepare Claude branch and draft PR" in workflow
    assert 'branch_name="claude/schema-drift-${ISSUE_NUMBER}-${GITHUB_RUN_ID}"' in workflow
    assert "git commit --allow-empty" in workflow
    assert 'prepared_sha="$(git rev-parse HEAD)"' in workflow
    assert "gh pr create \\" in workflow
    assert "CLAUDE_BRANCH: ${{ steps.prepare.outputs.branch_name }}" in workflow
    assert "display_report: true" in workflow
    assert "--max-turns" not in workflow
    assert "--allowedTools" in workflow
    assert "Bash(git:*)" in workflow
    assert "Bash(gh:*)" in workflow
    assert "Edit,MultiEdit,Write,Read" in workflow
    assert "Read issue #${{ inputs.issue_number }}" in workflow
    assert "Commit and push changes to `${{ steps.prepare.outputs.branch_name }}`" in workflow
    assert "Verify Claude updated the draft PR" in workflow
    assert "steps.prepare.outputs.branch_name" in workflow
    assert "branch_sha=" in workflow
    assert "gh pr list \\" in workflow
    assert "Claude completed without pushing changes" in workflow
    assert "Claude pushed schema drift changes" in workflow

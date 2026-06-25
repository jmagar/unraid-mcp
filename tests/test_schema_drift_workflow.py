from pathlib import Path


WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"
CHECKOUT_SHA = "34e114876b0b11c390a56381ad16ebd13914f8d5"
CLAUDE_ACTION_SHA = "353cf256821e54f4bc89e4c7246f4c938acfb1cc"


def test_schema_drift_dispatches_claude_workflow_with_issue_context() -> None:
    schema_drift = (WORKFLOWS / "schema-drift.yml").read_text(encoding="utf-8")

    assert "actions: write" in schema_drift
    assert "id: issue" in schema_drift
    assert "astral-sh/setup-uv@d0d8abe699bfb85fec6de9f7adb5ae17292296ff" in schema_drift
    assert "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02" in schema_drift
    assert "sha256sum upstream-schema.graphql" in schema_drift
    assert "upstream-schema-sha256:" in schema_drift
    assert "schema-drift" in schema_drift
    assert "max_body_bytes=60000" in schema_drift
    assert "append_with_budget schema-summary.md" in schema_drift
    assert "append_with_budget schema.diff" in schema_drift
    assert "unraid-schema-drift-${GITHUB_RUN_ID}" in schema_drift
    assert 'contains(\\"<!-- upstream-schema-sha256:\\")' in schema_drift
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
    assert f"uses: actions/checkout@{CHECKOUT_SHA}" in workflow
    assert f"uses: anthropics/claude-code-action@{CLAUDE_ACTION_SHA}" in workflow
    assert "anthropics/claude-code-action@v1" not in workflow
    assert "actions/checkout@v4" not in workflow
    assert "claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}" in workflow
    assert "additional_permissions: |\n            actions: read" in workflow
    assert "additional_permissions: |\n            actions: read\n            contents: write" not in workflow
    assert "Prepare Claude branch and draft PR" in workflow
    assert 'branch_name="claude/schema-drift-${ISSUE_NUMBER}-${GITHUB_RUN_ID}"' in workflow
    assert "git commit --allow-empty" in workflow
    assert 'prepared_sha="$(git rev-parse HEAD)"' in workflow
    assert "gh pr create \\" in workflow
    assert "existing_pr_url=" in workflow
    assert 'startswith(\\"claude/schema-drift-${ISSUE_NUMBER}-\\")' in workflow
    assert "should_run=false" in workflow
    assert "steps.prepare.outputs.should_run == 'true'" in workflow
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
    assert "GH_TOKEN: ${{ github.token }}" in workflow
    assert "GH_TOKEN: ${{ steps.claude.outputs.github_token || github.token }}" not in workflow
    assert "steps.prepare.outputs.branch_name" in workflow
    assert "branch_sha=" in workflow
    assert "gh pr list \\" in workflow
    assert "Claude completed without pushing changes" in workflow
    assert "Claude pushed schema drift changes" in workflow


def test_sensitive_workflows_pin_privileged_actions() -> None:
    sensitive_workflows = [
        "claude.yml",
        "claude-code-review.yml",
        "claude-schema-drift.yml",
        "release-please.yml",
        "schema-drift.yml",
    ]
    combined = "\n".join(
        (WORKFLOWS / workflow).read_text(encoding="utf-8")
        for workflow in sensitive_workflows
    )

    assert "actions/checkout@v4" not in combined
    assert "anthropics/claude-code-action@v1" not in combined
    assert "googleapis/release-please-action@v5" not in combined
    assert f"actions/checkout@{CHECKOUT_SHA}" in combined
    assert f"anthropics/claude-code-action@{CLAUDE_ACTION_SHA}" in combined
    assert "googleapis/release-please-action@0dfd8538845b8e92600d271a895a5372865d4062" in combined

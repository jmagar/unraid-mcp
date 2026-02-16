# Destructive Actions Inventory

This file lists all destructive actions across the unraid-mcp tools. Fill in the "Testing Strategy" column to specify how each should be tested in the mcporter integration test suite.

**Last Updated:** 2026-02-15

---

## Summary

- **Total Destructive Actions:** 8 (after removing 4 array operations)
- **Tools with Destructive Actions:** 6
- **Environment Variable Gates:** 6 (one per tool)

---

## Destructive Actions by Tool

### 1. Docker (1 action)

| Action | Description | Risk Level | Env Var Gate | Testing Strategy |
|--------|-------------|------------|--------------|------------------|
| `remove` | Permanently delete a Docker container | **HIGH** - Data loss, irreversible | `UNRAID_ALLOW_DOCKER_DESTRUCTIVE` | **TODO: Specify testing approach** |

**Notes:**
- Container must be stopped first
- Removes container config and any non-volume data
- Cannot be undone

---

### 2. Virtual Machines (2 actions)

| Action | Description | Risk Level | Env Var Gate | Testing Strategy |
|--------|-------------|------------|--------------|------------------|
| `force_stop` | Forcefully power off a running VM (equivalent to pulling power cord) | **MEDIUM** - Severe but recoverable, risk of data corruption | `UNRAID_ALLOW_VM_DESTRUCTIVE` | **TODO: Specify testing approach** |
| `reset` | Hard reset a VM (power cycle without graceful shutdown) | **MEDIUM** - Severe but recoverable, risk of data corruption | `UNRAID_ALLOW_VM_DESTRUCTIVE` | **TODO: Specify testing approach** |

**Notes:**
- Both bypass graceful shutdown procedures
- May corrupt VM filesystem if used during write operations
- Use `stop` action instead for graceful shutdown

---

### 3. Notifications (2 actions)

| Action | Description | Risk Level | Env Var Gate | Testing Strategy |
|--------|-------------|------------|--------------|------------------|
| `delete` | Permanently delete a notification | **HIGH** - Data loss, irreversible | `UNRAID_ALLOW_NOTIFICATIONS_DESTRUCTIVE` | **TODO: Specify testing approach** |
| `delete_archived` | Permanently delete all archived notifications | **HIGH** - Bulk data loss, irreversible | `UNRAID_ALLOW_NOTIFICATIONS_DESTRUCTIVE` | **TODO: Specify testing approach** |

**Notes:**
- Cannot recover deleted notifications
- `delete_archived` affects ALL archived notifications (bulk operation)

---

### 4. Rclone (1 action)

| Action | Description | Risk Level | Env Var Gate | Testing Strategy |
|--------|-------------|------------|--------------|------------------|
| `delete_remote` | Permanently delete an rclone remote configuration | **HIGH** - Data loss, irreversible | `UNRAID_ALLOW_RCLONE_DESTRUCTIVE` | **TODO: Specify testing approach** |

**Notes:**
- Removes cloud storage connection configuration
- Does NOT delete data in the remote storage
- Must reconfigure remote from scratch if deleted

---

### 5. Users (1 action)

| Action | Description | Risk Level | Env Var Gate | Testing Strategy |
|--------|-------------|------------|--------------|------------------|
| `delete` | Permanently delete a user account | **HIGH** - Data loss, irreversible | `UNRAID_ALLOW_USERS_DESTRUCTIVE` | **TODO: Specify testing approach** |

**Notes:**
- Removes user account and permissions
- Cannot delete the root user
- User's data may remain but become orphaned

---

### 6. API Keys (1 action)

| Action | Description | Risk Level | Env Var Gate | Testing Strategy |
|--------|-------------|------------|--------------|------------------|
| `delete` | Permanently delete an API key | **HIGH** - Data loss, irreversible, breaks integrations | `UNRAID_ALLOW_KEYS_DESTRUCTIVE` | **TODO: Specify testing approach** |

**Notes:**
- Immediately revokes API key access
- Will break any integrations using the deleted key
- Cannot be undone - must create new key

---

## Removed Actions (No Longer Exposed)

These actions were previously marked as destructive but have been **removed** from the array tool per the implementation plan:

| Action | Former Risk Level | Reason for Removal |
|--------|-------------------|-------------------|
| `start` | CRITICAL | System-wide impact - should not be exposed via MCP |
| `stop` | CRITICAL | System-wide impact - should not be exposed via MCP |
| `shutdown` | CRITICAL | System-wide impact - could cause data loss |
| `reboot` | CRITICAL | System-wide impact - disrupts all services |

---

## Testing Strategy Options

Choose one of the following for each action in the "Testing Strategy" column:

### Option 1: Mock/Validation Only
- Test parameter validation
- Test `confirm=True` requirement
- Test env var gate requirement
- **DO NOT** execute the actual action

### Option 2: Dry-Run Testing
- Test with `confirm=false` to verify rejection
- Test without env var to verify gate
- **DO NOT** execute with both gates passed

### Option 3: Test Server Execution
- Execute on a dedicated test Unraid server (e.g., shart)
- Requires pre-created test resources (containers, VMs, notifications)
- Verify action succeeds and state changes as expected
- Clean up after test

### Option 4: Manual Test Checklist
- Document manual verification steps
- Do not automate in mcporter suite
- Requires human operator to execute and verify

### Option 5: Skip Testing
- Too dangerous to automate
- Rely on unit tests only
- Document why testing is skipped

---

## Example Testing Strategies

**Safe approach (recommended for most):**
```
Option 1: Mock/Validation Only
- Verify action requires UNRAID_ALLOW_DOCKER_DESTRUCTIVE=true
- Verify action requires confirm=True
- Do not execute actual deletion
```

**Comprehensive approach (for test server only):**
```
Option 3: Test Server Execution on 'shart'
- Create test container 'mcporter-test-container'
- Execute remove with gates enabled
- Verify container is deleted
- Clean up not needed (container already removed)
```

**Hybrid approach:**
```
Option 1 + Option 4: Mock validation + Manual checklist
- Automated: Test gate requirements
- Manual: Human operator verifies on test server
```

---

## Usage in mcporter Tests

Each tool test script will check the testing strategy:

```bash
# Example from test_docker.sh
test_remove_action() {
    local strategy="TODO: Specify testing approach"  # From this file

    case "$strategy" in
        *"Option 1"*|*"Mock"*)
            # Mock/validation testing
            test_remove_requires_env_var
            test_remove_requires_confirm
            ;;
        *"Option 3"*|*"Test Server"*)
            # Real execution on test server
            if [[ "$UNRAID_TEST_SERVER" != "unraid-shart" ]]; then
                echo "SKIP: Destructive test only runs on test server"
                return 2
            fi
            test_remove_real_execution
            ;;
        *"Option 5"*|*"Skip"*)
            echo "SKIP: Testing disabled for this action"
            return 2
            ;;
    esac
}
```

---

## Security Model

**Two-tier security for destructive actions:**

1. **Environment Variable Gate** (first line of defense)
   - Must be explicitly enabled per tool
   - Defaults to disabled (safe)
   - Prevents accidental execution

2. **Runtime Confirmation** (second line of defense)
   - Must pass `confirm=True` in each call
   - Forces explicit acknowledgment per operation
   - Cannot be cached or preset

**Both must pass for execution.**

---

## Next Steps

1. **Fill in Testing Strategy column** for each action above
2. **Create test fixtures** if using Option 3 (test containers, VMs, etc.)
3. **Implement tool test scripts** following the specified strategies
4. **Document any special setup** required for destructive testing

---

## Questions to Consider

For each action, ask:
- Is this safe to automate on a test server?
- Do we have test fixtures/resources available?
- What cleanup is required after testing?
- What's the blast radius if something goes wrong?
- Can we verify the action worked without side effects?


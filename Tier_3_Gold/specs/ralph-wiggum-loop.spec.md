# Specification: Ralph Wiggum Loop Pattern (Gold Tier)

## Overview

The "Ralph Wiggum Loop" is a persistence pattern for autonomous multi-step task completion without requiring human intervention between steps.

**Name Origin**: "I'm in danger" - Ralph's iconic phrase from The Simpsons represents a looping state machine that keeps trying to escape until it succeeds or hits a timeout.

## Pattern Definition

### Core Concept

Instead of Claude exiting after creating a plan, Claude **persists** in executing until one of these conditions is met:

1. ✅ **Success**: Task completed and moved to /Done
2. ❌ **Blocked**: Task requires human approval (moved to /Pending_Approval)
3. ⏱️ **Timeout**: 30 minutes elapsed for current iteration
4. 🔁 **Max Iterations**: 10 iterations attempted

### State Machine Diagram

```
START
  │
  ├─→ [1] Read task from /Needs_Action
  │         │
  │         ├─→ File not found? STOP (success, already moved)
  │         │
  │         └─→ File found? Continue
  │
  ├─→ [2] Analyze task and create execution plan
  │         │
  │         ├─→ Plan fails? Error → log to /Logs, stay in loop
  │         │
  │         └─→ Plan succeeds? Continue
  │
  ├─→ [3] Execute first subtask
  │         │
  │         ├─→ Blocked by external (API down)?
  │         │   Wait 30 sec, retry (same iteration)
  │         │
  │         ├─→ Requires approval?
  │         │   Move to /Pending_Approval → STOP
  │         │
  │         ├─→ Execution fails?
  │         │   Log error, break into smaller subtask → loop continues
  │         │
  │         └─→ Success? Continue
  │
  ├─→ [4] Execute remaining subtasks
  │         (repeat for each subtask)
  │
  ├─→ [5] Create checklist in task file marking complete
  │
  ├─→ [6] Move task file to /Done
  │
  └─→ STOP (loop exits because file no longer in /Needs_Action)

Safety Mechanisms:
- If iteration count >= 10: STOP (max iterations exceeded)
- If elapsed_time > 30 minutes: STOP (timeout, mark as in-progress)
- If user moves file to /Rejected: STOP immediately
```

### State Transitions

```
/Needs_Action → Loop starts
     ↓
Processing (execution plan) → Subtask 1 → Subtask 2 → ... → Complete?
     ↓                                                            ↓
     ├─────────────────────── NO ─────────────────────────────┤
     │                                                         │
     └─────────────────────── YES ───────────────────────────┬─→ /Done
                                                                   (loop exits)
     Approval Needed? → /Pending_Approval → Await user action
     ↓
User moves to /Approved → Resume loop from /Needs_Action
User moves to /Rejected → /Done (failed)
```

## Implementation

### Pseudocode

```python
def ralph_wiggum_loop(vault_path: Path, max_iterations: int = 10):
    """
    Persistence pattern for multi-step task completion.

    The loop continues until:
    - Task moved to /Done (success)
    - Task moved to /Rejected (failure)
    - Max iterations reached (10)
    - Timeout exceeded (30 minutes per iteration)
    """
    iteration = 0
    start_time = datetime.now()

    while True:
        iteration += 1
        iteration_start = datetime.now()

        # Safety check 1: Max iterations
        if iteration > max_iterations:
            logger.warning(f"Max iterations ({max_iterations}) exceeded")
            return False

        # Safety check 2: Timeout
        if (datetime.now() - start_time).total_seconds() > 30 * 60:
            logger.warning(f"Task timeout (30 minutes) exceeded")
            return False

        # [1] Read task from /Needs_Action
        task_file = vault_path / 'Needs_Action' / '<task_name>.md'
        if not task_file.exists():
            logger.info(f"Task file moved out of Needs_Action - SUCCESS")
            return True  # Task completed or manually processed

        task_content = task_file.read_text()

        # [2] Analyze and create execution plan
        plan = claude.create_plan(task_content)
        if plan.is_invalid():
            logger.error(f"Plan creation failed: {plan.error}")
            continue  # Retry in next iteration

        # [3-4] Execute subtasks
        for subtask in plan.subtasks:
            try:
                result = claude.execute_subtask(subtask)

                if result.requires_approval:
                    # Move to Pending_Approval and STOP looping
                    move_to_pending_approval(task_file, subtask)
                    logger.info(f"Task blocked for approval: {subtask}")
                    return None  # Loop paused

                if result.success:
                    logger.info(f"Subtask complete: {subtask}")
                else:
                    # Break into smaller subtasks
                    logger.info(f"Subtask failed, breaking down further")
                    smaller_subtasks = claude.decompose_subtask(subtask)
                    plan.insert_subtasks(smaller_subtasks)

            except ExternalAPIError as e:
                # Retry on external failures (same iteration)
                logger.warning(f"External API error, retrying: {e}")
                time.sleep(30)
                continue
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                continue

        # [5] Mark all subtasks complete
        task_file_updated = update_task_checklist(task_file, plan)

        # [6] Move to /Done
        done_path = vault_path / 'Done' / task_file.name
        task_file_updated.rename(done_path)

        logger.info(f"Task completed after {iteration} iterations")
        return True  # Loop exits
```

### Key Design Patterns

**1. Atomic State Transitions**
- Only move file between folders after successful execution
- Use atomic rename operation (prevents corruption)
- Always write backup before moving

**2. Error Recovery**
- External API errors: Retry with exponential backoff (same iteration)
- Execution errors: Decompose task into smaller subtasks
- Planning errors: Log and retry in next iteration

**3. HITL Integration**
- When approval needed: Move to /Pending_Approval
- Loop pauses automatically
- Resume when user moves file back to /Needs_Action or /Approved

**4. Timeout Handling**
- Per iteration: 30 minutes (safety for hung processes)
- Total: 5+ hours (10 iterations × 30 min + overhead)
- On timeout: Mark as in-progress, human review required

**5. Logging & Observability**
- Every iteration logged with:
  - Timestamp, iteration number, elapsed time
  - Subtask name and status
  - Errors and recovery attempts
  - Performance metrics (duration per subtask)

## HITL Integration (Constitution Section II)

**When Ralph Wiggum Loop Creates Approval**:

| Scenario | Example | Action |
|----------|---------|--------|
| Payment > $50 | Approve invoice payment | Move to /Pending_Approval |
| New contact (email) | Send reply to unknown sender | Move to /Pending_Approval |
| Financial transaction | Withdraw from account | Move to /Pending_Approval |
| Delete file | Archive folder with data | Move to /Pending_Approval |
| Social media post | Publish to LinkedIn | Move to /Pending_Approval |
| Contract signature | Sign PDF document | Move to /Pending_Approval |

**User Actions**:
- **Move to /Approved**: Resume loop, execute with approval
- **Move to /Rejected**: Move to /Done marked as failed
- **Edit and move to /Needs_Action**: Restart from beginning with modifications

## Tests Required (3 tests for Gold tier)

1. `test_ralph_wiggum_loop_completes_multi_step_task`
   - Verify loop completes a 3+ step task end-to-end
   - Check all subtasks executed in order
   - Verify task moved to /Done
   - Verify audit logs complete

2. `test_ralph_wiggum_loop_respects_max_iterations`
   - Create task that requires >10 iterations to complete
   - Verify loop stops at iteration 10
   - Verify error logged
   - Verify task remains in /Needs_Action (manual review)

3. `test_ralph_wiggum_loop_kill_switch`
   - Start loop on complex task
   - User moves file to /Rejected
   - Verify loop stops immediately
   - Verify task moved to /Done (marked failed)
   - Verify cleanup occurred

## Safety Mechanisms

### Kill Switch
**User can force-stop any loop**:
```bash
# Move task to /Rejected folder
mv /Needs_Action/task.md /Done/task.md
# Loop detects file no longer in /Needs_Action and exits
```

### Timeout
**Automatic timeout after 30 minutes per iteration**:
```python
if iteration_elapsed > 30 * 60:
    logger.error("Iteration timeout - exiting loop")
    break
```

### Max Iterations
**Automatic stop after 10 attempts**:
```python
if iteration > 10:
    logger.error("Max iterations exceeded - manual review required")
    break
```

### Resource Limits
- Memory cap: 500MB (enforced by PM2)
- CPU usage: Monitor and warn if >80%
- Disk space: Fail if <100MB free

## Example: Ralph Wiggum Loop in Action

**Task**: "Generate Q1 2026 Financial Report"

```
Iteration 1:
  [✓] Read task from /Needs_Action
  [✓] Create plan:
      - Fetch invoices from Odoo
      - Calculate revenue metrics
      - Generate charts
      - Create PDF report
  [✓] Execute: Fetch invoices from Odoo
      → Subtask complete (245 invoices retrieved)
  [⏸] Requires approval: Export to /Pending_Approval (wait for user)

[User reviews and approves]

Iteration 2:
  [✓] Read task from /Needs_Action (user moved from /Approved)
  [✓] Plan resume from previous checkpoint
  [✓] Execute: Calculate revenue metrics
      → Subtask complete (metrics calculated)
  [✓] Execute: Generate charts
      → Subtask complete (3 charts created)
  [✓] Execute: Create PDF report
      → Subtask complete (report.pdf created)
  [✓] Update task checklist (all items ✓)
  [✓] Move to /Done
  [✓] Loop exits - SUCCESS

Result: Q1 Report generated and moved to /Done/report.md
Time: 45 minutes across 2 iterations with 1 approval
```

## Monitoring & Alerts

**Metrics to track**:
- Iteration count (warn if > 5)
- Elapsed time (warn if > 20 minutes)
- Subtask execution time (track for optimization)
- Error rates (% of iterations that error)

**Alerts**:
- ⚠️ Warning: Iteration 7/10 - may hit timeout
- ⚠️ Warning: Elapsed 25 min/30 min - approaching timeout
- ❌ Error: Max iterations exceeded - manual review needed
- ❌ Error: Loop killed by user - task rejected

## Limitations & Future Work

1. **No Caching**: Each iteration re-fetches data
   - Future: Implement session cache for multi-iteration tasks

2. **No State Snapshots**: Full re-plan each iteration
   - Future: Save checkpoint after each subtask

3. **No Parallel Subtasks**: Sequential execution only
   - Future: Parallel execution for independent subtasks

4. **No Cross-Task Coordination**: Single task isolation
   - Future: Coordinate multiple Ralph Wiggum loops

---

**Created**: 2026-02-26 | **Status**: Ready for implementation | **Tier**: Gold | **Pattern**: Looping State Machine

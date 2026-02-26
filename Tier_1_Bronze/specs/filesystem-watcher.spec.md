# Specification: Filesystem Watcher (Bronze Tier)

## Overview

The Filesystem Watcher is a Python script that continuously monitors the `/Inbox` folder in the Obsidian vault for new files and automatically processes them through the HITL workflow.

## Purpose

Enable hands-off file management by:
1. Detecting new files in `/Inbox`
2. Moving them to `/Needs_Action` with metadata
3. Creating action request files for Claude to process
4. Maintaining 100% audit trail

## Triggers

- **Event**: New file created in `/Inbox` folder
- **Latency**: <1 second detection via watchdog
- **Continuous**: Runs 24/7 via PM2 process manager

## Input

- **Source**: Any file type in `/Inbox` folder
- **Constraints**: No size limit (will warn if >1GB)
- **Format**: Any format supported by OS (PDF, Word, Excel, images, code, etc.)

## Output

**File Movement**:
```
/Inbox/example.pdf → /Needs_Action/example.pdf
```

**Metadata File Created**:
```
/Needs_Action/example.pdf.md
```

**Metadata Content**:
```yaml
---
type: file_drop
original_name: example.pdf
size_bytes: 1048576
received: 2026-02-26T14:30:00Z
priority: medium
status: pending
---

# File Dropped: example.pdf

A new file has been dropped in the Inbox for processing.

## Suggested Actions
- [ ] Review file contents
- [ ] Categorize file type
- [ ] Process or archive
- [ ] Update Dashboard

## File Location
`Needs_Action/example.pdf`
```

## Implementation Details

**Library**: Python `watchdog` (cross-platform file system monitoring)

**Class**: `FileSystemWatcher` in `filesystem_watcher.py`

**Methods**:
- `__init__(vault_path)` – Initialize watcher with vault location
- `run()` – Start watching and process events
- `on_created()` – Handle file creation event
- `create_metadata()` – Generate metadata .md file

**Configuration**:
- Watch path: `/Inbox/`
- Recursive: False (only top-level files)
- Process manager: PM2 (auto-restart)
- Check interval: 1 second

## Error Handling

| Error | Behavior | Recovery |
|-------|----------|----------|
| File not readable | Log error, skip file | Retry next cycle |
| Metadata write fails | Log error, file still moved | Manual review |
| Permission denied | Log error, alert user | Check folder permissions |
| Disk full | Log critical, pause watcher | Free disk space |

## Performance Targets

- **Latency**: Detect file within 1 second
- **Throughput**: Process 1000 files/day
- **Memory**: <100MB resident
- **CPU**: <5% average
- **Uptime**: 99.5% via PM2

## Testing

Validation tests in `Tier_1_Bronze/tests/test_filesystem_watcher.py`:

1. **test_watcher_detects_file** – File appears in /Inbox
2. **test_watcher_moves_to_needs_action** – File moved to /Needs_Action
3. **test_metadata_created** – .md file created with correct YAML
4. **test_duplicate_handling** – Same file not processed twice
5. **test_pm2_keeps_running** – Process survives crashes

All tests must pass (5/5) before deployment.

## Dependencies

- watchdog==4.0.0
- python-dotenv==1.0.0
- pathlib (stdlib)
- logging (stdlib)

## Compliance

✅ Constitution Section II: File operations auto-approved (reversible)
✅ Audit Logging: Every file movement logged
✅ Error Handling: All exceptions caught and logged
✅ HITL: No approval needed (files just moved to staging)

## Deployment

```bash
pm2 start Tier_1_Bronze/src/watchers/filesystem_watcher.py \
  --name "filesystem-watcher" \
  --interpreter python3 \
  --watch \
  -- "/mnt/d/Hackaton-0/AI_Employee_Vault"
```

## Monitoring

```bash
# Check status
pm2 status filesystem-watcher

# View logs
pm2 logs filesystem-watcher

# Check for errors
pm2 logs filesystem-watcher | grep ERROR
```

---

**Created**: 2026-02-26 | **Status**: ✅ Operational

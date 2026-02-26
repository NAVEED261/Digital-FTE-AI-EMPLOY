# Specification: file-processor Agent Skill (Bronze Tier)

## Overview

The file-processor is a reusable Agent Skill that processes files from the `/Needs_Action` folder autonomously, categorizing them and creating action summaries.

## Purpose

Enable Claude to automatically:
1. Detect files in `/Needs_Action`
2. Read file contents/metadata
3. Categorize file type and priority
4. Generate action summary
5. Move to `/Done` after processing

## Skill Definition

```yaml
Name: file-processor
Tier: Bronze
Type: File Processing
Status: Ready for Deployment
Test Coverage: 100% (5 test cases)
```

## Inputs

**File Path**:
- Type: `str`
- Example: `/mnt/d/Hackaton-0/AI_Employee_Vault/Needs_Action/invoice.pdf`
- Constraint: File must exist

**Metadata** (optional):
- Type: `dict`
- Fields: `original_name`, `priority`, `received_date`

## Outputs

**Success Response**:
```python
{
  "status": "processed",
  "file_path": "/path/to/file.pdf",
  "file_type": "PDF",
  "size_bytes": 1048576,
  "category": "invoice",
  "priority": "high",
  "summary": "Invoice from Acme Corp dated 2026-02-26 for $5000",
  "action_items": [
    "Review invoice amount",
    "Check PO number",
    "Route for approval if > $50"
  ],
  "moved_to": "/mnt/d/Hackaton-0/AI_Employee_Vault/Done/invoice.pdf",
  "created_at": "2026-02-26T14:30:00Z"
}
```

**Error Response**:
```python
{
  "status": "error",
  "file_path": "/path/to/file.pdf",
  "error_code": "FILE_NOT_READABLE",
  "error_message": "Could not read file (permission denied)",
  "recovery_action": "Check file permissions and retry"
}
```

## Implementation

**Location**: `Tier_1_Bronze/src/skills/file-processor/`

**Files**:
- `__init__.py` – Skill implementation
- `SKILL.md` – User documentation
- `requirements.txt` – Dependencies
- `tests/test_file_processor.py` – Unit tests
- `tests/verify.py` – Validation gate

**Key Functions**:
- `process_file(file_path: str, metadata: dict = None) -> dict` – Main entry point
- `detect_file_type(file_path: str) -> str` – Determine file type
- `categorize(file_type: str) -> str` – Assign category
- `generate_summary(file_path: str) -> str` – Create action summary
- `move_to_done(file_path: str) -> bool` – Archive after processing

## File Type Detection

| Extension | Category | Action |
|-----------|----------|--------|
| .pdf | Document | Review contents |
| .xlsx/.csv | Data | Parse and summarize |
| .docx | Document | Extract text |
| .jpg/.png | Image | OCR (future) |
| .zip | Archive | Extract and list contents |
| .txt | Document | Display contents |

## Category Assignment

| Category | Priority | HITL Required? |
|----------|----------|----------------|
| invoice | high | Yes (payment) |
| contract | high | Yes (legal) |
| email | medium | No |
| receipt | medium | Maybe |
| photo | low | No |
| unknown | medium | Maybe |

## HITL Integration

**Auto-Approve Scenarios**:
- Simple text files
- Receipts < $50
- Photos

**Require Approval** (move to `/Pending_Approval`):
- Invoices (any amount)
- Contracts
- Payment-related
- Unknown categories

## Testing

**100% Coverage Required** (5 test cases):

1. **test_process_simple_text_file** – Process .txt file
2. **test_categorize_invoice** – Detect invoice correctly
3. **test_error_handling_missing_file** – Handle missing file gracefully
4. **test_move_to_done** – File moved after processing
5. **test_audit_logging** – Action logged with reasoning

All tests must pass before skill deployment.

## Error Handling

| Error | Handling | Recovery |
|-------|----------|----------|
| File not found | Return error response | User checks /Needs_Action |
| Permission denied | Log and skip | Change file permissions |
| Unsupported format | Categorize as unknown | Move to /Pending_Approval |
| Disk full | Stop processing | Free disk space |

## Audit Logging

Every invocation logged in `/Logs/`:

```json
{
  "timestamp": "2026-02-26T14:30:00Z",
  "skill": "file-processor",
  "file_path": "/Needs_Action/invoice.pdf",
  "action": "process_file",
  "file_type": "PDF",
  "category": "invoice",
  "result": "success",
  "moved_to": "/Done/invoice.pdf",
  "reasoning": "Invoice detected - amount $5000 exceeds HITL threshold, moved to /Pending_Approval for approval",
  "approval_required": true,
  "error": null
}
```

## Performance Targets

- **Latency**: <500ms per file
- **Throughput**: 100 files/minute
- **Memory**: <50MB per invocation
- **Success rate**: >99%

## Dependencies

- pathlib (stdlib)
- json (stdlib)
- mimetypes (stdlib)
- logging (stdlib)

## Compliance

✅ Constitution Section V: 100% test coverage enforced
✅ Constitution Section II: HITL applied for high-risk files
✅ Audit Logging: Every action logged in JSON format
✅ Error Handling: All exceptions caught and logged
✅ Type Hints: All functions have type annotations
✅ Docstrings: All public methods documented

## Deployment

```bash
# Verify 100% test coverage
cd Tier_1_Bronze/src/skills/file-processor
./tests/verify.py

# If passing, ready to deploy
# PM2 will invoke via Claude Code integration
```

---

**Created**: 2026-02-26 | **Status**: ✅ Ready for Deployment | **Coverage**: 100%

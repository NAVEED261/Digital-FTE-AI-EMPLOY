# Agent Skill: file-processor

**Status:** Bronze Tier
**Version:** 1.0
**Created:** 2026-02-16
**Tested:** ✅

---

## Overview

The `file-processor` skill enables Claude Code to autonomously process files dropped in `/Needs_Action` by:
1. Reading file metadata and content
2. Creating a processing plan (Plan.md)
3. Determining next action (immediate execution vs human approval)
4. Moving files to appropriate destination (/Done or /Pending_Approval)

**Use Case:** When a file appears in /Needs_Action, Claude invokes this skill to decide what to do with it.

---

## Invocation

```bash
/file-processor --file-path "Needs_Action/document.txt" --auto-execute
```

Or from Claude Code prompt:
```
claude "Process the file in Needs_Action/important_email.md using /file-processor"
```

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Relative path from vault root (e.g., Needs_Action/file.txt) |
| `auto_execute` | boolean | No | false | If true, execute action if low-risk; else create approval request |
| `priority` | string | No | medium | Override priority: low/medium/high/urgent |

---

## Processing Logic

```
INPUT: file_path (e.g., Needs_Action/report.pdf)
│
├─ READ: File content + metadata
│
├─ ANALYZE: File type, size, content, context
│
├─ PLAN: Determine action
│  ├─ If text/markdown → Parse and summarize
│  ├─ If data (CSV/JSON) → Analyze structure
│  ├─ If binary → Flag for manual review
│  └─ If archive → Extract and categorize
│
├─ DECIDE: Approval needed?
│  ├─ Low risk → Move to /Done with summary
│  └─ High risk → Move to /Pending_Approval with decision request
│
└─ LOG: Record action in Logs/
```

---

## Action Rules

**Auto-Execute (move to /Done immediately):**
- Text files < 1MB, no suspicious content
- Data files with clear structure (CSV, JSON)
- Simple documents from known sources
- Duplicates of previous files

**Approval Required (move to /Pending_Approval):**
- Executable files (.exe, .sh, .jar)
- Files from unknown sources
- Large files (> 50MB)
- Mixed content (embedded executables)
- Files requiring complex decisions

**Escalate 🚨 (flag for immediate attention):**
- Corrupted files
- Permission errors
- Unexpected file types
- Metadata inconsistencies

---

## Output Files

### 1. Plan.md (in /Plans)
```markdown
# Processing Plan: document.pdf

**File:** Needs_Action/document.pdf
**Size:** 2.3 MB
**Type:** PDF Document
**Analyzed:** 2026-02-16 20:15 UTC

## Summary
Document is a business proposal from Acme Corp. Contains:
- 12 pages
- Cost estimate: $50,000
- Timeline: Q2 2026
- Status: Draft (needs review)

## Recommended Action
✅ Store in Archive/Proposals/ for review
- [ ] Review details
- [ ] Discuss with team
- [ ] Provide feedback

## Processing Status
[✓] File analyzed
[✓] Plan created
[ ] Action executed
```

### 2. Result Log (in /Logs/{date}.json)
```json
{
  "timestamp": "2026-02-16T20:15:30Z",
  "watcher": "file-processor",
  "event_type": "file_processed",
  "data": {
    "filename": "document.pdf",
    "status": "approved",
    "destination": "Done/document.pdf",
    "size_bytes": 2400000,
    "processing_time_sec": 5.3
  }
}
```

---

## Implementation Details

### Dependencies
- Python 3.12+
- pathlib, json, hashlib (stdlib)
- Optional: PyPDF2 (for PDF parsing, Gold tier)
- Optional: python-magic (for file type detection)

### Key Functions

#### `analyze_file(filepath: Path) -> Dict`
Extract metadata and content preview.
- Returns: {title, size, type, preview, hash, priority}

#### `create_plan(analysis: Dict) -> Path`
Generate Plan.md in /Plans folder.
- Returns: Path to created plan file

#### `should_approve(analysis: Dict) -> bool`
Decide if file needs HITL approval.
- Returns: True if approval needed, False for auto-execute

#### `move_file(source: Path, destination: str) -> Path`
Move file to Done or Pending_Approval.
- Returns: Path to new location

---

## Error Handling

| Error | Handling | Escalation |
|-------|----------|-----------|
| File not found | Log warning, skip | None |
| Permission denied | Create escalation note | 🚨 |
| Corruption detected | Create escalation note | 🚨 |
| Unknown file type | Create plan with query | None |
| Parsing failed | Move to Pending_Approval | None |

---

## Testing

### Test Case 1: Simple Text File
```bash
echo "test document" > /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox/test.txt
# Expected: File moves to Done/ with summary
```

### Test Case 2: Requires Approval
```bash
echo "Important: Review this carefully" > /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox/review.md
# Add metadata header with priority: high
# Expected: File moves to Pending_Approval/
```

### Test Case 3: Error Handling
```bash
# Create file, then delete before processing
# Expected: Graceful error log, continue processing
```

Run tests:
```bash
python scripts/verify.py
```

---

## Limitations (Bronze Tier)

- ❌ Cannot parse binary formats (use Gold tier PyPDF2)
- ❌ No image recognition (use Gold tier vision API)
- ❌ No external API calls (use Silver tier+)
- ⚠️ Text preview limited to 500 chars

---

## Future Enhancements (Silver+)

- [ ] PDF parsing and extraction
- [ ] Email attachment handling
- [ ] Image OCR for scanned documents
- [ ] Integration with Odoo for document management
- [ ] Smart categorization using embeddings
- [ ] Automatic routing based on Company_Handbook rules

---

## Related Skills

- **email-processor** (Silver tier) - Handle email attachments
- **data-analyzer** (Gold tier) - Advanced data processing
- **document-classifier** (Gold tier) - ML-based categorization

---

## Support

**Questions?** Add to `/Inbox/question-{{date}}.md`
**Bugs?** File in `/Pending_Approval/bug-report-{{date}}.md`
**Improvements?** Create PR to `/vault-improvement/` folder

**Last Updated:** 2026-02-16
**Tested By:** AI Employee v1.0
**Status:** Production Ready 🚀

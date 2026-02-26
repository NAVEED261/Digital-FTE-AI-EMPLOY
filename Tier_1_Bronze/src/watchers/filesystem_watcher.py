"""
FileSystem Watcher - Monitors /Inbox folder and moves files to /Needs_Action

Watches for new files dropped in /Inbox and:
1. Moves the file to /Needs_Action
2. Creates a .md metadata file with context for Claude
3. Logs the event

Usage:
    python filesystem_watcher.py /path/to/AI_Employee_Vault
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import json

from base_watcher import BaseWatcher


class FileSystemWatcher(BaseWatcher):
    """Monitor /Inbox folder for new files"""

    def __init__(self, vault_path: str, check_interval: int = 5):
        super().__init__(vault_path, check_interval=check_interval, name='FileSystemWatcher')
        self.inbox = self.vault_path / 'Inbox'
        self.processed = set()  # Track processed files to avoid duplicates

        # Ensure Inbox exists
        self.inbox.mkdir(parents=True, exist_ok=True)

        self.logger.info(f'Watching: {self.inbox}')

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check /Inbox for new files.

        Returns:
            List of dicts with file metadata
        """
        items = []

        if not self.inbox.exists():
            return items

        for file_path in self.inbox.iterdir():
            if file_path.is_file() and file_path.name not in self.processed:
                # Ignore .md metadata files
                if file_path.suffix == '.md':
                    continue

                try:
                    # Read file info
                    stat = file_path.stat()

                    # Determine if file is complete (no longer being written)
                    # Simple heuristic: file hasn't changed in 2 seconds
                    current_mtime = stat.st_mtime
                    time.sleep(0.5)
                    new_stat = file_path.stat()

                    if new_stat.st_mtime == current_mtime:
                        # File is stable, process it
                        items.append({
                            'path': file_path,
                            'title': file_path.name,
                            'size': stat.st_size,
                            'suffix': file_path.suffix,
                            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        })
                        self.processed.add(file_path.name)
                except Exception as e:
                    self.logger.warning(f'Failed to check file {file_path}: {e}')

        return items

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Move file from /Inbox to /Needs_Action and create metadata.

        Args:
            item: File metadata dict from check_for_updates()

        Returns:
            Path to created metadata file
        """
        source = item['path']
        dest = self.needs_action / source.name

        # Move file (handle potential duplicates)
        if dest.exists():
            base = dest.stem
            counter = 1
            while dest.exists():
                dest = self.needs_action / f'{base}_{counter}{source.suffix}'
                counter += 1

        source.rename(dest)

        # Create metadata markdown file
        meta_path = dest.with_stem(dest.stem + '_meta')

        # Read first 500 chars of text files for preview
        preview = ''
        if dest.suffix.lower() in ['.txt', '.md', '.csv', '.json', '.log']:
            try:
                with open(dest, 'r', encoding='utf-8', errors='ignore') as f:
                    preview = f.read(500)
                    if len(preview) == 500:
                        preview += '...\n(truncated)'
            except Exception as e:
                preview = f'(Could not preview: {e})'

        # Build metadata content
        content = f'''---
type: file_drop
original_name: {source.name}
file_path: {dest.relative_to(self.vault_path)}
size_bytes: {item['size']}
file_type: {item['suffix'] or 'no extension'}
received: {item['created']}
priority: medium
status: pending
processed_by: filesystem_watcher
---

# File Dropped: {source.name}

A new file was added to your Inbox and is ready for processing.

## File Details
- **Size:** {item['size']:,} bytes
- **Type:** {item['suffix'] or 'Plain text'}
- **Received:** {item['created']}

## Preview
```
{preview}
```

## Suggested Claude Actions
- [ ] Review file contents
- [ ] Categorize file (document, data, resource, etc.)
- [ ] Determine urgency (low/medium/high)
- [ ] Create processing plan if needed
- [ ] Move to appropriate folder (/Done, /Pending_Approval, etc.)

## File Location
`{dest.relative_to(self.vault_path)}`

## Next Step
Claude Code should read this file, decide on processing steps, and update this metadata with decisions.
'''

        meta_path.write_text(content)

        return meta_path

    def run(self):
        """Override run() to add filesystem-specific startup message"""
        print(f'👁️  Watching {self.inbox} for new files...')
        print('📝 Files will be moved to Needs_Action/ and processed by Claude')
        print('Press Ctrl+C to stop\n')
        super().run()


def main():
    """Entry point for filesystem watcher"""
    vault_path = sys.argv[1] if len(sys.argv) > 1 else '/mnt/d/Hackaton-0/AI_Employee_Vault'

    vault = Path(vault_path)
    if not vault.exists():
        print(f'❌ Vault not found: {vault_path}')
        sys.exit(1)

    watcher = FileSystemWatcher(str(vault_path))
    try:
        watcher.run()
    except KeyboardInterrupt:
        print('\n🛑 FileSystem watcher stopped by user')
        watcher.stop()
    except Exception as e:
        print(f'❌ Fatal error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()

"""
Base Watcher Class - Abstract base for all AI Employee watchers

All watcher implementations inherit from BaseWatcher and implement:
- check_for_updates(): Poll source for new items
- create_action_file(): Write .md file to /Needs_Action

This ensures consistent logging, error handling, and vault integration.
"""

import time
import logging
import json
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any


class BaseWatcher(ABC):
    """Abstract base class for all watcher scripts"""

    def __init__(self, vault_path: str, check_interval: int = 60, name: str = None):
        """
        Initialize watcher.

        Args:
            vault_path: Path to AI_Employee_Vault
            check_interval: Seconds between checks (default 60)
            name: Optional custom name (defaults to class name)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs_dir = self.vault_path / 'Logs'
        self.check_interval = check_interval
        self.watcher_name = name or self.__class__.__name__

        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = self._setup_logging()
        self.logger.info(f'Initialized {self.watcher_name}')

    def _setup_logging(self) -> logging.Logger:
        """Configure logging to both file and console"""
        logger = logging.getLogger(self.watcher_name)
        logger.setLevel(logging.INFO)

        # File handler (one file per watcher)
        log_file = self.logs_dir / f'{self.watcher_name}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger

    @abstractmethod
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check source for new items.

        Returns:
            List of dictionaries, each representing an item to process.
            Each dict must have at least: {'title': str, 'content': str}
        """
        pass

    @abstractmethod
    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Create .md file in Needs_Action folder for Claude to process.

        Args:
            item: Dictionary with item data from check_for_updates()

        Returns:
            Path to created file
        """
        pass

    def log_json(self, event_type: str, data: Dict[str, Any]):
        """
        Log event as JSON for structured analysis.

        Args:
            event_type: Type of event (e.g., 'file_created', 'error')
            data: Event-specific data dictionary
        """
        json_log_file = self.logs_dir / f'{datetime.now().strftime("%Y-%m-%d")}.json'

        event = {
            'timestamp': datetime.now().isoformat(),
            'watcher': self.watcher_name,
            'event_type': event_type,
            'data': data
        }

        try:
            if json_log_file.exists():
                with open(json_log_file, 'a') as f:
                    f.write(json.dumps(event) + '\n')
            else:
                with open(json_log_file, 'w') as f:
                    f.write(json.dumps(event) + '\n')
        except Exception as e:
            self.logger.error(f'Failed to write JSON log: {e}')

    def run(self):
        """Main loop - runs continuously, checking for updates"""
        self.logger.info(f'Starting {self.watcher_name} (check interval: {self.check_interval}s)')
        print(f'✅ {self.watcher_name} started (interval: {self.check_interval}s)')

        error_count = 0
        max_errors = 5

        while True:
            try:
                items = self.check_for_updates()

                if items:
                    for item in items:
                        try:
                            filepath = self.create_action_file(item)
                            self.logger.info(f'Created action file: {filepath.name}')
                            self.log_json('file_created', {
                                'filename': filepath.name,
                                'title': item.get('title', 'Unknown'),
                                'source': self.watcher_name
                            })
                            print(f'📝 New action: {filepath.name}')
                        except Exception as e:
                            self.logger.error(f'Failed to create action file for item: {e}', exc_info=True)
                            self.log_json('error_action_file', {
                                'item': item,
                                'error': str(e)
                            })

                # Reset error count on successful iteration
                error_count = 0

            except Exception as e:
                error_count += 1
                self.logger.error(f'Error in main loop (attempt {error_count}/{max_errors}): {e}', exc_info=True)
                self.log_json('error_main_loop', {
                    'attempt': error_count,
                    'error': str(e)
                })

                if error_count >= max_errors:
                    self.logger.critical(f'Max errors reached ({max_errors}). Exiting.')
                    print(f'❌ {self.watcher_name} stopped due to repeated errors')
                    raise

                # Backoff before retry
                time.sleep(self.check_interval)

            time.sleep(self.check_interval)

    def stop(self):
        """Graceful shutdown"""
        self.logger.info(f'Stopping {self.watcher_name}')
        print(f'🛑 {self.watcher_name} stopping')


if __name__ == '__main__':
    print('ℹ️  BaseWatcher is abstract. Use subclasses like FileSystemWatcher.')

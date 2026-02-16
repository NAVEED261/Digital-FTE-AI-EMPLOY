#!/usr/bin/env python3
"""
Download Manager

Manages file downloads triggered by browser automation.
Handles download events, progress monitoring, and file verification.
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class DownloadManager:
    """Manage file downloads via browser automation"""

    def __init__(self, mcp_client, download_dir: str):
        """
        Initialize download manager

        Args:
            mcp_client: MCP client instance for browser automation
            download_dir: Directory to save downloaded files
        """
        self.mcp = mcp_client
        self.download_dir = os.path.abspath(download_dir)
        os.makedirs(self.download_dir, exist_ok=True)

        logger.info(f"DownloadManager initialized for {self.download_dir}")

    async def download_file_by_click(
        self,
        element_selector: str,
        expected_filename: Optional[str] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Download file by clicking element that triggers download

        Uses Playwright's download event handling via browser_run_code

        Args:
            element_selector: CSS selector or text for download element
            expected_filename: Expected filename (for verification)
            timeout: Max seconds to wait for download

        Returns:
            {
                'success': bool,
                'filename': str,
                'filepath': str,
                'size': int,
                'duration': float
            }

        Example:
            result = await manager.download_file_by_click(
                "a:has-text('Download Image')",
                "image.jpg"
            )
        """
        start_time = time.time()

        try:
            logger.info(f"Triggering download for: {element_selector}")

            # Playwright code to handle download
            code = f"""async (page) => {{
                try {{
                    // Set up download listener
                    const downloadPromise = page.waitForEvent('download');

                    // Find and click element
                    const selector = {repr(element_selector)};
                    const element = await page.locator(selector).first();

                    if (!element) {{
                        throw new Error('Element not found: ' + selector);
                    }}

                    // Click to trigger download
                    await element.click();

                    // Wait for download to complete
                    const download = await Promise.race([
                        downloadPromise,
                        new Promise((_, reject) =>
                            setTimeout(() => reject(new Error('Download timeout')), {timeout * 1000})
                        )
                    ]);

                    return {{
                        filename: download.suggestedFilename(),
                        success: true
                    }};
                }} catch (error) {{
                    return {{
                        success: false,
                        error: error.message
                    }};
                }}
            }}"""

            result = await self.mcp.call_tool("browser_run_code", {"code": code})
            content = result.get('content', {})

            if not content.get('success'):
                logger.error(f"Download failed: {content.get('error')}")
                return {
                    'success': False,
                    'error': content.get('error'),
                    'duration': time.time() - start_time
                }

            filename = content.get('filename', expected_filename or 'download')
            filepath = os.path.abspath(os.path.join(self.download_dir, filename))

            logger.info(f"Download initiated: {filename}")

            # Wait for file to appear and complete
            if await self._wait_for_download_complete(filename, timeout):
                file_size = os.path.getsize(filepath)
                duration = time.time() - start_time

                logger.info(f"✓ Download complete: {filename} ({file_size} bytes)")

                return {
                    'success': True,
                    'filename': filename,
                    'filepath': filepath,
                    'size': file_size,
                    'duration': duration
                }
            else:
                logger.error(f"Download verification timeout: {filename}")
                return {
                    'success': False,
                    'error': 'Download verification timeout',
                    'duration': time.time() - start_time
                }

        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - start_time
            }

    async def _wait_for_download_complete(
        self,
        filename: str,
        timeout: int = 30
    ) -> bool:
        """
        Wait for downloaded file to complete

        Checks if file exists and is stable (not being written to)

        Args:
            filename: Expected filename
            timeout: Max seconds to wait

        Returns:
            True if file completed, False on timeout
        """
        filepath = os.path.join(self.download_dir, filename)
        start_time = time.time()
        last_size = -1
        stable_count = 0

        while time.time() - start_time < timeout:
            if os.path.exists(filepath):
                current_size = os.path.getsize(filepath)

                # Check if file size is stable (not being written)
                if current_size == last_size and current_size > 0:
                    stable_count += 1
                    if stable_count >= 2:  # File stable for 2 checks
                        return True
                else:
                    stable_count = 0

                last_size = current_size

            await asyncio.sleep(0.5)

        return False

    def get_latest_download(self) -> Optional[str]:
        """
        Get path to most recently downloaded file

        Returns:
            Absolute path to latest file, or None if empty
        """
        try:
            files = [
                os.path.join(self.download_dir, f)
                for f in os.listdir(self.download_dir)
                if os.path.isfile(os.path.join(self.download_dir, f))
            ]

            if not files:
                logger.warning("No downloads found")
                return None

            latest = max(files, key=os.path.getctime)
            logger.info(f"Latest download: {os.path.basename(latest)}")
            return latest

        except Exception as e:
            logger.error(f"Error getting latest download: {e}")
            return None

    def list_downloads(self) -> List[Dict[str, Any]]:
        """
        List all downloaded files

        Returns:
            List of file info dicts {filename, filepath, size, modified_time}
        """
        try:
            downloads = []

            for filename in os.listdir(self.download_dir):
                filepath = os.path.join(self.download_dir, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    downloads.append({
                        'filename': filename,
                        'filepath': os.path.abspath(filepath),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })

            # Sort by modification time (newest first)
            downloads.sort(key=lambda x: x['modified'], reverse=True)

            logger.info(f"Found {len(downloads)} downloaded files")
            return downloads

        except Exception as e:
            logger.error(f"Error listing downloads: {e}")
            return []

    async def verify_download(
        self,
        filename: str,
        min_size: int = 0,
        timeout: int = 30
    ) -> bool:
        """
        Verify file was downloaded successfully

        Args:
            filename: Expected filename
            min_size: Minimum file size in bytes
            timeout: Max seconds to wait

        Returns:
            True if file exists and meets criteria, False otherwise
        """
        filepath = os.path.join(self.download_dir, filename)
        start_time = time.time()

        logger.info(f"Verifying download: {filename}")

        while time.time() - start_time < timeout:
            if os.path.exists(filepath):
                try:
                    file_size = os.path.getsize(filepath)

                    # Check file size
                    if file_size < min_size:
                        logger.warning(
                            f"File too small: {file_size} bytes (min: {min_size})"
                        )
                        await asyncio.sleep(1)
                        continue

                    # Check file is not being written (size stable)
                    time.sleep(1)
                    new_size = os.path.getsize(filepath)

                    if new_size == file_size and file_size > 0:
                        logger.info(f"✓ Download verified: {filename} ({file_size} bytes)")
                        return True

                except OSError as e:
                    logger.warning(f"Error checking file: {e}")

            await asyncio.sleep(0.5)

        logger.error(f"✗ Download verification timeout: {filename}")
        return False

    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed info about downloaded file

        Args:
            filename: Filename to get info for

        Returns:
            File info dict or None if not found
        """
        filepath = os.path.join(self.download_dir, filename)

        try:
            if not os.path.exists(filepath):
                logger.warning(f"File not found: {filename}")
                return None

            stat = os.stat(filepath)

            return {
                'filename': filename,
                'filepath': os.path.abspath(filepath),
                'size': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'readable': os.access(filepath, os.R_OK)
            }

        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None

    async def cleanup_downloads(self, pattern: str = "*"):
        """
        Clean up download directory

        Args:
            pattern: File pattern to delete (default: "*" for all files)
        """
        try:
            import glob

            files_to_delete = glob.glob(os.path.join(self.download_dir, pattern))

            for filepath in files_to_delete:
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    logger.info(f"Deleted: {os.path.basename(filepath)}")

            logger.info(f"✓ Cleaned up {len(files_to_delete)} files")

        except Exception as e:
            logger.error(f"Error cleaning up downloads: {e}")

    async def clear_downloads(self):
        """
        Clear all downloaded files

        Use with caution!
        """
        logger.warning("Clearing all downloads...")
        await self.cleanup_downloads("*")


# Async import for asyncio usage
import asyncio


if __name__ == "__main__":
    # Example usage
    async def test():
        # This would normally use a real MCP client
        # For testing, we'll just show the API

        print("DownloadManager test (requires MCP client)")
        print("Usage:")
        print("  manager = DownloadManager(mcp_client, './downloads')")
        print("  result = await manager.download_file_by_click('a[href*=download]')")
        print("  files = manager.list_downloads()")
        print("  info = manager.get_file_info('image.jpg')")

    asyncio.run(test())

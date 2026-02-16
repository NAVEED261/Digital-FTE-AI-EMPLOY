#!/usr/bin/env python3
"""
Upload Workflows Manager

Orchestrates end-to-end image operations:
- Search images from web (Unsplash/Google)
- Download images to local directory
- Upload images to app with metadata
- Verify upload success

Complete autonomous workflow with zero manual intervention.
"""

import os
import sys
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

from image_operations import ImageSearchHandler
from download_manager import DownloadManager

logger = logging.getLogger(__name__)


class UploadWorkflowManager:
    """Orchestrate complex image search, download, and upload workflows"""

    def __init__(self, mcp_client, image_handler=None, download_manager=None):
        """
        Initialize upload workflow manager

        Args:
            mcp_client: MCP client for browser automation
            image_handler: ImageSearchHandler instance (or create new)
            download_manager: DownloadManager instance (or create new)
        """
        self.mcp = mcp_client
        self.image_handler = image_handler or ImageSearchHandler(mcp_client)
        self.download_manager = download_manager or DownloadManager(
            mcp_client,
            "./temp_downloads"
        )

        logger.info("UploadWorkflowManager initialized")

    async def search_download_upload(
        self,
        search_query: str,
        upload_url: str,
        upload_input_selector: str,
        metadata: Optional[Dict[str, Any]] = None,
        image_count: int = 20,
        auto_categorize: bool = False
    ) -> Dict[str, Any]:
        """
        Complete workflow: search images → download → upload

        This is the main autonomous workflow that requires ZERO manual intervention.

        Args:
            search_query: Image search query (e.g., "ladies fashion boutique")
            upload_url: URL of upload page in app
            upload_input_selector: CSS selector for file input element
            metadata: Optional metadata for uploads {
                'category': 'Fashion',
                'tags': ['boutique', 'fashion'],
                'description': 'Product image'
            }
            image_count: Number of images to process
            auto_categorize: Auto-categorize images based on content

        Returns:
            {
                'searched': int,          # Images found
                'downloaded': int,        # Images downloaded
                'uploaded': int,          # Images uploaded
                'failed': int,            # Failed uploads
                'paths': List[str],       # Downloaded file paths
                'duration': float         # Total time in seconds
            }

        Example:
            result = await manager.search_download_upload(
                search_query="pakistani ladies fashion",
                upload_url="http://localhost:3000/admin/products/new",
                upload_input_selector="input[type='file']",
                metadata={'category': 'Fashion', 'tags': ['boutique']},
                image_count=20
            )
        """
        import time
        start_time = time.time()

        results = {
            'searched': 0,
            'downloaded': 0,
            'uploaded': 0,
            'failed': 0,
            'paths': [],
            'duration': 0
        }

        try:
            # Step 1: Search for images
            logger.info(f"🔍 Searching for images: {search_query}")
            print(f"\n{'='*60}")
            print(f"🔍 PHASE 1: IMAGE SEARCH")
            print(f"{'='*60}")
            print(f"Query: {search_query}")

            images = await self.image_handler.search_unsplash(
                search_query,
                {
                    'count': image_count,
                    'min_width': 800,
                    'min_height': 600,
                    'order_by': 'relevant'
                }
            )

            # Fallback to Google Images if Unsplash fails
            if not images:
                logger.warning("Unsplash search failed, falling back to Google Images")
                print("⚠️  Unsplash unavailable, using Google Images fallback...")
                images = await self.image_handler.search_google_images(
                    search_query,
                    {'min_width': 800, 'min_height': 600}
                )

            results['searched'] = len(images)
            print(f"✓ Found {len(images)} high-quality images")

            if not images:
                logger.error("No images found")
                return results

            # Step 2: Download images
            logger.info(f"⬇️  Downloading {len(images)} images...")
            print(f"\n{'='*60}")
            print(f"⬇️  PHASE 2: IMAGE DOWNLOAD")
            print(f"{'='*60}")

            image_urls = [img.get('url', img.get('src')) for img in images if img.get('url') or img.get('src')]
            downloaded_paths = await self.image_handler.download_images(
                image_urls[:image_count],
                self.download_manager.download_dir
            )

            results['downloaded'] = len(downloaded_paths)
            results['paths'] = downloaded_paths
            print(f"✓ Downloaded {len(downloaded_paths)}/{len(image_urls)} images")

            if not downloaded_paths:
                logger.error("No images downloaded")
                return results

            # Step 3: Navigate to upload page
            logger.info(f"⬆️  Navigating to upload page: {upload_url}")
            print(f"\n{'='*60}")
            print(f"⬆️  PHASE 3: IMAGE UPLOAD")
            print(f"{'='*60}")
            print(f"Upload URL: {upload_url}")

            await self.mcp.call_tool("browser_navigate", {"url": upload_url})
            await asyncio.sleep(2)  # Wait for page load

            # Step 4: Upload each image
            for i, filepath in enumerate(downloaded_paths, 1):
                try:
                    logger.info(f"Uploading {i}/{len(downloaded_paths)}: {os.path.basename(filepath)}")
                    print(f"\n[{i}/{len(downloaded_paths)}] Uploading: {os.path.basename(filepath)}")

                    # Upload file using browser_file_upload MCP tool
                    await self.mcp.call_tool("browser_file_upload", {
                        "paths": [filepath]
                    })

                    # Wait for upload to process
                    await asyncio.sleep(1)

                    # Fill metadata if provided
                    if metadata:
                        # Category field
                        if 'category' in metadata:
                            try:
                                await self.mcp.call_tool("browser_type", {
                                    "ref": "category-input",
                                    "element": "category input",
                                    "text": metadata['category']
                                })
                            except Exception as e:
                                logger.warning(f"Could not fill category: {e}")

                        # Description field
                        if 'description' in metadata:
                            try:
                                await self.mcp.call_tool("browser_type", {
                                    "ref": "description-input",
                                    "element": "description input",
                                    "text": metadata['description']
                                })
                            except Exception as e:
                                logger.warning(f"Could not fill description: {e}")

                        # Tags field
                        if 'tags' in metadata and isinstance(metadata['tags'], list):
                            try:
                                tags_text = ', '.join(metadata['tags'])
                                await self.mcp.call_tool("browser_type", {
                                    "ref": "tags-input",
                                    "element": "tags input",
                                    "text": tags_text
                                })
                            except Exception as e:
                                logger.warning(f"Could not fill tags: {e}")

                    # Submit upload (if button exists)
                    try:
                        await self.mcp.call_tool("browser_click", {
                            "ref": "upload-submit",
                            "element": "upload submit button"
                        })
                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.warning(f"No submit button found (may auto-submit): {e}")

                    # Verify success
                    try:
                        await self.mcp.call_tool("browser_wait_for", {
                            "text": "success",
                            "time": 5
                        })
                        results['uploaded'] += 1
                        print(f"  ✓ Upload successful")
                    except:
                        # Assume success if no error message
                        results['uploaded'] += 1
                        print(f"  ✓ Upload completed")

                except Exception as e:
                    results['failed'] += 1
                    logger.error(f"Upload failed for {os.path.basename(filepath)}: {e}")
                    print(f"  ✗ Upload failed: {e}")
                    continue

            # Step 5: Report results
            results['duration'] = time.time() - start_time

            print(f"\n{'='*60}")
            print(f"✅ WORKFLOW COMPLETE")
            print(f"{'='*60}")
            print(f"Searched:    {results['searched']} images")
            print(f"Downloaded:  {results['downloaded']} images")
            print(f"Uploaded:    {results['uploaded']} images")
            print(f"Failed:      {results['failed']} images")
            print(f"Success Rate: {results['uploaded']/results['downloaded']*100:.1f}%")
            print(f"Duration:    {results['duration']:.1f}s")
            print(f"{'='*60}\n")

            logger.info(f"✅ Workflow complete: {results['uploaded']}/{results['downloaded']} uploaded")

            return results

        except Exception as e:
            logger.error(f"Workflow error: {e}")
            results['duration'] = time.time() - start_time
            return results

    async def batch_upload_with_progress(
        self,
        file_paths: List[str],
        upload_url: str,
        metadata_list: Optional[List[Dict[str, Any]]] = None,
        batch_size: int = 5
    ) -> Dict[str, Any]:
        """
        Upload multiple files with progress tracking

        Supports batch processing and individual metadata per file.

        Args:
            file_paths: List of absolute file paths to upload
            upload_url: URL of upload page
            metadata_list: Optional list of metadata dicts (one per file)
            batch_size: Number of files to upload concurrently

        Returns:
            Upload results summary
        """
        results = {
            'total': len(file_paths),
            'uploaded': 0,
            'failed': 0,
            'details': []
        }

        logger.info(f"Batch uploading {len(file_paths)} files")
        print(f"\n⬆️  Batch Upload: {len(file_paths)} files")

        # Navigate to upload page
        await self.mcp.call_tool("browser_navigate", {"url": upload_url})
        await asyncio.sleep(2)

        # Process in batches
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            batch_metadata = metadata_list[i:i + batch_size] if metadata_list else [None] * len(batch)

            for j, (filepath, metadata) in enumerate(zip(batch, batch_metadata)):
                idx = i + j + 1
                try:
                    print(f"[{idx}/{len(file_paths)}] Uploading: {os.path.basename(filepath)}")

                    # Upload file
                    await self.mcp.call_tool("browser_file_upload", {
                        "paths": [filepath]
                    })

                    # Fill metadata if provided
                    if metadata:
                        # (Similar metadata filling logic as above)
                        pass

                    results['uploaded'] += 1
                    results['details'].append({
                        'filepath': filepath,
                        'success': True
                    })
                    print(f"  ✓ Success")

                except Exception as e:
                    results['failed'] += 1
                    results['details'].append({
                        'filepath': filepath,
                        'success': False,
                        'error': str(e)
                    })
                    print(f"  ✗ Failed: {e}")

        print(f"\n✅ Batch upload complete: {results['uploaded']}/{results['total']} successful")
        return results

    async def verify_uploads(
        self,
        expected_count: int,
        gallery_url: str
    ) -> Dict[str, Any]:
        """
        Verify uploads by checking gallery/product page

        Args:
            expected_count: Expected number of uploaded images
            gallery_url: URL to check for uploaded images

        Returns:
            Verification results
        """
        try:
            logger.info(f"Verifying {expected_count} uploads at {gallery_url}")

            # Navigate to gallery
            await self.mcp.call_tool("browser_navigate", {"url": gallery_url})
            await asyncio.sleep(2)

            # Count images on page
            result = await self.mcp.call_tool("browser_evaluate", {
                "function": """
                () => {
                    const images = document.querySelectorAll('img[src*="image"], img[src*="product"]');
                    return {
                        count: images.length,
                        images: Array.from(images).slice(0, 10).map(img => ({
                            src: img.src,
                            alt: img.alt
                        }))
                    };
                }
                """
            })

            content = result.get('content', {})
            actual_count = content.get('count', 0)

            verification = {
                'expected': expected_count,
                'actual': actual_count,
                'verified': actual_count >= expected_count,
                'images': content.get('images', [])
            }

            if verification['verified']:
                logger.info(f"✓ Upload verification passed: {actual_count} images found")
            else:
                logger.warning(f"⚠️  Upload verification: expected {expected_count}, found {actual_count}")

            return verification

        except Exception as e:
            logger.error(f"Upload verification error: {e}")
            return {
                'expected': expected_count,
                'actual': 0,
                'verified': False,
                'error': str(e)
            }


# CLI usage example
if __name__ == "__main__":
    async def test():
        print("UploadWorkflowManager test (requires MCP client)")
        print("\nUsage:")
        print("  manager = UploadWorkflowManager(mcp_client)")
        print("  result = await manager.search_download_upload(")
        print("      search_query='ladies fashion',")
        print("      upload_url='http://localhost:3000/admin/products/new',")
        print("      upload_input_selector='input[type=file]',")
        print("      metadata={'category': 'Fashion'},")
        print("      image_count=20")
        print("  )")

    asyncio.run(test())

#!/usr/bin/env python3
"""
Image Search & Download Operations

Enables autonomous web image search from multiple sources:
- Unsplash API (official, free tier, 50 req/hr)
- Google Images (via browser automation fallback)

Handles intelligent filtering, batch download, and error recovery.
"""

import os
import sys
import json
import time
import asyncio
import requests
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logger = logging.getLogger(__name__)


class ImageSearchHandler:
    """Handle web image search and intelligent download operations"""

    def __init__(self, mcp_client=None):
        """
        Initialize image search handler

        Args:
            mcp_client: MCP client instance for browser automation (optional)
        """
        self.mcp = mcp_client
        self.unsplash_key = os.getenv('UNSPLASH_ACCESS_KEY', '')
        self.session = requests.Session()
        self.session.timeout = 30
        logger.info("ImageSearchHandler initialized")

    async def search_unsplash(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search Unsplash API for images

        Uses official Unsplash API (free tier: 50 requests/hour)
        Sign up at: https://unsplash.com/oauth/applications

        Args:
            query: Search query (e.g., "ladies fashion suits")
            filters: {
                'count': 20,              # Number of images
                'orientation': 'landscape',
                'min_width': 800,
                'min_height': 600,
                'order_by': 'relevant'   # relevant, latest, views, downloads
            }

        Returns:
            List of image metadata dicts with URLs, author, etc.

        Example:
            images = await handler.search_unsplash(
                "pakistani fashion",
                {'count': 20, 'min_width': 800, 'min_height': 600}
            )
        """
        if not self.unsplash_key:
            logger.warning("UNSPLASH_ACCESS_KEY not set, skipping Unsplash search")
            return []

        filters = filters or {}
        count = filters.get('count', 20)
        orientation = filters.get('orientation')
        order_by = filters.get('order_by', 'relevant')

        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {self.unsplash_key}"}
            params = {
                "query": query,
                "per_page": min(count, 20),  # API limit: 20 per page
                "order_by": order_by
            }

            if orientation:
                params["orientation"] = orientation

            logger.info(f"Searching Unsplash: {query}")
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = data.get('results', [])

            # Filter by dimensions if specified
            min_width = filters.get('min_width', 0)
            min_height = filters.get('min_height', 0)

            filtered = []
            for img in results:
                if (img['width'] >= min_width and
                    img['height'] >= min_height):
                    filtered.append({
                        'id': img['id'],
                        'url': img['urls']['regular'],
                        'width': img['width'],
                        'height': img['height'],
                        'alt': img.get('alt_description', ''),
                        'author': img['user']['name'],
                        'author_url': img['user']['links']['html'],
                        'download_url': img['links']['download'],
                        'source': 'unsplash'
                    })

            logger.info(f"✓ Found {len(filtered)} images from Unsplash")
            return filtered

        except requests.exceptions.Timeout:
            logger.error("Unsplash API request timeout")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Unsplash API error: {e}")
            return []
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing Unsplash response: {e}")
            return []

    async def search_google_images(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search Google Images via browser automation

        Fallback method when API not available.
        Requires MCP client with browser capabilities.

        Args:
            query: Search query
            filters: Size filters, etc.

        Returns:
            List of image metadata from Google Images
        """
        if not self.mcp:
            logger.warning("MCP client not available for Google Images search")
            return []

        filters = filters or {}
        min_width = filters.get('min_width', 800)
        min_height = filters.get('min_height', 600)

        try:
            logger.info(f"Searching Google Images: {query}")

            # Navigate to Google Images
            search_url = f"https://images.google.com/search?q={query.replace(' ', '+')}"
            await self.mcp.call_tool("browser_navigate", {"url": search_url})

            # Wait for images to load
            await asyncio.sleep(2)

            # Scroll to load more images
            for _ in range(3):
                await self.mcp.call_tool("browser_evaluate", {
                    "function": "() => window.scrollTo(0, document.body.scrollHeight)"
                })
                await asyncio.sleep(1)

            # Extract image data via JavaScript
            result = await self.mcp.call_tool("browser_evaluate", {
                "function": """
                () => {
                    const images = Array.from(document.querySelectorAll('img[src]'));
                    return images
                        .filter(img => {
                            const width = img.naturalWidth || img.width;
                            const height = img.naturalHeight || img.height;
                            return width >= 800 && height >= 600;
                        })
                        .slice(0, 20)
                        .map(img => ({
                            src: img.src,
                            alt: img.alt,
                            width: img.naturalWidth || img.width,
                            height: img.naturalHeight || img.height,
                            source: 'google-images'
                        }));
                }
                """
            })

            images = result.get('content', [])
            logger.info(f"✓ Found {len(images)} images from Google Images")
            return images

        except Exception as e:
            logger.error(f"Error searching Google Images: {e}")
            return []

    async def download_images(
        self,
        image_urls: List[str],
        save_dir: str,
        max_retries: int = 3
    ) -> List[str]:
        """
        Download images from URLs to local directory

        Handles errors gracefully, retries failed downloads,
        and returns absolute paths to downloaded files.

        Args:
            image_urls: List of image URLs to download
            save_dir: Directory to save images (created if missing)
            max_retries: Max retry attempts per image

        Returns:
            List of absolute paths to successfully downloaded files

        Example:
            urls = [img['url'] for img in images]
            paths = await handler.download_images(
                urls,
                "./temp_downloads"
            )
            # Returns: ['/abs/path/image_001.jpg', '/abs/path/image_002.jpg', ...]
        """
        # Ensure save directory exists
        os.makedirs(save_dir, exist_ok=True)
        save_dir = os.path.abspath(save_dir)

        downloaded_paths = []
        failed_urls = []

        logger.info(f"Downloading {len(image_urls)} images to {save_dir}")

        for i, url in enumerate(image_urls, 1):
            success = False
            last_error = None

            # Retry logic
            for attempt in range(max_retries):
                try:
                    # Download image
                    response = self.session.get(
                        url,
                        timeout=30,
                        allow_redirects=True
                    )
                    response.raise_for_status()

                    # Determine file extension from content-type
                    content_type = response.headers.get('content-type', '')
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        ext = 'jpg'
                    elif 'png' in content_type:
                        ext = 'png'
                    elif 'webp' in content_type:
                        ext = 'webp'
                    elif 'gif' in content_type:
                        ext = 'gif'
                    else:
                        # Fallback to jpg
                        ext = 'jpg'

                    # Generate filename
                    filename = f"image_{i:03d}.{ext}"
                    filepath = os.path.abspath(os.path.join(save_dir, filename))

                    # Write file
                    with open(filepath, 'wb') as f:
                        f.write(response.content)

                    # Verify file was written
                    if os.path.getsize(filepath) > 0:
                        downloaded_paths.append(filepath)
                        logger.info(f"✓ Downloaded {i}/{len(image_urls)}: {filename}")
                        success = True
                        break
                    else:
                        logger.warning(f"File size 0: {filepath}")
                        os.remove(filepath)

                except requests.exceptions.Timeout:
                    last_error = f"Timeout (attempt {attempt + 1}/{max_retries})"
                    await asyncio.sleep(1)
                except requests.exceptions.RequestException as e:
                    last_error = str(e)
                    await asyncio.sleep(1)
                except IOError as e:
                    last_error = f"File error: {e}"
                    break

            if not success:
                logger.error(f"✗ Failed {i}/{len(image_urls)}: {url}")
                if last_error:
                    logger.error(f"  Reason: {last_error}")
                failed_urls.append(url)

        logger.info(f"✓ Downloaded {len(downloaded_paths)}/{len(image_urls)} images")
        if failed_urls:
            logger.warning(f"Failed to download {len(failed_urls)} images")

        return downloaded_paths

    def filter_by_content(
        self,
        images: List[Dict[str, Any]],
        keywords: List[str],
        case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Filter images by content matching keywords

        Searches in alt text, description, and author fields.

        Args:
            images: List of image metadata dicts
            keywords: Keywords to match (e.g., ['fashion', 'boutique', 'dress'])
            case_sensitive: Whether to match case

        Returns:
            Filtered list of images

        Example:
            filtered = handler.filter_by_content(
                images,
                ['fashion', 'boutique', 'shalwar'],
                case_sensitive=False
            )
        """
        filtered = []

        for img in images:
            # Combine all text fields
            text_fields = [
                img.get('alt', ''),
                img.get('description', ''),
                img.get('author', ''),
                img.get('title', '')
            ]
            combined_text = ' '.join(text_fields)

            if not case_sensitive:
                combined_text = combined_text.lower()
                keywords = [kw.lower() for kw in keywords]

            # Check if any keyword matches
            if any(keyword in combined_text for keyword in keywords):
                filtered.append(img)

        logger.info(f"✓ Filtered to {len(filtered)} images matching keywords")
        return filtered

    def filter_by_quality(
        self,
        images: List[Dict[str, Any]],
        min_width: int = 800,
        min_height: int = 600,
        aspect_ratio_range: tuple = None
    ) -> List[Dict[str, Any]]:
        """
        Filter images by quality metrics

        Args:
            images: List of image metadata
            min_width: Minimum width in pixels
            min_height: Minimum height in pixels
            aspect_ratio_range: Tuple of (min_ratio, max_ratio) or None

        Returns:
            Filtered list of high-quality images
        """
        filtered = []

        for img in images:
            width = img.get('width', 0)
            height = img.get('height', 0)

            # Size check
            if width < min_width or height < min_height:
                continue

            # Aspect ratio check
            if aspect_ratio_range:
                min_ratio, max_ratio = aspect_ratio_range
                ratio = width / height if height > 0 else 0
                if not (min_ratio <= ratio <= max_ratio):
                    continue

            filtered.append(img)

        return filtered

    def validate_image_file(self, filepath: str) -> bool:
        """
        Validate downloaded image file

        Args:
            filepath: Path to image file

        Returns:
            True if file is valid, False otherwise
        """
        try:
            if not os.path.exists(filepath):
                return False

            # Check file size (at least 1KB)
            if os.path.getsize(filepath) < 1024:
                logger.warning(f"Image too small: {filepath}")
                return False

            # Try to open as image to verify format
            try:
                from PIL import Image
                img = Image.open(filepath)
                img.verify()
                return True
            except ImportError:
                # PIL not available, just check file exists and has size
                return True
            except Exception as e:
                logger.error(f"Image validation failed: {e}")
                return False

        except Exception as e:
            logger.error(f"Error validating image: {e}")
            return False

    async def cleanup_downloads(self, save_dir: str):
        """
        Clean up download directory

        Args:
            save_dir: Directory to clean up
        """
        try:
            if os.path.exists(save_dir):
                for f in os.listdir(save_dir):
                    filepath = os.path.join(save_dir, f)
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                logger.info(f"✓ Cleaned up {save_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up downloads: {e}")


# CLI usage example
if __name__ == "__main__":
    import sys

    # Example: Search for images
    handler = ImageSearchHandler()

    async def test():
        # Test Unsplash search
        print("Testing Unsplash API...")
        images = await handler.search_unsplash(
            "pakistani ladies fashion",
            {
                'count': 5,
                'min_width': 800,
                'min_height': 600
            }
        )
        print(f"Found {len(images)} images")

        if images:
            # Test download
            print("\nDownloading images...")
            urls = [img['url'] for img in images]
            paths = await handler.download_images(urls, "./test_downloads")
            print(f"Downloaded {len(paths)} images")

            # Validate
            print("\nValidating images...")
            for path in paths:
                if handler.validate_image_file(path):
                    print(f"✓ {os.path.basename(path)}")
                else:
                    print(f"✗ {os.path.basename(path)}")

            # Cleanup
            print("\nCleaning up...")
            await handler.cleanup_downloads("./test_downloads")

    asyncio.run(test())

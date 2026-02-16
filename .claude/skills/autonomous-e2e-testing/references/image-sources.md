# Image Search Sources Reference

## Overview

The autonomous-e2e-testing skill supports multiple image search sources with automatic fallback. This document describes each source, their APIs, rate limits, and usage.

---

## Primary Source: Unsplash API

### About
- **Official API**: Yes
- **Quality**: Professional, high-quality images
- **License**: Free to use (Unsplash License)
- **Rate Limit**: 50 requests/hour (free tier)
- **Commercial Use**: Yes
- **Attribution**: Recommended but not required

### Setup

1. **Create Account**: https://unsplash.com/join
2. **Create Application**: https://unsplash.com/oauth/applications
3. **Get Access Key**: Copy "Access Key" from your application
4. **Set Environment Variable**:
   ```bash
   export UNSPLASH_ACCESS_KEY="your_access_key_here"
   # Or add to .env file
   ```

### API Features

| Feature | Supported | Notes |
|---------|-----------|-------|
| Search | ✅ | By keyword, 20 results per page |
| Filter by orientation | ✅ | landscape, portrait, squarish |
| Filter by dimensions | ✅ | Client-side filtering |
| Order results | ✅ | relevant, latest, views, downloads |
| High-resolution URLs | ✅ | Multiple sizes available |
| Image metadata | ✅ | Author, description, dimensions |
| Collection search | ✅ | Search within collections |

### Usage Example

```python
from image_operations import ImageSearchHandler

handler = ImageSearchHandler()

# Basic search
images = await handler.search_unsplash(
    "ladies fashion boutique",
    {
        'count': 20,
        'orientation': 'landscape',
        'min_width': 800,
        'min_height': 600,
        'order_by': 'relevant'
    }
)

# Results include:
# - id: Unique image ID
# - url: High-quality download URL
# - width, height: Image dimensions
# - alt: Alt text/description
# - author: Photographer name
# - author_url: Photographer profile
```

### Rate Limits

- **Free Tier**: 50 requests/hour
- **Response**: 429 Too Many Requests when exceeded
- **Reset**: Every hour

**Best Practices**:
- Cache search results when possible
- Use specific queries to reduce API calls
- Implement exponential backoff on rate limit errors
- Consider Google Images fallback for high-volume needs

### Error Handling

```python
try:
    images = await handler.search_unsplash(query, filters)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        print("Rate limit exceeded, using Google Images fallback")
        images = await handler.search_google_images(query, filters)
```

---

## Fallback Source: Google Images

### About
- **Official API**: No (browser automation)
- **Quality**: Mixed (user-uploaded content)
- **License**: Varies (must check per image)
- **Rate Limit**: None (browser automation)
- **Commercial Use**: Varies
- **Attribution**: Required for most

### How It Works

Uses Playwright browser automation to:
1. Navigate to Google Images search
2. Enter search query
3. Scroll to load more images
4. Extract image URLs via JavaScript
5. Filter by dimensions client-side

### Limitations

- **Slower**: 5-10 seconds vs 2 seconds for API
- **Requires Browser**: Needs Playwright MCP server running
- **License Uncertainty**: Can't verify commercial use automatically
- **Variable Quality**: Mix of professional and amateur photos

### Usage Example

```python
# Automatically used as fallback when Unsplash fails
images = await handler.search_google_images(
    "pakistani fashion shalwar qameez",
    {
        'min_width': 800,
        'min_height': 600
    }
)
```

### When To Use

✅ **Good for**:
- High-volume image needs (>50/hour)
- Specific niche queries
- Testing and development
- Backup when API unavailable

❌ **Avoid for**:
- Commercial products without license verification
- When speed is critical
- When consistent quality is required

---

## Future Sources (Planned)

### Pexels API
- **Status**: Planned for Phase 2
- **Rate Limit**: 200 requests/hour (free)
- **Quality**: Professional stock photos
- **License**: Free for commercial use

### Pixabay API
- **Status**: Planned for Phase 2
- **Rate Limit**: 5000 requests/hour (free)
- **Quality**: Mixed professional/amateur
- **License**: Free for commercial use

### Custom Image Collections
- **Status**: Planned for Phase 3
- **Source**: Local filesystem or private CDN
- **Use Case**: Company-specific image libraries

---

## Image Quality Filtering

All sources support client-side quality filtering:

```python
# Filter by dimensions
quality_images = handler.filter_by_quality(
    images,
    min_width=1200,
    min_height=800,
    aspect_ratio_range=(1.3, 1.8)  # Landscape
)

# Filter by content
relevant_images = handler.filter_by_content(
    images,
    keywords=['fashion', 'boutique', 'dress'],
    case_sensitive=False
)
```

### Quality Criteria

| Criterion | Minimum | Recommended |
|-----------|---------|-------------|
| Width | 800px | 1200px |
| Height | 600px | 800px |
| File Size | 100KB | 500KB |
| Aspect Ratio | 1:1 to 2:1 | 4:3 or 16:9 |

---

## License Compliance

### Unsplash License
```
✅ Free to use for any purpose
✅ Commercial use allowed
✅ No attribution required (but appreciated)
❌ Cannot sell unmodified copies
❌ Cannot create competing image service
```

### Google Images
```
⚠️  License varies per image
⚠️  Must check individual image license
⚠️  Many require attribution
⚠️  Some are copyrighted
```

**Recommendation**: Use Unsplash for production, Google Images for testing only.

---

## Performance Comparison

| Source | Search Time | Quality | Reliability | Rate Limit |
|--------|-------------|---------|-------------|------------|
| Unsplash API | ~2s | ★★★★★ | ★★★★★ | 50/hr |
| Google Images | ~7s | ★★★☆☆ | ★★★★☆ | Unlimited |
| Pexels (planned) | ~2s | ★★★★☆ | ★★★★★ | 200/hr |
| Pixabay (planned) | ~2s | ★★★☆☆ | ★★★★★ | 5000/hr |

---

## Automatic Source Selection

The image handler automatically selects the best source:

```python
async def search_with_fallback(query, filters):
    """Automatic source selection with fallback"""

    # Try Unsplash first (best quality)
    if UNSPLASH_ACCESS_KEY:
        try:
            images = await search_unsplash(query, filters)
            if images:
                return images
        except Exception as e:
            logger.warning(f"Unsplash failed: {e}")

    # Fallback to Google Images
    logger.info("Using Google Images fallback")
    return await search_google_images(query, filters)
```

---

## Best Practices

### 1. Cache Search Results
```python
# Save search results to avoid repeated API calls
import json

results = await handler.search_unsplash(query, filters)
with open(f'cache/{query}.json', 'w') as f:
    json.dump(results, f)
```

### 2. Batch Operations
```python
# Search multiple queries in one session
queries = ["ladies fashion", "shalwar qameez", "boutique dress"]
all_images = []

for query in queries:
    images = await handler.search_unsplash(query, {'count': 10})
    all_images.extend(images)
    await asyncio.sleep(1)  # Rate limiting
```

### 3. Error Recovery
```python
# Implement retry logic
max_retries = 3
for attempt in range(max_retries):
    try:
        images = await handler.search_unsplash(query, filters)
        break
    except Exception as e:
        if attempt == max_retries - 1:
            # Use fallback after all retries
            images = await handler.search_google_images(query, filters)
        await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 4. Quality Assurance
```python
# Validate images before download
valid_images = [
    img for img in images
    if img['width'] >= 800 and
       img['height'] >= 600 and
       'ladies' in img.get('alt', '').lower()
]
```

---

## Troubleshooting

### Issue: "UNSPLASH_ACCESS_KEY not set"
**Solution**: Add API key to .env file:
```bash
echo "UNSPLASH_ACCESS_KEY=your_key_here" >> .env
```

### Issue: "Rate limit exceeded"
**Solution**: Wait 1 hour, or use Google Images:
```python
images = await handler.search_google_images(query, filters)
```

### Issue: "No images found"
**Solutions**:
1. Try different search terms
2. Reduce minimum dimension requirements
3. Check API key is valid
4. Verify internet connection

### Issue: "Google Images not working"
**Solution**: Ensure Playwright MCP server is running:
```bash
./scripts/start-server.sh
```

---

## API Response Examples

### Unsplash Response
```json
{
    "id": "abc123",
    "url": "https://images.unsplash.com/photo-...",
    "width": 1920,
    "height": 1080,
    "alt": "Woman in traditional Pakistani dress",
    "author": "Jane Doe",
    "author_url": "https://unsplash.com/@janedoe",
    "download_url": "https://unsplash.com/photos/abc123/download",
    "source": "unsplash"
}
```

### Google Images Response
```json
{
    "src": "https://example.com/image.jpg",
    "alt": "Fashion image",
    "width": 1200,
    "height": 800,
    "source": "google-images"
}
```

---

## Resources

- [Unsplash API Documentation](https://unsplash.com/documentation)
- [Unsplash License](https://unsplash.com/license)
- [Playwright Documentation](https://playwright.dev/)
- [Google Images Search Tips](https://support.google.com/websearch/answer/29508)

---

**Last Updated**: 2026-01-28
**Version**: 1.0.0

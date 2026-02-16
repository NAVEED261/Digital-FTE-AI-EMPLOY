# Quick Start: Image Operations

**One-page guide to using 101% browser-use expertise for autonomous image operations**

---

## 30-Second Setup

```bash
# 1. Get Unsplash API key (free)
# Visit: https://unsplash.com/oauth/applications

# 2. Add to environment
cd .claude/skills/autonomous-e2e-testing
echo "UNSPLASH_ACCESS_KEY=your_key_here" >> .env

# 3. Test it works
python3 scripts/test_image_operations.py
```

---

## Usage Patterns

### Pattern 1: Search Only
```bash
python3 scripts/test-orchestrator.py \
  --search-images "ladies fashion"
```
**Result**: Finds and lists images

### Pattern 2: Search + Download
```bash
python3 scripts/test-orchestrator.py \
  --search-images "pakistani fashion" \
  --image-count 20
```
**Result**: Downloads 20 images to `./temp_downloads/`

### Pattern 3: Complete Workflow (Search + Download + Upload)
```bash
python3 scripts/test-orchestrator.py \
  --url http://localhost:3000 \
  --search-images "fatima zehra boutique ladies fashion" \
  --upload-images \
  --image-count 20 \
  --image-category "Ladies Fashion" \
  --image-tags "boutique,fashion,shalwar qameez"
```
**Result**: 20 images uploaded to your app with metadata

---

## Common Use Cases

### Upload 40 Product Images
```bash
python3 scripts/test-orchestrator.py \
  --url http://localhost:3000 \
  --search-images "pakistani ladies fashion collection" \
  --upload-images \
  --image-count 40 \
  --image-category "Ladies Fashion"
```

### Build Image Gallery
```bash
python3 scripts/test-orchestrator.py \
  --url http://localhost:3000 \
  --search-images "boutique fashion lookbook" \
  --upload-images \
  --image-count 50 \
  --image-tags "gallery,lookbook"
```

### Test Upload Feature
```bash
python3 scripts/test-orchestrator.py \
  --url http://localhost:3000 \
  --search-images "test fashion images" \
  --upload-images \
  --image-count 5
```

---

## CLI Flags Reference

| Flag | Required | Example | Description |
|------|----------|---------|-------------|
| `--url` | Yes (for upload) | `http://localhost:3000` | Your app URL |
| `--search-images` | Yes | `"ladies fashion"` | Search query |
| `--upload-images` | No | (flag) | Upload after download |
| `--image-count` | No | `20` | Number of images (default: 20) |
| `--image-category` | No | `"Fashion"` | Category for uploads |
| `--image-tags` | No | `"tag1,tag2,tag3"` | Comma-separated tags |
| `--upload-url` | No | `http://...` | Custom upload URL |

---

## Troubleshooting (5 Seconds)

| Problem | Fix |
|---------|-----|
| "UNSPLASH_ACCESS_KEY not set" | Add key to .env file |
| "No images found" | Try different search query |
| "Download failed" | Check internet connection |
| "Upload failed" | Verify app is running |
| "MCP client error" | Run `./scripts/start-server.sh` |

---

## What Happens (Autonomous)

```
🔍 PHASE 1: IMAGE SEARCH
   ✓ Searching Unsplash...
   ✓ Found 47 images
   ✓ Filtered to 20 high-quality

⬇️  PHASE 2: DOWNLOAD
   [████████████████] 20/20
   ✓ All downloaded

⬆️  PHASE 3: UPLOAD
   [1/20] ✓
   [2/20] ✓
   ...
   [20/20] ✓

✅ COMPLETE (3m 45s)
```

---

## Performance

| Operation | Time |
|-----------|------|
| Search | ~2s |
| Download (20 images) | ~40s |
| Upload (20 images) | ~60s |
| **Total (20 images)** | **~2-3 min** |
| **Total (40 images)** | **~4-5 min** |

---

## Next Steps

1. Run verification: `python3 scripts/test_image_operations.py`
2. Try 5 image workflow (test)
3. Run 20-40 image workflow (production)
4. Check uploaded images in app

---

**Questions?** See `SKILL.md` for full documentation
**Issues?** See `IMPLEMENTATION_COMPLETE.md` for details

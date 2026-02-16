# Docker Installation Guide for Windows

Complete step-by-step guide to install and configure Docker Desktop on Windows 10/11.

## Prerequisites Check

Before installing Docker, verify your system meets requirements:

### System Requirements
- **Windows 10 Pro, Enterprise, or Education (Build 16299+)**, OR
- **Windows 11 Pro, Enterprise, or Education**
- 64-bit processor
- At least 4GB RAM (8GB recommended for development)
- BIOS virtualization enabled

### Check Your Windows Version
1. Open PowerShell (Right-click → Run as Administrator)
2. Run: `winver`
3. Look for "Edition" (Pro/Enterprise/Education required) and "Build number"

**❌ Home Edition detected?** You'll need to upgrade or use Docker Toolbox (legacy).

## Step 1: Enable WSL 2 (Windows Subsystem for Linux)

WSL 2 is Docker Desktop's backend on Windows - it provides Linux kernel support needed for containerization.

### 1.1 Open PowerShell as Administrator
- Press `Windows Key + X`
- Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

### 1.2 Enable WSL Feature
Run this command:
```powershell
wsl --install
```

This command:
- Installs WSL 2
- Downloads Ubuntu 24.04 LTS kernel
- May restart your computer (allow it)

**What happens behind the scenes:**
- Enables Hyper-V feature (required for virtualization)
- Downloads ~500MB Linux kernel
- Configures WSL 2 as default

### 1.3 Set WSL 2 as Default Version
After restart, run:
```powershell
wsl --set-default-version 2
```

### 1.4 Verify WSL 2 Installation
```powershell
wsl --version
# Should show:
# WSL version: 2.x.x
# Linux kernel version: 5.x.x
```

**🔴 Still on WSL 1?** Run:
```powershell
wsl --set-version Ubuntu 2
```

## Step 2: Download Docker Desktop

### 2.1 Visit Docker Download Page
- Go to: https://www.docker.com/products/docker-desktop
- Click "Download for Windows"

### 2.2 Two Download Options
You'll see:
- **Docker Desktop Installer (Windows)** - Recommended for most users
- **Docker Desktop WSL 2 backend** - Optimized for WSL 2

Choose: **Docker Desktop Installer (Windows)** ✓

File size: ~500MB (includes everything)

### 2.3 Verify Download
After download, you should have: `Docker Desktop Installer.exe` (~500MB)

## Step 3: Install Docker Desktop

### 3.1 Run the Installer
1. Open downloaded file: `Docker Desktop Installer.exe`
2. Click "Install"
3. When prompted for credentials: Enter Windows admin password
4. Installation begins (~5-10 minutes depending on system)

### 3.2 Installation Options
Default options are fine for development:
- ✓ Install required components for WSL 2
- ✓ Add shortcut to desktop
- ✓ Add Docker to PATH
- ✓ Enable WSL 2 integration

### 3.3 Restart Computer
After installation completes:
- You'll see: "Installation succeeded"
- Restart your computer when prompted

**During restart:**
- Hyper-V services start
- WSL 2 kernel loads
- Docker daemon initializes
- (Takes 2-3 minutes total)

## Step 4: Verify Installation

### 4.1 Open PowerShell
After restart, open PowerShell (regular user, not admin required):

### 4.2 Check Docker Version
```powershell
docker --version
# Expected: Docker version 24.x.x or later
```

**❌ Command not found?**
- Restart PowerShell completely (close and reopen)
- If still missing, reinstall Docker Desktop

### 4.3 Test Docker Daemon
```powershell
docker run hello-world
```

Expected output:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```

**❌ Cannot connect to Docker daemon?**
- Open Docker Desktop app from Start menu
- Wait for icon in system tray to show "Docker is running"
- Wait 30 seconds for daemon startup
- Try command again

### 4.4 Verify docker-compose
```powershell
docker-compose --version
# Expected: Docker Compose version 2.x.x or later
```

### 4.5 Check WSL 2 Integration
```powershell
docker run -it ubuntu bash
# Should open Linux shell
# Type: exit
```

If successful, you're in WSL 2 Linux kernel running in Docker!

## Step 5: Configure Docker Desktop for Development

### 5.1 Open Docker Desktop Settings
1. Click Docker icon in system tray (bottom right)
2. Select "Settings"
3. Configure:

#### Resources Tab
- **Memory:** Allocate 4-6 GB (out of available RAM)
  - Too high: Your Windows system will be slow
  - Too low: Containers won't run well
- **CPUs:** Allocate 4-8 cores
- **Disk image size:** 64-128 GB (for practice exercises)

Click "Apply & Restart"

#### WSL Integration Tab
- ✓ Enable integration with your Linux distribution(s)
- ✓ Enable integration with "Ubuntu"
- ✓ Enable integration with your project drive (if using WSL for development)

Click "Apply & Restart"

#### General Tab
- ✓ Start Docker Desktop when you log in
- ✓ Show tip of the day

### 5.2 Restart Docker Desktop
After configuration changes:
- Click "Apply & Restart" in settings
- Wait for daemon to restart (30 seconds)
- Icon in tray shows "Docker is running"

## Step 6: Verify Project Directory Access

Docker needs access to your project files. Verify path sharing:

### 6.1 Check Docker Desktop Settings
1. Settings → Resources → File Sharing
2. Verify your project drive is listed
3. For `C:\Users\xpert\OneDrive\Desktop\CLOUD_NATIVE_AI-400\ai-400-project-1`:
   - Drive `C:` should be shared ✓
   - Path should be accessible

### 6.2 Test Docker Access to Your Files
```powershell
cd C:\Users\xpert\OneDrive\Desktop\CLOUD_NATIVE_AI-400\ai-400-project-1
docker run -v $(pwd):/workspace -it ubuntu ls /workspace
# Should list files from your project directory
```

**❌ Permission denied?**
- Verify `C:` drive in File Sharing settings
- Restart Docker Desktop
- Try command again

## Step 7: Run Docker Learning Verification Script

Verify your complete Docker setup:

```powershell
cd C:\Users\xpert\OneDrive\Desktop\CLOUD_NATIVE_AI-400\ai-400-project-1
python .claude/skills/docker-learning/scripts/verify.py
```

Expected output:
```
✓ Docker installed (version 24.0.0)
✓ Docker daemon running
✓ docker-compose available (version 2.x.x)
✓ WSL 2 enabled
✓ Container runtime healthy
✓ Can access project files from containers

✅ Docker installation verified successfully!
```

**Some checks failing?** See troubleshooting section below.

## Troubleshooting

### Problem: "Cannot connect to Docker daemon"

**Cause:** Docker Desktop daemon not running

**Solutions (in order):**
1. Open Docker Desktop app from Start menu
2. Wait 1 minute for daemon startup
3. Try command again
4. If still failing: Settings → General → "Start Docker Desktop when you log in"
5. Restart computer

### Problem: "docker: command not found"

**Cause:** Docker not in system PATH

**Solutions:**
1. Restart PowerShell completely (close and reopen)
2. Verify installation: "Add Docker to PATH" was checked during install
3. If unchecked: Uninstall and reinstall Docker, ensuring PATH checkbox is selected
4. Manually add to PATH (advanced): `C:\Program Files\Docker\Docker\resources\bin`

### Problem: WSL 2 Installation Fails

**Error:** "Hyper-V feature not available" or similar

**Cause:** Virtualization disabled in BIOS or Hyper-V incompatible

**Solutions:**
1. Check BIOS: Restart computer, press `Del` or `F2` during startup
   - Find "Virtualization Technology" or "VT-x" setting
   - Enable it
   - Save and restart
2. Check Hyper-V: Open PowerShell (Admin):
   ```powershell
   Get-WindowsOptionalFeature -FeatureName Hyper-V -Online
   # Look for: State = Enabled
   ```
3. Enable manually (Admin PowerShell):
   ```powershell
   Enable-WindowsOptionalFeature -FeatureName Microsoft-Hyper-V -All -Online
   ```

### Problem: "Insufficient disk space for Docker images"

**Cause:** Docker disk image size too small or Windows partition full

**Solutions:**
1. Free up disk space: Delete temporary files, old files, or move files
2. Increase Docker disk image:
   - Settings → Resources → Disk image size
   - Increase to 128 GB or more
   - Click "Apply & Restart"

### Problem: Containers run very slowly on Windows

**Cause:** WSL 2 integration not enabled or insufficient resources

**Solutions:**
1. Verify WSL 2: Run `wsl --version` (should show WSL 2, not 1)
2. Increase memory allocation:
   - Settings → Resources → Memory
   - Increase to 6-8 GB
   - Click "Apply & Restart"
3. Disable antivirus scanning of Docker directories:
   - Windows Security → Virus & threat protection
   - Manage settings → Add exclusions
   - Add: `C:\Users\<username>\AppData\Local\Docker\`

### Problem: "No such file or directory" in Dockerfile

**Cause:** Line endings are Windows (CRLF) but Docker expects Unix (LF)

**Solutions:**
1. Configure git globally:
   ```powershell
   git config --global core.autocrlf input
   ```
2. Or in your project repository:
   ```powershell
   git config core.autocrlf input
   ```
3. Re-checkout files:
   ```powershell
   git rm --cached -r .
   git reset --hard
   ```

### Problem: Can't access containerized app from browser

**Issue:** Container is running but `http://localhost:8000` shows "Connection refused"

**Cause:** Port not properly mapped or container crashed

**Solutions:**
1. Verify port mapping:
   ```powershell
   docker ps
   # Look for: 0.0.0.0:8000->8000/tcp
   ```
2. Check container logs:
   ```powershell
   docker logs <container_id>
   ```
3. If using docker-compose:
   ```powershell
   docker-compose logs api
   ```

### Problem: Permission denied errors in Docker

**Cause:** User not in docker group (rare on Windows, more common in WSL)

**Solution (Windows):**
- Usually not applicable - Windows uses named pipes
- Try: Restart Docker Desktop → Restart PowerShell

**Solution (WSL - if using WSL terminal):**
```bash
# Inside WSL terminal:
sudo usermod -aG docker $USER
newgrp docker
```

## Uninstall Docker (if needed)

If you need to start over:

1. **Uninstall Docker Desktop:**
   - Settings → Apps → Apps & features
   - Search "Docker"
   - Click → Uninstall
   - Follow prompts (may need restart)

2. **Uninstall WSL (optional):**
   ```powershell
   wsl --uninstall --all
   ```

3. **Restart computer**

4. **Reinstall fresh:** Start from Step 1

## Next Steps

Once Docker is installed and verified:

1. **Run the learning verification script:**
   ```powershell
   python .claude/skills/docker-learning/scripts/verify.py
   ```

2. **Start learning with the docker-learning-tutor agent:**
   ```
   "I want to learn Docker from scratch"
   ```

3. **Complete Phase 1 exercises:**
   - Exercise 01: Your first Dockerfile
   - Exercise 02: Multi-stage optimization
   - Exercise 03: Containerize your Task API

## Windows-Specific Docker Behaviors

### Path Mounting
Windows paths in docker commands:
```powershell
# ✓ Correct - use PowerShell $(pwd) variable
docker run -v $(pwd):/app image:tag

# ✗ Incorrect - don't mix Windows backslashes
docker run -v C:\Users\xpert\project:/app image:tag  # Wrong syntax
```

### Line Endings (CRLF vs LF)
- Windows uses CRLF (`\r\n`)
- Docker/Linux uses LF (`\n`)
- Dockerfiles and shell scripts need LF
- Configure: `git config --global core.autocrlf input`

### Drive Letters and Paths
- `C:\` becomes `/c/` inside containers
- Example: `C:\Users\xpert` → `/c/Users/xpert`
- Docker Desktop handles this automatically in mounts

### Performance Optimization
- Avoid storing Docker data on network drives (OneDrive, network shares)
- Keep project files on local SSD for best performance
- If using OneDrive: Consider creating work directory outside OneDrive

## Getting Help

If you encounter issues not covered here:

1. **Check Docker logs:**
   ```powershell
   docker logs <container_id>
   ```

2. **Get system info:**
   ```powershell
   docker system info
   ```

3. **Use the docker-learning-tutor agent:**
   ```
   "I'm getting this Docker error: [paste error message]"
   ```

4. **Docker documentation:** https://docs.docker.com/
5. **Stack Overflow:** Tag: `docker`

---

**Last Updated:** 2026-01-20 | **Created for:** Windows 10/11 with Python 3.13

# VPS One-Click Deployment Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automate 1-click zero-downtime deployment from local workspace to VPS (`https://verischolar.duckdns.org`) using pre-built web bundles and rsync synchronization.

**Architecture:** Local build and verification (4 gates: ruff, pytest, npm test, npm build) followed by SSH-authenticated `rsync` of web distribution assets to `/var/www/verischolar/web` and backend monorepo to `/home/VeriScholar/Workspace/VeriScholar`, remote dependency resolution via `uv sync`, systemd service restart (`verischolar-api.service`), and live HTTPS health probe.

**Tech Stack:** Bash, rsync, OpenSSH, Systemd, Nginx, Python 3.12 (uv), React 19 / Vite.

**Spec:** [Approved VPS Deployment Design Doc](../specs/2026-10-26-vps-deployment-design.md)

## Global Constraints

- **AGENTS.md Rule 5 Compliance:** All Markdown documentation must use relative links only; never use absolute server URLs (`file://...`).
- **AGENTS.md Rule 6 Compliance:** Product-grade minimalism (no engineering brag, no internal hex colors, clear readable status).
- **Safety Gate:** No code or bundle is synced to the remote VPS if any of the 4 verification gates fails locally.
- **Data Protection:** Remote `.env`, PostgreSQL docker container, and Redis container on the VPS must never be overwritten or removed.

## Review Focus

1. **SSH key missing or bad permissions:** Script must check key existence and set `chmod 400` automatically.
2. **Local gate failure stops deployment:** Any failure in `pytest` or `npm build` immediately aborts before any remote touch.
3. **Dry-run mode safety:** `--dry-run` flag tests commands and logs actions without performing remote changes.
4. **Clean sync exclusions:** Ensure `.git`, `node_modules`, `.venv`, `.env`, and caches are excluded from rsync to protect remote environment.
5. **Post-deploy verification failure:** Script fails with non-zero exit code if `curl -fsS https://verischolar.duckdns.org/health` fails or times out.

---

### Task 1: Create Remote Deployment Script (`scripts/deploy_to_vps.sh`)

**Files:**
- Create: `scripts/deploy_to_vps.sh`
- Test: `tests/test_deploy_script.py`

**Interfaces:**
- CLI Flags: `--dry-run` (simulate actions), `--skip-gate` (skip local tests for fast hotfix), `--help` (display usage)
- Environment Variables:
  - `SSH_KEY`: Path to private key (default: `/home/dammanhdungvn/Downloads/VPS/VeriScholar_key.pem`)
  - `SSH_HOST`: Target host or IP (default: `48.193.46.15`)
  - `SSH_USER`: Remote username (default: `VeriScholar`)
  - `REMOTE_DIR`: Remote workspace directory (default: `/home/VeriScholar/Workspace/VeriScholar`)
  - `REMOTE_WEB_DIR`: Remote Nginx web root (default: `/var/www/verischolar/web`)
  - `PUBLIC_URL`: Remote live URL (default: `https://verischolar.duckdns.org`)

- [x] **Step 1: Write the failing test for deploy script argument parsing and help output**

```python
import subprocess
import pytest
from pathlib import Path

def test_deploy_script_help():
    script_path = Path("scripts/deploy_to_vps.sh")
    assert script_path.exists(), "scripts/deploy_to_vps.sh does not exist"
    res = subprocess.run(["bash", str(script_path), "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Usage: scripts/deploy_to_vps.sh" in res.stdout
    assert "--dry-run" in res.stdout
```

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_deploy_script.py -v`
Expected: FAIL with `AssertionError: scripts/deploy_to_vps.sh does not exist`

- [x] **Step 3: Implement `scripts/deploy_to_vps.sh`**

Implement bash script with:
- Error handling: `set -euo pipefail`
- Argument parsing: `--help`, `--dry-run`, `--skip-gate`
- Verification Gates execution (if not skipped)
- Local Web Frontend Build: `npm --prefix apps/web run build`
- Rsync of `apps/web/dist/` to `$SSH_USER@$SSH_HOST:$REMOTE_WEB_DIR/`
- Rsync of monorepo code to `$SSH_USER@$SSH_HOST:$REMOTE_DIR/` excluding `.git`, `node_modules`, `.venv`, `.env`, `__pycache__`
- Remote command via SSH: `uv sync --all-packages --frozen && sudo systemctl restart verischolar-api.service`
- Post-deploy health probe: `curl -fsS --max-time 15 "$PUBLIC_URL/health"`
- Chmod +x `scripts/deploy_to_vps.sh`

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_deploy_script.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add scripts/deploy_to_vps.sh tests/test_deploy_script.py
git commit -m "feat(deploy): implement automated VPS one-click deployment script"
```

---

### Task 2: Add Dry-Run and Validation Tests for Deploy Script

**Files:**
- Modify: `tests/test_deploy_script.py`

**Interfaces:**
- Consumes: `scripts/deploy_to_vps.sh`
- Tests: `--dry-run` flag behavior, non-existent key validation.

- [x] **Step 1: Write additional test cases in `tests/test_deploy_script.py`**

```python
def test_deploy_script_dry_run_with_skip_gate():
    script_path = Path("scripts/deploy_to_vps.sh")
    res = subprocess.run(
        ["bash", str(script_path), "--dry-run", "--skip-gate"],
        capture_output=True,
        text=True,
        env={"SSH_KEY": "/home/dammanhdungvn/Downloads/VPS/VeriScholar_key.pem", "PATH": subprocess.os.environ["PATH"]}
    )
    assert res.returncode == 0
    assert "[DRY-RUN]" in res.stdout
    assert "https://verischolar.duckdns.org" in res.stdout

def test_deploy_script_missing_key_fails():
    script_path = Path("scripts/deploy_to_vps.sh")
    res = subprocess.run(
        ["bash", str(script_path), "--dry-run", "--skip-gate"],
        capture_output=True,
        text=True,
        env={"SSH_KEY": "/non/existent/key.pem", "PATH": subprocess.os.environ["PATH"]}
    )
    assert res.returncode != 0
    assert "SSH key not found" in res.stderr or "SSH key not found" in res.stdout
```

- [x] **Step 2: Run test to verify it passes or check implementation needs**

Run: `uv run pytest tests/test_deploy_script.py -v`
Expected: PASS

- [x] **Step 3: Commit**

```bash
git add tests/test_deploy_script.py
git commit -m "test(deploy): add dry-run and missing key validation tests"
```

---

### Task 3: Execute Live Deployment to VPS

**Files:**
- Execute: `scripts/deploy_to_vps.sh`

**Interfaces:**
- Live SSH Target: `VeriScholar@48.193.46.15`
- Target URL: `https://verischolar.duckdns.org`

- [x] **Step 1: Execute live deployment script**

Run: `./scripts/deploy_to_vps.sh`
Expected:
- All 4 local verification gates pass (ruff, pytest, npm test, npm build).
- Web dist synced to `/var/www/verischolar/web`.
- Monorepo code synced to `/home/VeriScholar/Workspace/VeriScholar`.
- Remote `verischolar-api.service` restarted.
- Health check `https://verischolar.duckdns.org/health` returns status `ok`.

- [x] **Step 2: Verify live endpoint and web frontend**

Run: `curl -fsS https://verischolar.duckdns.org/health`
Run: `curl -fsS https://verischolar.duckdns.org/ | grep -i "VeriScholar"`
Expected: HTTP 200 with valid content.

- [x] **Step 3: Commit deployment confirmation and log**

```bash
git add scripts/deploy_to_vps.sh tests/test_deploy_script.py docs/superpowers/plans/2026-10-26-vps-one-click-deployment.md
git commit -m "chore(deploy): successfully deploy VeriScholar MVP with 5.6-Luna reasoning to VPS"
```

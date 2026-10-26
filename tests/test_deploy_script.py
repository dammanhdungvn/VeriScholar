import os
import subprocess
from pathlib import Path


def test_deploy_script_help():
    script_path = Path("scripts/deploy_to_vps.sh")
    assert script_path.exists(), "scripts/deploy_to_vps.sh does not exist"
    res = subprocess.run(["bash", str(script_path), "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Usage: scripts/deploy_to_vps.sh" in res.stdout
    assert "--dry-run" in res.stdout
    assert "--no-sync-db" in res.stdout


def test_deploy_script_dry_run_with_skip_gate():
    script_path = Path("scripts/deploy_to_vps.sh")
    env = {**os.environ, "SSH_KEY": "/home/dammanhdungvn/Downloads/VPS/VeriScholar_key.pem"}
    res = subprocess.run(
        ["bash", str(script_path), "--dry-run", "--skip-gate"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode == 0
    assert "[DRY-RUN]" in res.stdout
    assert "https://verischolar.duckdns.org" in res.stdout


def test_deploy_script_missing_key_fails():
    script_path = Path("scripts/deploy_to_vps.sh")
    env = {**os.environ, "SSH_KEY": "/non/existent/key.pem"}
    res = subprocess.run(
        ["bash", str(script_path), "--dry-run", "--skip-gate"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode != 0
    assert "SSH key not found" in res.stderr or "SSH key not found" in res.stdout


def test_deploy_script_unknown_argument_fails():
    script_path = Path("scripts/deploy_to_vps.sh")
    res = subprocess.run(
        ["bash", str(script_path), "--invalid-option"],
        capture_output=True,
        text=True,
    )
    assert res.returncode != 0
    assert "Unknown argument" in res.stderr or "Unknown argument" in res.stdout

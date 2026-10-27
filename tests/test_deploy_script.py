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


def test_deploy_script_dry_run_with_skip_gate(tmp_path):
    script_path = Path("scripts/deploy_to_vps.sh")
    dummy_key = tmp_path / "dummy_key.pem"
    dummy_key.write_text("dummy private key")
    dummy_key.chmod(0o400)
    env = {**os.environ, "SSH_KEY": str(dummy_key)}
    res = subprocess.run(
        ["bash", str(script_path), "--dry-run", "--skip-gate"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode == 0
    assert "[DRY-RUN]" in res.stdout


def test_deploy_script_offline_vps_exits_zero_fast(tmp_path):
    import time

    script_path = Path("scripts/deploy_to_vps.sh")
    dummy_key = tmp_path / "dummy_key.pem"
    dummy_key.write_text("dummy private key")
    dummy_key.chmod(0o400)
    # 192.0.2.1 is reserved by RFC 5737 as documentation net (unroutable/unreachable)
    env = {**os.environ, "SSH_KEY": str(dummy_key), "SSH_HOST": "192.0.2.1"}
    start = time.time()
    res = subprocess.run(
        ["bash", str(script_path), "--fast"],
        capture_output=True,
        text=True,
        env=env,
    )
    elapsed = time.time() - start
    assert res.returncode == 0
    assert elapsed < 4.0, f"Expected fast failover in < 4s, took {elapsed:.2f}s"
    assert "offline" in res.stdout.lower() or "unreachable" in res.stdout.lower()

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


def test_deploy_script_fast_flag_help():
    script_path = Path("scripts/deploy_to_vps.sh")
    res = subprocess.run(["bash", str(script_path), "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "--fast" in res.stdout


def test_deploy_script_fast_flag_dry_run(tmp_path):
    script_path = Path("scripts/deploy_to_vps.sh")
    dummy_key = tmp_path / "dummy_key.pem"
    dummy_key.write_text("dummy private key")
    dummy_key.chmod(0o400)
    env = {**os.environ, "SSH_KEY": str(dummy_key)}
    res = subprocess.run(
        ["bash", str(script_path), "--dry-run", "--fast"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode == 0
    assert "[DRY-RUN]" in res.stdout


def test_deploy_script_offline_vps_exits_zero_fast(tmp_path):
    import time

    script_path = Path("scripts/deploy_to_vps.sh")
    dummy_key = tmp_path / "dummy_key.pem"
    dummy_key.write_text("dummy private key")
    dummy_key.chmod(0o400)
    # 192.0.2.1 is reserved by RFC 5737 as documentation net (unroutable/unreachable)
    env = {**os.environ, "SSH_KEY": str(dummy_key), "SSH_HOST": "192.0.2.1"}
    start = time.time()
    res = subprocess.run(
        ["bash", str(script_path), "--fast"],
        capture_output=True,
        text=True,
        env=env,
    )
    elapsed = time.time() - start
    assert res.returncode == 0
    assert elapsed < 4.0, f"Expected fast failover in < 4s, took {elapsed:.2f}s"
    assert "offline" in res.stdout.lower() or "unreachable" in res.stdout.lower()



import subprocess
from pathlib import Path


def test_deploy_script_help():
    script_path = Path("scripts/deploy_to_vps.sh")
    assert script_path.exists(), "scripts/deploy_to_vps.sh does not exist"
    res = subprocess.run(["bash", str(script_path), "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Usage: scripts/deploy_to_vps.sh" in res.stdout
    assert "--dry-run" in res.stdout

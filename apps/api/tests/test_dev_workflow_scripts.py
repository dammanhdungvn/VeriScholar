import os
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]


def test_verify_script_exists_and_enforces_four_gates():
    verify_script = ROOT_DIR / "scripts" / "dev" / "verify.sh"
    assert verify_script.exists(), "scripts/dev/verify.sh must exist"
    assert os.access(verify_script, os.X_OK), "scripts/dev/verify.sh must be executable"

    # Syntax check via bash -n
    res = subprocess.run(["bash", "-n", str(verify_script)], capture_output=True, text=True)
    assert res.returncode == 0, f"bash -n failed: {res.stderr}"

    content = verify_script.read_text(encoding="utf-8")
    assert "uv run ruff check ." in content
    assert "uv run ruff format --check ." in content
    assert "uv run pytest" in content
    assert "npm --prefix apps/web run test" in content
    assert "npm --prefix apps/web run build" in content


def test_setup_script_automates_env_deps_db_and_pre_push_hook():
    setup_script = ROOT_DIR / "scripts" / "dev" / "setup.sh"
    assert setup_script.exists(), "scripts/dev/setup.sh must exist"
    assert os.access(setup_script, os.X_OK), "scripts/dev/setup.sh must be executable"

    res = subprocess.run(["bash", "-n", str(setup_script)], capture_output=True, text=True)
    assert res.returncode == 0, f"bash -n failed: {res.stderr}"

    content = setup_script.read_text(encoding="utf-8")
    assert "ln -sf ../../.env apps/api/.env" in content
    assert "uv sync --all-packages" in content
    assert "api.db.init_db" in content
    assert ".git/hooks/pre-push" in content
    assert "--start" in content


def test_makefile_and_ci_reference_dev_scripts():
    makefile = ROOT_DIR / "Makefile"
    assert makefile.exists(), "Root Makefile must exist"
    mk_content = makefile.read_text(encoding="utf-8")
    for target in ("setup:", "dev:", "verify:"):
        assert target in mk_content, f"Makefile missing target {target}"

    ci_yml = ROOT_DIR / ".github" / "workflows" / "ci.yml"
    ci_content = ci_yml.read_text(encoding="utf-8")
    assert "scripts/dev/verify.sh" in ci_content

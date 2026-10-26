import json
from pathlib import Path


def test_vscode_latex_settings():
    settings_path = Path(".vscode/settings.json")
    assert settings_path.exists()
    settings = json.loads(settings_path.read_text(encoding="utf-8"))

    # Đảm bảo cấu hình XeLaTeX tool và recipe
    assert "latex-workshop.latex.tools" in settings
    tools = {t["name"]: t for t in settings["latex-workshop.latex.tools"]}
    assert "xelatex" in tools
    assert tools["xelatex"]["command"] == "xelatex"

    assert "latex-workshop.latex.recipes" in settings
    recipes = {r["name"]: r for r in settings["latex-workshop.latex.recipes"]}
    assert "xelatex" in recipes

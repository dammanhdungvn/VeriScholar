"""Prompts-as-Code Engine and Template Registry.

Parses .prompt.md files containing YAML frontmatter metadata and Jinja2-templated
markdown instruction bodies for production-grade LLM prompting.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import yaml
from jinja2.sandbox import SandboxedEnvironment
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

# Sandboxed Jinja2 environment to prevent arbitrary code execution
_SANDBOX_ENV = SandboxedEnvironment(
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)


class PromptMetadata(BaseModel):
    """YAML Frontmatter metadata for a prompt artifact."""

    model_config = ConfigDict(extra="ignore")

    name: str
    version: str = "1.0.0"
    description: str = ""
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    input_variables: list[str] = Field(default_factory=list)


class PromptTemplate:
    """Executable Prompt Unit parsed from a .prompt.md file."""

    def __init__(
        self,
        metadata: PromptMetadata,
        raw_body: str,
        source_path: Path | None = None,
    ) -> None:
        self.metadata = metadata
        self.raw_body = raw_body
        self.source_path = source_path
        self._system_raw, self._user_raw = self._split_roles(raw_body)
        self._system_tmpl = _SANDBOX_ENV.from_string(self._system_raw) if self._system_raw else None
        self._user_tmpl = _SANDBOX_ENV.from_string(self._user_raw) if self._user_raw else None
        self._full_tmpl = _SANDBOX_ENV.from_string(raw_body)

    @staticmethod
    def _split_roles(body: str) -> tuple[str | None, str | None]:
        """Split markdown into system and user sections if demarcated by headers."""
        system_match = re.search(r"#\s*System\s*\n(.*?)(?=\n#\s*User|\Z)", body, re.DOTALL)
        user_match = re.search(r"#\s*User\s*\n(.*)", body, re.DOTALL)

        system_part = system_match.group(1).strip() if system_match else None
        user_part = user_match.group(1).strip() if user_match else None
        return system_part, user_part

    def render(self, **kwargs: Any) -> str:
        """Render the complete prompt body with injected variables."""
        return self._full_tmpl.render(**kwargs).strip()

    def render_messages(self, **kwargs: Any) -> list[dict[str, str]]:
        """Render structured OpenAI-compatible messages list [system, user]."""
        messages: list[dict[str, str]] = []
        if self._system_tmpl:
            sys_rendered = self._system_tmpl.render(**kwargs).strip()
            messages.append({"role": "system", "content": sys_rendered})
        if self._user_tmpl:
            usr_rendered = self._user_tmpl.render(**kwargs).strip()
            messages.append({"role": "user", "content": usr_rendered})

        if not messages:
            messages.append({"role": "user", "content": self.render(**kwargs)})
        return messages

    @classmethod
    def from_file(cls, path: Path | str) -> PromptTemplate:
        """Load and parse a .prompt.md file."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        raw_text = file_path.read_text(encoding="utf-8")
        return cls.from_string(raw_text, source_path=file_path)

    @classmethod
    def from_string(cls, text: str, source_path: Path | None = None) -> PromptTemplate:
        """Parse raw prompt content with YAML frontmatter."""
        # Match frontmatter between leading --- delimiters
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
        if not frontmatter_match:
            # No frontmatter provided; use default metadata
            meta = PromptMetadata(name=source_path.stem if source_path else "unnamed_prompt")
            return cls(metadata=meta, raw_body=text.strip(), source_path=source_path)

        yaml_content = frontmatter_match.group(1)
        body_content = frontmatter_match.group(2).strip()

        parsed_meta = yaml.safe_load(yaml_content) or {}
        if not isinstance(parsed_meta, dict):
            parsed_meta = {}

        if "name" not in parsed_meta and source_path:
            parsed_meta["name"] = source_path.stem

        meta = PromptMetadata(**parsed_meta)
        return cls(metadata=meta, raw_body=body_content, source_path=source_path)


class PromptRegistry:
    """Central registry caching parsed prompt artifacts."""

    def __init__(self, base_dir: Path | None = None) -> None:
        if base_dir is None:
            # Default to core/prompts directory
            base_dir = Path(__file__).parent
        self.base_dir = Path(base_dir)
        self._cache: dict[str, dict[str, PromptTemplate]] = {}
        self._scanned = False

    def scan(self) -> None:
        """Scan directory tree for all .prompt.md files."""
        if not self.base_dir.exists():
            return

        for p_file in self.base_dir.rglob("*.prompt.md"):
            try:
                tmpl = PromptTemplate.from_file(p_file)
                name = tmpl.metadata.name
                version = tmpl.metadata.version
                if name not in self._cache:
                    self._cache[name] = {}
                self._cache[name][version] = tmpl
            except Exception as exc:
                logger.warning("Failed to load prompt from %s: %s", p_file, exc)
        self._scanned = True

    def get(self, name: str, version: str = "latest") -> PromptTemplate:
        """Retrieve a cached prompt template by name and optional version."""
        if not self._scanned:
            self.scan()

        if name not in self._cache:
            raise KeyError(f"Prompt '{name}' not found in registry at {self.base_dir}")

        versions = self._cache[name]
        if version == "latest":
            # Select highest version or only available
            latest_v = sorted(versions.keys())[-1]
            return versions[latest_v]

        if version not in versions:
            avail = list(versions.keys())
            raise KeyError(f"Prompt '{name}' version '{version}' not found. Available: {avail}")

        return versions[version]


# Global singleton registry instance
default_registry = PromptRegistry()

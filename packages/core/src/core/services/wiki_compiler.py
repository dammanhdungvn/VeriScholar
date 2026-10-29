"""Pure domain Wiki Compiler service for Compiled Academic LLM Wiki.

Strictly adheres to Rule 2 (Hexagonal Isolation): Standard Library + Pydantic only.
Zero framework, ORM, or external YAML dependencies.
"""

import re
import unicodedata
from typing import Any

from core.models.wiki import WikiCompileResult, WikiPageDraft


class WikiCompiler:
    """Pure domain service for compiling and parsing academic wiki markdown pages.

    Features:
    - Normalizes titles into URL-safe slugs.
    - Generates and parses YAML frontmatter without external libraries.
    - Resolves and extracts [[wikilinks]] (including piped [[Target|Alias]]).
    - Produces structured WikiCompileResult.
    """

    WIKILINK_PATTERN = re.compile(r"\[\[(.*?)\]\]")
    FRONTMATTER_PATTERN = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)

    def slugify(self, text: str) -> str:
        """Converts an arbitrary title or heading into a clean URL-safe slug."""
        normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        subbed = re.sub(r"[^\w\s-]", "-", normalized).strip().lower()
        return re.sub(r"[-\s]+", "-", subbed).strip("-")

    def extract_wikilinks(self, text: str) -> list[str]:
        """Extracts unique [[wikilink]] targets preserving order of occurrence.

        Handles standard links `[[Concept]]` and piped links `[[Concept|Display]]`.
        """
        seen: set[str] = set()
        links: list[str] = []
        for match in self.WIKILINK_PATTERN.findall(text):
            target = match.split("|")[0].strip()
            if target and target not in seen:
                seen.add(target)
                links.append(target)
        return links

    def _parse_yaml_scalar(self, val: str) -> Any:
        """Parses a primitive scalar value from YAML."""
        val = val.strip()
        if not val:
            return ""
        is_double_quoted = val.startswith('"') and val.endswith('"')
        is_single_quoted = val.startswith("'") and val.endswith("'")
        if is_double_quoted or is_single_quoted:
            return val[1:-1].replace('\\"', '"').replace("\\'", "'")
        lower = val.lower()
        if lower in ("true", "yes", "on"):
            return True
        if lower in ("false", "no", "off"):
            return False
        if lower in ("null", "none", "~"):
            return None
        # Try integer
        try:
            return int(val)
        except ValueError:
            pass
        # Try float
        try:
            return float(val)
        except ValueError:
            pass
        return val

    def _parse_yaml_flow_list(self, raw_items: str) -> list[Any]:
        """Parses a YAML flow sequence `[item1, item2]`."""
        items: list[Any] = []
        # Split by comma not inside quotes
        pattern = r",\s*(?=(?:[^\'\"]*[\'\"][^\'\"]*[\'\"])*[^\'\"]*$)"
        parts = re.split(pattern, raw_items)
        for part in parts:
            cleaned = part.strip()
            if cleaned:
                items.append(self._parse_yaml_scalar(cleaned))
        return items

    def _parse_yaml_lines(self, yaml_str: str) -> dict[str, Any]:
        """Parses YAML frontmatter key-values using pure standard library regex."""
        metadata: dict[str, Any] = {}
        current_list_key: str | None = None

        for raw_line in yaml_str.splitlines():
            line = raw_line.rstrip()
            if not line or line.strip().startswith("#"):
                continue

            # Check block list item `  - item` or `- item`
            list_match = re.match(r"^\s*-\s+(.*)$", line)
            if list_match and current_list_key is not None:
                scalar = self._parse_yaml_scalar(list_match.group(1))
                metadata[current_list_key].append(scalar)
                continue

            # Key-value line `key: value` or `key:`
            kv_match = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
            if kv_match:
                key = kv_match.group(1)
                raw_val = kv_match.group(2).strip()

                if not raw_val:
                    # Expecting subsequent block list items
                    metadata[key] = []
                    current_list_key = key
                elif raw_val.startswith("[") and raw_val.endswith("]"):
                    current_list_key = None
                    metadata[key] = self._parse_yaml_flow_list(raw_val[1:-1])
                else:
                    current_list_key = None
                    metadata[key] = self._parse_yaml_scalar(raw_val)
            else:
                current_list_key = None

        return metadata

    def parse_frontmatter(self, text: str) -> tuple[dict[str, Any], str]:
        """Extracts YAML frontmatter dictionary and markdown body from document."""
        match = self.FRONTMATTER_PATTERN.search(text)
        if not match:
            return {}, text
        frontmatter_str = match.group(1)
        body = text[match.end() :]
        metadata = self._parse_yaml_lines(frontmatter_str)
        return metadata, body

    def format_frontmatter(self, metadata: dict[str, Any]) -> str:
        """Formats a metadata dictionary into YAML frontmatter string."""
        lines = ["---"]
        for k, v in metadata.items():
            if isinstance(v, list):
                if not v:
                    lines.append(f"{k}: []")
                elif all(isinstance(x, (str, int, float, bool)) for x in v):
                    formatted_items = []
                    for item in v:
                        if isinstance(item, bool):
                            formatted_items.append("true" if item else "false")
                        elif isinstance(item, (int, float)):
                            formatted_items.append(str(item))
                        else:
                            s_item = str(item)
                            if any(c in s_item for c in [",", "[", "]", ":", '"', "'"]):
                                escaped = s_item.replace('"', '\\"')
                                formatted_items.append(f'"{escaped}"')
                            else:
                                formatted_items.append(s_item)
                    lines.append(f"{k}: [{', '.join(formatted_items)}]")
                else:
                    lines.append(f"{k}:")
                    for item in v:
                        lines.append(f"  - {item}")
            elif isinstance(v, bool):
                lines.append(f"{k}: {'true' if v else 'false'}")
            elif v is None:
                lines.append(f"{k}: null")
            elif isinstance(v, (int, float)):
                lines.append(f"{k}: {v}")
            else:
                s_val = str(v)
                special_chars = (":", "#", "\n", '"', "'")
                has_special = any(c in s_val for c in special_chars)
                has_prefix = s_val.startswith(("[", "{", "-"))
                if has_special or has_prefix:
                    escaped = s_val.replace('"', '\\"')
                    lines.append(f'{k}: "{escaped}"')
                else:
                    lines.append(f"{k}: {s_val}")
        lines.append("---")
        return "\n".join(lines)

    def compile_page(self, draft: WikiPageDraft) -> WikiCompileResult:
        """Compiles a WikiPageDraft into a markdown document with frontmatter and wikilinks."""
        slug = draft.slug or self.slugify(draft.title)
        yaml_metadata: dict[str, Any] = {
            "title": draft.title,
            "slug": slug,
        }
        if draft.tags:
            yaml_metadata["tags"] = draft.tags
        if draft.source_papers:
            yaml_metadata["source_papers"] = draft.source_papers
        if draft.related_entities:
            yaml_metadata["related_entities"] = draft.related_entities
        if draft.custom_metadata:
            for k, v in draft.custom_metadata.items():
                if k not in yaml_metadata:
                    yaml_metadata[k] = v

        sections: list[str] = [f"# {draft.title}"]
        if draft.summary:
            sections.append(draft.summary)

        if draft.content:
            sections.append(draft.content)

        if draft.key_insights:
            insights_lines = ["## Key Insights"]
            for insight in draft.key_insights:
                insights_lines.append(f"- {insight}")
            sections.append("\n".join(insights_lines))

        if draft.related_entities:
            entities_lines = ["## Related Concepts"]
            for entity in draft.related_entities:
                entities_lines.append(f"- [[{entity}]]")
            sections.append("\n".join(entities_lines))

        if draft.source_papers:
            papers_lines = ["## Source Papers"]
            for paper in draft.source_papers:
                papers_lines.append(f"- {paper}")
            sections.append("\n".join(papers_lines))

        body = "\n\n".join(sections).strip()
        frontmatter_str = self.format_frontmatter(yaml_metadata)
        full_markdown = f"{frontmatter_str}\n\n{body}\n"
        wikilinks = self.extract_wikilinks(full_markdown)

        return WikiCompileResult(
            slug=slug,
            title=draft.title,
            markdown=full_markdown,
            yaml_metadata=yaml_metadata,
            wikilinks=wikilinks,
            body=body,
        )

    def parse_markdown(self, raw: str) -> WikiCompileResult:
        """Parses a markdown document with YAML frontmatter into a WikiCompileResult."""
        yaml_metadata, body = self.parse_frontmatter(raw)
        title = ""
        if "title" in yaml_metadata and yaml_metadata["title"]:
            title = str(yaml_metadata["title"])
        else:
            heading_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
            if heading_match:
                title = heading_match.group(1).strip()
            elif "slug" in yaml_metadata:
                title = str(yaml_metadata["slug"]).replace("-", " ").title()
            else:
                title = "Untitled"

        slug = str(yaml_metadata.get("slug") or self.slugify(title))
        yaml_metadata.setdefault("slug", slug)
        yaml_metadata.setdefault("title", title)

        wikilinks = self.extract_wikilinks(raw)

        return WikiCompileResult(
            slug=slug,
            title=title,
            markdown=raw,
            yaml_metadata=yaml_metadata,
            wikilinks=wikilinks,
            body=body.strip(),
        )

"""Entity sanity and semantic invariant checks (preventing corrupted authors and dates)."""

import re
from datetime import datetime
from typing import Any

from scripts.eval.metrics.base import BaseEvalMetric, MetricResult

# Keywords that indicate text parser erroneously extracted institution/org as author
FORBIDDEN_AUTHOR_KEYWORDS = {
    "university",
    "department",
    "institute",
    "faculty",
    "school",
    "laboratory",
    "center",
    "centre",
    "hospital",
    "college",
    "corporation",
    "foundation",
    "inc.",
    "ltd.",
    "gmbh",
    "dept.",
    "div.",
}


class EntitySanityMetric(BaseEvalMetric):
    """Verifies academic entity metadata sanity against extraction hallucinations."""

    def __init__(self, current_year: int | None = None):
        self.current_year = current_year or datetime.now().year

    @property
    def name(self) -> str:
        return "entity_sanity"

    def measure(self, prediction: Any, ground_truth: Any = None, **kwargs: Any) -> MetricResult:
        """Prediction: list of reference dicts or metadata dict with 'authors', 'year', 'title'."""
        entities: list[dict[str, Any]] = []
        if isinstance(prediction, list):
            for item in prediction:
                if isinstance(item, dict):
                    entities.append(item.get("parsed", item))
        elif isinstance(prediction, dict):
            if "references" in prediction and isinstance(prediction["references"], list):
                for item in prediction["references"]:
                    if isinstance(item, dict):
                        entities.append(item.get("parsed", item))
            else:
                entities.append(prediction)

        if not entities:
            return MetricResult(
                name=self.name,
                score=1.0,
                threshold=0.9,
                passed=True,
                details={"total_entities": 0},
                reasoning="No entities present in payload to evaluate.",
            )

        anomalies: list[dict[str, Any]] = []

        for idx, ent in enumerate(entities):
            item_id = ent.get("title") or ent.get("raw_text") or f"Item #{idx}"
            if len(item_id) > 60:
                item_id = item_id[:57] + "..."

            # 1. Check Author validity
            authors = ent.get("authors") or []
            if isinstance(authors, str):
                authors = [authors]

            for auth in authors:
                clean_auth = str(auth).strip()
                auth_lower = clean_auth.lower()

                # Author name length bound check
                if len(clean_auth) > 60:
                    anomalies.append(
                        {
                            "item_id": item_id,
                            "error": "AUTHOR_TOO_LONG",
                            "author": clean_auth[:50] + "...",
                            "detail": f"Author name length {len(clean_auth)} > 60.",
                        }
                    )
                elif len(clean_auth) < 2 and clean_auth != "":
                    anomalies.append(
                        {
                            "item_id": item_id,
                            "error": "AUTHOR_TOO_SHORT",
                            "author": clean_auth,
                            "detail": f"Author name '{clean_auth}' too short (< 2).",
                        }
                    )

                # Author should not contain email symbol '@'
                if "@" in clean_auth:
                    anomalies.append(
                        {
                            "item_id": item_id,
                            "error": "EMAIL_AS_AUTHOR",
                            "author": clean_auth,
                            "detail": "Email address found in author name.",
                        }
                    )

                # Author should not contain organizational / institutional keywords
                for kw in FORBIDDEN_AUTHOR_KEYWORDS:
                    if re.search(r"\b" + re.escape(kw) + r"\b", auth_lower):
                        anomalies.append(
                            {
                                "item_id": item_id,
                                "error": "ORGANIZATION_AS_AUTHOR",
                                "author": clean_auth,
                                "keyword": kw,
                                "detail": (
                                    f"Author '{clean_auth}' has organizational keyword '{kw}'."
                                ),
                            }
                        )
                        break

            # 2. Check Publication Year Validity [1800, current_year + 1]
            year = ent.get("year") or ent.get("publication_year")
            if year is not None:
                try:
                    year_int = int(year)
                    max_yr = self.current_year + 1
                    if year_int < 1800 or year_int > max_yr:
                        anomalies.append(
                            {
                                "item_id": item_id,
                                "error": "INVALID_PUBLICATION_YEAR",
                                "year": year_int,
                                "detail": f"Year {year_int} out of bounds [1800, {max_yr}].",
                            }
                        )
                except (ValueError, TypeError):
                    anomalies.append(
                        {
                            "item_id": item_id,
                            "error": "NON_NUMERIC_YEAR",
                            "year": str(year),
                            "detail": f"Year value '{year}' is not an integer.",
                        }
                    )

            # 3. Check Title Validity (not just digits/punctuation)
            title = ent.get("title")
            if title and isinstance(title, str):
                clean_title = title.strip()
                if len(clean_title) < 3:
                    anomalies.append(
                        {
                            "item_id": item_id,
                            "error": "TITLE_TOO_SHORT",
                            "title": clean_title,
                            "detail": f"Title '{clean_title}' is fewer than 3 chars.",
                        }
                    )

        total_checks = max(1, len(entities))
        score = max(0.0, 1.0 - (len(anomalies) / total_checks))
        passed = len(anomalies) == 0

        return MetricResult(
            name=self.name,
            score=round(score, 4),
            threshold=1.0,
            passed=passed,
            details={"total_entities": len(entities), "anomalies_count": len(anomalies)},
            error_samples=anomalies[:5],
            reasoning=(
                "All entities passed sanity invariants."
                if passed
                else f"Found {len(anomalies)} entity anomalies."
            ),
        )

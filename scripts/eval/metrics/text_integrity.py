"""Text integrity metric (Zero-Token heuristics against Mojibake and truncation)."""

from typing import Any

from scripts.eval.metrics.base import BaseEvalMetric, MetricResult


class TextIntegrityMetric(BaseEvalMetric):
    """Measures text extraction completeness, encoding sanity, and structural cleanliness."""

    def __init__(self, min_coverage: float = 0.75, max_word_length: int = 25):
        self.min_coverage = min_coverage
        self.max_word_length = max_word_length

    @property
    def name(self) -> str:
        return "text_integrity"

    def measure(self, prediction: Any, ground_truth: Any = None, **kwargs: Any) -> MetricResult:
        """Prediction: string, list of chunks/references, or dict containing chunks/references.

        Ground truth: raw text string or total char count (optional).
        """
        # Unpack dict if needed
        if isinstance(prediction, dict):
            if "chunks" in prediction and isinstance(prediction["chunks"], list):
                prediction = prediction["chunks"]
            elif "references" in prediction and isinstance(prediction["references"], list):
                prediction = [
                    r.get("raw_text", "") for r in prediction["references"] if isinstance(r, dict)
                ]
            elif "text" in prediction and isinstance(prediction["text"], str):
                prediction = prediction["text"]
            elif "content" in prediction and isinstance(prediction["content"], str):
                prediction = prediction["content"]

        # 1. Extract plain text from prediction
        if isinstance(prediction, str):
            extracted_text = prediction
        elif isinstance(prediction, list):
            extracted_text = " ".join(
                c.get("text", "")
                if isinstance(c, dict)
                else (c.get("raw_text", "") if isinstance(c, dict) else str(c))
                for c in prediction
            )
        else:
            return MetricResult(
                name=self.name,
                score=0.0,
                threshold=1.0,
                passed=False,
                reasoning=f"Unsupported prediction type: {type(prediction)}",
            )

        anomalies: list[dict[str, Any]] = []
        total_chars = len(extracted_text)

        # 2. Check empty or near-empty extraction
        if total_chars == 0:
            return MetricResult(
                name=self.name,
                score=0.0,
                threshold=self.min_coverage,
                passed=False,
                details={"total_chars": 0},
                error_samples=[{"error": "EMPTY_TEXT", "detail": "Extracted 0 characters."}],
                reasoning="Prediction output is completely empty.",
            )

        # 3. Check Unicode Mojibake / invalid replacement characters
        mojibake_count = extracted_text.count("\ufffd")
        if mojibake_count > 0:
            anomalies.append(
                {
                    "error": "UNICODE_MOJIBAKE",
                    "count": mojibake_count,
                    "detail": f"Found {mojibake_count} unicode replacement characters (\\ufffd).",
                }
            )

        # 4. Check invalid ASCII control characters (excluding newline, tab, carriage return)
        control_chars = [c for c in extracted_text if ord(c) < 32 and c not in ("\n", "\t", "\r")]
        if control_chars:
            anomalies.append(
                {
                    "error": "CONTROL_CHARACTERS",
                    "count": len(control_chars),
                    "detail": f"Found {len(control_chars)} raw control characters.",
                }
            )

        # 5. Check word gluing (extreme average word length)
        words = extracted_text.split()
        if words:
            avg_word_len = sum(len(w) for w in words) / len(words)
            if avg_word_len > self.max_word_length:
                anomalies.append(
                    {
                        "error": "WORD_GLUING",
                        "avg_word_length": round(avg_word_len, 2),
                        "detail": (
                            f"Average word length {avg_word_len:.1f} > {self.max_word_length}."
                        ),
                    }
                )

        # 6. Check Text Coverage Ratio if ground_truth text provided
        coverage_ratio = 1.0
        if ground_truth:
            if isinstance(ground_truth, str):
                gt_len = len(ground_truth)
            elif isinstance(ground_truth, (int, float)):
                gt_len = int(ground_truth)
            else:
                gt_len = 0

            if gt_len > 0:
                coverage_ratio = min(1.0, total_chars / gt_len)
                if coverage_ratio < self.min_coverage:
                    anomalies.append(
                        {
                            "error": "TRUNCATION_DETECTED",
                            "coverage_ratio": round(coverage_ratio, 4),
                            "extracted_chars": total_chars,
                            "expected_chars": gt_len,
                            "detail": f"Extracted only {coverage_ratio:.1%} of raw document text.",
                        }
                    )

        score = 1.0 if not anomalies else max(0.0, 1.0 - (len(anomalies) * 0.25))
        passed = score >= 0.75 and mojibake_count == 0 and coverage_ratio >= self.min_coverage

        return MetricResult(
            name=self.name,
            score=round(score, 4),
            threshold=0.75,
            passed=passed,
            details={
                "total_chars": total_chars,
                "coverage_ratio": round(coverage_ratio, 4),
                "mojibake_count": mojibake_count,
                "anomalies_count": len(anomalies),
            },
            error_samples=anomalies[:5],
            reasoning=(
                "Text passed integrity and encoding checks."
                if passed
                else f"Text failed integrity: {len(anomalies)} anomalies detected."
            ),
        )

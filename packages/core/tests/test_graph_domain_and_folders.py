from uuid import uuid4

import pytest
from core.services.graph_extractor import (
    ExtractedGraphPayload,
    detect_folder_cycle,
    normalize_canonical_name,
)
from pydantic import ValidationError


def test_normalize_canonical_name_lowercases_and_collapses_spaces():
    assert normalize_canonical_name("  Transformer   Architecture \n") == "transformer architecture"
    assert normalize_canonical_name("\tBERT \t  Large \r\n") == "bert large"
    assert normalize_canonical_name(" ResNet-50 ") == "resnet-50"


def test_extracted_graph_payload_validates_strict_schema():
    payload = {
        "entities": [
            {"type": "Paper", "name": "Attention Is All You Need", "page_number": 1},
            {"type": "Method", "name": "Transformer", "page_number": 3},
            {"type": "Dataset", "name": "WMT-2014 En-De", "page_number": 6},
            {
                "type": "MetricResult",
                "name": "BLEU: 28.4",
                "page_number": 8,
                "context_tuple": {
                    "dataset": "WMT-2014 En-De",
                    "task": "Translation",
                    "split": "test",
                    "metric_name": "BLEU",
                    "value": 28.4,
                    "unit": "points",
                },
            },
        ],
        "relations": [
            {
                "source_name": "Attention Is All You Need",
                "target_name": "Transformer",
                "type": "PROPOSES",
                "page_number": 3,
            },
            {
                "source_name": "Transformer",
                "target_name": "WMT-2014 En-De",
                "type": "EVALUATED_ON",
                "page_number": 6,
            },
            {
                "source_name": "Transformer",
                "target_name": "BLEU: 28.4",
                "type": "ACHIEVES",
                "page_number": 8,
            },
            {
                "source_name": "Attention Is All You Need",
                "target_name": "Neural Machine Translation",
                "type": "CITES",
                "page_number": 10,
            },
        ],
    }
    validated = ExtractedGraphPayload.model_validate(payload)
    assert len(validated.entities) == 4
    assert len(validated.relations) == 4
    assert validated.entities[3].context_tuple is not None
    assert validated.entities[3].context_tuple.metric_name == "BLEU"
    assert validated.entities[3].context_tuple.value == 28.4


def test_extracted_graph_payload_rejects_invalid_entity_or_edge_type():
    with pytest.raises(ValidationError):
        ExtractedGraphPayload.model_validate(
            {
                "entities": [{"type": "Author", "name": "Vaswani", "page_number": 1}],
                "relations": [],
            }
        )

    with pytest.raises(ValidationError):
        ExtractedGraphPayload.model_validate(
            {
                "entities": [{"type": "Method", "name": "Transformer", "page_number": 1}],
                "relations": [
                    {
                        "source_name": "Transformer",
                        "target_name": "Attention",
                        "type": "USES",
                        "page_number": 1,
                    }
                ],
            }
        )


def test_detect_folder_cycle_catches_self_and_descendant_parent():
    a, b, c, d = uuid4(), uuid4(), uuid4(), uuid4()
    parent_map = {a: None, b: a, c: b, d: c}

    # Cannot move node into itself
    assert detect_folder_cycle(a, a, parent_map) is True
    assert detect_folder_cycle(b, b, parent_map) is True

    # Cannot move parent into child or grandchild
    assert detect_folder_cycle(a, b, parent_map) is True
    assert detect_folder_cycle(a, c, parent_map) is True
    assert detect_folder_cycle(a, d, parent_map) is True
    assert detect_folder_cycle(b, d, parent_map) is True

    # Safe moves
    assert detect_folder_cycle(c, a, parent_map) is False
    assert detect_folder_cycle(d, a, parent_map) is False
    assert detect_folder_cycle(a, None, parent_map) is False
    assert detect_folder_cycle(c, None, parent_map) is False

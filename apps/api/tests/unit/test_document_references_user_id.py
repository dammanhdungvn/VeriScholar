from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from api.db.models.document import DocumentModel
from api.db.models.reference import ReferenceItemModel
from api.services.document_service import DocumentService


@pytest.mark.asyncio
async def test_extract_references_assigns_user_id():
    service = DocumentService(storage=MagicMock())
    test_user_id = uuid4()
    test_doc_id = uuid4()

    mock_doc = MagicMock(spec=DocumentModel)
    mock_doc.id = test_doc_id
    mock_doc.user_id = test_user_id
    mock_doc.content_hash = "mock_hash"

    mock_db = AsyncMock()
    mock_exec_res = MagicMock()
    mock_exec_res.scalar_one_or_none.return_value = mock_doc
    mock_exec_res.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_exec_res

    with (
        patch.object(service.storage, "blob_exists", AsyncMock(return_value=True)),
        patch.object(service.storage, "read_blob", AsyncMock(return_value=b"%PDF-1.4 mock")),
        patch(
            "asyncio.to_thread",
            AsyncMock(
                return_value=[
                    MagicMock(
                        ref_index=1,
                        raw_text="Sample Ref",
                        parsed=MagicMock(
                            title="Sample Title",
                            authors=["Author A"],
                            year=2024,
                            doi=None,
                            arxiv_id=None,
                        ),
                    )
                ]
            ),
        ),
    ):
        added_models = []
        mock_db.add = MagicMock(side_effect=lambda m: added_models.append(m))

        await service.extract_document_references(
            document_id=test_doc_id,
            user_id=test_user_id,
            db=mock_db,
            force_reextract=True,
        )

        assert len(added_models) == 1
        ref_model = added_models[0]
        assert isinstance(ref_model, ReferenceItemModel)
        assert ref_model.user_id == test_user_id
        assert ref_model.document_id == test_doc_id

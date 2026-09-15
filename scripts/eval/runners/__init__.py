"""Registry mapping API aliases to individual runner implementations."""

from scripts.eval.runners.base import BaseAPIRunner
from scripts.eval.runners.delete_documents import DeleteDocumentAPIRunner
from scripts.eval.runners.get_documents_detail import DocumentDetailAPIRunner
from scripts.eval.runners.get_documents_file_stream import StreamFileAPIRunner
from scripts.eval.runners.get_documents_list import ListDocumentsAPIRunner
from scripts.eval.runners.get_documents_status import DocumentStatusAPIRunner
from scripts.eval.runners.post_documents_extract_references import ExtractReferencesAPIRunner
from scripts.eval.runners.post_documents_parse import ParseDocumentAPIRunner
from scripts.eval.runners.post_documents_star import StarDocumentAPIRunner
from scripts.eval.runners.post_documents_upload import UploadAPIRunner

RUNNERS_MAP: dict[str, type[BaseAPIRunner]] = {
    # Friendly Short Aliases
    "upload": UploadAPIRunner,
    "list": ListDocumentsAPIRunner,
    "detail": DocumentDetailAPIRunner,
    "stream": StreamFileAPIRunner,
    "status": DocumentStatusAPIRunner,
    "star": StarDocumentAPIRunner,
    "parse": ParseDocumentAPIRunner,
    "extract-references": ExtractReferencesAPIRunner,
    "delete": DeleteDocumentAPIRunner,
    # Canonical Endpoint Identifiers (Matching File Names 1-to-1)
    "post_documents_upload": UploadAPIRunner,
    "get_documents_list": ListDocumentsAPIRunner,
    "get_documents_detail": DocumentDetailAPIRunner,
    "get_documents_file_stream": StreamFileAPIRunner,
    "get_documents_status": DocumentStatusAPIRunner,
    "post_documents_star": StarDocumentAPIRunner,
    "post_documents_parse": ParseDocumentAPIRunner,
    "post_documents_extract_references": ExtractReferencesAPIRunner,
    "delete_documents": DeleteDocumentAPIRunner,
}

MODULE_1_ORDER = [
    "post_documents_upload",
    "get_documents_list",
    "get_documents_detail",
    "get_documents_file_stream",
    "get_documents_status",
    "post_documents_star",
    "post_documents_parse",
    "post_documents_extract_references",
    "delete_documents",
]

__all__ = [
    "BaseAPIRunner",
    "UploadAPIRunner",
    "ListDocumentsAPIRunner",
    "DocumentDetailAPIRunner",
    "StreamFileAPIRunner",
    "DocumentStatusAPIRunner",
    "StarDocumentAPIRunner",
    "ParseDocumentAPIRunner",
    "ExtractReferencesAPIRunner",
    "DeleteDocumentAPIRunner",
    "RUNNERS_MAP",
    "MODULE_1_ORDER",
]

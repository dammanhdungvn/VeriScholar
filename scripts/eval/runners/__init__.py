"""Registry mapping API aliases to individual runner implementations."""

from scripts.eval.runners.base import BaseAPIRunner
from scripts.eval.runners.test_delete import DeleteDocumentAPIRunner
from scripts.eval.runners.test_detail import DocumentDetailAPIRunner
from scripts.eval.runners.test_extract_refs import ExtractReferencesAPIRunner
from scripts.eval.runners.test_list import ListDocumentsAPIRunner
from scripts.eval.runners.test_parse import ParseDocumentAPIRunner
from scripts.eval.runners.test_star import StarDocumentAPIRunner
from scripts.eval.runners.test_status import DocumentStatusAPIRunner
from scripts.eval.runners.test_stream import StreamFileAPIRunner
from scripts.eval.runners.test_upload import UploadAPIRunner

RUNNERS_MAP: dict[str, type[BaseAPIRunner]] = {
    "upload": UploadAPIRunner,
    "list": ListDocumentsAPIRunner,
    "detail": DocumentDetailAPIRunner,
    "stream": StreamFileAPIRunner,
    "status": DocumentStatusAPIRunner,
    "star": StarDocumentAPIRunner,
    "parse": ParseDocumentAPIRunner,
    "extract-references": ExtractReferencesAPIRunner,
    "delete": DeleteDocumentAPIRunner,
}

MODULE_1_ORDER = [
    "upload",
    "list",
    "detail",
    "stream",
    "status",
    "star",
    "parse",
    "extract-references",
    "delete",
]

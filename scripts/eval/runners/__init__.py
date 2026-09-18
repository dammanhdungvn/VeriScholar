"""Registry mapping API aliases to individual runner implementations."""

from scripts.eval.runners.base import BaseAPIRunner
from scripts.eval.runners.delete_documents import DeleteDocumentAPIRunner
from scripts.eval.runners.get_documents_chunk_detail import DocumentChunkDetailAPIRunner
from scripts.eval.runners.get_documents_chunks import DocumentChunksAPIRunner
from scripts.eval.runners.get_documents_detail import DocumentDetailAPIRunner
from scripts.eval.runners.get_documents_export_pdf import DocumentExportPdfAPIRunner
from scripts.eval.runners.get_documents_file_stream import StreamFileAPIRunner
from scripts.eval.runners.get_documents_list import ListDocumentsAPIRunner
from scripts.eval.runners.get_documents_status import DocumentStatusAPIRunner
from scripts.eval.runners.get_documents_structure import DocumentStructureAPIRunner
from scripts.eval.runners.get_documents_summary import DocumentSummaryAPIRunner
from scripts.eval.runners.get_sessions_list import ListSessionsAPIRunner
from scripts.eval.runners.notes_and_synthesis_runner import NotesAndSynthesisAPIRunner
from scripts.eval.runners.post_document_summary_stream import DocumentSummaryStreamAPIRunner
from scripts.eval.runners.post_documents_extract_references import ExtractReferencesAPIRunner
from scripts.eval.runners.post_documents_parse import ParseDocumentAPIRunner
from scripts.eval.runners.post_documents_star import StarDocumentAPIRunner
from scripts.eval.runners.post_documents_summary_generate import DocumentSummaryGenerateAPIRunner
from scripts.eval.runners.post_documents_upload import UploadAPIRunner
from scripts.eval.runners.post_sessions_chat import PostSessionsChatAPIRunner
from scripts.eval.runners.post_sessions_create import CreateSessionAPIRunner
from scripts.eval.runners.sessions_lifecycle_runner import SessionsLifecycleAPIRunner

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
    "extract-refs": ExtractReferencesAPIRunner,
    "structure": DocumentStructureAPIRunner,
    "chunks": DocumentChunksAPIRunner,
    "chunk_detail": DocumentChunkDetailAPIRunner,
    "chunk-detail": DocumentChunkDetailAPIRunner,
    "chunk": DocumentChunkDetailAPIRunner,
    "summary": DocumentSummaryAPIRunner,
    "document-summary": DocumentSummaryAPIRunner,
    "summary-generate": DocumentSummaryGenerateAPIRunner,
    "summary_generate": DocumentSummaryGenerateAPIRunner,
    "generate-summary": DocumentSummaryGenerateAPIRunner,
    "summary-stream": DocumentSummaryStreamAPIRunner,
    "summary_stream": DocumentSummaryStreamAPIRunner,
    "post_document_summary_stream": DocumentSummaryStreamAPIRunner,
    "post_documents_summary_stream": DocumentSummaryStreamAPIRunner,
    "document_summary_stream": DocumentSummaryStreamAPIRunner,
    "export-pdf": DocumentExportPdfAPIRunner,
    "export_pdf": DocumentExportPdfAPIRunner,
    "export": DocumentExportPdfAPIRunner,
    "delete": DeleteDocumentAPIRunner,
    "create-session": CreateSessionAPIRunner,
    "create_session": CreateSessionAPIRunner,
    "sessions-create": CreateSessionAPIRunner,
    "post_sessions": CreateSessionAPIRunner,
    "sessions": CreateSessionAPIRunner,
    "get-sessions": ListSessionsAPIRunner,
    "get_sessions": ListSessionsAPIRunner,
    "get_sessions_list": ListSessionsAPIRunner,
    "sessions_list": ListSessionsAPIRunner,
    "list_sessions": ListSessionsAPIRunner,
    "list-sessions": ListSessionsAPIRunner,
    "sessions-lifecycle": SessionsLifecycleAPIRunner,
    "sessions_lifecycle": SessionsLifecycleAPIRunner,
    "lifecycle": SessionsLifecycleAPIRunner,
    "sessions-chat": PostSessionsChatAPIRunner,
    "chat": PostSessionsChatAPIRunner,
    "post_sessions_chat": PostSessionsChatAPIRunner,
    "sessions_chat": PostSessionsChatAPIRunner,
    "notes": NotesAndSynthesisAPIRunner,
    "notes_and_synthesis": NotesAndSynthesisAPIRunner,
    "notes-and-synthesis": NotesAndSynthesisAPIRunner,
    "note": NotesAndSynthesisAPIRunner,
    "synthesize": NotesAndSynthesisAPIRunner,
    # Canonical Endpoint Identifiers (Matching File Names 1-to-1)
    "post_documents_upload": UploadAPIRunner,
    "get_documents_list": ListDocumentsAPIRunner,
    "get_documents_detail": DocumentDetailAPIRunner,
    "get_documents_file_stream": StreamFileAPIRunner,
    "get_documents_status": DocumentStatusAPIRunner,
    "post_documents_star": StarDocumentAPIRunner,
    "post_documents_parse": ParseDocumentAPIRunner,
    "post_documents_extract_references": ExtractReferencesAPIRunner,
    "get_documents_structure": DocumentStructureAPIRunner,
    "get_documents_chunks": DocumentChunksAPIRunner,
    "get_documents_chunk_detail": DocumentChunkDetailAPIRunner,
    "get_documents_summary": DocumentSummaryAPIRunner,
    "post_documents_summary_generate": DocumentSummaryGenerateAPIRunner,
    "get_documents_export_pdf": DocumentExportPdfAPIRunner,
    "delete_documents": DeleteDocumentAPIRunner,
    "post_sessions_create": CreateSessionAPIRunner,
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
    "get_documents_structure",
    "get_documents_chunks",
    "get_documents_chunk_detail",
    "get_documents_summary",
    "post_documents_summary_generate",
    "get_documents_export_pdf",
    "delete_documents",
    "post_sessions_create",
    "get_sessions_list",
    "sessions_lifecycle",
    "post_sessions_chat",
    "notes_and_synthesis",
]

__all__ = [
    "BaseAPIRunner",
    "CreateSessionAPIRunner",
    "DeleteDocumentAPIRunner",
    "DocumentChunkDetailAPIRunner",
    "DocumentChunksAPIRunner",
    "DocumentDetailAPIRunner",
    "DocumentExportPdfAPIRunner",
    "DocumentStatusAPIRunner",
    "DocumentStructureAPIRunner",
    "DocumentSummaryAPIRunner",
    "DocumentSummaryGenerateAPIRunner",
    "DocumentSummaryStreamAPIRunner",
    "ExtractReferencesAPIRunner",
    "ListDocumentsAPIRunner",
    "ListSessionsAPIRunner",
    "MODULE_1_ORDER",
    "NotesAndSynthesisAPIRunner",
    "ParseDocumentAPIRunner",
    "PostSessionsChatAPIRunner",
    "RUNNERS_MAP",
    "SessionsLifecycleAPIRunner",
    "StarDocumentAPIRunner",
    "StreamFileAPIRunner",
    "UploadAPIRunner",
]

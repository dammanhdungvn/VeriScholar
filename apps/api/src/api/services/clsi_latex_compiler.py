"""Overleaf CLSI LaTeX Compiler, incremental cache archive, and local SyncTeX runner."""

from __future__ import annotations

import asyncio
import os
import re
import shutil
import tarfile
import time
from typing import Any
from uuid import UUID

import structlog
from core.services.draft_skeleton import (
    ZipSlipSecurityError,
    sanitize_and_validate_asset_filename,
)
from core.services.latex_log_parser import LatexDiagnostic, LatexLogParser

logger = structlog.get_logger(__name__)


class CLSILatexCompiler:
    """Overleaf-style CLSI compiler using latexmk, caching, and local SyncTeX."""

    def __init__(
        self,
        work_dir: str = "/tmp/drafts",
        e2b_api_key: str | None = None,
        latexmk_binary: str | None = None,
    ) -> None:
        self.work_dir = os.path.abspath(work_dir)
        self.e2b_api_key = e2b_api_key
        self.latexmk_binary = latexmk_binary
        os.makedirs(self.work_dir, exist_ok=True)

    @staticmethod
    def detect_engine(main_tex: str) -> tuple[str, str]:
        """Detect whether pdflatex or xelatex is required.

        Returns (engine_name, engine_flag):
        - ("xelatex", "-xelatex") if fontspec, XeTeX, or Unicode characters are present.
        - ("pdflatex", "-pdf") otherwise.
        """
        if not main_tex:
            return ("pdflatex", "-pdf")

        # Check for fontspec package or xetex indications or non-ASCII unicode
        fontspec_pattern = re.compile(r"\\usepackage(?:\[.*?\])?\{fontspec\}")
        if (
            fontspec_pattern.search(main_tex)
            or "fontspec" in main_tex
            or "xelatex" in main_tex.lower()
            or any(ord(char) > 127 for char in main_tex)
        ):
            return ("xelatex", "-xelatex")

        return ("pdflatex", "-pdf")

    async def compile(
        self,
        draft_id: UUID,
        main_tex: str,
        bib_content: str = "",
        assets: list[dict[str, Any]] | None = None,
        clear_cache: bool = False,
        timeout_seconds: float = 15.0,
    ) -> dict[str, Any]:
        """Compile a LaTeX draft into PDF using latexmk with incremental caching."""
        start_time = time.perf_counter()
        draft_dir = os.path.join(self.work_dir, str(draft_id))
        cache_dir = os.path.join(draft_dir, "cache")
        output_dir = os.path.join(draft_dir, "output")
        figures_dir = os.path.join(draft_dir, "figures")
        cache_archive = os.path.join(draft_dir, "cache.tar.gz")

        os.makedirs(draft_dir, exist_ok=True)

        # Cache management
        if clear_cache:
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir, ignore_errors=True)
            if os.path.exists(cache_archive):
                try:
                    os.remove(cache_archive)
                except OSError:
                    pass
            os.makedirs(cache_dir, exist_ok=True)
            is_cached = False
        else:
            if (
                (not os.path.exists(cache_dir) or not os.listdir(cache_dir))
                and os.path.exists(cache_archive)
                and tarfile.is_tarfile(cache_archive)
            ):
                try:
                    with tarfile.open(cache_archive, "r:gz") as tar:
                        tar.extractall(path=cache_dir, filter="data")
                except Exception as exc:
                    logger.warning("Failed to extract cache archive", error=str(exc))

            is_cached = bool(os.path.exists(cache_dir) and os.listdir(cache_dir))
            os.makedirs(cache_dir, exist_ok=True)

        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(figures_dir, exist_ok=True)

        # Remove stale output artifacts from prior runs to prevent serving stale files on failure
        stale_files = [
            os.path.join(output_dir, "output.pdf"),
            os.path.join(output_dir, "output.synctex.gz"),
            os.path.join(output_dir, "output.synctex"),
        ]
        for fpath in stale_files:
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except OSError:
                    pass

        # Write main.tex
        main_tex_path = os.path.join(draft_dir, "main.tex")
        with open(main_tex_path, "w", encoding="utf-8") as f:
            f.write(main_tex)

        # Write references.bib
        bib_path = os.path.join(draft_dir, "references.bib")
        with open(bib_path, "w", encoding="utf-8") as f:
            f.write(bib_content or "")

        # Write assets into figures/ with path traversal & size guard
        if assets:
            real_figures_dir = os.path.realpath(figures_dir)
            figures_prefix = real_figures_dir + os.sep
            for item in assets:
                raw_filename = item.get("filename") or item.get("file_name")
                if not raw_filename or not isinstance(raw_filename, str):
                    continue

                content = item.get("content")
                storage_path = item.get("storage_path")
                byte_size = 1
                if content is not None:
                    byte_size = (
                        len(content.encode("utf-8")) if isinstance(content, str) else len(content)
                    )
                elif storage_path and os.path.isfile(storage_path):
                    try:
                        byte_size = os.path.getsize(storage_path)
                    except OSError:
                        byte_size = 1

                try:
                    safe_name = sanitize_and_validate_asset_filename(
                        raw_filename, byte_size=max(byte_size, 1)
                    )
                except (ZipSlipSecurityError, ValueError) as exc:
                    logger.warning(
                        "Skipping invalid or unsafe asset filename",
                        filename=raw_filename,
                        error=str(exc),
                    )
                    continue

                target_path = os.path.join(figures_dir, safe_name)
                real_target = os.path.realpath(target_path)
                if not real_target.startswith(figures_prefix):
                    logger.warning(
                        "Skipping asset escaping figures directory",
                        target=target_path,
                    )
                    continue

                if os.path.isdir(real_target):
                    logger.warning(
                        "Skipping asset target because it is an existing directory",
                        target=target_path,
                    )
                    continue

                try:
                    if content is not None:
                        if isinstance(content, str):
                            with open(target_path, "w", encoding="utf-8") as f:
                                f.write(content)
                        elif isinstance(content, (bytes, bytearray)):
                            with open(target_path, "wb") as f:
                                f.write(content)
                    elif storage_path and os.path.isfile(storage_path):
                        shutil.copyfile(storage_path, target_path)
                except (OSError, IOError) as exc:
                    logger.warning(
                        "Failed to write asset file",
                        target=target_path,
                        error=str(exc),
                    )
                    continue

        engine_name, engine_flag = self.detect_engine(main_tex)
        latexmk_bin = self.latexmk_binary or shutil.which("latexmk") or "/usr/bin/latexmk"

        cmd = [
            latexmk_bin,
            "-cd",
            "-f",
            "-jobname=output",
            f"-auxdir={cache_dir}",
            f"-outdir={output_dir}",
            "-synctex=1",
            "-interaction=batchmode",
            engine_flag,
            "main.tex",
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=draft_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                start_new_session=True,
            )
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout_seconds,
            )
            stdout = stdout_bytes.decode("utf-8", errors="replace")
            stderr = stderr_bytes.decode("utf-8", errors="replace")
        except FileNotFoundError as e:
            not_found_msg = f"LaTeX compiler executable not found: {e.filename or latexmk_bin}"
            diagnostic: LatexDiagnostic = {
                "file": "main.tex",
                "line": 1,
                "column": 1,
                "severity": "error",
                "message": not_found_msg,
                "context": "",
                "hint": "Ensure TeXLive and latexmk are installed on the host environment.",
            }
            return {
                "draft_id": draft_id,
                "success": False,
                "pdf_path": None,
                "synctex_path": None,
                "log_path": None,
                "logs": not_found_msg,
                "diagnostics": [diagnostic],
                "errors": [diagnostic],
                "is_cached": is_cached,
                "engine": engine_name,
                "duration_seconds": round(time.time() - start_time, 3),
            }
        except asyncio.TimeoutError:
            try:
                if proc.pid:
                    os.killpg(os.getpgid(proc.pid), 9)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            try:
                await proc.wait()
            except Exception:
                pass
            timeout_msg = f"LaTeX compilation timed out after {timeout_seconds} seconds"
            diagnostic: LatexDiagnostic = {
                "file": "main.tex",
                "line": 1,
                "column": 1,
                "severity": "error",
                "message": timeout_msg,
                "context": "",
                "hint": "Optimize images or simplify complex macros to reduce compile time.",
            }
            return {
                "draft_id": draft_id,
                "success": False,
                "pdf_path": None,
                "synctex_path": None,
                "log_path": None,
                "logs": timeout_msg,
                "diagnostics": [diagnostic],
                "errors": [diagnostic],
                "is_cached": is_cached,
                "engine": engine_name,
                "duration_seconds": timeout_seconds,
            }

        # Locate output.log
        log_path: str | None = None
        log_candidates = [
            os.path.join(cache_dir, "output.log"),
            os.path.join(output_dir, "output.log"),
            os.path.join(draft_dir, "output.log"),
        ]
        for cand in log_candidates:
            if os.path.exists(cand):
                log_path = cand
                break

        log_text = ""
        if log_path and os.path.exists(log_path):
            with open(log_path, encoding="utf-8", errors="replace") as f:
                log_text = f.read()
        else:
            log_text = f"{stdout}\n{stderr}".strip()

        # Parse diagnostics using LatexLogParser
        diagnostics = LatexLogParser.parse_log(log_text)

        pdf_path = os.path.join(output_dir, "output.pdf")
        has_pdf = os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0
        has_error = any(d.get("severity") == "error" for d in diagnostics)

        success = (proc.returncode == 0) and (not has_error) and has_pdf

        # Locate synctex file only if compilation succeeded
        synctex_path: str | None = None
        if success:
            synctex_candidates = [
                os.path.join(output_dir, "output.synctex.gz"),
                os.path.join(output_dir, "output.synctex"),
                os.path.join(cache_dir, "output.synctex.gz"),
                os.path.join(cache_dir, "output.synctex"),
            ]
            for cand in synctex_candidates:
                if os.path.exists(cand):
                    synctex_path = cand
                    break

        # Archive cache on success for durability
        if success and os.path.exists(cache_dir):
            try:
                with tarfile.open(cache_archive, "w:gz") as tar:
                    for item in os.listdir(cache_dir):
                        item_path = os.path.join(cache_dir, item)
                        tar.add(item_path, arcname=item)
            except Exception as exc:
                logger.warning("Failed to archive latex cache", error=str(exc))

        duration = time.perf_counter() - start_time

        return {
            "draft_id": draft_id,
            "success": success,
            "pdf_path": pdf_path if (success and has_pdf) else None,
            "synctex_path": synctex_path if success else None,
            "log_path": log_path,
            "logs": log_text,
            "diagnostics": diagnostics,
            "errors": diagnostics,
            "is_cached": is_cached,
            "engine": engine_name,
            "duration_seconds": duration,
        }

    async def synctex_forward(
        self,
        draft_id: UUID,
        file: str,
        line: int,
        column: int = 1,
    ) -> dict[str, Any]:
        """Perform SyncTeX forward search (source code line/col -> PDF coordinates)."""
        output_dir = os.path.join(self.work_dir, str(draft_id), "output")
        pdf_path = os.path.join(output_dir, "output.pdf")
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF output not found for draft {draft_id}: {pdf_path}")

        draft_dir = os.path.join(self.work_dir, str(draft_id))
        synctex_bin = shutil.which("synctex") or "/usr/bin/synctex"

        cmd = [
            synctex_bin,
            "view",
            "-i",
            f"{line}:{column}:{file}",
            "-o",
            pdf_path,
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=draft_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                start_new_session=True,
            )
            stdout_bytes, _ = await asyncio.wait_for(proc.communicate(), timeout=3.0)
            stdout = stdout_bytes.decode("utf-8", errors="replace")
        except FileNotFoundError:
            return {
                "page": 1,
                "h": 0.0,
                "v": 0.0,
                "width": 0.0,
                "height": 0.0,
            }
        except asyncio.TimeoutError:
            try:
                if proc.pid:
                    os.killpg(os.getpgid(proc.pid), 9)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            try:
                await proc.wait()
            except Exception:
                pass
            stdout = ""

        page = 1
        h = 0.0
        v = 0.0
        width = 0.0
        height = 0.0
        found = False

        for raw_line in stdout.splitlines():
            s = raw_line.strip()
            if s.startswith("Page:") and not found:
                try:
                    page = int(s.split(":", 1)[1])
                except ValueError:
                    pass
            elif s.startswith("h:") and not found:
                try:
                    h = float(s.split(":", 1)[1])
                except ValueError:
                    pass
            elif s.startswith("v:") and not found:
                try:
                    v = float(s.split(":", 1)[1])
                except ValueError:
                    pass
            elif s.startswith("W:") and not found:
                try:
                    width = float(s.split(":", 1)[1])
                except ValueError:
                    pass
            elif s.startswith("H:") and not found:
                try:
                    height = float(s.split(":", 1)[1])
                    found = True
                except ValueError:
                    pass

        return {
            "page": page,
            "h": h,
            "v": v,
            "width": width,
            "height": height,
        }

    async def synctex_inverse(
        self,
        draft_id: UUID,
        page: int,
        x: float,
        y: float,
    ) -> dict[str, Any]:
        """Perform SyncTeX inverse search (PDF coordinates -> source code line/col)."""
        output_dir = os.path.join(self.work_dir, str(draft_id), "output")
        pdf_path = os.path.join(output_dir, "output.pdf")
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF output not found for draft {draft_id}: {pdf_path}")

        draft_dir = os.path.join(self.work_dir, str(draft_id))
        synctex_bin = shutil.which("synctex") or "/usr/bin/synctex"

        cmd = [
            synctex_bin,
            "edit",
            "-o",
            f"{page}:{x}:{y}:{pdf_path}",
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=draft_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                start_new_session=True,
            )
            stdout_bytes, _ = await asyncio.wait_for(proc.communicate(), timeout=3.0)
            stdout = stdout_bytes.decode("utf-8", errors="replace")
        except FileNotFoundError:
            return {
                "file": "main.tex",
                "line": 1,
                "column": 1,
            }
        except asyncio.TimeoutError:
            try:
                if proc.pid:
                    os.killpg(os.getpgid(proc.pid), 9)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            try:
                await proc.wait()
            except Exception:
                pass
            stdout = ""

        res_file = "main.tex"
        line_num = 1
        col_num = 1
        found = False

        for raw_line in stdout.splitlines():
            s = raw_line.strip()
            if s.startswith("Input:") and not found:
                raw_input = s.split(":", 1)[1].strip()
                res_file = os.path.basename(raw_input)
            elif s.startswith("Line:") and not found:
                try:
                    line_num = int(s.split(":", 1)[1])
                except ValueError:
                    pass
            elif s.startswith("Column:") and not found:
                try:
                    col_val = int(s.split(":", 1)[1])
                    col_num = max(1, col_val)
                    found = True
                except ValueError:
                    pass

        return {
            "file": res_file,
            "line": line_num,
            "column": col_num,
        }

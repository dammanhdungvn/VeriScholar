"""Configuration, path definitions, and Quality Budget thresholds."""

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Find project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env
API_ENV = PROJECT_ROOT / "apps" / "api" / ".env"
ROOT_ENV = PROJECT_ROOT / ".env"
if API_ENV.exists():
    load_dotenv(API_ENV)
elif ROOT_ENV.exists():
    load_dotenv(ROOT_ENV)

# Paths
DATA_PAPERS_DIR = PROJECT_ROOT / "data" / "papers"
PAPERS_DIR = DATA_PAPERS_DIR
FIXTURES_DIR = DATA_PAPERS_DIR / "fixtures"
TEMP_OUTPUT_TEST_DIR = PROJECT_ROOT / "temp" / "output" / "test"
REPORTS_DIR = TEMP_OUTPUT_TEST_DIR
LEGACY_REPORTS_DIR = PROJECT_ROOT / "docs" / "eval-reports"
ARTIFACTS_DIR = PROJECT_ROOT / "tests" / ".artifacts"

# Ensure directories exist
TEMP_OUTPUT_TEST_DIR.mkdir(parents=True, exist_ok=True)
LEGACY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def get_available_papers() -> list[Path]:
    """Returns all non-corrupted PDF files currently present in DATA_PAPERS_DIR."""
    return sorted([p for p in DATA_PAPERS_DIR.glob("*.pdf") if not p.name.startswith("corrupted")])


def get_default_paper() -> Path | None:
    """Returns the primary available PDF paper for prerequisite uploads."""
    papers = get_available_papers()
    return papers[0] if papers else None


@dataclass(frozen=True)
class QualityBudget:
    """Quality budget thresholds for CI/CD gates and evaluation passes."""

    min_recall: float = 0.90
    min_precision: float = 0.95
    min_spatial_iou: float = 0.70
    max_latency_ms: float = 10000.0
    allow_critical_warnings: bool = False

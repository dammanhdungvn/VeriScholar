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
FIXTURES_DIR = DATA_PAPERS_DIR / "fixtures"
REPORTS_DIR = PROJECT_ROOT / "docs" / "eval-reports"
ARTIFACTS_DIR = PROJECT_ROOT / "tests" / ".artifacts"

# Ensure directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class QualityBudget:
    """Quality budget thresholds for CI/CD gates and evaluation passes."""

    min_recall: float = 0.90
    min_precision: float = 0.95
    min_spatial_iou: float = 0.70
    max_latency_ms: float = 10000.0
    allow_critical_warnings: bool = False

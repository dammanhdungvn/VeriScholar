"""Academic and Reputable Email Validator Adapter for VeriScholar Auth 2.0.

Re-exports pure domain validation logic from packages/core/src/core/services/email_validator.py.
Preserves internal compatibility across apps/api consumers.
"""

from core.services.email_validator import (
    AC_DOMAIN_PATTERN,
    ACADEMIC_TLD_SUFFIXES,
    DISPOSABLE_DOMAINS,
    DISPOSABLE_KEYWORDS,
    INSTITUTIONAL_TLD_SUFFIXES,
    KNOWN_ACADEMIC_DOMAINS,
    REPUTABLE_DOMAINS,
    EmailCategory,
    classify_email,
    ensure_valid_registration_email,
    extract_domain,
    get_academic_priority_score,
    is_academic_domain,
    is_disposable_domain,
    is_institutional_domain,
    is_reputable_domain,
    is_valid_email_syntax,
    mask_api_key,
    normalize_email,
    validate_academic_or_trusted_email,
    validate_orcid_id,
    validate_user_full_name,
)

__all__ = [
    "AC_DOMAIN_PATTERN",
    "ACADEMIC_TLD_SUFFIXES",
    "DISPOSABLE_DOMAINS",
    "DISPOSABLE_KEYWORDS",
    "INSTITUTIONAL_TLD_SUFFIXES",
    "KNOWN_ACADEMIC_DOMAINS",
    "REPUTABLE_DOMAINS",
    "EmailCategory",
    "classify_email",
    "ensure_valid_registration_email",
    "extract_domain",
    "get_academic_priority_score",
    "is_academic_domain",
    "is_disposable_domain",
    "is_institutional_domain",
    "is_reputable_domain",
    "is_valid_email_syntax",
    "mask_api_key",
    "normalize_email",
    "validate_academic_or_trusted_email",
    "validate_orcid_id",
    "validate_user_full_name",
]

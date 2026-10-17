"""Re-export email_validator utilities from api.core.email_validator."""

from api.core.email_validator import (
    ACADEMIC_TLD_SUFFIXES,
    DISPOSABLE_DOMAINS,
    DISPOSABLE_KEYWORDS,
    KNOWN_ACADEMIC_DOMAINS,
    REPUTABLE_DOMAINS,
    EmailCategory,
    classify_email,
    ensure_valid_registration_email,
    extract_domain,
    get_academic_priority_score,
    is_academic_domain,
    is_disposable_domain,
    is_reputable_domain,
    is_valid_email_syntax,
    normalize_email,
    validate_academic_or_trusted_email,
    validate_user_full_name,
)

# Aliases for backward compatibility
DISPOSABLE_EMAIL_DOMAINS = DISPOSABLE_DOMAINS
TRUSTED_MAJOR_PROVIDERS = REPUTABLE_DOMAINS
TRUSTED_ACADEMIC_SUFFIXES = ACADEMIC_TLD_SUFFIXES

__all__ = [
    "ACADEMIC_TLD_SUFFIXES",
    "DISPOSABLE_DOMAINS",
    "DISPOSABLE_EMAIL_DOMAINS",
    "DISPOSABLE_KEYWORDS",
    "KNOWN_ACADEMIC_DOMAINS",
    "REPUTABLE_DOMAINS",
    "TRUSTED_ACADEMIC_SUFFIXES",
    "TRUSTED_MAJOR_PROVIDERS",
    "EmailCategory",
    "classify_email",
    "ensure_valid_registration_email",
    "extract_domain",
    "get_academic_priority_score",
    "is_academic_domain",
    "is_disposable_domain",
    "is_reputable_domain",
    "is_valid_email_syntax",
    "normalize_email",
    "validate_academic_or_trusted_email",
    "validate_user_full_name",
]

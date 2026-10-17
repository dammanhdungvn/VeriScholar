"""Academic and Reputable Email Validator for VeriScholar Auth 2.0.

Provides robust validation, domain classification, and strict whitelist rejection
of disposable/temporary/burner email services and non-academic/non-whitelisted domains.
Pure domain service with zero framework dependencies (Hexagonal Architecture compliant).
"""

import re
from enum import Enum
from typing import Final

# RFC 5322 compliant regex for academic & professional emails
EMAIL_REGEX_PATTERN: Final[str] = (
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}"
    r"[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
)
EMAIL_COMPILED_REGEX: Final[re.Pattern[str]] = re.compile(EMAIL_REGEX_PATTERN)

# Regex pattern for academic .ac.* domains (e.g. ox.ac.uk, u-tokyo.ac.jp, univ.ac.vn)
AC_DOMAIN_PATTERN: Final[re.Pattern[str]] = re.compile(r"(?:^|\.)ac\.[a-z]{2,6}$")


class EmailCategory(str, Enum):
    """Categorization of email domains for tiered trust and verification."""

    ACADEMIC = "academic"
    REPUTABLE = "reputable"
    INSTITUTIONAL = "institutional"
    STANDARD = "standard"
    DISPOSABLE = "disposable"
    INVALID = "invalid"


# ------------------------------------------------------------------------------
# 1. Known Disposable / Temporary / Burner Email Domains (Strictly Blocked)
# ------------------------------------------------------------------------------
DISPOSABLE_DOMAINS: Final[frozenset[str]] = frozenset(
    {
        # Common temporary mail providers & burner domains
        "maxxspace.com",
        "10minutemail.com",
        "10minutemail.net",
        "10minutemail.org",
        "20minutemail.com",
        "airmail.news",
        "anonaddy.com",
        "anonaddy.me",
        "anonymouse.org",
        "armyspy.com",
        "binkmail.com",
        "bobmail.info",
        "burnermail.io",
        "chacuo.net",
        "crazymailing.com",
        "crazymail.com",
        "cuvox.de",
        "dayrep.com",
        "deadaddress.com",
        "discard.email",
        "discardmail.com",
        "dispostable.com",
        "disposable.email",
        "disposablemail.com",
        "dropmail.me",
        "einrot.com",
        "emailfake.com",
        "emailondeck.com",
        "emailsensei.com",
        "emkei.cz",
        "fakeinbox.com",
        "fakemail.net",
        "fakemailgenerator.com",
        "fakespot.com",
        "fleckens.hu",
        "generator.email",
        "getairmail.com",
        "getnada.com",
        "grr.la",
        "guerrillamail.biz",
        "guerrillamail.com",
        "guerrillamail.de",
        "guerrillamail.net",
        "guerrillamail.org",
        "guerrillamailblock.com",
        "gustr.com",
        "harakirimail.com",
        "inboxalias.com",
        "inboxbear.com",
        "inboxkitten.com",
        "inboxproxy.com",
        "incognitomail.org",
        "jetable.org",
        "jourrapide.com",
        "kasmail.com",
        "maildrop.cc",
        "mailcatch.com",
        "mailinator.com",
        "mailinator.net",
        "mailinator.org",
        "mailinator2.com",
        "mailnesia.com",
        "mailnull.com",
        "meltmail.com",
        "mohmal.com",
        "mohmal.in",
        "mytemp.email",
        "mytempemail.com",
        "nada.ltd",
        "nada.email",
        "nowmymail.com",
        "objectmail.com",
        "oneoffmail.com",
        "ownmail.net",
        "pokemail.net",
        "proxymail.eu",
        "rcpt.at",
        "rhyta.com",
        "safetymail.info",
        "sharklasers.com",
        "spam4.me",
        "spambog.com",
        "spambox.us",
        "spamgourmet.com",
        "spamspot.com",
        "superrito.com",
        "teleworm.us",
        "temp-mail.org",
        "temp-mail.ru",
        "tempail.com",
        "tempinbox.com",
        "tempmail.com",
        "tempmail.net",
        "tempmail.ninja",
        "tempmailo.com",
        "throwaway.email",
        "throwawaymail.com",
        "tmail.com",
        "trashinbox.com",
        "trashmail.com",
        "trashmail.de",
        "trashmail.net",
        "trashmail.org",
        "trbvm.com",
        "yopmail.com",
        "yopmail.fr",
        "yopmail.net",
        "zippymail.info",
    }
)

DISPOSABLE_KEYWORDS: Final[tuple[str, ...]] = (
    "disposable",
    "throwaway",
    "tempmail",
    "trashmail",
    "fakemail",
    "10minutemail",
    "yopmail",
    "burnermail",
    "mailinator",
    "guerrillamail",
    "maxxspace",
)

# ------------------------------------------------------------------------------
# 2. Academic Suffixes & Top-Tier Research Domains (Priority Status)
# ------------------------------------------------------------------------------
ACADEMIC_TLD_SUFFIXES: Final[tuple[str, ...]] = (
    ".edu",
    ".edu.vn",
    ".ac.vn",
    ".ac.uk",
    ".ac.jp",
    ".edu.au",
    ".edu.sg",
    ".ac.in",
    ".edu.cn",
    ".ac.nz",
    ".ac.kr",
    ".edu.tw",
    ".edu.hk",
    ".edu.my",
    ".edu.ph",
    ".edu.pk",
    ".edu.eg",
    ".edu.tr",
    ".ac.za",
    ".edu.br",
    ".edu.mx",
    ".edu.co",
    ".edu.ar",
    ".ac.at",
    ".ac.be",
    ".ac.il",
    ".res.in",
    ".edu.in",
    ".edu.th",
    ".edu.ca",
    ".univ-",
)

KNOWN_ACADEMIC_DOMAINS: Final[frozenset[str]] = frozenset(
    {
        # Global top universities
        "stanford.edu",
        "mit.edu",
        "harvard.edu",
        "berkeley.edu",
        "ox.ac.uk",
        "cam.ac.uk",
        "caltech.edu",
        "cmu.edu",
        "princeton.edu",
        "columbia.edu",
        "yale.edu",
        "cornell.edu",
        "ucla.edu",
        "ethz.ch",
        "epfl.ch",
        "helsinki.fi",
        "sorbonne.fr",
        "sorbonne-universite.fr",
        "utoronto.ca",
        "mcgill.ca",
        "u-tokyo.ac.jp",
        "tsinghua.edu.cn",
        "pku.edu.cn",
        "nus.edu.sg",
        "ntu.edu.sg",
        "kaist.ac.kr",
        "snu.ac.kr",
        # Vietnam universities
        "vnu.edu.vn",
        "hust.edu.vn",
        "hcmut.edu.vn",
        "neu.edu.vn",
        "ftu.edu.vn",
        "uet.vnu.edu.vn",
        "ussh.vnu.edu.vn",
        "uit.edu.vn",
        "vnua.edu.vn",
        "dut.udn.vn",
        "hcmiu.edu.vn",
        "rmit.edu.vn",
        "vinuni.edu.vn",
        "fpt.edu.vn",
        "tonducthang.edu.vn",
    }
)

# ------------------------------------------------------------------------------
# 3. Reputable Consumer & Enterprise Mail Providers (STRICT WHITELIST)
# ------------------------------------------------------------------------------
REPUTABLE_DOMAINS: Final[frozenset[str]] = frozenset(
    {
        "gmail.com",
        "googlemail.com",
        "outlook.com",
        "hotmail.com",
        "live.com",
        "msn.com",
        "yahoo.com",
        "yahoo.com.vn",
        "ymail.com",
        "icloud.com",
        "me.com",
        "mac.com",
        "proton.me",
        "protonmail.com",
        "zoho.com",
        "aol.com",
        "fastmail.com",
        "verischolar.org",
        "verischolar.ai",
    }
)

INSTITUTIONAL_TLD_SUFFIXES: Final[tuple[str, ...]] = (
    ".gov",
    ".gov.vn",
    ".gov.uk",
    ".gov.au",
    ".org",
    ".org.vn",
    ".org.uk",
    ".mil",
    ".int",
)


def normalize_email(email: str) -> str:
    """Normalize email address by stripping whitespace and lowercasing."""
    if not email:
        return ""
    return email.strip().lower()


def extract_domain(email: str) -> str:
    """Extract domain portion of an email address."""
    normalized = normalize_email(email)
    if "@" not in normalized:
        return ""
    parts = normalized.split("@", 1)
    return parts[1].strip()


def is_valid_email_syntax(email: str) -> bool:
    """Check standard RFC syntax conformance."""
    normalized = normalize_email(email)
    if not normalized or len(normalized) > 254:
        return False
    if not EMAIL_COMPILED_REGEX.match(normalized):
        return False
    parts = normalized.split("@")
    if len(parts) != 2:
        return False
    local_part, domain = parts
    if len(local_part) > 64 or len(domain) > 253:
        return False
    if ".." in normalized or domain.startswith("-") or domain.endswith("-"):
        return False
    return True


def is_disposable_domain(domain: str) -> bool:
    """Detect whether a domain is a known burner / disposable email provider."""
    d = domain.lower().strip()
    if not d:
        return False

    # 1. Exact match
    if d in DISPOSABLE_DOMAINS:
        return True

    # 2. Subdomain check (e.g. sub.mailinator.com)
    for disp in DISPOSABLE_DOMAINS:
        if d.endswith(f".{disp}"):
            return True

    # 3. Keyword heuristic check
    for keyword in DISPOSABLE_KEYWORDS:
        if keyword in d:
            return True

    return False


def is_academic_domain(domain: str) -> bool:
    """Check if domain belongs to an accredited university or academic institution.

    Accepts:
        - Exact matches or subdomains of KNOWN_ACADEMIC_DOMAINS
        - TLDs ending in .edu, .edu.vn, .edu.*
        - Suffixes matching .ac.* (e.g. .ac.uk, .ac.jp, .ac.vn, .ac.kr)
        - Specific academic TLD suffixes (e.g. .res.in)
    """
    d = domain.lower().strip()
    if not d:
        return False

    # 1. Known exact domains
    if d in KNOWN_ACADEMIC_DOMAINS:
        return True

    # 2. Known subdomains (e.g. cs.stanford.edu, uet.vnu.edu.vn)
    for known in KNOWN_ACADEMIC_DOMAINS:
        if d.endswith(f".{known}"):
            return True

    # 3. Academic TLD suffixes (.edu, .edu.vn, .edu.au, etc.)
    if d.endswith(".edu") or d.endswith(".edu.vn"):
        return True

    for suffix in ACADEMIC_TLD_SUFFIXES:
        if d.endswith(suffix):
            return True

    # 4. Pattern check for .ac.* (e.g. .ac.uk, .ac.jp, .ac.za, .ac.in)
    if AC_DOMAIN_PATTERN.search(d):
        return True

    return False


def is_institutional_domain(domain: str) -> bool:
    """Check if domain is a recognized government, non-profit, or international agency."""
    d = domain.lower().strip()
    if not d:
        return False

    for suffix in INSTITUTIONAL_TLD_SUFFIXES:
        if d.endswith(suffix):
            return True

    return False


def is_reputable_domain(domain: str) -> bool:
    """Check if domain is an approved reputable public or enterprise email service."""
    d = domain.lower().strip()
    if not d:
        return False

    if d in REPUTABLE_DOMAINS:
        return True

    for rep in REPUTABLE_DOMAINS:
        if d.endswith(f".{rep}"):
            return True

    # Check institutional TLDs (.org, .gov, .mil, .int)
    if is_institutional_domain(d):
        return True

    return False


def classify_email(email: str) -> EmailCategory:
    """Classify email into tiered categories: Academic, Reputable, Institutional, Disposable."""
    if not is_valid_email_syntax(email):
        return EmailCategory.INVALID

    domain = extract_domain(email)
    if not domain:
        return EmailCategory.INVALID

    if is_disposable_domain(domain):
        return EmailCategory.DISPOSABLE

    if is_academic_domain(domain):
        return EmailCategory.ACADEMIC

    if is_institutional_domain(domain):
        return EmailCategory.INSTITUTIONAL

    if domain in REPUTABLE_DOMAINS or any(domain.endswith(f".{r}") for r in REPUTABLE_DOMAINS):
        return EmailCategory.REPUTABLE

    return EmailCategory.STANDARD


def get_academic_priority_score(email: str) -> int:
    """Calculate trust & priority score (0-100) based on domain reputation."""
    category = classify_email(email)
    if category == EmailCategory.ACADEMIC:
        return 100
    if category == EmailCategory.INSTITUTIONAL:
        return 80
    if category == EmailCategory.REPUTABLE:
        return 60
    if category == EmailCategory.STANDARD:
        return 40
    return 0


def validate_academic_or_trusted_email(email: str) -> tuple[bool, str | None]:
    """Verify that email address belongs to a trusted academic or reputable source.

    STRICT WHITELIST RULES:
    Only accepts:
    1. Academic domains (.edu, .edu.vn, .ac.*, etc.)
    2. Reputable major providers (gmail.com, outlook.com, hotmail.com, icloud.com, proton.me, etc.)
    3. Institutional organizations (.gov, .org, .mil, .int)

    Arbitrary commercial / unverified domains (including maxxspace.com) are strictly rejected.

    Returns:
        (is_valid, error_message_if_invalid)
    """
    clean_email = normalize_email(email)
    if not is_valid_email_syntax(clean_email):
        return (
            False,
            "Địa chỉ email không đúng định dạng chuẩn RFC (ví dụ: scholar@university.edu).",
        )

    domain = extract_domain(clean_email)
    if is_disposable_domain(domain):
        return (
            False,
            f"Tên miền '{domain}' là dịch vụ email tạm thời. Hệ thống VeriScholar "
            "yêu cầu sử dụng email học thuật hoặc nhà cung cấp uy tín.",
        )

    # 1. Permit academic institutional domains (.edu, .edu.vn, .ac.*)
    if is_academic_domain(domain):
        return True, None

    # 2. Permit reputable major providers (Gmail, Outlook, Proton, iCloud, etc.)
    if is_reputable_domain(domain):
        return True, None

    # 3. Permit institutional domains (.gov, .org, .mil, .int)
    if is_institutional_domain(domain):
        return True, None

    # STRICT REJECTION: Fallback is removed. Non-whitelisted domains are rejected.
    return (
        False,
        f"Tên miền '{domain}' không thuộc danh sách email học thuật (.edu, .ac.*), "
        "nhà cung cấp uy tín (Gmail, Outlook, Proton...) hoặc tổ chức nghiên cứu được phê duyệt.",
    )


def validate_user_full_name(full_name: str) -> tuple[bool, str | None]:
    """Validate full name: between 2 and 100 chars, no HTML/script injection."""
    clean_name = " ".join(full_name.strip().split())
    if len(clean_name) < 2:
        return False, "Họ và tên cần có tối thiểu 2 ký tự."
    if len(clean_name) > 100:
        return False, "Họ và tên không được vượt quá 100 ký tự."

    # Prevent HTML / script injection
    if any(char in clean_name for char in '<>{};$"\\'):
        return False, "Họ và tên chứa ký tự đặc biệt không hợp lệ."

    return True, None


def ensure_valid_registration_email(email: str) -> str:
    """Validate and sanitize email address for scholar registration.

    Raises:
        ValueError: If email is malformed, has invalid syntax, or uses a
            disposable/untrusted domain.

    Returns:
        str: Normalized, lowercase email address.
    """
    clean_email = normalize_email(email)
    is_valid, err_msg = validate_academic_or_trusted_email(clean_email)
    if not is_valid:
        raise ValueError(
            err_msg
            or "Email tạm thời (disposable email) hoặc không thuộc nguồn học thuật/uy tín "
            "không được chấp nhận. Vui lòng sử dụng email học thuật (.edu, .ac) hoặc email uy tín."
        )
    return clean_email

/**
 * Email & Identity Validation Utilities for Academic Security (Tier 1 Client-Side Validation).
 * Synchronized with Backend Security Standards (apps/api/src/api/utils/email_validator.py).
 */

// Comprehensive set of disposable, throwaway, and temporary email providers
export const DISPOSABLE_EMAIL_DOMAINS: ReadonlySet<string> = new Set([
  "mailinator.com",
  "10minutemail.com",
  "tempmail.com",
  "temp-mail.org",
  "guerrillamail.com",
  "guerrillamail.net",
  "guerrillamail.org",
  "trashmail.com",
  "trashmail.net",
  "yopmail.com",
  "yopmail.fr",
  "yopmail.net",
  "dispostable.com",
  "sharklasers.com",
  "getairmail.com",
  "throwawaymail.com",
  "maildrop.cc",
  "fakeinbox.com",
  "inboxkitten.com",
  "mohmal.com",
  "crazymailing.com",
  "tmail.com",
  "burnermail.io",
  "emailondeck.com",
  "tempmailo.com",
  "generator.email",
  "mytemp.email",
  "mailnesia.com",
  "nada.ltd",
  "getnada.com",
  "tempail.com",
  "trashinbox.com",
  "fakemailgenerator.com",
  "armyspy.com",
  "cuvox.de",
  "dayrep.com",
  "fleckens.hu",
  "gustr.com",
  "jourrapide.com",
  "rhyta.com",
  "superrito.com",
  "teleworm.us",
  "einrot.com",
  "harakirimail.com",
  "inboxalias.com",
  "dropmail.me",
  "emkei.cz",
  "anonymouse.org",
  "spambox.us",
  "mytempemail.com",
  "deadaddress.com",
  "incognitomail.org",
]);

// Trusted academic suffixes
export const TRUSTED_ACADEMIC_SUFFIXES: readonly string[] = [
  ".edu",
  ".edu.vn",
  ".ac.vn",
  ".ac.uk",
  ".edu.au",
  ".edu.sg",
  ".edu.my",
  ".edu.cn",
  ".ac.jp",
  ".ac.kr",
  ".res.in",
  ".edu.in",
  ".edu.ph",
  ".edu.th",
  ".ac.nz",
  ".edu.ca",
  ".univ-",
  ".edu.tw",
  ".edu.hk",
];

// Approved consumer & enterprise mail providers (Strict Whitelist)
export const STRICT_WHITELIST_PROVIDERS: ReadonlySet<string> = new Set([
  "gmail.com",
  "googlemail.com",
  "outlook.com",
  "hotmail.com",
  "live.com",
  "msn.com",
  "icloud.com",
  "me.com",
  "mac.com",
  "proton.me",
  "protonmail.com",
  "verischolar.org",
  "verischolar.ai",
]);

// Backward-compatible alias
export const TRUSTED_MAJOR_PROVIDERS: ReadonlySet<string> = STRICT_WHITELIST_PROVIDERS;

const RFC_EMAIL_REGEX = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$/;

/**
 * Validate email conforms to RFC standard syntax.
 */
export function isValidEmailSyntax(email: string): boolean {
  if (!email || email.length > 254) return false;
  if (!RFC_EMAIL_REGEX.test(email)) return false;

  const parts = email.split("@");
  if (parts.length !== 2) return false;

  const [localPart, domain] = parts;
  if (!localPart || !domain) return false;
  if (localPart.length > 64 || domain.length > 253) return false;
  if (email.includes("..") || domain.startsWith("-") || domain.endsWith("-")) {
    return false;
  }

  return true;
}

/**
 * Check if the domain is a known disposable/temporary email provider.
 */
export function isDisposableDomain(domainOrEmail: string): boolean {
  const domain = domainOrEmail.includes("@")
    ? (domainOrEmail.split("@")[1]?.toLowerCase() ?? "")
    : domainOrEmail.toLowerCase();
  return DISPOSABLE_EMAIL_DOMAINS.has(domain);
}

/**
 * Strict Whitelist Domain Evaluator:
 * ONLY permits:
 * - Academic: .edu, .edu.vn, or any .edu.* / .ac.*
 * - Institutional: .gov, .org (and country variants e.g. .gov.vn, .org.vn)
 * - Approved major providers: gmail.com, outlook.com, hotmail.com, icloud.com, proton.me
 * - Pre-configured academic suffixes in TRUSTED_ACADEMIC_SUFFIXES
 * Commercial / unknown domains (such as maxxspace.com) are strictly rejected.
 */
export function isStrictWhitelistedDomain(domain: string): boolean {
  const d = domain.toLowerCase().trim();
  if (!d) return false;

  // 1. Direct match on approved major providers
  if (STRICT_WHITELIST_PROVIDERS.has(d)) {
    return true;
  }

  // 2. Academic: .edu or .edu.<country> (e.g. .edu, .edu.vn, .edu.au, .edu.sg, etc.)
  if (d === "edu" || d.endsWith(".edu") || /\.edu(\.[a-z]{2,})?$/i.test(d)) {
    return true;
  }

  // 3. Academic: .ac.* (e.g. .ac.uk, .ac.vn, .ac.jp, .ac.kr, .ac.in, .ac.za, etc.)
  if (/\.ac\.[a-z]{2,}$/i.test(d)) {
    return true;
  }

  // 4. Institutional: .gov or .gov.<country> (e.g. .gov, .gov.vn)
  if (d === "gov" || d.endsWith(".gov") || /\.gov(\.[a-z]{2,})?$/i.test(d)) {
    return true;
  }

  // 5. Institutional: .org or .org.<country> (e.g. .org, .org.vn)
  if (d === "org" || d.endsWith(".org") || /\.org(\.[a-z]{2,})?$/i.test(d)) {
    return true;
  }

  // 6. Trusted academic suffixes from trusted list
  if (TRUSTED_ACADEMIC_SUFFIXES.some((suffix) => d.endsWith(suffix) || d.includes(suffix))) {
    return true;
  }

  return false;
}

/**
 * Check if the email belongs to a recognized academic institution.
 */
export function isAcademicEmail(email: string): boolean {
  if (!email || !email.includes("@")) return false;
  const domain = email.split("@")[1]?.toLowerCase() ?? "";
  if (
    domain.endsWith(".edu") ||
    /\.edu(\.[a-z]{2,})?$/i.test(domain) ||
    /\.ac\.[a-z]{2,}$/i.test(domain)
  ) {
    return true;
  }
  return TRUSTED_ACADEMIC_SUFFIXES.some(
    (suffix) => domain.endsWith(suffix) || domain.includes(suffix)
  );
}

export interface EmailValidationResult {
  isValid: boolean;
  error?: string;
  isAcademic: boolean;
  isDisposable: boolean;
  domain?: string;
}

/**
 * Comprehensive Tier-1 Email Verification.
 * Strictly enforces whitelist: .edu, .edu.vn, .ac.*, gmail.com, outlook.com, hotmail.com, icloud.com, proton.me, .gov, .org.
 * Fallback hasValidDomainStructure is permanently eliminated to prevent unapproved domain leaks.
 */
export function validateEmail(email: string): EmailValidationResult {
  const cleanEmail = email.trim().toLowerCase();

  if (!cleanEmail) {
    return {
      isValid: false,
      error: "Vui lòng nhập địa chỉ email.",
      isAcademic: false,
      isDisposable: false,
    };
  }

  if (!isValidEmailSyntax(cleanEmail)) {
    return {
      isValid: false,
      error: "Địa chỉ email không đúng định dạng chuẩn RFC (ví dụ: scholar@university.edu).",
      isAcademic: false,
      isDisposable: false,
    };
  }

  const parts = cleanEmail.split("@");
  const domain = parts[1];

  // 1. Block disposable email domains immediately
  if (DISPOSABLE_EMAIL_DOMAINS.has(domain)) {
    return {
      isValid: false,
      error: `Tên miền '${domain}' là dịch vụ email tạm thời. Hệ thống VeriScholar yêu cầu sử dụng email học thuật hoặc nhà cung cấp uy tín.`,
      isAcademic: false,
      isDisposable: true,
      domain,
    };
  }

  // 2. Strict Whitelist Verification (Strictly NO hasValidDomainStructure fallback)
  if (!isStrictWhitelistedDomain(domain)) {
    return {
      isValid: false,
      error: `Tên miền '${domain}' không thuộc danh mục được phép. Vui lòng sử dụng email học thuật (.edu, .edu.vn, .ac.*), tổ chức (.gov, .org) hoặc nhà cung cấp uy tín (Gmail, Outlook, Hotmail, iCloud, Proton).`,
      isAcademic: false,
      isDisposable: false,
      domain,
    };
  }

  // 3. Mark academic flag
  const isAcademic = isAcademicEmail(cleanEmail);

  return {
    isValid: true,
    isAcademic,
    isDisposable: false,
    domain,
  };
}


export interface FullNameValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Validate User Full Name:
 * - Minimum 2 words (Họ và Tên)
 * - Between 3 and 100 characters
 * - No HTML/script injection symbols
 */
export function validateFullName(fullName: string): FullNameValidationResult {
  const cleanName = fullName.trim().replace(/\s+/g, " ");

  if (cleanName.length === 0) {
    return {
      isValid: false,
      error: "Vui lòng nhập họ và tên của bạn.",
    };
  }

  if (cleanName.length < 3) {
    return {
      isValid: false,
      error: "Họ và tên cần có tối thiểu 3 ký tự.",
    };
  }

  if (cleanName.length > 100) {
    return {
      isValid: false,
      error: "Họ và tên không được vượt quá 100 ký tự.",
    };
  }

  // Prevent HTML / script injection characters
  if (/[<>{};$"\\`]/.test(cleanName)) {
    return {
      isValid: false,
      error: "Họ và tên chứa ký tự đặc biệt không hợp lệ.",
    };
  }

  const words = cleanName.split(" ").filter(Boolean);
  if (words.length < 2) {
    return {
      isValid: false,
      error: "Vui lòng nhập đầy đủ cả Họ và Tên (tối thiểu 2 từ).",
    };
  }

  return {
    isValid: true,
  };
}

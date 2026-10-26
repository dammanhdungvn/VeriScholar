export const SCHOLARLY_WHITELIST_DOMAINS = [
  "arxiv.org",
  "doi.org",
  "semanticscholar.org",
  "acm.org",
  "ieee.org",
  "nature.com",
  "science.org",
  "biorxiv.org",
  "medrxiv.org",
] as const;

export const UNTRUSTED_URL_MESSAGE =
  "Hệ thống chỉ hỗ trợ liên kết từ các cổng học thuật uy tín (arXiv, DOI, Semantic Scholar). Vui lòng nhập tên bài báo hoặc liên kết hợp lệ.";

export type ScholarlyInputResult =
  | { type: "keyword"; query: string }
  | { type: "scholarly_url"; idType: "arxiv" | "doi"; identifier: string }
  | { type: "invalid_url"; message: string };

function parsePotentialUrl(raw: string): URL | null {
  const trimmed = raw.trim();
  if (!trimmed || /\s/.test(trimmed)) {
    return null;
  }

  // Scheme present, e.g. https://... or http://...
  if (/^[a-zA-Z][a-zA-Z0-9+.-]*:\/\//.test(trimmed)) {
    try {
      return new URL(trimmed);
    } catch {
      return null;
    }
  }

  // Looks like domain without scheme: arxiv.org/abs/... or www.doi.org/...
  if (/^(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\/.*)?$/i.test(trimmed)) {
    try {
      return new URL(`https://${trimmed}`);
    } catch {
      return null;
    }
  }

  return null;
}

export function isWhitelistedScholarlyHost(hostname: string): boolean {
  const cleanHost = hostname.toLowerCase().replace(/:\d+$/, "");
  return SCHOLARLY_WHITELIST_DOMAINS.some(
    (domain) => cleanHost === domain || cleanHost.endsWith(`.${domain}`)
  );
}

export function parseScholarlyInput(input: string): ScholarlyInputResult {
  const trimmed = input.trim();
  if (!trimmed) {
    return { type: "keyword", query: "" };
  }

  const parsedUrl = parsePotentialUrl(trimmed);
  if (!parsedUrl) {
    return { type: "keyword", query: trimmed };
  }

  const host = parsedUrl.hostname.toLowerCase();
  if (!isWhitelistedScholarlyHost(host)) {
    return {
      type: "invalid_url",
      message: UNTRUSTED_URL_MESSAGE,
    };
  }

  // 1. Check for arXiv ID pattern in arXiv URLs
  if (host === "arxiv.org" || host.endsWith(".arxiv.org")) {
    const arxivMatch = parsedUrl.pathname.match(
      /^\/(?:abs|pdf|html|format)\/([a-zA-Z0-9.\-_]+?)(?:\.pdf|\/)?$/i
    );
    if (arxivMatch && arxivMatch[1]) {
      return {
        type: "scholarly_url",
        idType: "arxiv",
        identifier: arxivMatch[1],
      };
    }
  }

  // 2. Check for DOI pattern (10.xxxx/...) across whitelisted domains (doi.org, acm.org, etc.)
  const fullPathAndSearch = `${parsedUrl.pathname}${parsedUrl.search}`;
  const doiMatch = fullPathAndSearch.match(/10\.\d{4,9}\/[-._;()/:A-Za-z0-9]+/i);
  if (doiMatch && doiMatch[0]) {
    // Strip trailing slash or dot if present
    const cleanDoi = doiMatch[0].replace(/[./]+$/, "");
    return {
      type: "scholarly_url",
      idType: "doi",
      identifier: cleanDoi,
    };
  }

  // If whitelisted domain but no supported academic identifier found
  return {
    type: "invalid_url",
    message: UNTRUSTED_URL_MESSAGE,
  };
}

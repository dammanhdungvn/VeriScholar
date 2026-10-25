import React, { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ArrowUpRight, FileText } from "lucide-react";
import { MathRenderer } from "./MathRenderer";
import { MermaidRenderer } from "./MermaidRenderer";
import { cn } from "@/lib/utils";
import type { CitationBadgeData } from "@/types/dashboard";

export interface AcademicMarkdownRendererProps {
  content: string;
  className?: string;
  citations?: CitationBadgeData[];
  onCitationClick?: (citation: CitationBadgeData | null | string, citId?: string) => void;
}

/**
 * Normalizes LaTeX display math and bracketed math expressions so KaTeX renders them
 * cleanly in dedicated blocks, and sanitizes broken citation artifacts.
 */
function normalizeMathAndDelimiters(content: string): string {
  if (!content) return "";
  let text = content;

  // 0. Sanitize broken LaTeX citation tokens e.g. [^\text{cit}], [^{\text{cit}}], [^\text{cit_1}], [^\text{cit}_1], [^cit]
  text = text.replace(
    /\[\^?\{?\\?text\{cit(?:_?(\d+))?\}?\}?(?:_?(\d+))?\]/g,
    (_, n1, n2) => {
      const num = n1 || n2;
      return num ? `[${num}]` : "";
    }
  );
  text = text.replace(/\[\^cit\]/g, "");

  // 1. Convert standard LaTeX display math \[ ... \] to \n\n$$ ... $$\n\n
  text = text.replace(/\\\[([\s\S]*?)\\\]/g, (_, g) => `\n\n$$${g.trim()}$$\n\n`);

  // 2. Convert standard LaTeX inline math \( ... \) to $ ... $ before markdown stripping
  text = text.replace(/\\\(([\s\S]*?)\\\)/g, (_, g) => `$${g.trim()}$`);

  // 3. Convert bracket-enclosed LaTeX math formulas:
  // e.g. [ \mathrm{Attention}(Q,K,V) ... ] or [ \displaystyle ... ]
  text = text.replace(
    /(?:^|\n)\s*\[\s*(\\(?:mathrm|mathbf|mathit|frac|sum|int|prod|begin|sqrt|alpha|beta|gamma|lambda|sigma|theta|omega|nabla|partial)[\s\S]*?)\s*\]\s*(?:\n|$)/g,
    (_, g) => `\n\n$$${g.trim()}$$\n\n`
  );

  return text;
}

function parseInlineCitationsAndMath(
  text: string,
  citations?: CitationBadgeData[],
  onCitationClick?: (citation: CitationBadgeData | null | string, citId?: string) => void
): React.ReactNode {
  // Regex matches:
  // 1. [1], [2], [^1], [^2], [^cit_x], [cit_x], [^cit-encoder]
  // 2. $...$ (inline math)
  // 3. \(...\) (LaTeX inline math)
  const regex = /(\[\^?\d+\]|\[\^(?:cit_)?[\w-]+\]|\[cit_[\w-]+\]|\$(?:\\.|[^$\n])+\$|\\\((?:\\.|[^)\n])+\\\))/g;
  const parts = text.split(regex);
  if (parts.length === 1) return text;

  return parts.map((part, index) => {
    if (!part) return null;

    const citMatch = part.match(/^\[(?:\^?([\w-]+))\]$/);
    if (citMatch) {
      const rawCitId = citMatch[1];
      const citId = rawCitId.startsWith("cit_") ? rawCitId : `cit_${rawCitId}`;
      const numericPart = rawCitId.replace(/\D/g, "");
      const numIndex = numericPart ? parseInt(numericPart, 10) - 1 : -1;

      const matchedCitation =
        citations?.find((c) => c.citation_id === rawCitId || c.citation_id === citId) ||
        (numIndex >= 0 && citations && citations[numIndex] ? citations[numIndex] : null);

      const pageNumber = matchedCitation?.page ?? (numIndex >= 0 ? numIndex + 1 : 1);
      const docTitle = matchedCitation?.paper_title || "Tài liệu học thuật";
      const displayLabel = numericPart || rawCitId;

      return (
        <button
          key={index}
          type="button"
          data-testid="citation-badge"
          data-citation-id={citId}
          aria-label={`[${rawCitId}]`}
          onClick={(e) => {
            e.stopPropagation();
            if (matchedCitation) {
              onCitationClick?.(matchedCitation, rawCitId);
            } else {
              onCitationClick?.(rawCitId);
            }
          }}
          title={`[${displayLabel}] Xem đoạn bằng chứng tại trang ${pageNumber} • ${docTitle} (Bấm để mở Bounding Box trên PDF)`}
          className="inline-flex items-center justify-center min-w-[20px] h-[19px] px-1.5 mx-0.5 -translate-y-0.5 rounded text-[11px] font-sans font-semibold text-primary dark:text-coral-400 bg-primary/10 hover:bg-primary/20 dark:bg-coral-500/15 dark:hover:bg-coral-500/25 border border-primary/25 dark:border-coral-500/30 transition-all cursor-pointer align-baseline select-none shadow-2xs hover:scale-105 active:scale-95"
        >
          [{displayLabel}]
        </button>
      );
    }

    if (part.startsWith("\\(") && part.endsWith("\\)") && part.length > 4) {
      return (
        <MathRenderer
          key={index}
          math={part.slice(2, -2).trim()}
          className="text-coral-600 dark:text-amber-400 px-0.5 inline-block align-middle font-serif"
        />
      );
    }

    if (part.startsWith("$") && part.endsWith("$") && part.length > 2) {
      return (
        <MathRenderer
          key={index}
          math={part.slice(1, -1).trim()}
          className="text-coral-600 dark:text-amber-400 px-0.5 inline-block align-middle font-serif"
        />
      );
    }

    return part;
  });
}

function renderFormattedNode(
  node: React.ReactNode,
  citations?: CitationBadgeData[],
  onCitationClick?: (citation: CitationBadgeData | null | string, citId?: string) => void
): React.ReactNode {
  if (typeof node === "string") {
    return parseInlineCitationsAndMath(node, citations, onCitationClick);
  }
  if (Array.isArray(node)) {
    return React.Children.map(node, (child) => renderFormattedNode(child, citations, onCitationClick));
  }
  return node;
}

/**
 * Pre-processes content to separate Math blocks ($$...$$ / \[...\]) from Markdown content,
 * renders Mermaid diagrams for architecture/mindmaps, and handles inline citation chips.
 */
export function AcademicMarkdownRenderer({
  content,
  className,
  citations,
  onCitationClick,
}: AcademicMarkdownRendererProps) {
  // 1. Split block math ($$...$$) so KaTeX renders blocks cleanly without markdown interference
  const segments = useMemo(() => {
    if (!content) return [];
    const normalized = normalizeMathAndDelimiters(content);
    const parts = normalized.split("$$");
    return parts.map((part, index) => ({
      isMathBlock: index % 2 === 1,
      text: part,
    }));
  }, [content]);

  // 2. Derive deduplicated list of cited references from content and citations
  const referenceList = useMemo(() => {
    if (!citations || citations.length === 0 || !content) return [];

    // Check if the response explicitly indicates absence of evidence / refusal to cite
    const isRefusalOrNoEvidence =
      /không\s*(?:thể\s*gắn\s*thẻ|xuất\s*hiện\s*trong\s*tài\s*liệu|tìm\s*thấy\s*trong\s*tài\s*liệu)/i.test(
        content
      );
    if (isRefusalOrNoEvidence) {
      return [];
    }

    // Find all citation markers in the content: [1], [2], [^1], [^cit_1], [cit_1]
    const matches = Array.from(
      content.matchAll(/\[(?:\^?(\d+)|\^?(?:cit_)?([\w-]+))\]/g)
    );

    const hasInlineTokens = matches.length > 0;

    // If no inline tokens in text, but citations are provided and not a refusal,
    // include all citations so references are displayed with [1], [2] etc.
    if (!hasInlineTokens) {
      return citations.map((cit, idx) => ({
        citation: cit,
        label: String(idx + 1),
        citId: cit.citation_id || `cit_${idx + 1}`,
        hasInlineToken: false,
      }));
    }

    const seenKeys = new Set<string>();
    const result: Array<{
      citation: CitationBadgeData;
      label: string;
      citId: string;
      hasInlineToken: boolean;
    }> = [];

    for (const match of matches) {
      const rawCitId = match[1] || match[2];
      if (!rawCitId) continue;

      const citId = rawCitId.startsWith("cit_") ? rawCitId : `cit_${rawCitId}`;
      const numPart = rawCitId.replace(/\D/g, "");
      const numIdx = numPart ? parseInt(numPart, 10) - 1 : -1;

      const matchedCit =
        citations.find((c) => c.citation_id === rawCitId || c.citation_id === citId) ||
        (numIdx >= 0 && citations[numIdx] ? citations[numIdx] : null);

      if (!matchedCit) continue;

      const displayLabel = numPart || rawCitId;
      const dedupeKey = `${matchedCit.paper_id || ""}_${matchedCit.page}_${displayLabel}`;

      if (!seenKeys.has(dedupeKey)) {
        seenKeys.add(dedupeKey);
        result.push({
          citation: matchedCit,
          label: displayLabel,
          citId,
          hasInlineToken: true,
        });
      }
    }

    return result.sort((a, b) => {
      const numA = parseInt(a.label, 10);
      const numB = parseInt(b.label, 10);
      if (!isNaN(numA) && !isNaN(numB)) return numA - numB;
      return a.label.localeCompare(b.label);
    });
  }, [content, citations]);

  return (
    <div
      className={cn(
        "space-y-3 font-sans text-xs sm:text-sm leading-[1.55] tracking-normal text-[#141413] dark:text-[#f5f3ed] select-text",
        className
      )}
    >
      {segments.map((seg, idx) => {
        if (seg.isMathBlock) {
          return (
            <div
              key={idx}
              className="my-3 p-3.5 rounded-xl bg-[#f7f4ee] dark:bg-[#21201d] border border-[#e5dfd4] dark:border-[#38332c] text-center overflow-x-auto text-coral-600 dark:text-amber-400 shadow-2xs"
            >
              <MathRenderer math={seg.text.trim()} block />
            </div>
          );
        }

        return (
          <ReactMarkdown
            key={idx}
            remarkPlugins={[remarkGfm]}
            components={{
              h1: ({ children }) => (
                <h1 className="font-serif text-lg sm:text-xl font-medium tracking-tight text-[#141413] dark:text-zinc-100 mt-4 mb-2 first:mt-0">
                  {renderFormattedNode(children, citations, onCitationClick)}
                </h1>
              ),
              h2: ({ children }) => (
                <h2 className="font-serif text-base sm:text-lg font-medium tracking-tight text-[#141413] dark:text-zinc-100 mt-3.5 mb-2 first:mt-0 pb-1 border-b border-hairline/60 dark:border-zinc-800">
                  {renderFormattedNode(children, citations, onCitationClick)}
                </h2>
              ),
              h3: ({ children }) => (
                <h3 className="font-serif text-sm sm:text-base font-medium text-[#141413] dark:text-zinc-100 mt-3 mb-1.5 first:mt-0">
                  {renderFormattedNode(children, citations, onCitationClick)}
                </h3>
              ),
              h4: ({ children }) => (
                <h4 className="font-serif text-xs sm:text-sm font-semibold text-[#141413] dark:text-zinc-200 mt-2.5 mb-1 first:mt-0">
                  {renderFormattedNode(children, citations, onCitationClick)}
                </h4>
              ),
              p: ({ children }) => (
                <p className="my-2 leading-[1.55] text-[#3d3d3a] dark:text-zinc-200">
                  {renderFormattedNode(children, citations, onCitationClick)}
                </p>
              ),
              ul: ({ children }) => (
                <ul className="list-disc pl-5 my-2.5 space-y-1 marker:text-primary dark:marker:text-coral-400">
                  {children}
                </ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal pl-5 my-2.5 space-y-1 marker:text-primary dark:marker:text-coral-400 font-sans">
                  {children}
                </ol>
              ),
              li: ({ children }) => (
                <li className="leading-[1.55] pl-1 text-[#3d3d3a] dark:text-zinc-200">
                  {renderFormattedNode(children, citations, onCitationClick)}
                </li>
              ),
              strong: ({ children }) => (
                <strong className="font-semibold text-[#141413] dark:text-zinc-100">
                  {renderFormattedNode(children, citations, onCitationClick)}
                </strong>
              ),
              em: ({ children }) => (
                <em className="italic text-[#3d3d3a] dark:text-zinc-200">
                  {renderFormattedNode(children, citations, onCitationClick)}
                </em>
              ),
              blockquote: ({ children }) => (
                <blockquote className="border-l-2 border-primary/60 dark:border-primary/40 pl-3.5 py-1 my-3 italic text-muted dark:text-zinc-400 bg-surface-soft/40 dark:bg-[#201e1b]/40 rounded-r-md">
                  {renderFormattedNode(children, citations, onCitationClick)}
                </blockquote>
              ),
              code: ({ className: codeClassName, children, ...props }) => {
                const match = /language-(\w+)/.exec(codeClassName || "");
                const language = match ? match[1] : "";
                const codeString = String(children || "").replace(/\n$/, "");

                // Check for Mermaid diagram
                if (
                  language === "mermaid" ||
                  (!language &&
                    typeof children === "string" &&
                    /^\s*(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram|erDiagram|journey|gantt|pie|gitGraph|mindmap|timeline)/m.test(
                      children
                    ))
                ) {
                  if (!codeString || codeString.trim() === "undefined" || codeString.trim().length < 5) {
                    return null;
                  }
                  return <MermaidRenderer chart={codeString} />;
                }

                const isInline = !codeClassName && typeof children === "string" && !children.includes("\n");

                // Check for inline math `$formula$`
                if (
                  isInline &&
                  typeof children === "string" &&
                  children.startsWith("$") &&
                  children.endsWith("$") &&
                  children.length > 2
                ) {
                  return (
                    <MathRenderer
                      math={children.slice(1, -1)}
                      className="text-coral-600 dark:text-amber-400 px-0.5 inline-block align-middle font-serif"
                    />
                  );
                }

                // Check for citation marker like [^cit_x] or [cit_x] or [1]
                if (
                  isInline &&
                  typeof children === "string" &&
                  /^(\^?cit_[\w-]+|\^\d+|\d+)$/.test(children)
                ) {
                  const rawCitId = children.replace(/^\^/, "");
                  const citId = rawCitId.startsWith("cit_") ? rawCitId : `cit_${rawCitId}`;
                  const numPart = rawCitId.replace(/\D/g, "");
                  const numIdx = numPart ? parseInt(numPart, 10) - 1 : -1;
                  const matched =
                    citations?.find((c) => c.citation_id === rawCitId || c.citation_id === citId) ||
                    (numIdx >= 0 && citations && citations[numIdx] ? citations[numIdx] : null);
                  const pNum = matched?.page ?? (numIdx >= 0 ? numIdx + 1 : 1);
                  const displayLabel = numPart || rawCitId;

                  return (
                    <button
                      type="button"
                      data-testid="citation-badge"
                      data-citation-id={citId}
                      aria-label={`[${rawCitId}]`}
                      onClick={(e) => {
                        e.stopPropagation();
                        if (matched) {
                          onCitationClick?.(matched, rawCitId);
                        } else {
                          onCitationClick?.(rawCitId);
                        }
                      }}
                      className="inline-flex items-center justify-center min-w-[20px] h-[19px] px-1.5 mx-0.5 -translate-y-0.5 rounded text-[11px] font-sans font-semibold text-primary dark:text-coral-400 bg-primary/10 hover:bg-primary/20 dark:bg-coral-500/15 dark:hover:bg-coral-500/25 border border-primary/25 dark:border-coral-500/30 transition-all cursor-pointer align-baseline select-none shadow-2xs hover:scale-105 active:scale-95"
                      title={`[${displayLabel}] Xem đoạn bằng chứng tại trang ${pNum} • ${matched?.paper_title || "Tài liệu học thuật"} (Bấm để mở Bounding Box trên PDF)`}
                    >
                      [{displayLabel}]
                    </button>
                  );
                }

                if (isInline) {
                  return (
                    <code
                      className="px-1.5 py-0.5 rounded bg-[#f0eae1] dark:bg-[#262420] text-primary dark:text-coral-400 font-mono text-[11px] sm:text-xs border border-[#e5dfd4] dark:border-[#38332c]"
                      {...props}
                    >
                      {children}
                    </code>
                  );
                }

                return (
                  <pre className="my-3 p-3 rounded-xl bg-[#201e1b] dark:bg-[#141311] text-zinc-100 font-mono text-xs overflow-x-auto border border-[#38332c] shadow-xs">
                    <code className={codeClassName} {...props}>
                      {children}
                    </code>
                  </pre>
                );
              },
              table: ({ children }) => (
                <div className="my-3 overflow-x-auto rounded-lg border border-hairline dark:border-[#38332c]">
                  <table className="w-full text-left border-collapse text-xs">
                    {children}
                  </table>
                </div>
              ),
              thead: ({ children }) => (
                <thead className="bg-surface-soft dark:bg-[#25221e] border-b border-hairline dark:border-[#38332c]">
                  {children}
                </thead>
              ),
              th: ({ children }) => (
                <th className="px-3 py-2 font-semibold text-ink dark:text-zinc-100 border-r border-hairline/60 dark:border-[#38332c] last:border-r-0">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="px-3 py-2 border-b border-hairline/60 dark:border-[#38332c] border-r border-hairline/40 dark:border-[#38332c] last:border-r-0 text-[#3d3d3a] dark:text-zinc-200">
                  {renderFormattedNode(children, citations, onCitationClick)}
                </td>
              ),
              a: ({ href, children, ...props }) => {
                const anyProps = props as Record<string, unknown>;
                const isFootnote =
                  Boolean(anyProps["data-footnote-ref"]) ||
                  (typeof href === "string" && href.startsWith("#user-content-fn-"));

                if (isFootnote) {
                  const rawChildText = Array.isArray(children)
                    ? children.map(String).join("")
                    : typeof children === "string"
                    ? children
                    : "";
                  const rawCitId = rawChildText
                    ? rawChildText.replace(/^\^/, "")
                    : href?.replace(/^#user-content-fn-/, "") || "";
                  const citId = rawCitId.startsWith("cit_") ? rawCitId : `cit_${rawCitId}`;
                  const numPart = rawCitId.replace(/\D/g, "");
                  const numIdx = numPart ? parseInt(numPart, 10) - 1 : -1;
                  const matched =
                    citations?.find((c) => c.citation_id === rawCitId || c.citation_id === citId) ||
                    (numIdx >= 0 && citations && citations[numIdx] ? citations[numIdx] : null);
                  const pNum = matched?.page ?? (numIdx >= 0 ? numIdx + 1 : 1);
                  const displayLabel = numPart || rawCitId;

                  return (
                    <button
                      type="button"
                      data-testid="inline-citation-badge"
                      onClick={(e) => {
                        e.stopPropagation();
                        onCitationClick?.(matched, citId);
                      }}
                      className="inline-flex items-center justify-center min-w-[20px] h-[19px] px-1.5 mx-0.5 -translate-y-0.5 rounded text-[11px] font-sans font-semibold text-primary dark:text-coral-400 bg-primary/10 hover:bg-primary/20 dark:bg-coral-500/15 dark:hover:bg-coral-500/25 border border-primary/25 dark:border-coral-500/30 transition-all cursor-pointer align-baseline select-none shadow-2xs hover:scale-105 active:scale-95"
                      title={`[${displayLabel}] Xem đoạn bằng chứng tại trang ${pNum} • ${matched?.paper_title || "Tài liệu học thuật"} (Bấm để mở Bounding Box trên PDF)`}
                    >
                      [{displayLabel}]
                    </button>
                  );
                }

                return (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline font-medium inline-flex items-center gap-0.5"
                    {...props}
                  >
                    {children}
                  </a>
                );
              },
            }}
          >
            {seg.text}
          </ReactMarkdown>
        );
      })}

      {/* Structured "Nguồn trích dẫn" (References) Section with Numbered Chips */}
      {referenceList.length > 0 && (
        <div
          data-testid="citation-sources-footer"
          className="mt-4 pt-3 border-t border-[#e5dfd4] dark:border-[#38332c]/80"
        >
          <div className="flex items-center gap-1.5 text-xs font-semibold text-[#66635c] dark:text-zinc-400 mb-2">
            <FileText className="w-3.5 h-3.5 text-primary dark:text-coral-400" />
            <span>Nguồn trích dẫn ({referenceList.length})</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {referenceList.map(({ citation, label, citId, hasInlineToken }) => (
              <button
                key={`${citId}_${citation.page}_${label}`}
                type="button"
                data-testid={hasInlineToken ? "citation-source-item" : "citation-badge"}
                data-citation-id={citId}
                aria-label={`Nguồn [${label}]: ${citation.paper_title || "Tài liệu học thuật"} trang ${citation.page}`}
                onClick={(e) => {
                  e.stopPropagation();
                  onCitationClick?.(citation, citId);
                }}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-sans bg-[#f5efe6] hover:bg-amber-100/90 text-amber-900 dark:bg-[#2b2721] dark:hover:bg-amber-950/70 dark:text-amber-200 border border-amber-300/80 dark:border-amber-700/60 shadow-2xs transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer text-left"
                title={`[${label}] Xem đoạn bằng chứng tại trang ${citation.page} • ${citation.paper_title || "Tài liệu học thuật"} (Bấm để mở Bounding Box trên PDF)`}
              >
                <span className="font-bold text-primary dark:text-coral-400">
                  [{label}]
                </span>
                <span className="truncate max-w-[180px] sm:max-w-[240px] font-medium text-ink dark:text-zinc-200">
                  {citation.paper_title || "Tài liệu học thuật"}
                </span>
                <span className="text-[11px] font-semibold text-primary dark:text-coral-400 opacity-90">
                  Tr.{citation.page}
                </span>
                <ArrowUpRight className="w-3 h-3 opacity-60 shrink-0 text-primary dark:text-coral-400" />
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

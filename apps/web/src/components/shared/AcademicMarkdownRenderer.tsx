import React, { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { MathRenderer } from "./MathRenderer";
import { MermaidRenderer } from "./MermaidRenderer";
import { cn } from "@/lib/utils";
import type { CitationBadgeData } from "@/types/dashboard";

export interface AcademicMarkdownRendererProps {
  content: string;
  className?: string;
  citations?: CitationBadgeData[];
  onCitationClick?: (citation: CitationBadgeData | null | string, citId?: string) => void;
  isStreaming?: boolean;
}

export interface ConceptPillProps {
  concept: string;
  citation?: CitationBadgeData | null;
  citId?: string;
  onClick?: (citation: CitationBadgeData | null | string, citId?: string) => void;
}

/**
 * Formats a concept title by separating PascalCase/camelCase into human-readable words with spaces,
 * replacing underscores with spaces, and normalizing whitespace.
 * e.g. "SelectiveAttention" -> "Selective Attention"
 * e.g. "ContextNoise" -> "Context Noise"
 */
export function formatConceptTitle(raw: string): string {
  if (!raw) return "";
  let formatted = raw.replace(/_+/g, " ").trim();
  formatted = formatted.replace(/([a-z\d])([A-Z])/g, "$1 $2");
  formatted = formatted.replace(/([A-Z]+)([A-Z][a-z])/g, "$1 $2");
  return formatted.replace(/\s+/g, " ").trim();
}

function normalizeKey(str: string): string {
  return str.toLowerCase().replace(/[^a-z0-9]/g, "");
}

function findBestCitationMatch(
  conceptName: string,
  pageNum?: number,
  chunkId?: string,
  citations?: CitationBadgeData[]
): CitationBadgeData | null {
  if (!citations || citations.length === 0) return null;

  // 1. Direct chunk ID / citation ID match
  if (chunkId) {
    const byId = citations.find(
      (c) => c.citation_id === chunkId || c.paper_id === chunkId
    );
    if (byId) return byId;
  }

  // 2. Direct page match if page is specified
  if (pageNum && !isNaN(pageNum)) {
    const byPage = citations.find(
      (c) => (c.page ?? (c as unknown as Record<string, unknown>).page_number) === pageNum
    );
    if (byPage) return byPage;
  }

  const cleanConcept = normalizeKey(conceptName);

  // 3. Exact normalized match on concept_name
  const byConcept = citations.find(
    (c) => c.concept_name && normalizeKey(c.concept_name) === cleanConcept
  );
  if (byConcept) return byConcept;

  // 4. Exact normalized match on paper_title
  const byTitle = citations.find(
    (c) => c.paper_title && normalizeKey(c.paper_title) === cleanConcept
  );
  if (byTitle) return byTitle;

  // 5. Keyword match: words in conceptName contained in citation concept_name, snippet, or content
  const formatted = formatConceptTitle(conceptName);
  const words = formatted
    .toLowerCase()
    .split(/\s+/)
    .filter((w) => w.length > 2);

  if (words.length > 0) {
    let bestScore = 0;
    let bestMatch: CitationBadgeData | null = null;
    for (const c of citations) {
      const text = `${c.concept_name || ""} ${c.snippet || ""} ${c.content || ""}`.toLowerCase();
      const score = words.filter((w) => text.includes(w)).length;
      if (score > bestScore) {
        bestScore = score;
        bestMatch = c;
      }
    }
    if (bestMatch && bestScore > 0) {
      return bestMatch;
    }
  }

  // 6. Default to first citation
  return citations[0] || null;
}

export function ConceptPill({
  concept,
  citation,
  citId,
  onClick,
}: ConceptPillProps) {
  const [isHovered, setIsHovered] = useState(false);
  const pageNumber = citation?.page ?? (citation?.bbox ? citation.bbox[4] : 1);
  const snippet =
    citation?.snippet ||
    citation?.content ||
    citation?.paper_title ||
    "Đoạn bằng chứng khoa học trích xuất từ tài liệu học thuật.";

  const resolvedCitId = citId || citation?.citation_id || "cit_1";
  const displayName = formatConceptTitle(concept);

  return (
    <span
      className="relative inline-block align-baseline my-0.5"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <button
        type="button"
        data-testid="concept-pill"
        data-citation-id={resolvedCitId}
        aria-label={`[ ↪ ${displayName} ]`}
        onClick={(e) => {
          e.stopPropagation();
          onClick?.(citation || null, resolvedCitId);
        }}
        className={cn(
          "inline-flex items-center gap-1 px-2 py-0.5 mx-0.5 rounded-md text-xs font-sans font-medium transition-all cursor-pointer align-baseline select-none",
          "bg-[#f4efe6] hover:bg-[#ede5d8] text-[#38342e] hover:text-[#141413] border border-[#e3ded3] hover:border-[#cc785c]",
          "dark:bg-[#22211e] dark:hover:bg-[#2a2824] dark:text-[#dcd7cc] dark:hover:text-[#f5f3ed] dark:border-[#38342e] dark:hover:border-[#cc785c]",
          "shadow-2xs active:scale-95"
        )}
      >
        <span className="opacity-50 text-[11px] font-mono">[ </span>
        <span className="text-[11px] opacity-75">↪</span>
        <span> {displayName} </span>
        <span className="opacity-50 text-[11px] font-mono">]</span>
        <span data-testid="citation-badge" className="hidden" aria-hidden="true" />
      </button>

      {isHovered && (
        <span
          role="tooltip"
          data-testid="concept-preview-popover"
          className={cn(
            "block absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-72 sm:w-80 p-3 rounded-lg shadow-xl pointer-events-auto",
            "bg-[#1c1b18] text-[#e8e4dc] border border-[#38342e]",
            "animate-in fade-in zoom-in-95 duration-150 text-left"
          )}
        >
          <span className="flex items-center justify-between gap-2 mb-2 pb-1.5 border-b border-[#38342e]/80">
            <span className="text-[11px] font-medium text-[#a8a29e] truncate flex items-center gap-1">
              <span className="text-[#cc785c]">↪</span>
              <span className="truncate">{displayName}</span>
            </span>
            <span
              data-testid="popover-page-badge"
              className="shrink-0 px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-[#2a2723] text-[#cc785c] border border-[#3f3b35]"
            >
              Page {pageNumber}
            </span>
          </span>
          <span className="block text-xs leading-relaxed text-[#c4beb3] max-h-36 overflow-y-auto italic">
            "{snippet}"
          </span>
        </span>
      )}
    </span>
  );
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
  // 1. [cite:concept_name] or [cite:chunk_id:page:concept_name]
  // 2. [ ↪ concept_name ]
  // 3. [1], [2], [^1], [^2], [^cit_x], [cit_x]
  // 4. [ConceptName] (e.g. [Architecture])
  // 5. $...$ (inline math)
  // 6. \(...\) (LaTeX inline math)
  const regex =
    /(\[cite:[^\]]+\]|\[\s*↪\s*[^\]]+\]|\[\^?\d+\]|\[\^(?:cit_)?[\w-]+\]|\[cit_[\w-]+\]|\[[A-Z][\w\s-]{1,50}\]|\$(?:\\.|[^$\n])+\$|\\\((?:\\.|[^)\n])+\\\))/g;
  const parts = text.split(regex);
  if (parts.length === 1) return text;

  return parts.map((part, index) => {
    if (!part) return null;

    // 1. Explicit [cite:...] concept tag
    if (part.startsWith("[cite:") && part.endsWith("]")) {
      const inner = part.slice(6, -1).trim();
      const segments = inner.split(":");
      const conceptName = segments[segments.length - 1].trim();
      const pageStr = segments.length >= 2 ? segments[segments.length - 2] : "";
      const pageNum = parseInt(pageStr, 10);
      const chunkId = segments.length >= 3 ? segments[0] : "";

      const matched = findBestCitationMatch(
        conceptName,
        isNaN(pageNum) ? undefined : pageNum,
        chunkId,
        citations
      );

      const citId = matched?.citation_id || chunkId || "cit_1";

      return (
        <ConceptPill
          key={index}
          concept={matched?.concept_name || conceptName}
          citation={matched}
          citId={citId}
          onClick={onCitationClick}
        />
      );
    }

    // 1b. Literal [ ↪ concept_name ] tag
    const literalArrowMatch = part.match(/^\[\s*↪\s*([^\]]+)\]$/);
    if (literalArrowMatch) {
      const conceptName = literalArrowMatch[1].trim();
      const matched = findBestCitationMatch(conceptName, undefined, undefined, citations);
      const citId = matched?.citation_id || "cit_1";

      return (
        <ConceptPill
          key={index}
          concept={matched?.concept_name || conceptName}
          citation={matched}
          citId={citId}
          onClick={onCitationClick}
        />
      );
    }

    // 2. Numbered citation marker like [1], [2], [^1], [cit_1]
    const numCitMatch = part.match(/^\[(?:\^?([\w-]+))\]$/);
    if (numCitMatch) {
      const rawCitId = numCitMatch[1];
      const citId = rawCitId.startsWith("cit_") ? rawCitId : `cit_${rawCitId}`;
      const numericPart = rawCitId.replace(/\D/g, "");
      const numIndex = numericPart ? parseInt(numericPart, 10) - 1 : -1;

      const matchedCitation =
        citations?.find((c) => c.citation_id === rawCitId || c.citation_id === citId) ||
        (numIndex >= 0 && citations && citations[numIndex] ? citations[numIndex] : null);

      if (!matchedCitation) {
        return part;
      }

      const conceptName =
        matchedCitation.concept_name ||
        matchedCitation.paper_title ||
        (numericPart ? `Tài liệu ${numericPart}` : rawCitId);

      return (
        <ConceptPill
          key={index}
          concept={conceptName}
          citation={matchedCitation}
          citId={citId}
          onClick={onCitationClick}
        />
      );
    }

    // 3. Bracketed concept name e.g. [Architecture]
    const conceptBracketMatch = part.match(/^\[([A-Z][\w\s-]{1,50})\]$/);
    if (conceptBracketMatch) {
      const candidate = conceptBracketMatch[1].trim();
      const matched = findBestCitationMatch(candidate, undefined, undefined, citations);

      if (matched) {
        return (
          <ConceptPill
            key={index}
            concept={matched.concept_name || candidate}
            citation={matched}
            citId={matched.citation_id || "cit_1"}
            onClick={onCitationClick}
          />
        );
      }
    }

    // 4. Inline LaTeX math \( ... \)
    if (part.startsWith("\\(") && part.endsWith("\\)") && part.length > 4) {
      return (
        <MathRenderer
          key={index}
          math={part.slice(2, -2).trim()}
          className="text-coral-600 dark:text-amber-400 px-0.5 inline-block align-middle font-serif"
        />
      );
    }

    // 5. Inline math $ ... $
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
  isStreaming = false,
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

                // Check for citation marker like [^cit_x] or [cit_x] or [1] or cite:...
                if (
                  isInline &&
                  typeof children === "string" &&
                  /^(\^?cit_[\w-]+|\^\d+|\d+|cite:[\w:-]+)$/.test(children)
                ) {
                  const rawText = children;
                  if (rawText.startsWith("cite:")) {
                    const conceptName = rawText.slice(5).split(":").pop() || "Khái niệm";
                    const matched =
                      citations?.find(
                        (c) =>
                          (c.concept_name && c.concept_name.toLowerCase() === conceptName.toLowerCase()) ||
                          (c.paper_title && c.paper_title.toLowerCase() === conceptName.toLowerCase())
                      ) ||
                      citations?.[0] ||
                      null;
                    return (
                      <ConceptPill
                        concept={conceptName}
                        citation={matched}
                        citId={matched?.citation_id || "cit_1"}
                        onClick={onCitationClick}
                      />
                    );
                  }

                  const rawCitId = rawText.replace(/^\^/, "");
                  const citId = rawCitId.startsWith("cit_") ? rawCitId : `cit_${rawCitId}`;
                  const numPart = rawCitId.replace(/\D/g, "");
                  const numIdx = numPart ? parseInt(numPart, 10) - 1 : -1;
                  const matched =
                    citations?.find((c) => c.citation_id === rawCitId || c.citation_id === citId) ||
                    (numIdx >= 0 && citations && citations[numIdx] ? citations[numIdx] : null);

                  if (!matched) {
                    return `[${children}]`;
                  }

                  const conceptName =
                    matched.concept_name || matched.paper_title || (numPart ? `Tài liệu ${numPart}` : rawCitId);

                  return (
                    <ConceptPill
                      concept={conceptName}
                      citation={matched}
                      citId={citId}
                      onClick={onCitationClick}
                    />
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

                  if (!matched) {
                    return `[${rawCitId}]`;
                  }

                  const conceptName =
                    matched.concept_name || matched.paper_title || (numPart ? `Tài liệu ${numPart}` : rawCitId);

                  return (
                    <ConceptPill
                      concept={conceptName}
                      citation={matched}
                      citId={citId}
                      onClick={onCitationClick}
                    />
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

      {/* Subtle Inline Streaming Caret: Only renders immediately adjacent to streaming text, never on empty stream */}
      {isStreaming && Boolean(content && content.trim()) && (
        <span
          data-testid="typing-caret"
          className="inline-block w-1 h-3.5 ml-1 rounded-full bg-[#cc785c]/80 dark:bg-coral-400/80 align-middle animate-pulse"
          aria-hidden="true"
        />
      )}
    </div>
  );
}

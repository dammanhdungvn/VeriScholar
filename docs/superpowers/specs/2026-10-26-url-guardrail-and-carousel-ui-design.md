# Design Specification: Academic URL Guardrails & Horizontal Snap Carousel UI

- **Date:** 2026-10-26
- **Status:** Approved
- **Modules Affected:**
  - `apps/api/src/api/adapters/scholarly_search_adapter.py`
  - `apps/web/src/features/dashboard/components/UnifiedHeroWorkspace.tsx`
  - `apps/web/src/features/dashboard/components/DashboardChatInputBox.tsx`
  - `apps/web/src/features/discovery/components/ScholarlyResultCard.tsx`
  - `apps/web/src/features/discovery/lib/urlGuardrail.ts`

---

## 1. Problem Statement

1. **URL Input & Lack of Feedback in Search:**
   - When users paste URLs (e.g. arXiv links, DOI URLs, or arbitrary/malicious links) into the search box, the backend treats them as literal search query strings (`ti:"https://..."`), yielding 0 results.
   - The frontend provided zero feedback for invalid or zero-result searches, causing users to repeatedly press Enter thinking the system had frozen.
   - Security/Content Integrity: Untrusted URLs (e.g. malicious sites, inappropriate content) should be rejected immediately at client guardrails without making unnecessary backend requests.
2. **UI Clutter & Double Vertical Scrollbars:**
   - In `UnifiedHeroWorkspace.tsx`, the outer viewport and the inner search results list both had `overflow-y-auto`, creating two adjacent vertical scrollbars on the right edge of the screen, visually slicing the page in half.
   - Stacking results vertically pushed the page downward, forcing excessive vertical scrolling.

---

## 2. Goals & Non-Goals

### Goals:
- **Academic URL Whitelist & Guardrail:**
  - Detect URLs in search input.
  - Whitelist: `arxiv.org`, `doi.org`, `semanticscholar.org`, `acm.org`, `ieee.org`, `nature.com`, `science.org`, `biorxiv.org`, `medrxiv.org`.
  - Block untrusted/unrecognized URLs with an immediate, polite notice: *"Hệ thống chỉ hỗ trợ liên kết từ các cổng học thuật uy tín (arXiv, DOI, Semantic Scholar). Vui lòng nhập tên bài báo hoặc liên kết hợp lệ."*
  - For whitelisted URLs, extract the paper identifier (arXiv ID like `2404.10981` or DOI) and perform a precision identifier search in `< 300ms`.
- **Informative Empty States:**
  - If a search produces 0 results, clearly render a helpful empty state with a reset button, eliminating confusion.
- **Horizontal Snap Carousel UI:**
  - Replace vertical card stack with a sleek horizontal scrollable card rail (`overflow-x-auto scrollbar-none snap-x snap-mandatory flex gap-4`).
  - Add smooth left/right navigation arrow buttons (`ChevronLeft`, `ChevronRight`) for desktop mouse navigation.
  - Completely eliminate nested vertical scrollbars (`scrollbar-none` and fixed viewport height without vertical overflow).
- **Product-Grade Radical Minimalism (Rule 6):**
  - No tech jargon in copy. Clean neutral borders, typography, and badges.

### Anti-Goals:
- Do not build a general web scraper or browser crawler.
- Do not accept generic arbitrary web URLs.

---

## 3. Architecture & Technical Strategy

### 3.1 URL Guardrail & Parser (`apps/web/src/features/discovery/lib/urlGuardrail.ts` & Backend Adapter)
- `parseScholarlyInput(input: string)`:
  - Detect if string contains a URL scheme (`http://`, `https://`) or matches URL patterns.
  - If not a URL: return `{ type: "keyword", query: input }`.
  - If URL:
    - Check hostname against whitelist (`arxiv.org`, `doi.org`, `semanticscholar.org`, etc.).
    - If not in whitelist: return `{ type: "invalid_url", message: "..." }`.
    - If in whitelist:
      - If arXiv URL (`arxiv.org/abs/{id}` or `arxiv.org/pdf/{id}.pdf`): extract clean arXiv ID (e.g. `2404.10981`).
      - If DOI URL (`doi.org/{doi}`): extract DOI string.
      - Return `{ type: "scholarly_url", idType: "arxiv" | "doi", identifier: string }`.
- In `scholarly_search_adapter.py`:
  - When query matches an arXiv ID format (e.g. `\d{4}\.\d{4,5}(v\d+)?`) or DOI format (`10.\d{4,9}/[-._;()/:A-Za-z0-9]+`), query arXiv API using `id_list={id}` for instant direct lookup!

### 3.2 Horizontal Snap Carousel UI (`UnifiedHeroWorkspace.tsx`)
- Container:
  ```tsx
  <div className="relative w-full max-w-5xl mt-3">
    {/* Left Navigation Arrow */}
    {canScrollLeft && (
      <button onClick={() => scrollCarousel("left")} className="absolute left-0 top-1/2 -translate-y-1/2 z-20 w-8 h-8 rounded-full bg-white/90 dark:bg-zinc-800/90 shadow-md flex items-center justify-center ...">
        <ChevronLeft className="w-4 h-4" />
      </button>
    )}
    
    {/* Horizontal Snap Rail */}
    <div ref={carouselRef} className="flex gap-4 overflow-x-auto scrollbar-none snap-x snap-mandatory py-2 px-1">
      {displayedResults.map((paper) => (
        <div key={paper.title} className="w-[340px] sm:w-[380px] shrink-0 snap-start">
          <ScholarlyResultCard paper={paper} onOpenReading={handlePaperClick} />
        </div>
      ))}
    </div>

    {/* Right Navigation Arrow */}
    {canScrollRight && (
      <button onClick={() => scrollCarousel("right")} className="absolute right-0 top-1/2 -translate-y-1/2 z-20 w-8 h-8 rounded-full bg-white/90 dark:bg-zinc-800/90 shadow-md flex items-center justify-center ...">
        <ChevronRight className="w-4 h-4" />
      </button>
    )}
  </div>
  ```
- Outer container in `UnifiedHeroWorkspace.tsx`: remove `overflow-y-auto` from the main flow when showing carousel so no vertical scrollbar ever appears!

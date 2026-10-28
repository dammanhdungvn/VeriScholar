# Design Spec: Untruncated Chunk Context & Citation Ghost Badge Elimination

## Problem Statement
1. **Mid-Word Chunk Context Truncation ("Transfor..."):**
   In `apps/api/src/api/services/session_chat_service.py:2665`, `snippet_content = matched_content[:1000] if matched_content else "(Nội dung trang)"` hard-cuts chunk content at 1000 characters. For paper abstracts or paragraphs exceeding 1000 characters (e.g., Abstract of *Attention Is All You Need* is 1,138 characters), the text fed to the LLM is cut mid-word (`... ure. We show that the Transfor`). As a result, the AI honestly translates up to that word and outputs `[phần văn bản trong tài liệu được cung cấp bị cắt tại đây]`.
2. **Ghost Citation Badges ([13], [7]):**
   In `apps/web/src/components/shared/AcademicMarkdownRenderer.tsx`, regex `\[\^?\d+\]` captures any bracketed number in text. When the AI translates text containing the paper's original bibliography numbers (`[13]`, `[7]`), the renderer wraps them in `<button data-testid="citation-badge">` with orange styling and hover effects, even though `matchedCitation` is `null`. Clicking them does nothing because no RAG citation exists for index 12 or 6.

## Proposed Architecture & Solution

### 1. Backend: Untruncated Chunk Context
- In `session_chat_service.py`, remove `[:1000]`.
- Use the full `matched_content`.
- Chunks in VeriScholar are already constrained by the chunker token limit (~500–1000 tokens) and global token budget (`global_token_budget`). A safety ceiling of 12,000 characters per chunk ensures no single runaway chunk can overflow LLM prompts, while guaranteeing no legitimate academic paragraph or abstract is truncated.

### 2. Frontend: Strict Citation Badge Grounding
- In `AcademicMarkdownRenderer.tsx`:
  - In `parseInlineCitationsAndMath`:
    - Lookup `matchedCitation` in `citations`.
    - If `!matchedCitation`: Return the original text token `part` (e.g. `"[13]"`, `"[7]"`), as a plain text node. DO NOT wrap in a button or citation badge style.
  - In `ReactMarkdown` `code` renderer:
    - Same check: if `!matched`, render as standard code or text, NOT as a citation badge button.
- In `DashboardWorkspace.tsx` and `DashboardChatStreamView.tsx`:
  - Guard `onCitationClick` so that clicks on genuine citations (`matchedCitation`) smoothly scroll and highlight the bounding box.

## Testing Strategy
1. **Backend Unit Test (`test_chunk_context_not_truncated`):**
   - Provide a chunk with >1000 characters (e.g. 1500 chars).
   - Verify that `evidence_blocks[0]["content"]` retains the full 1500 characters and does not cut off at 1000.
2. **Frontend Unit Test (`AcademicMarkdownRenderer.test.tsx`):**
   - Provide content with `[1]` (exists in `citations`) and `[13]`, `[7]` (do not exist in `citations`).
   - Verify that `screen.getAllByTestId("citation-badge")` returns only 1 button (`[1]`).
   - Verify that `[13]` and `[7]` are rendered as plain text within the paragraph.

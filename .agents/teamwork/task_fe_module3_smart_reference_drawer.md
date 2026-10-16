# TASK CONTRACT: Frontend Implementation of Module 3 (PRD §3.3)
# Smart Reference Card Drawer, Session Capacity Guard & Multi-Paper Ingestion

## 1. Context & Objectives
You are the **Senior Frontend Specialist** on VeriScholar.
Module 2 is 100% closed, certified, and committed.
Your mission is to implement the frontend user experience for **Module 3: Multi-Paper Cross Synthesis & Automated Literature Review (PRD §3.3)**.

### Objectives:
1. Create `SmartReferenceDrawer.tsx` (or upgrade `ReferenceListModal.tsx`) conforming 100% to PRD §3.3 specifications.
2. Implement 3-column table:
   - **Column 1 (Checkbox):** Selection checkbox for each item, plus header "Chọn tất cả / Bỏ chọn" checkbox.
   - **Column 2 (Information & Status Badge):**
     - Bold title linking to external publication (opens in new window).
     - Subline with Authors and Publication Year.
     - Status Badge: `[🟢 Đã tìm thấy PDF Open-Access]` (green) if open-access PDF is available; `[🟡 Chỉ có Abstract]` (yellow/amber) if only metadata/abstract is available.
   - **Column 3 (Academic Sources & External Link):**
     - Source badges (arXiv, Crossref, Semantic Scholar, Exa, PubMed) with external link icon `↗`.
3. Implement Footer Actions & Capacity Constraint:
   - `[Hủy / Cancel]`: Closes modal/drawer without action.
   - `[➕ Thêm vào Nghiên cứu / Add to Session]`: Triggers ingestion API.
   - **Session Capacity Constraint Guard (PRD §3.3):**
     - Show current session count: e.g. `Đang mở: ${currentDocCount}/5 bài. Còn trống: ${5 - currentDocCount} bài.`
     - If user selects more than remaining available capacity (`currentDocCount + selectedCount > 5`):
       - Disable `[➕ Thêm vào Nghiên cứu]` button.
       - Display alert / warning banner:
         *"Phiên đọc sâu giới hạn tối đa 5 bài báo. Vui lòng bỏ bớt bài hoặc lưu vào Thư viện (Module 4) để quản lý kho lớn hơn"*.
4. Update `documentsApi.ts` and `sessionsApi.ts`:
   - `documentsApi.resolveReferences(documentId: string): Promise<ResolvedReferenceCard[]>`
   - `sessionsApi.ingestReferences(sessionId: string, documentId: string, refIndices: number[]): Promise<SessionIngestResponse>`
   - `sessionsApi.getCitationGraph(sessionId: string): Promise<CitationGraphData>`
5. Wire up Reader Toolbar and Workspace:
   - Ensure the toolbar button `[📚 Trích xuất Tài liệu Tham khảo]` opens `SmartReferenceDrawer`.
   - When papers are ingested, update `openDocumentIds` and active tab in `DocumentTabBar.tsx`.
6. Write unit tests:
   - `apps/web/src/features/reader/components/SmartReferenceDrawer.test.tsx`
   - Test 3-column rendering, open-access badges, capacity constraint disabling button, and trigger calls.
   - Run `npx vitest run src/features/reader` and `npx tsc -b`.

---

## 2. Technical Specifications & Invariants

### Types (`apps/web/src/types/document.ts` or `apps/web/src/features/reader/types/reference.ts`)
```typescript
export interface ResolvedReferenceCard {
  ref_index: number;
  raw_text: string;
  title: string;
  authors: string[];
  year?: number | null;
  doi?: string | null;
  arxiv_id?: string | null;
  open_access_pdf_url?: string | null;
  abstract?: string | null;
  citation_count?: number | null;
  sources: string[];
  landing_url?: string | null;
  is_ingested?: boolean;
  resolved_document_id?: string | null;
}
```

### Ingestion Response
```typescript
export interface SessionIngestResponse {
  session_id: string;
  ingested_documents: Array<{
    id: string;
    title: string;
    filename: string;
  }>;
  total_documents_in_session: number;
}
```

---

## 3. Execution Instructions
1. Implement the components and APIs cleanly with proper ARIA attributes, semantic markup, and Tailwind CSS.
2. Run `npm test src/features/reader` and `npx tsc -b` to verify 0 errors.
3. Provide full reproduction commands and verification output in your completion summary.

# Design Specification: VeriScholar PRD Modernization & Comprehensive Alignment

- **Document Type:** Technical & Business Analysis Specification
- **Date:** 2026-10-29
- **Status:** Approved by User
- **Target Files:**
  - `docs/PRD/00-overview-and-cleanup.md`
  - `docs/PRD/04-context-table-and-roadmap.md`
  - `docs/PRD/05-favorite-library-and-graphrag.md`
  - `docs/PRD/06-agentic-overleaf-writing.md`

---

## 1. Intent & The Why

VeriScholar has matured from an initial MVP concept into a comprehensive, world-class Academic AI Companion. Through deep-dive brainstorming on the real-world cognitive psychology of researchers (Cognitive Load Theory, Vygotsky's Zone of Proximal Development, and the Modern Information Paradox), critical gaps were identified between the current PRD documents and the system's actual product vision:

1. **`PRD-00` (Overview & Scope):** Only covers 5 surface-level mechanics. It lacks the historical contrast (early research eras vs. modern AI information overload) and the full **9-Pain-Point Lifecycle** (mathematical shock, jumping steps $A \to D$, illusion of competence, theory-to-code gap, PDF graveyard, LaTeX compilation hell, and research gap paralysis).
2. **`PRD-04` (Context Table & Socratic Roadmap):** The current roadmap hint wording is authoritarian (*"Để nắm vững... bạn cần tốt nghiệp..."*), which presumes user incompetence. It must be updated to **Opt-in Non-Intrusive Guidance** (*"Nếu bạn là người mới... hãy tham khảo lộ trình..."*), and enriched with **Mathematical Intuition Explainer** and **Math-to-Tensor Grounding** (bridging formulas to PyTorch tensor shapes).
3. **`PRD-05` (Library & GraphRAG):** Lists 4 entities (`Paper`, `Method`, `Dataset`, `MetricResult`) but lacks the fundamental explanation of why these 4 entities represent the immutable DNA of empirical science. It also lacks **Causal Evolution Lineage** (why prior methods failed, necessitating new ones) and the **Research Gap Extractor** (mining paper limitations for novel thesis topics).
4. **`PRD-06` (Agentic Writing):** Over-indexed on missing bracket errors (only 15% of real failures). It must document the **4 real-world LaTeX error classes** (unescaped special characters, missing packages, table mismatches, syntax brackets) and introduce the **Simulated Peer Reviewer ("Reviewer #2")** to critique scientific claims and statistical evidence prior to submission.

---

## 2. Goals, Non-Goals & Anti-Goals

### 2.1. Goals
- **G1 (PRD-00 Alignment):** Upgrade PRD-00 with the Historical Context & Information Paradox, the 9-Pain-Point Lifecycle, and the 3-Pillar RAG Architecture (Advanced RAG, GraphRAG, Agentic RAG).
- **G2 (PRD-04 Alignment):** Modernize UC-ROAD-03 with Opt-in Non-Intrusive Guidance, Mathematical Intuition Explainer, Math-to-Tensor Grounding, and Active Recall Probes.
- **G3 (PRD-05 Alignment):** Document the 4-Entity DNA of empirical science, Causal Lineage Evolution ($Bậc\ 1 \to 4$), and the Research Gap Extractor from *Limitations & Future Work*.
- **G4 (PRD-06 Alignment):** Expand LaTeX self-healing to the 4 real-world error classes, and document the Simulated Peer Reviewer ("Reviewer #2") for scientific argument auditing.
- **G5 (Strict Markdown Compliance):** Maintain relative Markdown links, radical minimalism (Rule 6), and pass all 4 verification gates.

### 2.2. Non-Goals
- Modifying backend database relational schemas (all database tables already support these features).
- Adding complex multi-tenant billing or organizational hierarchies.

### 2.3. Anti-Goals
- No condescending or judgmental phrasing about user capability.
- No absolute URLs in markdown documentation (`file://...`).

---

## 3. Detailed PRD Modifications

### 3.1. `docs/PRD/00-overview-and-cleanup.md`
- **Add Section 1.2:** "Nghịch lý Thông tin Thời hiện đại & 9 Nỗi đau Vòng đời Học thuật".
  - Detail 9 pain points with quantifiable metrics:
    1. Cú sốc ký hiệu & Rào cản trực giác toán học.
    2. Bẫy học nhảy cóc ($Bậc\ 1 \to 4$ vs. nhảy thẳng vào Bậc 4 như *Attention Is All You Need*).
    3. Đứt gãy dòng tập trung sâu khi tra cứu trích dẫn (15–23 phút mất Deep Flow).
    4. Ảo giác số liệu bảng biểu 2 cột (30%–40% lỗi).
    5. Ảo tưởng năng lực (đọc gật gù nhưng 1 tuần sau quên sạch).
    6. Hố sâu tử thần giữa Toán học và Code (Theory-to-Code gap).
    7. "Nghĩa địa PDF" & 30–50 giờ chép tay ma trận SOTA.
    8. Đứt gãy Đọc sang Viết & Ác mộng biên dịch LaTeX (mất 6–10 giờ).
    9. Tê liệt tìm ý tưởng mới & Điểm mù phản biện.
- **Update Section 1.3:** "Bảng Đối Chiếu Giá Trị Trước & Sau".
- **Update Section 4:** "Bánh Đà Tri Thức Toàn Trình (3 Trụ Cột RAG Hợp Nhất)".

### 3.2. `docs/PRD/04-context-table-and-roadmap.md`
- **Update Section 1 & UC-ROAD-03:**
  - Replace authoritarian prompt with gentle, opt-in scaffolding:
    `"💡 Bài báo bạn đang đọc thuộc Bậc 4 (Kiến trúc Transformer). Nếu bạn là người mới chưa có kiến thức vững vàng thì hãy tham khảo lộ trình dưới đây để hiểu bản chất của paper hơn nha:"`
  - Introduce **Mathematical Intuition Explainer**: Explaining geometric/physical meaning of formulas.
  - Introduce **Math-to-Tensor Grounding**: Mapping mathematical formulas to PyTorch tensor dimensions `[batch, heads, seq, dim]`.
  - Introduce **Active Recall Probes**: Proactive Socratic questions to reinforce retention.

### 3.3. `docs/PRD/05-favorite-library-and-graphrag.md`
- **Update Section 1:**
  - Deep-dive into why the 4 entities (`Paper`, `Method`, `Dataset`, `MetricResult`) are the immutable DNA of scientific papers.
  - Detail why eliminating them reduces the library to a static folder and destroys automated SOTA matrix generation.
- **Add UC-LIB-06:** **Khai Phá Khoảng Trống Nghiên Cứu (Research Gap & Limitations Extractor)**
  - Mining *Limitations & Future Work* across library papers to discover unaddressed research problems for students' theses.
- **Update UC-LIB-05:** **Phổ Hệ Nhân Quả Tri Thức (Causal Evolution Lineage)**
  - Explaining the historical friction/breakthrough between levels ($Bậc\ 1 \to 2 \to 3 \to 4$).

### 3.4. `docs/PRD/06-agentic-overleaf-writing.md`
- **Update UC-WRITE-04:**
  - Expand self-healing to the 4 real-world LaTeX error classes:
    1. Unescaped special characters (`&`, `%`, `_`, `#`).
    2. Missing packages (`amsmath`, `amssymb`, `graphicx`).
    3. Table column alignment mismatches (`\begin{tabular}`).
    4. Mathematical syntax brackets (`$`, `\begin{...}\end{...}`).
- **Add UC-WRITE-06:** **Bộ Giả Lập Phản Biện Hội Đồng (Simulated Peer Reviewer - "Reviewer #2")**
  - Auditing manuscripts for unsupported claims, missing baseline comparisons, and missing statistical p-values.

# Chuẩn hóa Hệ thống Sơ đồ Đồ án theo Kiến trúc Tối giản Học thuật Quốc tế (Minimalist Academic Diagrams) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuẩn hóa triệt để toàn bộ hệ thống sơ đồ TikZ trong báo cáo đồ án tốt nghiệp (`report-datn`) theo chuẩn kiến trúc tối giản của các bài báo khoa học quốc tế đỉnh cao (NeurIPS, ICML, Stanford/DeepMind: Lilian Weng 2023, Reflexion - Shinn et al. 2023, Generative Agents - Park et al. 2023), triệt tiêu hoàn toàn hiện tượng ríu rít, quá tải chữ trong hộp và va chạm mũi tên, đồng thời bảo toàn cấu trúc chuẩn 51 trang và vượt qua 4 cổng xác minh.

**Architecture:** Phương án tối ưu nhất được lựa chọn là **Phương án 1: Tối giản hóa thông tin trong TikZ theo chuẩn Paper Quốc tế (Minimalist Academic TikZ Architecture)** kết hợp nguyên tắc phân tầng trực giao (*Orthogonal Bus & Grid Matrix*). Mỗi nút bấm/hộp chỉ giữ lại hạt nhân khái niệm (tối đa 1–2 dòng), toàn bộ diễn giải chi tiết kỹ thuật được đưa vào lời văn thuyết minh bài báo; khoảng trắng (*whitespace*) đạt $\ge 40\%$, chiều dài mũi tên $\ge 1.5\,\text{cm}$.

**Tech Stack:** XeLaTeX, TikZ, PGF, Python 3.12 (Pytest, Ruff, PyMuPDF/Pillow), React 19 / Vitest.

**Spec:** `AGENTS.md` (Quy chuẩn 7 Liêm chính học thuật, Quy chuẩn 8 Kiến trúc bài báo khoa học chuẩn quốc tế, Quy chuẩn 4 Cổng kiểm thử).

## Global Constraints

- Chiều rộng văn bản khổ A4: `\textwidth = 15.0cm` (426.79pt). Chiều rộng bounding box TikZ sau tỷ lệ (`scale`) tuyệt đối không vượt quá $15.0\,\text{cm}$ để tránh cảnh báo `Overfull \hbox`.
- Số trang toàn bộ bản thảo đồ án tốt nghiệp bắt buộc giữ vững chuẩn **51 trang** (`report-datn/main.pdf`).
- Quy chuẩn liêm chính học thuật (Rule 7): Không đưa tên hàm/biến mã nguồn nội bộ hoặc đường dẫn file vào Chương 2 và Chương 3.
- Mọi bảng biểu tuân thủ $100\%$ định dạng bảng kẻ ô hoàn chỉnh (*Full Grid Table* với đầy đủ viền dọc, ngang và cột STT căn giữa).
- Đồng bộ VPS tự động (Rule 9): Sau mỗi commit, chạy `bash scripts/deploy_to_vps.sh --fast`.

## Review Focus

1. **Hiện tượng chữ quá tải làm phình hộp (*Node Bloating*):** Giới hạn tối đa 2 dòng cho mỗi box trong sơ đồ, tuyệt đối không chèn danh sách gạch đầu dòng 3–4 tầng vào trong hộp.
2. **Hiện tượng mũi tên chạm chữ (*Arrowhead Collision*):** Chiều dài tối thiểu của mũi tên liên kết giữa các hộp phải $\ge 1.2\,\text{cm}$; các nhãn rẽ nhánh (`Đạt chuẩn`, `Không đạt`) phải nằm phía trên thân mũi tên (`above=2pt`), không cắt đứt đường nối.
3. **Va chạm giữa đường phản hồi và nhãn phân vùng (*Band Label Collision*):** Nhãn phân vùng dải màu phải đặt ngoài hành lang lưu thông của các mũi tên hồi quy (ưu tiên lề trái hoặc góc không có luồng dữ liệu).
4. **Bảo toàn số trang 51 trang:** Mọi điều chỉnh co dãn TikZ phải đảm bảo XeLaTeX compile đúng 51 trang, không làm trôi dạt các section sang trang mới.
5. **Đạt 100% Bốn Cổng Xác Minh:** Ruff format check pass, Pytest 118 tests pass, Vitest 72 tests pass, Vite production build pass.

---

### Task 1: Tối giản hóa và Chuẩn hóa Hình 2-4 (LLM-Powered Autonomous Agent)

**Files:**
- Modify: `report-datn/chapters/ch2/2_4_react_agent.tex`
- Test: `tests/test_thesis_structure_and_compile.py`

**Interfaces:**
- Consumes: Cấu trúc 4 trụ cột của Lilian Weng (2023) trong `2_4_react_agent.tex`.
- Produces: Sơ đồ TikZ Hình 2-4 thông thoáng, các khối con tối giản 1-2 dòng, cấu trúc Bus trực giao 100%, mũi tên rơi tự do thông thoáng.

- [ ] **Step 1: Tinh gọn nội dung trong các hộp Hình 2-4 theo chuẩn Paper Quốc tế**
  - Khối Trung tâm: `TÁC NHÂN AI` / `(LLM Agent Brain)`.
  - Khối Bộ nhớ (Top): `BỘ NHỚ (Memory)` rẽ nhánh trực giao sang 2 lá: `Bộ nhớ ngắn hạn (Working Memory)` và `Bộ nhớ dài hạn (Knowledge Memory)`.
  - Khối Công cụ (Left): 4 lá rẽ nhánh từ bus đứng: `Truy xuất tri thức lai`, `Định vị PDF Canvas`, `Hộp cát Firecracker`, `Tìm kiếm học thuật DOI`.
  - Khối Kế hoạch (Right): 4 lá rẽ nhánh từ bus đứng: `Tự phản tư (Reflection)`, `Kiểm định trích dẫn`, `Chuỗi suy luận (CoT)`, `Phân rã mục tiêu`.
  - Khối Hành động (Bottom): `HÀNH ĐỘNG (Action)` rẽ nhánh sang: `Truyền phát câu trả lời` và `Định vị khung viền vàng`.
  - Đảm bảo mỗi khối lá có `minimum width=3.8cm, text width=3.6cm`, tiêu đề không bị ngắt dòng luộm thuộm.

- [ ] **Step 2: Biên dịch và kiểm tra không gian hiển thị**
  Run: `cd report-datn && xelatex -interaction=nonstopmode main.tex`
  Expected: Exit code 0, 0 lỗi `Overfull \hbox`.

- [ ] **Step 3: Trích xuất ảnh trang 23 và kiểm định thị giác**
  Run: `pdftoppm -png -r 150 -f 23 -l 23 report-datn/main.pdf /tmp/task1_p23 && python3 -c "from PIL import Image; im=Image.open('/tmp/task1_p23-23.png'); im.crop((60, 40, im.width-60, 1050)).save('/tmp/task1_crop24.png'); print('Done')"`
  Expected: Không còn bất kỳ điểm tiếp xúc hay va chạm nào giữa mũi tên và chữ.

- [ ] **Step 4: Commit và đồng bộ VPS**
  ```bash
  git add report-datn/chapters/ch2/2_4_react_agent.tex report-datn/main.pdf
  git commit -m "refactor(thesis): standardize Fig 2-4 to minimalist international paper architecture"
  bash scripts/deploy_to_vps.sh --fast
  ```

---

### Task 2: Tối giản hóa và Chuẩn hóa Hình 3-3 (Dual-Band Reflexion Architecture)

**Files:**
- Modify: `report-datn/chapters/ch3/3_3_kien_truc.tex`
- Test: `tests/test_thesis_structure_and_compile.py`

**Interfaces:**
- Consumes: Cấu trúc dải màu ReAct và Reflect của Shinn et al. (2023).
- Produces: Sơ đồ TikZ Hình 3-3 hai dải màu cân đối, nhãn phân vùng không giao cắt với luồng hồi quy đỏ, các mũi tên quyết định rõ ràng.

- [ ] **Step 1: Tối ưu hóa bố cục dải màu và tinh gọn văn bản các nút**
  - Dải 1 (Luồng thực thi ReAct): 5 khối đặt đối xứng tại các tọa độ $x = -6.8, -3.4, 0.0, 3.4, 6.8$ ($\Delta x = 3.4\,\text{cm}$):
    * `Truy vấn Học giả` ($q$)
    * `Lõi Tác nhân AI` (Reasoner)
    * `Gọi Công cụ` ($a_t$)
    * `Môi trường` ($\mathcal{E}$)
    * `Bằng chứng` ($o_t$)
  - Hành lang chuyển giao kết quả: Chiều cao $2.1\,\text{cm}$, đường chuyển giao $o_t$ chạy từ $(6.8, 0.05)$ rẽ trực giao xuống Trạm Kiểm định $(1.8, -1.8)$.
  - Dải 2 (Luồng Phản tư & Kiểm định):
    * Badge `DẢI 2: PHẢN TƯ & KIỂM ĐỊNH` đặt gọn gàng tại góc tây bắc dải màu kết thúc trước $x = -5.0$.
    * Khối `Phản tư Ngôn ngữ` tại $x = -3.4$.
    * Khối `Trạm Kiểm định Liêm chính` tại $x = 1.8$.
    * Khối `Xuất bản Minh chứng` tại $x = 6.8$.
    * Mũi tên đỏ hồi quy phản tư `(refl.north) -- (reasoner.south)` chạy thẳng đứng dọc theo trục $x = -3.4$, hoàn toàn không cắt qua bất kỳ badge hay khung chữ nào.
    * Nhãn `Đạt chuẩn` và `Không đạt` đặt phía trên mũi tên (`above=2pt`).

- [ ] **Step 2: Biên dịch và kiểm tra không gian hiển thị**
  Run: `cd report-datn && xelatex -interaction=nonstopmode main.tex`
  Expected: Exit code 0, 0 lỗi `Overfull \hbox`.

- [ ] **Step 3: Trích xuất ảnh trang 34 và kiểm định thị giác**
  Run: `pdftoppm -png -r 150 -f 34 -l 34 report-datn/main.pdf /tmp/task2_p34 && python3 -c "from PIL import Image; im=Image.open('/tmp/task2_p34-34.png'); im.crop((60, 60, im.width-60, 800)).save('/tmp/task2_crop33.png'); print('Done')"`
  Expected: Đường hồi quy đỏ thẳng tắp, thông thoáng; 2 dải màu sắc nét.

- [ ] **Step 4: Commit và đồng bộ VPS**
  ```bash
  git add report-datn/chapters/ch3/3_3_kien_truc.tex report-datn/main.pdf
  git commit -m "refactor(thesis): clean up Fig 3-3 dual-band reflexion and feedback loop"
  bash scripts/deploy_to_vps.sh --fast
  ```

---

### Task 3: Chuẩn hóa Bố cục và Khoảng thở Hình 3-2 (Phân rã Năng lực VeriScholar)

**Files:**
- Modify: `report-datn/chapters/ch3/3_2_usecase.tex`
- Test: `tests/test_thesis_structure_and_compile.py`

**Interfaces:**
- Consumes: Cấu trúc 3 phân vùng năng lực trong `3_2_usecase.tex`.
- Produces: Sơ đồ phân rã năng lực Hình 3-2 cân đối, căn giữa badge, khoảng cách đều giữa các thẻ con.

- [ ] **Step 1: Căn chỉnh tỷ lệ và khoảng cách thẻ con**
  - Mở rộng card chứa lên $17.2\,\text{cm} \times 14.8\,\text{cm}$ với `scale=0.76`.
  - Khối Retrieval Pipeline ở trên: 5 nút ngang dãn đều với bước nhảy $3.0\,\text{cm}$, mũi tên $0.5\,\text{cm}$.
  - Cột trái (Năng lực Tác nhân): Badge căn giữa `anchor=north`, 4 thẻ con phân bổ đều với khoảng cách `below=13pt` mỗi thẻ.
  - Cột phải (Hạ tầng & Quản trị): Badge căn giữa `anchor=north`, 4 thẻ con phân bổ đều với khoảng cách `below=13pt` mỗi thẻ.
  - Tối giản văn bản phụ trong các thẻ con, tránh dồn ép các thuật ngữ kỹ thuật dài vào một dòng hẹp.

- [ ] **Step 2: Biên dịch và kiểm tra trang 29**
  Run: `cd report-datn && xelatex -interaction=nonstopmode main.tex`
  Expected: Exit code 0, toàn bộ văn bản Section 3.2.3 vừa vặn ở nửa dưới trang 29, không làm tràn Bảng 3-1 sang trang 31.

- [ ] **Step 3: Commit và đồng bộ VPS**
  ```bash
  git add report-datn/chapters/ch3/3_2_usecase.tex report-datn/main.pdf
  git commit -m "refactor(thesis): standardize Fig 3-2 functional capability decomposition card"
  bash scripts/deploy_to_vps.sh --fast
  ```

---

### Task 4: Rà soát Đồng bộ Toàn bộ Các Sơ đồ Còn lại (Hình 2-1, 2-2, 2-3, 3-1, 3-5, 4-1)

**Files:**
- Modify: `report-datn/chapters/ch2/2_1_hexagonal.tex`, `report-datn/chapters/ch2/2_2_hybrid_rag.tex`, `report-datn/chapters/ch3/3_1_khao_sat.tex`
- Test: `tests/test_thesis_structure_and_compile.py`

**Interfaces:**
- Consumes: Toàn bộ mã TikZ các hình vẽ trong luận văn.
- Produces: $100\%$ các hình vẽ trong luận văn đồng nhất về khoảng cách, tỷ lệ bo góc, phông chữ và không có một điểm chạm nét nào.

- [ ] **Step 1: Kiểm tra mũi tên đầu vào Hình 3-1 (AS-IS vs TO-BE)**
  - Tinh chỉnh điểm neo mũi tên từ tiêu đề `QUY TRÌNH VERISCHOLAR (TO-BE)` xuống bước 1 để tạo khoảng hở tối thiểu $3\,\text{mm}$ trước dòng chữ *"1. Khám phá liên hợp"*.
- [ ] **Step 2: Kiểm tra khoảng cách trực giao Hình 2-2 (Hybrid RAG Dataflow)**
  - Xác nhận các đường rẽ nhánh tầng cao ($y = -1.2$) và tầng thấp ($y = -1.8$) giữ nguyên tính vuông góc, không chồng đè lên nhãn PostgreSQL.
- [ ] **Step 3: Biên dịch toàn thể và xác nhận trang chuẩn**
  Run: `cd report-datn && xelatex -interaction=nonstopmode main.tex`
  Expected: Đúng 51 trang, 0 lỗi cảnh báo.

- [ ] **Step 4: Commit và đồng bộ VPS**
  ```bash
  git add report-datn/chapters/ report-datn/main.pdf
  git commit -m "style(thesis): harmonize spacing and arrow anchors across all remaining figures"
  bash scripts/deploy_to_vps.sh --fast
  ```

---

### Task 5: Xác minh Toàn diện 4 Cổng Kiểm thử và Bàn giao

**Files:**
- Test: Toàn bộ test suite dự án (`pytest`, `vitest`, `build`, `ruff`).

- [ ] **Step 1: Chạy Cổng 1 (Python Linter & Formatter)**
  Run: `uv run ruff check . && uv run ruff format --check .`
  Expected: Exit code 0, 100% files passed.

- [ ] **Step 2: Chạy Cổng 2 (Backend & Thesis Unit Tests)**
  Run: `uv run pytest`
  Expected: Exit code 0, 118/118 tests passed.

- [ ] **Step 3: Chạy Cổng 3 (Frontend Unit Tests)**
  Run: `npm --prefix apps/web run test`
  Expected: Exit code 0, 72/72 tests passed.

- [ ] **Step 4: Chạy Cổng 4 (Frontend Production Build)**
  Run: `npm --prefix apps/web run build`
  Expected: Exit code 0, bundle built successfully.

- [ ] **Step 5: Kiểm tra trực quan 100% hình ảnh trên PDF cuối cùng**
  - Trích xuất ảnh toàn bộ 8 hình vẽ từ `main.pdf` và xác nhận sạch sẽ từng chi tiết.
- [ ] **Step 6: Triển khai đồng bộ lên VPS môi trường thực tế**
  Run: `bash scripts/deploy_to_vps.sh --fast`
  Expected: Deployment Successful lên `https://verischolar.duckdns.org`.

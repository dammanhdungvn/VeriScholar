# Kế Hoạch Thực Hiện: Tái Cấu Trúc Thị Giác Sơ Đồ TikZ & Chuẩn Hóa Bố Cục Trang In Luận Văn A4 (A4 Print-Proof Radical Polish)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tái cấu trúc toàn diện 8 sơ đồ TikZ và bố cục trang Đề cương ĐATN để triệt tiêu 100% lỗi chồng đè, cắt xén chữ, khoảng trắng trang vô lý và bảo đảm phông chữ in ấn A4 sắc nét ($\ge 7{,}5\text{--}8\,\text{pt}$) cho hội đồng chấm đồ án.

**Architecture:** Tiếp cận theo phương pháp tách phân trang độc lập cho các biểu đồ tuần tự phức tạp, áp dụng tinh thần tối giản 80/20 cho biểu đồ lớp thực thể miền, nới rộng bounding box và khoảng cách tọa độ TikZ để loại bỏ hoàn toàn clipping, đồng thời tinh chỉnh khoảng cách dòng để tối ưu hóa không gian trang văn bản hành chính.

**Tech Stack:** XeLaTeX, TikZ, PGF/TikZ libraries (`arrows.meta`, `positioning`, `shapes.geometric`, `calc`), Poppler Utilities (`pdftoppm`), Python 3.12, FastAPI, React 19.

**Spec:** [`docs/superpowers/specs/2026-11-03-thesis-visual-and-diagram-polish-design.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/superpowers/specs/2026-11-03-thesis-visual-and-diagram-polish-design.md)

---

## Global Constraints

- **Quy tắc lề và khổ in:** Khổ giấy A4 đứng tiêu chuẩn HUMG, chiều rộng in ấn tối đa $15{,}5\,\text{cm}$.
- **Quy tắc cỡ chữ in ấn tối thiểu:** Tuyệt đối cấm scale hình vẽ dưới $0{,}70$. Mọi nhãn chữ trong TikZ sau khi scale phải đạt cỡ chữ thực tế $\ge 7{,}5\,\text{pt}$ trên giấy in A4.
- **Quy tắc độc lập phân trang:** Không dồn ép 2 biểu đồ tuần tự nhiều bước vào chung 1 trang giấy; mỗi biểu đồ tuần tự phải đứng riêng 1 trang với `\clearpage`.
- **Quy chuẩn Markdown & Liên kết tương đối:** Giữ nguyên các nhãn tham chiếu chéo `\ref{fig:...}` trong toàn bộ tài liệu.
- **Bốn Cổng Xác Minh Bắt Buộc:** Trước khi kết thúc kế hoạch, bắt buộc 100% exit code 0 cho `ruff`, `pytest`, `npm test`, `npm build`.
- **Đồng bộ VPS tự động:** Sau mỗi commit thành công, chạy `bash scripts/deploy_to_vps.sh --fast`.

---

## Review Focus

1. **Lỗi tràn chữ / cắt mép (Text Clipping):** Tiêu đề `LÕI MIỀN NGHIỆP VỤ THUẦN KHIẾT (packages/core)` trong Hình 3-2 và chuỗi `Deduplication CAS SHA-256` không được chạm hoặc bị viền khung cắt mất ký tự.
2. **Lỗi chồng đè hình oval (Overlapping Ellipses):** 5 hình oval Use Case con trong Hình 3-5 phải có khoảng cách rời nhau tối thiểu $0{,}2\,\text{cm}$, không được vẽ lồng viền lên nhau.
3. **Lỗi chữ nhỏ li ti (Unreadable 4pt Text):** Tất cả 4 biểu đồ tuần tự (Hình 3-8 đến 3-11) và biểu đồ lớp (Hình 3-12) phải dùng `scale >= 0.75` và phông chữ $\ge \text{\scriptsize}$ để đọc được bằng mắt thường khi in A4.
4. **Lỗi khoảng trắng đề cương (Page "v" Orphan Whitespace):** Chân trang "v" phải chứa trọn vẹn tiêu đề `3. Mục tiêu của đề tài` và tiểu mục `-- Mục tiêu tổng quát:`, không để lại khoảng trống thừa.
5. **Độ ổn định biên dịch XeLaTeX:** Biên dịch tài liệu không phát sinh lỗi nghiêm trọng và số trang tổng thể được duy trì cân đối.

---

## Task 1: Chuẩn hóa trang mở đầu Đề cương ĐATN (Trang "v")

**Files:**
- Modify: `report-datn/frontmatter/de_cuong_datn.tex:60-140`
- Test: `scripts/verify_thesis_format.py`

**Interfaces:**
- Consumes: Bố cục Đề cương ĐATN 3 trang quy định bởi HUMG.
- Produces: Trang "v" hiển thị liền mạch không khoảng trắng thừa, kéo Mục 3 lên trang 1 của đề cương.

- [ ] **Step 1: Viết test kiểm tra bố cục trang "v"**
  - Chạy lệnh kiểm tra render trang v và vi hiện tại ra file PNG để làm mốc đối chứng:
  ```bash
  pdftoppm -png -r 150 -f 5 -l 6 report-datn/main.pdf /tmp/test_task1_before
  ```
  - Xác nhận có khoảng trắng lớn ở chân trang 5 (trang v).

- [ ] **Step 2: Chỉnh sửa `de_cuong_datn.tex`**
  - Giảm `\arraystretch` bảng cán bộ từ `1.12` xuống `1.05`.
  - Giảm khoảng cách `\vspace` giữa mục 1 và mục 2 từ `0.10cm` xuống `0.05cm`.
  - Đưa `\noindent \textbf{3. Mục tiêu của đề tài}` và `\noindent \textbf{-- Mục tiêu tổng quát:}` cùng 3 gạch đầu dòng lên trang "v".
  - Đặt `\newpage \thispagestyle{adminform}` ngay trước `\noindent \textbf{-- Về sản phẩm:}` để trang "vi" chứa trọn vẹn Về sản phẩm, Về kiến thức và Mục 4 Các nhiệm vụ cụ thể.

- [ ] **Step 3: Biên dịch và kiểm tra thị giác trang "v"**
  - Chạy biên dịch XeLaTeX:
  ```bash
  latexmk -xelatex -interaction=nonstopmode -output-directory=report-datn report-datn/main.tex
  pdftoppm -png -r 150 -f 5 -l 6 report-datn/main.pdf /tmp/test_task1_after
  ```
  - Xác nhận trang v được lấp đầy cân đối, không còn khoảng trống thừa.

- [ ] **Step 4: Commit và đồng bộ VPS**
  ```bash
  git add report-datn/frontmatter/de_cuong_datn.tex
  git commit -m "style(thesis): eliminate orphan whitespace on page v of proposal"
  bash scripts/deploy_to_vps.sh --fast
  ```

---

## Task 2: Tái cấu trúc thị giác Hình 2-1 (RRF) & Hình 2-4 (ReAct E2B)

**Files:**
- Modify: `report-datn/chapters/ch2/2_2_hybrid_rag.tex:85-165` (Hình 2-1)
- Modify: `report-datn/chapters/ch2/2_5_agentic_react.tex:55-130` (Hình 2-4)

**Interfaces:**
- Consumes: Thuật toán RRF $k=60$ và chu trình ReAct Reflexion trong sandbox E2B.
- Produces: Hình 2-1 và Hình 2-4 đạt chuẩn A4, loại bỏ 100% chồng đè văn bản và dính viền.

- [ ] **Step 1: Viết test đối chứng trực quan trước khi sửa**
  - Render các trang chứa Hình 2-1 và Hình 2-4 ra ảnh PNG đối chứng.

- [ ] **Step 2: Cập nhật mã nguồn TikZ Hình 2-1 (`2_2_hybrid_rag.tex`)**
  - Tách tiêu đề phụ cách tiêu đề chính tối thiểu $0{,}45\,\text{cm}$.
  - Đặt nhãn `Nhúng Vector` và `Tách từ khóa` tại `above left` và `above right` của đường rẽ nhánh, có `fill=white, inner sep=2pt`.
  - Mở rộng khối RRF Scores Engine ra $14{,}2\,\text{cm}$, nâng công thức lên font `\small`.
  - Nâng `scale=0.72, transform shape`.

- [ ] **Step 3: Cập nhật mã nguồn TikZ Hình 2-4 (`2_5_agentic_react.tex`)**
  - Mở rộng bán kính uốn cung của mũi tên đỏ phản hồi sang trái ($x = -0{,}6\,\text{cm}$), nhãn `Phản hồi vòng lặp sửa cú pháp` đặt riêng với `fill=white`.
  - Dời nhãn `No (Lỗi)` ra phía ngoài đỉnh trái hình thoi $0{,}2\,\text{cm}$; nhãn `Yes (Exit 0)` đặt cách đáy hình thoi $0{,}3\,\text{cm}$.
  - Nâng `scale=0.75, transform shape`, tăng font các khối lên `\small`.

- [ ] **Step 4: Biên dịch và kiểm tra xác nhận**
  - Chạy `latexmk -xelatex -output-directory=report-datn report-datn/main.tex`.
  - Render kiểm tra ảnh kết quả, xác nhận 0 lỗi đè chữ.

- [ ] **Step 5: Commit và đồng bộ VPS**
  ```bash
  git add report-datn/chapters/ch2/2_2_hybrid_rag.tex report-datn/chapters/ch2/2_5_agentic_react.tex
  git commit -m "style(thesis): eliminate text overlaps in fig 2-1 and fig 2-4"
  bash scripts/deploy_to_vps.sh --fast
  ```

---

## Task 3: Tái cấu trúc thị giác Hình 3-1 (AS-IS vs TO-BE) & Hình 3-2 (Kiến trúc Lục giác)

**Files:**
- Modify: `report-datn/chapters/ch3/3_1_mo_hinh_as_is_to_be.tex:15-85` (Hình 3-1)
- Modify: `report-datn/chapters/ch3/3_2_kien_truc_tong_the.tex:20-110` (Hình 3-2)

**Interfaces:**
- Consumes: Mô hình đối chiếu AS-IS/TO-BE và Kiến trúc Lục giác 4 Không gian nghiên cứu.
- Produces: Hình 3-1 và Hình 3-2 sắc nét, triệt tiêu 100% lỗi clipping tiêu đề và chữ li ti.

- [ ] **Step 1: Cập nhật mã nguồn TikZ Hình 3-1 (`3_1_mo_hinh_as_is_to_be.tex`)**
  - Mở rộng chiều rộng hộp AS-IS và TO-BE ra $6{,}2\,\text{cm}$.
  - Thay 4 nhãn nét đứt trung tâm bằng các badge bo tròn `draw=teal!80, fill=teal!10, font=\scriptsize\bfseries`, kích thước $2{,}2\,\text{cm} \times 0{,}6\,\text{cm}$.
  - Nâng `scale=0.78, transform shape`, nâng font nội dung lên `\footnotesize`.

- [ ] **Step 2: Cập nhật mã nguồn TikZ Hình 3-2 (`3_2_kien_truc_tong_the.tex`)**
  - Mở rộng bounding box đỉnh khung lõi miền thêm $0{,}7\,\text{cm}$.
  - Đặt tiêu đề `LÕI MIỀN NGHIỆP VỤ THUẦN KHIẾT (packages/core)` hoàn toàn bên trong khung viền xanh, căn giữa tuyệt đối, không chạm viền trên hay viền hông.
  - Nới rộng hộp Discovery Space để hiển thị trọn vẹn chuỗi `Deduplication CAS SHA-256`.
  - Đặt hai huy hiệu `Driving (Primary)` và `Driven (Secondary)` cách đỉnh ngoài $0{,}3\,\text{cm}$.
  - Nâng `scale=0.76, transform shape`.

- [ ] **Step 3: Biên dịch và kiểm tra xác nhận**
  - Biên dịch XeLaTeX và render trang chứa Hình 3-1 và Hình 3-2.
  - Xác nhận không còn bị cắt chữ `L` hoặc `packages/core`.

- [ ] **Step 4: Commit và đồng bộ VPS**
  ```bash
  git add report-datn/chapters/ch3/3_1_mo_hinh_as_is_to_be.tex report-datn/chapters/ch3/3_2_kien_truc_tong_the.tex
  git commit -m "style(thesis): fix clipping and enlarge tokens in fig 3-1 and fig 3-2"
  bash scripts/deploy_to_vps.sh --fast
  ```

---

## Task 4: Tái cấu trúc thị giác Hình 3-5 (Use Case con Đọc sâu)

**Files:**
- Modify: `report-datn/chapters/ch3/3_4_phan_tich_usecase.tex:160-230`

**Interfaces:**
- Consumes: Đặc tả Use Case con "Hỏi đáp đọc sâu và kiểm chứng trích dẫn tọa độ".
- Produces: Hình 3-5 chuẩn UML, 5 oval Use Case con tách biệt hoàn toàn không đè viền.

- [ ] **Step 1: Cập nhật mã nguồn TikZ Hình 3-5**
  - Đưa nhãn tiêu đề `PHÂN HỆ ĐỌC SÂU VÀ KIỂM CHỨNG TRÍCH DẪN` lên phía trên đường viền nét đứt hoặc đặt trong hộp nhãn có viền và nền che nét đứt.
  - Đặt khoảng cách trục $y$ giữa các tâm oval Use Case con là $1{,}3\,\text{cm}$ (tọa độ $y = 1.95, 0.65, -0.65, -1.95, -3.25$).
  - Đặt bán kính oval cố định: `x radius = 2.35cm`, `y radius = 0.50cm` $\rightarrow$ khoảng cách khe hở giữa 2 oval liền kề luôn đạt $\ge 0{,}30\,\text{cm}$.
  - Căn chỉnh các mũi tên `<<include>>` và `<<extend>>` tỏa đều từ Use Case chính sang các oval con, nhãn đặt tại trung điểm với `fill=white, inner sep=1.5pt`.
  - Nâng `scale=0.78, transform shape`.

- [ ] **Step 2: Biên dịch và kiểm tra trực quan**
  - Biên dịch XeLaTeX và render trang chứa Hình 3-5.
  - Xác nhận 5 oval hoàn toàn tách rời, tiêu đề khung rõ ràng.

- [ ] **Step 3: Commit và đồng bộ VPS**
  ```bash
  git add report-datn/chapters/ch3/3_4_phan_tich_usecase.tex
  git commit -m "style(thesis): eliminate ellipse overlaps in fig 3-5 use case diagram"
  bash scripts/deploy_to_vps.sh --fast
  ```

---

## Task 5: Tái cấu trúc 4 Biểu đồ tuần tự (Hình 3-8 $\rightarrow$ 3-11) chuẩn in A4

**Files:**
- Modify: `report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex`

**Interfaces:**
- Consumes: Quy trình phối hợp 4 Use Case tương ứng 4 Không gian nghiên cứu.
- Produces: 4 biểu đồ tuần tự độc lập mỗi hình 1 trang, cỡ chữ in A4 to rõ nét $\ge 8\,\text{pt}$.

- [ ] **Step 1: Thiết lập cấu trúc phân trang độc lập**
  - Chèn `\clearpage` trước tiểu mục Hình 3-9, Hình 3-10, Hình 3-11.
  - Bảo đảm mỗi Use Case có đoạn mở đầu ngắn và 1 biểu đồ tuần tự trọn vẹn trên 1 trang giấy.

- [ ] **Step 2: Cập nhật thông số kích thước và phông chữ**
  - Đổi hệ số scale toàn bộ 4 biểu đồ từ `0.60` lên **`scale=0.80, transform shape`**.
  - Đổi font nhãn thông điệp `lbl/.style` từ `\scriptsize` lên **`\footnotesize`**.
  - Đổi font thực thể `entity/.style` thành `\small\bfseries`.
  - Mở rộng khoảng cách lifelines: các cột $x = 0, 3.7, 7.4, 11.1, 14.8\,\text{cm}$.
  - Giãn khoảng cách các bước thông điệp theo trục $y$ từ $0{,}6\,\text{cm} \rightarrow 0{,}85\,\text{cm}$.
  - Nới rộng khung điều kiện `opt`, `loop`, `alt` để nhãn khung không đè lên đường lifelines.

- [ ] **Step 3: Biên dịch và kiểm tra trực quan 4 trang biểu đồ**
  - Biên dịch XeLaTeX và render 4 trang liên tiếp chứa Hình 3-8, 3-9, 3-10, 3-11.
  - Xác nhận chữ to rõ, khoảng cách thoáng đãng, đạt chuẩn in ấn A4.

- [ ] **Step 4: Commit và đồng bộ VPS**
  ```bash
  git add report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex
  git commit -m "style(thesis): enlarge sequence diagrams to scale 0.80 for a4 readability"
  bash scripts/deploy_to_vps.sh --fast
  ```

---

## Task 6: Tinh gọn 80/20 Biểu đồ lớp miền Hình 3-12 (Class Diagram) & Định tuyến trực giao

**Files:**
- Modify: `report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex:14-180`

**Interfaces:**
- Consumes: Danh mục thực thể miền thuần khiết (Domain POPO Entities).
- Produces: Hình 3-12 tinh gọn chuẩn 80/20, các đường liên kết trực giao vuông góc không cắt chéo, chữ in rõ nét.

- [ ] **Step 1: Tinh gọn danh sách thuộc tính và phương thức các lớp**
  - Thu gọn mỗi lớp chỉ giữ $3\text{--}4$ trường dữ liệu cốt lõi và $1\text{--}2$ phương thức nghiệp vụ đại diện (loại bỏ các hàm phụ như `link_orcid`, `update_title`, `is_valid` v.v.).
  - Giảm chiều cao các hộp lớp từ $\approx 3\,\text{cm} \rightarrow 1{,}8\text{--}2{,}2\,\text{cm}$.

- [ ] **Step 2: Định tuyến lại các đường quan hệ theo lưới trực giao**
  - Dùng cú pháp `|-` và `-|` để nối các đường quan hệ giữa User, ScholarProfile, Document, SessionTurn.
  - Triệt tiêu 100% các đường cắt chéo qua thân lớp khác.

- [ ] **Step 3: Nâng tỉ lệ scale và phông chữ**
  - Đổi `scale=0.57` thành **`scale=0.75, transform shape`**.
  - Đổi phông chữ thuộc tính từ `\tiny` lên **`\scriptsize`**.
  - Đổi phông tên lớp thành `\small\bfseries`.

- [ ] **Step 4: Biên dịch và kiểm tra trực quan**
  - Biên dịch XeLaTeX và render trang chứa Hình 3-12.
  - Xác nhận chữ rõ nét, sơ đồ thoáng đãng, các đường liên kết chuẩn mực UML.

- [ ] **Step 5: Commit và đồng bộ VPS**
  ```bash
  git add report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex
  git commit -m "style(thesis): streamline domain class diagram with 80-20 rule and orthogonal routing"
  bash scripts/deploy_to_vps.sh --fast
  ```

---

## Task 7: Bốn Cổng Xác Minh Toàn Diện & Đồng Bộ VPS Tự Động

**Files:**
- Test: Toàn bộ test suite backend, frontend và kiểm tra định dạng luận văn.

**Interfaces:**
- Consumes: Toàn bộ mã nguồn và báo cáo sau khi hoàn thành Task 1 đến Task 6.
- Produces: 100% exit code 0 cho 4 Verification Gates và triển khai hoàn tất lên VPS.

- [ ] **Step 1: Chạy Cổng 1 - Linter & Formatter Python**
  ```bash
  uv run ruff check . && uv run ruff format --check .
  ```
  Xác nhận: Exit code 0.

- [ ] **Step 2: Chạy Cổng 2 - Backend & Boundary Tests**
  ```bash
  uv run pytest
  ```
  Xác nhận: 363/363 tests passed.

- [ ] **Step 3: Chạy Cổng 3 - Frontend Unit Tests**
  ```bash
  npm --prefix apps/web run test
  ```
  Xác nhận: 240/240 tests passed.

- [ ] **Step 4: Chạy Cổng 4 - Production Build Giao Diện**
  ```bash
  npm --prefix apps/web run build
  ```
  Xác nhận: Build thành công không có cảnh báo nghiêm trọng.

- [ ] **Step 5: Chạy kiểm tra quy chuẩn luận văn**
  ```bash
  python3 scripts/verify_thesis_format.py
  ```
  Xác nhận: Format và số lượng hình/bảng hợp lệ 100%.

- [ ] **Step 6: Đồng bộ VPS và tạo commit tổng kết**
  ```bash
  bash scripts/deploy_to_vps.sh --fast
  ```

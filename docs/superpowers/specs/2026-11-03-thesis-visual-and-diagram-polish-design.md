# Thiết Kế Chi Tiết: Tái Cấu Trúc Thị Giác Sơ Đồ TikZ & Chuẩn Hóa Bố Cục Trang In Luận Văn A4 (A4 Print-Proof Radical Polish)

**Mã tài liệu:** `SPEC-2026-11-03-THESIS-VISUAL-POLISH`  
**Dự án:** Luận văn tốt nghiệp VeriScholar — Đại học Mỏ - Địa chất (HUMG)  
**Tác giả:** VeriScholar Core Team & Google Antigravity Agent  
**Ngày lập:** 03/11/2026  
**Trạng thái:** Chờ phê duyệt (Pending Approval)

---

## 1. Bối Cảnh & Mục Đích (Intent & The Why)

Trong quá trình chuẩn bị in ấn luận văn tốt nghiệp phục vụ hội đồng chấm đồ án, việc in màu hoặc photocopy hai mặt trên khổ giấy tiêu chuẩn **A4** đặt ra yêu cầu khắt khe về độ phân giải, tỉ lệ kích thước phông chữ và bố cục trang. 

Qua kiểm tra rà soát trực quan trên bản in thử nghiệm PDF và ảnh chụp trang thực tế, một loạt các sơ đồ kiến trúc TikZ và trang văn bản hành chính đang gặp các khiếm khuyết thị giác nghiêm trọng:
1. **Chữ quá nhỏ khi in A4 ($3{,}4\text{--}4{,}8\,\text{pt}$)** do lạm dụng lệnh `scale=0.57` hoặc `scale=0.60` kèm `transform shape`, khiến người đọc và hội đồng chấm thi không thể đọc được nội dung các thông điệp tuần tự và thuộc tính lớp.
2. **Chồng đè văn bản và viền hình học (Overlapping & Clipping)**: Phụ đề đè lên tiêu đề (Hình 2-1), tiêu đề bị xén mép (Hình 3-2), viền nét đứt cắt ngang tiêu đề phân hệ (Hình 3-5), và các hình oval Use Case con bị vẽ lồng đè lên nhau.
3. **Khoảng trắng vô lý ở trang mở đầu đề cương (Trang "v")**: Mục "3. Mục tiêu của đề tài" bị rớt sang trang sau, để lại khoảng trống lớn $1/3$ trang.

Tài liệu thiết kế này quy định chi tiết giải pháp tái cấu trúc thị giác toàn diện, bảo đảm mọi sơ đồ khi xuất bản PDF và in ấn A4 đều hiển thị sắc nét, chữ rõ ràng ($\ge 7{,}5\text{--}8{,}5\,\text{pt}$ hiệu dụng), không có hiện tượng chồng đè hay cắt xén.

---

## 2. Mục Tiêu, Phi Mục Tiêu & Chống Mục Tiêu (Goals, Non-Goals, Anti-Goals)

### 2.1. Mục Tiêu (Goals)
- **G1 (Đề cương ĐATN - Trang "v"):** Tinh chỉnh khoảng cách dọc (`\vspace`, padding bảng cán bộ) để đưa tiêu đề "3. Mục tiêu của đề tài" và tiểu mục "-- Mục tiêu tổng quát:" lên trang "v", lấp đầy khoảng trắng và bảo đảm cấu trúc đề cương 3 trang (v, vi, vii) liền mạch, chuẩn chỉnh.
- **G2 (Hình 2-1 RRF & Hình 2-4 ReAct E2B):** Loại bỏ 100% chồng đè văn bản; mở rộng bề ngang khối RRF Scores Engine tận dụng khổ A4 ($14\,\text{cm}$); tách biệt nhãn Yes/No và mũi tên vòng lặp phản hồi.
- **G3 (Hình 3-1 AS-IS vs TO-BE & Hình 3-2 Kiến trúc Lục giác):** Mở rộng bounding box an toàn, triệt tiêu 100% lỗi clipping tiêu đề "LÕI MIỀN NGHIỆP VỤ THUẦN KHIẾT (packages/core)"; hiển thị trọn vẹn "SHA-256"; làm rõ 4 badge chuyển đổi trung tâm.
- **G4 (Hình 3-5 Use Case con Đọc sâu):** Giãn khoảng cách trục dọc giữa các oval con (tối thiểu $1{,}3\,\text{cm}$); loại bỏ hoàn toàn việc chồng đè thân oval; nâng tiêu đề phân hệ lên phía trên đường nét đứt.
- **G5 (Hình 3-8, 3-9, 3-10, 3-11 - 4 Biểu đồ tuần tự):** Tách mỗi biểu đồ chiếm trọn 1 trang độc lập (không dồn 2 hình vào 1 trang); nâng `scale` từ $0{,}60$ lên **$0{,}78\text{--}0{,}82$**; nâng font thông điệp lên `\footnotesize` (đạt cỡ chữ thực tế $\approx 8\,\text{pt}$ khi in A4).
- **G6 (Hình 3-12 - Biểu đồ lớp Class Diagram):** Áp dụng triệt để nguyên tắc 80/20, rút gọn mỗi lớp chỉ giữ $3\text{--}4$ thuộc tính đặc trưng và $1\text{--}2$ nghiệp vụ chính; định tuyến lại liên kết trực giao (orthogonal) không cắt chéo; nâng `scale` lên **$0{,}75$**, font $\ge 7{,}5\,\text{pt}$ in ấn rõ nét.
- **G7 (Bốn cổng kiểm tra chất lượng):** Giữ vững 100% exit code 0 cho 4 Verification Gates và CI workflow.

### 2.2. Phi Mục Tiêu (Non-Goals)
- Không vẽ lại sơ đồ ERD vật lý chi tiết 20 bảng (đã thống nhất bỏ sơ đồ ERD ở đợt tinh gọn trước và dùng bảng dữ liệu chuẩn).
- Không thay đổi logic ngữ nghĩa hay các thông số thuật toán (RRF $k=60$, IoU $\ge 0{,}85$, Louvain, E2B MicroVM).

### 2.3. Chống Mục Tiêu (Anti-Goals)
- **Tuyệt đối cấm scale hình xuống dưới $0{,}70$:** Không được vì lười chỉnh tọa độ mà dùng `scale=0.5x` làm chữ bị thu nhỏ như nhãn thuốc.
- **Không nhồi nhét 2 sơ đồ tuần tự phức tạp vào chung 1 trang giấy A4:** Việc dồn trang làm nát bố cục thị giác.

---

## 3. Ràng Buộc Kỹ Thuật (Constraints)
1. **Khổ giấy & Lề in ấn:** Khổ A4 đứng (`portrait`), lề trái $3{,}0\,\text{cm}$, lề phải $2{,}0\,\text{cm}$, lề trên $2{,}5\,\text{cm}$, lề dưới $2{,}5\,\text{cm}$. Chiều rộng vùng in khả dụng: $\approx 15{,}5\text{--}16{,}0\,\text{cm}$.
2. **Công cụ biên dịch LaTeX:** XeLaTeX + TikZ + PGF/TikZ libraries (`arrows.meta`, `positioning`, `shapes.geometric`, `calc`).
3. **Quy chuẩn Markdown & Báo cáo:** Tuân thủ quy chuẩn số hiệu hình vẽ và tham chiếu chéo `\ref{fig:...}` trong `main.tex`.

---

## 4. Các Phương Án Đã Cân Nhắc (Approaches Considered)

### Phương án A: Tối ưu hóa tọa độ TikZ & Tinh gọn 80/20 cho khổ A4 đứng (Phương án được chọn)
- **Cách làm:** 
  - Tách mỗi biểu đồ tuần tự sang một trang riêng, tận dụng chiều cao và mở rộng chiều ngang ra $14\text{--}15\,\text{cm}$, nâng scale lên $0{,}78\text{--}0{,}82$.
  - Tinh gọn Class Diagram theo chuẩn 80/20, giảm bớt thuộc tính thừa, nâng scale lên $0{,}75$.
  - Sửa lại tọa độ offset, padding và vị trí các nhãn trong Hình 2-1, 2-4, 3-1, 3-2, 3-5.
  - Tinh chỉnh vspace trang "v" để kéo Mục 3 lên trang 1 của đề cương.
- **Ưu điểm:** Giữ nguyên hướng trang đứng (`portrait`) đồng bộ của toàn bộ luận văn; khi photo màu hay đóng bìa đều thuận mắt, dễ đọc, chữ đạt chuẩn $\ge 8\,\text{pt}$.
- **Nhược điểm:** Cần tính toán lại tọa độ $y$ của các bước thông điệp trong TikZ một cách tỉ mỉ.

### Phương án B: Chuyển các sơ đồ sang khổ ngang (Landscape)
- **Cách làm:** Dùng môi trường `pdflscape` để xoay ngang trang chứa sơ đồ tuần tự và Class Diagram.
- **Ưu điểm:** Chiều ngang rất rộng ($25\,\text{cm}$), không cần tinh gọn nội dung.
- **Nhược điểm:** Khi in đóng quyển luận văn, người đọc phải xoay ngược quyển sách $90^\circ$ liên tục qua 4-5 trang; phá vỡ tính liền mạch của tài liệu học thuật tiêu chuẩn HUMG.

> **Kết luận lựa chọn:** Người dùng đã phê duyệt **Phương án A**.

---

## 5. Đặc Tả Kỹ Thuật Chi Tiết Cho Từng Thành Phần

### 5.1. Trang "v" (Đề cương ĐATN - `report-datn/frontmatter/de_cuong_datn.tex`)
- Giảm `\vspace{0.08cm}` và `\vspace{0.10cm}` giữa các mục 1, 2.
- Điều chỉnh bảng thông tin cán bộ hướng dẫn: `\renewcommand{\arraystretch}{1.05}`.
- Đẩy tiêu đề `\noindent \textbf{3. Mục tiêu của đề tài}` và `\noindent \textbf{-- Mục tiêu tổng quát:}` (3 mục) hiển thị trọn vẹn ở chân trang "v".
- Đặt `\newpage` hợp lý để trang "vi" bắt đầu bằng `\noindent \textbf{-- Về sản phẩm:}`, theo sau là `\noindent \textbf{-- Về kiến thức và kỹ năng:}` và `\noindent \textbf{4. Các nhiệm vụ cụ thể}`.
- Kết quả: Đề cương ĐATN chuẩn mực 3 trang (v, vi, vii), không còn khoảng trống thừa.

### 5.2. Hình 2-1: Cơ chế tìm kiếm lai RRF (`report-datn/chapters/ch2/2_2_hybrid_rag.tex`)
- Tách node phụ đề `Không gian tìm kiếm song song bổ trợ ngữ nghĩa và từ khóa`: Tăng khoảng cách $y$ giữa tiêu đề chính và phụ đề tối thiểu $0{,}45\,\text{cm}$.
- Nhãn `Nhúng Vector` và `Tách từ khóa`: Đặt tại `above left=1pt` và `above right=1pt` với `fill=white, inner sep=2pt, rounded corners=1pt`.
- Khối RRF Scores Engine: Mở rộng chiều ngang ra $14{,}2\,\text{cm}$, nâng font công thức $\frac{1}{60+r}$ lên `\small`.
- Nâng hệ số scale từ `0.60` lên **`0.72`**.

### 5.3. Hình 2-4: Chu trình ReAct E2B (`report-datn/chapters/ch2/2_5_agentic_react.tex`)
- Mũi tên cong đỏ phản hồi bên trái: Mở rộng cung uốn sang trái ($x = -0{,}6\,\text{cm}$), nhãn chữ đặt bên trái mũi tên với `fill=white`.
- Hình thoi điều kiện `Biên dịch thành công?`: Nhãn `No (Lỗi)` đặt phía trên đường rẽ trái $0{,}2\,\text{cm}$; nhãn `Yes (Exit 0)` đặt bên dưới đáy thoi $0{,}3\,\text{cm}$.
- Nâng hệ số scale từ `0.62` lên **`0.75`**, tăng font mô tả microVM lên `\small`.

### 5.4. Hình 3-1: Mô hình AS-IS vs TO-BE (`report-datn/chapters/ch3/3_1_mo_hinh_as_is_to_be.tex`)
- Mở rộng chiều rộng các hộp AS-IS và TO-BE: từ $5{,}4\,\text{cm} \rightarrow 6{,}2\,\text{cm}$.
- 4 badge trung tâm (`Deduplication`, `Minh chứng`, `Tự động`, `Tự sửa`): Đổi thành hình elip/chữ nhật bo tròn viền đậm `draw=teal!80, fill=teal!10`, font `\scriptsize\bfseries`, kích thước vừa vặn dễ đọc.
- Nâng font mô tả trong hộp lên `\footnotesize`, nâng scale lên **`0.78`**.

### 5.5. Hình 3-2: Kiến trúc Lục giác (`report-datn/chapters/ch3/3_2_kien_truc_tong_the.tex`)
- Bổ sung padding đỉnh: Mở rộng khung viền bao quanh thêm $0{,}7\,\text{cm}$ ở đỉnh.
- Tiêu đề `LÕI MIỀN NGHIỆP VỤ THUẦN KHIẾT (packages/core)`: Đặt thụt vào trong khung, căn giữa tuyệt đối, không chạm lề trên hay lề hông.
- Hộp Discovery Space: Nới rộng bề ngang để chuỗi `Deduplication CAS SHA-256` hiển thị trọn vẹn, không bị mất số 6.
- Đặt hai huy hiệu `Driving (Primary)` và `Driven (Secondary)` cách đỉnh khung $0{,}3\,\text{cm}$ phía ngoài, không đè lên viền.
- Nâng scale từ `0.68` lên **`0.76`**.

### 5.6. Hình 3-5: Use Case con Đọc sâu (`report-datn/chapters/ch3/3_4_phan_tich_usecase.tex`)
- Khung viền hệ thống nét đứt: Tiêu đề `PHÂN HỆ ĐỌC SÂU VÀ KIỂM CHỨNG TRÍCH DẪN` đặt trong node nhãn có nền trắng che viền hoặc đặt cách mép trên $0{,}4\,\text{cm}$.
- 5 hình oval Use Case con:
  - Tăng khoảng cách tâm giữa các oval theo trục $y$ lên $1{,}25\text{--}1{,}35\,\text{cm}$.
  - Cố định bán kính `x radius = 2.4cm`, `y radius = 0.50cm` bảo đảm các oval cách nhau tối thiểu $0{,}25\,\text{cm}$ khoảng trống, triệt tiêu 100% chồng đè.
- Đường mũi tên `<<include>>` và `<<extend>>`: Căn chỉnh góc tỏa từ Use Case cha, nhãn đặt tại trung điểm đường vẽ với nền `fill=white`.

### 5.7. Hình 3-8, 3-9, 3-10, 3-11: 4 Biểu đồ tuần tự (`report-datn/chapters/ch3/3_5_bieu_do_tuan_tu.tex`)
- **Bố cục phân trang:** Chèn `\clearpage` trước Hình 3-9, Hình 3-10, Hình 3-11 để mỗi biểu đồ tuần tự chiếm trọn vẹn một trang dọc độc lập.
- **Tỉ lệ & Kích thước:** Nâng `scale=0.60` lên **`scale=0.80`** (`transform shape`).
- **Phông chữ:**
  - Thực thể (Entity): `font=\small\bfseries`.
  - Nhãn thông điệp (Messages): Đổi từ `\scriptsize` lên `\footnotesize` (kết hợp scale 0.80 cho kích thước chữ in thực tế $\approx 8\,\text{pt}$).
- **Khoảng cách & Trục dọc:**
  - Khoảng cách giữa các Lifeline: $3{,}6\,\text{cm} \rightarrow 3{,}7\,\text{cm}$ (tổng chiều ngang $14{,}8\,\text{cm}$).
  - Khoảng cách giữa các bước thông điệp: $0{,}6\,\text{cm} \rightarrow 0{,}75\text{--}0{,}85\,\text{cm}$.
  - Khung `opt`, `loop`, `alt`: Nới rộng lề đệm, nhãn khung đặt rõ ràng không đè lên lifelines.

### 5.8. Hình 3-12: Biểu đồ lớp miền (`report-datn/chapters/ch3/3_6_thiet_ke_csdl.tex`)
- **Nguyên tắc 80/20:**
  - Lớp `User`: `+ id, + email, + full_name, + role` | `+ authenticate(), + is_admin()`.
  - Lớp `ScholarProfile`: `+ id, + user_id, + institution, + research_interests` | `+ update_affiliation()`.
  - Lớp `UserApiKey`: `+ id, + user_id, + provider, + key_hash` | `+ activate(), + is_valid()`.
  - Lớp `ResearchSession`: `+ id, + user_id, + title, + active_doc_id` | `+ update_title()`.
  - Lớp `SessionTurn`: `+ id, + session_id, + query, + answer, + grounding_metadata` | `+ get_citations()`.
  - Lớp `DocumentStorageBlob`: `+ id, + sha256_hash, + file_size, + ref_count` | `+ increment_ref()`.
  - Lớp `Document`: `+ id, + user_id, + blob_id, + title, + doi` | `+ mark_peer_reviewed()`.
  - Lớp `DocumentChunk`: `+ id, + doc_id, + chunk_index, + bbox, + embedding` | `+ is_on_page()`.
  - Lớp `GraphNode` & `GraphEdge`: 4 thuộc tính cốt lõi.
  - Lớp `Draft` & `DraftMessage`: 4 thuộc tính cốt lõi | `+ mark_healed()`.
- **Định tuyến liên kết:** Chuyển sang định tuyến trực giao (`|-` hoặc `-|`) tránh cắt chéo qua thân các lớp khác.
- **Tỉ lệ:** Nâng scale từ `0.57` lên **`0.75`**, phông chữ các thuộc tính nâng từ `\tiny` lên `\scriptsize`.

---

## 6. Trách Nhiệm Của Bên Triển Khai (What's Left to the Builder)
1. Cập nhật mã nguồn TikZ trong 6 tệp LaTeX tương ứng theo đúng các thông số kích thước, tọa độ và phông chữ đã thiết kế.
2. Biên dịch lại toàn bộ tài liệu bằng XeLaTeX (`latexmk -xelatex main.tex`).
3. Sử dụng `pdftoppm` render các trang tài liệu vừa sửa ra hình ảnh PNG độ phân giải cao (150 DPI) để rà soát thị giác bằng mắt thực tế.
4. Kiểm tra 4 Verification Gates (`ruff`, `pytest`, `npm test`, `npm build`).
5. Đồng bộ lên VPS qua `bash scripts/deploy_to_vps.sh --fast` và tạo commit git sạch.

---

## 7. Kế Hoạch Xác Minh (Verification Plan)
- **Kiểm tra trực quan (Visual Verification):** Chụp lại ảnh trang v, trang chứa Hình 2-1, 2-4, 3-1, 3-2, 3-5, 3-8, 3-9, 3-10, 3-11, 3-12. Xác nhận 0 lỗi cắt chữ, 0 lỗi đè văn bản, cỡ chữ in A4 to rõ nét.
- **Kiểm tra biên dịch:** `latexmk -xelatex -interaction=nonstopmode main.tex` exit code 0, không có cảnh báo Overfull \hbox nghiêm trọng.
- **Kiểm tra 4 Gates:** Đảm bảo toàn bộ test case hệ thống xanh 100%.

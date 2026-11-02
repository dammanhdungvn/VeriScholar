# Thiết Kế Chi Tiết: Tái Cấu Trúc Hệ Thống AGENTS.md và INFORMATION.md Cho Báo Cáo ĐATN

> **Tài liệu đặc tả thiết kế (Design Document)**  
> **Chủ đề:** Tái cấu trúc chuẩn hóa `AGENTS.md`, chuyển đổi `RULES.md` thành `INFORMATION.md` và ánh xạ mục lục kỹ thuật `docs/`  
> **Ngày lập:** 02/11/2026  
> **Trạng thái:** Chờ phê duyệt (Pending Approval)  

---

## 1. Bối Cảnh Và Lý Do Thực Hiện (Intent and the Why)

Trong hệ thống tài liệu biên soạn Báo cáo Đồ án Tốt nghiệp (ĐATN) tại thư mục `report-datn/`, có sự giao thoa và nhầm lẫn về thẩm quyền giữa tệp `RULES.md` và `AGENTS.md`. Đồng thời:
1. Người dùng vừa bổ sung 4 tệp quy định học thuật chính thức từ Khoa Công nghệ Thông tin — Trường Đại học Mỏ - Địa chất (HUMG) vào `report-datn/guide/`:
   - `Huong dan-Quy dinh-DATN.md`: Mục tiêu, 3 câu hỏi học thuật cốt lõi, quy trình 10 bước, kỷ luật 4 điều kiện đình chỉ, quy định nộp lưu trữ 3 bản mềm / 1 bản cứng bìa mạ nhũ vàng, cân đối phân lượng.
   - `Huong-dan-viet-DATN.md`: Trình tự bố cục toàn văn, quy chuẩn thể thức (Font Times New Roman cỡ 13, dãn dòng 1.5, lề 2.5-3.5-2.5-2.5cm, số trang ở dưới góc phải, phân cấp mục tối đa 4 cấp không có mục đơn lẻ, quy cách bảng biểu/hình vẽ/TLTK).
   - `Mau-De-cuong-DATN.md`: Mẫu đề cương ĐATN chuẩn 6 thành phần.
   - `Mẫu_HD_DATN.md`: Bản nhận xét của người hướng dẫn lưu hồ sơ tốt nghiệp.
2. Tệp `RULES.md` cần được đổi tên thành `INFORMATION.md` để phản ánh đúng bản chất là hồ sơ định danh dữ liệu của đề tài (Sinh viên Đàm Mạnh Dũng, GVHD ThS. Vũ Lan Phương, tên đề tài, nhiệm vụ, tiến độ 10 tuần).
3. Về nội dung kỹ thuật lập trình: Thay vì sao chép dàn trải các chi tiết code hoặc schema cơ sở dữ liệu làm phình to tệp và trùng lặp với mã nguồn, `INFORMATION.md` cần đóng vai trò **Mục lục phân loại (Spec Catalog)** dẫn hướng đến các tài liệu kiến trúc chuyên sâu trong thư mục `docs/`.
4. Mọi sự trùng lặp nội dung giữa `AGENTS.md` và `INFORMATION.md` phải được loại bỏ triệt để (Zero Duplication), và bất kỳ điểm nào trong `AGENTS.md` sai lệch so với hướng dẫn trong `report-datn/guide/` phải được chỉnh sửa ngay lập tức.
5. Bộ kiểm thử tự động `tests/test_thesis_rules*.py` hiện đang bị trượt 4 ca adversarial do chưa cập nhật đúng sự phân định này, cần được hiệu chỉnh đồng bộ.

---

## 2. Mục Tiêu, Giới Hạn Và Ranh Giới (Goals, Non-Goals, Anti-Goals)

### 2.1. Mục Tiêu (Goals)
1. **Đổi tên và tái cấu trúc `report-datn/INFORMATION.md`:** Chứa đầy đủ thông tin hành chính của đề tài (Sinh viên, GVHD, Đơn vị đào tạo, Tên đề tài song ngữ, Bối cảnh & 4 Không gian, Kế hoạch 10 tuần, 20 TLTK) và **Mục lục phân loại chi tiết các file specs trong `docs/`**.
2. **Rà soát & Sửa đổi `report-datn/AGENTS.md` theo chuẩn `./guide`:** Đảm bảo 100% tuân thủ 4 tài liệu trong `guide/`; loại bỏ toàn bộ dữ liệu cá nhân/duplicate; cập nhật toàn bộ tham chiếu từ `RULES.md` sang `INFORMATION.md`.
3. **Cập nhật bộ kiểm thử tự động:** Đồng bộ hóa `tests/test_thesis_rules.py` và `tests/test_thesis_rules_adversarial.py` trỏ vào `INFORMATION.md` và phân định đúng thẩm quyền (test quy tắc định dạng kiểm tra `AGENTS.md`, test hồ sơ đề tài/mục lục kiểm tra `INFORMATION.md`).
4. **Bảo đảm 4 Cổng xác minh (Verification Gates):** Toàn bộ `uv run ruff check .`, `uv run pytest`, `npm test`, `npm run build` đều đạt exit code 0.

### 2.2. Giới Hạn Nghiệp Vụ (Non-Goals)
- Không viết lại hoặc tái cấu trúc mã nguồn các chương báo cáo XeLaTeX trong `report-datn/chapters/`, `frontmatter/` hay `report-datn/main.tex` (bảo đảm cấu trúc trang hiện hữu và bộ kịch bản kiểm định định dạng `scripts/verify_thesis_format.py` ổn định tuyệt đối).
- Không thay đổi mã nguồn logic ứng dụng tại `apps/` hoặc `packages/core/`.

### 2.3. Hàng Rào Chống Sai Lệch (Anti-Goals)
- Tuyệt đối không để sót bất kỳ liên kết gãy nào đến `RULES.md`.
- Tuyệt đối không để xảy ra tình trạng trùng lặp thông tin giữa `AGENTS.md` và `INFORMATION.md`.
- Tuyệt đối không chép mã nguồn thô hàng nghìn dòng vào `INFORMATION.md` mà phải dùng bảng mục lục liên kết tương đối chuẩn sang `docs/`.

---

## 3. Các Phương Án Kỹ Thuật Đã Xem Xét (Approaches)

### 3.1. Phương án 1 (Đã chọn): Phân tách rạch ròi & Chuẩn hóa triệt để (Clean Separation & Full Decoupling)
- **Cơ chế:** Đổi tên `RULES.md` $\rightarrow$ `INFORMATION.md`. Trong `INFORMATION.md`, loại bỏ các đoạn mô tả bảng CSDL dàn trải, thay thế bằng Bảng mục lục phân cấp ánh xạ sang `docs/specs/`, `docs/PRD/`, `docs/DATABASE_ERD.md`, `docs/benchmarks/`. Hiệu chỉnh `AGENTS.md` chuẩn hóa theo 4 file guide và xóa bỏ duplicate. Cập nhật test suite tương ứng.
- **Đánh đổi:** Cần cập nhật đồng thời ở tài liệu và test suite. Đổi lại, hệ thống đạt độ tinh gọn tối đa, đáp ứng chuẩn mực SSOT và vượt qua 100% test.

### 3.2. Phương án 2 (Bị loại bỏ): Tinh giản cục bộ (Chỉ thêm link và giữ tóm tắt specs)
- **Cơ chế:** Giữ lại tóm tắt schema CSDL trong `INFORMATION.md` và bổ sung liên kết `docs/` ở cuối.
- **Lý do loại bỏ:** Vẫn còn trùng lặp nội dung, vi phạm yêu cầu "NẾU duplicate xóa bỏ" của người dùng và dễ gây lệch dữ liệu khi `docs/` thay đổi.

---

## 4. Thiết Kế Chi Tiết Các Tệp (Detailed Design)

### 4.1. Cấu trúc tệp `report-datn/INFORMATION.md`

Tệp được tổ chức thành 6 phần rõ ràng:

1. **Phần 1: Hồ sơ định danh sinh viên và cán bộ hướng dẫn**
   - Sinh viên thực hiện: Đàm Mạnh Dũng, MSSV: `2221050359`, Lớp: `DCCTCT67_09B` (Khóa K67), Ngành: Công nghệ thông tin (`7480201`), Chuyên ngành: Hệ thống thông tin và Tri thức, Đơn vị: Khoa CNTT — HUMG, SĐT: `0978461865`, Email: `dammanhdungvn@gmail.com`.
   - Giảng viên hướng dẫn: ThS. Vũ Lan Phương, Mã CB: `0802-09`, Bộ môn Công nghệ thông tin, SĐT: `0984223379`, Email: `vulanphuong@humg.edu.vn`.
   - Cơ sở đào tạo & Nơi thực hiện: Trường Đại học Mỏ - Địa chất (Số 18 Phố Viên, Đức Thắng, Bắc Từ Liêm, Hà Nội).
2. **Phần 2: Đặc tả đề tài tốt nghiệp, tính cấp thiết và mục tiêu**
   - Tên đề tài chính thức (tiếng Việt & tiếng Anh).
   - Tên hệ thống sản phẩm: VeriScholar Academic AI Platform.
   - Bối cảnh bài toán (đối tượng thụ hưởng học giả VinUni, vấn nạn ảo giác trích dẫn).
   - Mô hình 4 Không gian nghiên cứu khép kín (Khám phá, Đọc sâu kiểm chứng, Thư viện tri thức, Soạn thảo kiểm chứng).
   - Bốn đóng góp kỹ thuật cốt lõi của đề tài.
3. **Phần 3: Kế hoạch thực hiện 10 tuần chi tiết (Đề cương ĐATN)**
   - Lịch trình 10 tuần cụ thể (24/08/2026 đến 02/11/2026) với mốc Tuần 6 báo cáo tiến độ với Bộ môn và GVHD.
4. **Phần 4: Mục lục và Bản đồ tra cứu đặc tả kỹ thuật coding (`./docs`)**
   - Bảng phân loại liên kết tương đối đến toàn bộ tài liệu kỹ thuật trong `docs/`:
     - *Kiến trúc tổng thể & CSDL:* `docs/specs/00-foundation-architecture-and-db.md`, `docs/DATABASE_ERD.md` (chuẩn 20 bảng thực tế, 0 bảng giả).
     - *Xác thực & Bảo mật BYOK:* `docs/specs/01-auth-and-user-spec.md`, `docs/PRD/01-auth-and-user.md`.
     - *Khám phá & Thu thập tài liệu:* `docs/specs/02-discovery-and-documents-spec.md`, `docs/PRD/02-discovery-and-documents-crud.md`.
     - *Đọc sâu & BBox Grounding:* `docs/specs/03-sessions-and-deep-reading-spec.md`, `docs/PRD/03-sessions-and-deep-reading-crud.md`.
     - *Bảng ngữ cảnh & Tiến trình:* `docs/specs/04-context-table-and-roadmap-spec.md`, `docs/PRD/04-context-table-and-roadmap.md`.
     - *Thư viện tri thức & GraphRAG:* `docs/specs/05-favorite-library-and-graphrag-spec.md`, `docs/PRD/05-favorite-library-and-graphrag.md`.
     - *Soạn thảo Agentic & LaTeX Sandbox:* `docs/specs/06-agentic-overleaf-writing-spec.md`, `docs/PRD/06-agentic-overleaf-writing.md`.
     - *Giám sát & Langfuse Tracing:* `docs/specs/07-monitoring-and-langfuse-spec.md`, `docs/PRD/07-monitoring-and-langfuse.md`.
     - *Tác tử Universal Harness:* `docs/specs/08-universal-agent-harness-spec.md`.
     - *Triển khai VPS & Đánh giá:* `docs/specs/09-deployment-cicd-and-evaluation-spec.md`, `docs/PRD/08-deployment-and-system-evaluation.md`, `docs/benchmarks/thesis_benchmark_results.json`.
     - *Cẩm nang bảo vệ & Bản đồ đề cương:* `docs/THESIS_DEFENSE_GUIDE.md`, `docs/THESIS_OUTLINE_MAPPING.md`.
5. **Phần 5: Bảng tham số định lượng và benchmarks khóa cứng**
   - Bảng chỉ số thực nghiệm gốc (580 tests pass, thời gian 13.02s, DB latency 1.66ms, TTFT < 1.5s, IoU $\ge 0{,}85$, 20 bảng CSDL thực tế).
6. **Phần 6: Danh mục 20 tài liệu tham khảo chính thức của đề tài**
   - 2 tài liệu tiếng Việt (hướng dẫn HUMG) và 18 tài liệu tiếng Anh chuẩn IEEE/ACM/arXiv.

---

### 4.2. Hiệu chỉnh tệp `report-datn/AGENTS.md` theo chuẩn `./guide`

1. **Hiệu chỉnh các điểm sai lệch / thiếu sót so với 4 tài liệu trong `guide/`:**
   - **Bản nhận xét của GVHD (`Mẫu_HD_DATN.md`):** Ghi rõ đây là văn bản độc lập lưu trong hồ sơ tốt nghiệp của Nhà trường, không đóng vào thân bài như một chương, tránh nhầm lẫn cấu trúc.
   - **Quy định lưu trữ bản cứng và bản mềm (`Huong dan-Quy dinh-DATN.md` & `Huong-dan-viet-DATN.md`):**
     - Bản cứng: 03 quyển bìa mềm có chữ ký GVHD nộp trước bảo vệ (02 quyển nộp Bộ môn gồm 1 cho HĐ, 1 cho GVPB; 01 quyển cho GVHD). Sau bảo vệ nộp 01 quyển bìa cứng in chữ nhũ cho Bộ môn lưu trữ trong vòng 10 ngày.
     - Bản mềm: Lưu thư mục định dạng `MãSinhViên_HọTên_Khóa` (báo cáo, mã nguồn, sơ đồ).
   - **Quy chế kỷ luật và 3 câu hỏi học thuật cốt lõi:**
     - 4 điều kiện đình chỉ bảo vệ tốt nghiệp (nợ trường, không gặp/báo cáo GVHD hàng tuần, không nộp đúng hạn, GVHD đánh giá không đạt) và 3 câu hỏi lớn ("Làm gì? Cho đối tượng nào?", "Làm như thế nào?", "Kết quả ra sao?") được thể chế hóa đầy đủ trong `AGENTS.md` (không duplicate sang `INFORMATION.md`).
   - **Trật tự bố cục chuẩn mực:**
     - Bìa ngoài (chữ nhũ) $\rightarrow$ Bìa trong $\rightarrow$ Phiếu giao đề tài $\rightarrow$ Đề cương ĐATN $\rightarrow$ Mục lục $\rightarrow$ Danh mục chữ viết tắt $\rightarrow$ Danh mục bảng biểu (LoT) $\rightarrow$ Danh mục hình vẽ (LoF) $\rightarrow$ Lời cảm ơn (trang 1 Ả Rập trong XeLaTeX) $\rightarrow$ Lời mở đầu $\rightarrow$ Chương 1 (Mô tả bài toán: Làm gì? Cho đối tượng nào?) $\rightarrow$ Chương 2 (Cơ sở lý thuyết & Luận giải Tại sao chọn công nghệ) $\rightarrow$ Chương 3 (Quy trình 5 bước kỹ nghệ: Phân tích, Thiết kế, Cài đặt, Kiểm thử, Hiệu chỉnh) $\rightarrow$ Chương 4 (Kết quả thực nghiệm) $\rightarrow$ Kết luận $\rightarrow$ Danh mục TLTK $\rightarrow$ Phụ lục (không dày hơn phần chính).
   - **Thể thức Typography:**
     - Times New Roman 13pt, dãn dòng 1.5 lines, lề trên 2.5cm, dưới 2.5cm, trái 3.5cm, phải 2.5cm.
     - Đánh số trang: Dưới, phía bên phải mỗi trang giấy, in đứng thường (không in nghiêng).
     - Phân cấp đề mục: Tối đa 4 cấp (ví dụ 4.1.2.1), cấm tiểu mục đơn lẻ (ít nhất 2 tiểu mục con trong mỗi nhóm).
     - Bảng biểu/hình vẽ: Gắn với số chương, tiêu đề bảng ở trên, tiêu đề hình ở dưới, cấm dẫn chiếu tương đối.
     - Tài liệu tham khảo: Tiếng Việt trước (xếp ABC theo tên), Tiếng Anh sau (xếp ABC theo họ), lùi đầu dòng 1cm từ dòng thứ hai.
2. **Nạp Bảng ma trận chiến lược chắt lọc nội dung từ docs (Keep & Elevate vs. Omit):**
   - Chuyển toàn bộ Bảng ma trận chắt lọc nội dung (Phần 7 của `RULES.md` cũ) sang `AGENTS.md` (tại Mục 3.2, ngay dưới AP-01) để làm cẩm nang hướng dẫn hành vi viết bài cho tác tử AI.
3. **Loại bỏ trùng lặp và đồng bộ dẫn chiếu:**
   - Xóa bỏ mọi thông tin định danh cá nhân sinh viên/GVHD trong `AGENTS.md`.
   - Cập nhật toàn bộ các dòng tham chiếu từ `report-datn/RULES.md` sang `report-datn/INFORMATION.md`.

---

### 4.3. Cập nhật bộ kiểm thử tự động `tests/test_thesis_rules*.py`

1. **`tests/test_thesis_rules.py`:**
   - Thay đổi đường dẫn kiểm tra từ `report-datn/RULES.md` sang `report-datn/INFORMATION.md`.
   - Kiểm tra liên kết hai chiều giữa `AGENTS.md` và `INFORMATION.md`.
   - Kiểm tra sự hiện diện của Mục lục `docs/` và hồ sơ sinh viên trong `INFORMATION.md`.
   - Kiểm tra sự hiện diện của Bảng ma trận chiến lược chắt lọc (Keep/Omit) bên trong `AGENTS.md`.
2. **`tests/test_thesis_rules_adversarial.py`:**
   - Tách bạch phạm vi kiểm tra:
     - Các điều kiện quy chế khoa (4 điều kiện đình chỉ, 3 câu hỏi lớn), quy chuẩn thể thức (13pt, margins, stick figure UML, cấm booktabs, bắt buộc tabularx, trần $N_{\text{refs}} \le 20$): assert trên `AGENTS.md`.
     - Các thông tin định danh sinh viên, mốc thời gian, định dạng thư mục nộp `MãSinhViên_HọTên_Khóa`, chỉ số thực nghiệm gốc (580 tests, 13.02s, 1.66ms, 1.5s, 0.85) và 20 bảng CSDL: assert trên `INFORMATION.md`.
   - Khắc phục triệt để 4 ca test đang bị FAIL để toàn bộ 19 test trong 2 file đều PASS 100%.

---

## 5. Những Việc Giao Cho Người Thực Hiện (What's Left to the Builder)

1. Xóa hoặc di chuyển `report-datn/RULES.md` thành `report-datn/INFORMATION.md`.
2. Ghi nội dung chuẩn hóa cho `report-datn/INFORMATION.md`.
3. Cập nhật nội dung `report-datn/AGENTS.md` (sửa các điểm chưa khớp guide, xóa duplicate, đổi link sang `INFORMATION.md`).
4. Cập nhật `tests/test_thesis_rules.py` và `tests/test_thesis_rules_adversarial.py`.
5. Chạy 4 Cổng kiểm định:
   - `uv run ruff check . && uv run ruff format --check .`
   - `uv run pytest tests/test_thesis_rules.py tests/test_thesis_rules_adversarial.py`
   - `uv run pytest` (toàn bộ test suite)
   - `npm --prefix apps/web run test`
   - `npm --prefix apps/web run build`

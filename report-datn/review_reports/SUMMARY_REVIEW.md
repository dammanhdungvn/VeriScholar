# BÁO CÁO TỔNG HỢP TOÀN DIỆN VÀ ĐỀ XUẤT PHƯƠNG ÁN TINH GỌN BÁO CÁO ĐỒ ÁN TỐT NGHIỆP VERISCHOLAR
## (THESIS REVIEW SYNTHESIS REPORT & COMPREHENSIVE STREAMLINING ROADMAP)

> **Căn cứ pháp lý & Chuẩn mực đối soát:**
> - Quy chế và Hướng dẫn thực hiện Đồ án Tốt nghiệp Đại học — Khoa Công nghệ Thông tin, Trường Đại học Mỏ - Địa chất (`report-datn/guide/`).
> - Cẩm nang Vận hành AI Agent Biên soạn Báo cáo ĐATN (`report-datn/AGENTS.md`).
> - Hồ sơ Định danh Đề tài và Nguồn Chân lý Duy nhất (`report-datn/INFORMATION.md`).
> - Bản đồ Cấu trúc Vi mô Đồ án Tốt nghiệp (`report-datn/ROADMAP.md`).
> - Kết quả rà soát độc lập từ 5 tiểu ban chuyên trách (`chapter_1_review.md`, `chapter_2_review.md`, `chapter_3_review.md`, `chapter_4_review.md`, `frontmatter_and_conclusion_review.md`).
> - Toàn bộ mã nguồn thực tế, cơ sở dữ liệu và dữ liệu kiểm thử thực nghiệm trong Monorepo VeriScholar (`packages/core/`, `apps/api/`, `apps/web/`, `tests/`, `docs/benchmarks/`).
>
> **Đơn vị thực hiện:** Hội đồng Tổng hợp Đánh giá ĐATN VeriScholar (Thesis Review Synthesizer — Mentor's Chief Synthesizer).  
> **Thời điểm công bố:** Ngày 02 tháng 11 năm 2026.  
> **Tệp xuất bản:** `report-datn/review_reports/SUMMARY_REVIEW.md`.

---

## LỜI NÓI ĐẦU VÀ MỤC ĐÍCH TỔNG HỢP

Báo cáo Đồ án Tốt nghiệp (ĐATN) đại học ngành Công nghệ Thông tin không phải là một tập tài liệu hướng dẫn kỹ thuật nội bộ hay cẩm nang ghi chép phát triển phần mềm, mà là một **công trình nghiên cứu khoa học chính thức** chịu sự thẩm định khắt khe của Hội đồng chấm bảo vệ thuộc Khoa Công nghệ Thông tin — Trường Đại học Mỏ - Địa chất (HUMG).

Đề tài: *"Xây dựng nền tảng AI hỗ trợ nghiên cứu và viết bài báo khoa học VinUni dựa trên Agentic RAG, truy xuất tri thức học thuật và kiểm chứng trích dẫn"* (Sinh viên thực hiện: **Đàm Mạnh Dũng** — MSSV: `2221050359` — Lớp: `DCCTCT67_09B`; GVHD: **ThS. Vũ Lan Phương**) là một công trình có hàm lượng kỹ nghệ thực hành rất cao, sở hữu mã nguồn thực tế đồ sộ, vượt qua 100% các cổng kiểm thử tự động và đã được triển khai vận hành thực nghiệm trên máy chủ VPS đám mây công cộng.

Tuy nhiên, qua quá trình rà soát độc lập chuyên sâu của 5 tiểu ban chuyên trách trên toàn bộ các chương và phần mở đầu, báo cáo hiện tại đang bộc lộ những **điểm nghẽn học thuật nghiêm trọng**: số trang phình to vượt trần cho phép ($115$ trang so với ngân sách $75 \text{ -- } 95$ trang), tồn tại các lỗi cấu trúc biên dịch khiến mục lớn bị biến mất trong Mục lục, sa đà vào việc chép lý thuyết giáo trình đại cương và vẽ các mô hình kiến trúc "ảo" không có trong thực tế dự án, nhồi nhét hình ảnh chụp màn hình chất lượng thấp hoặc dính lỗi giao diện, và vi phạm hàng loạt quy chuẩn thể thức chế bản XeLaTeX.

Báo cáo tổng hợp này được biên soạn nhằm cung cấp **bức tranh toàn cảnh khách quan, trung thực và toàn diện nhất** về hiện trạng đồ án; bóc tách chi tiết 4 nhóm sai phạm cốt lõi; thiết lập Ma trận đánh giá và sàng lọc toàn bộ 52 hình ảnh/sơ đồ trên toàn đồ án; xây dựng Danh mục thứ tự ưu tiên xử lý dứt điểm (Ma trận P0 -- P3); và đưa ra dự báo định lượng về diện mạo báo cáo sau khi hoàn tất tinh gọn.

---

## PHẦN I: BỨC TRANH TỔNG THỂ HIỆN TRẠNG BÁO CÁO ĐATN VERISCHOLAR

### 1.1. Thống kê thông số kỹ thuật môi trường biên dịch XeLaTeX
Kiểm tra biên dịch thực tế trên tệp chủ `main.tex` bằng công cụ `latexmk -xelatex` (TeX Live 2023/Debian, XeTeX 3.141592653-2.6-0.999995) ghi nhận các thông số kỹ thuật nền tảng:
- **Mã thoát (Exit Code):** `0` (Quá trình biên dịch thành công, không gặp fatal error cản trở xuất bản).
- **Quy mô tệp PDF đầu ra (`main.pdf`):** $4.739.163 \text{ bytes}$ (~$4{,}74 \text{ MB}$).
- **Tổng số trang in hiện tại:** **115 trang** (khổ chuẩn A4: $595{,}28 \times 841{,}89 \text{ points}$).
  - Trang không đánh số: 2 trang bìa ngoài và bìa trong (`frontmatter/bia_chinh.tex`, `frontmatter/bia_phu.tex`).
  - Trang đánh số La Mã thường: 14 trang (từ trang `iii` đến trang `xvi`, gồm Phiếu giao đề tài, Đề cương 10 tuần, Mục lục, Danh mục hình, Danh mục bảng, Danh mục từ viết tắt).
  - Trang đánh số Ả Rập: 99 trang (từ trang `1` đến trang `99`, gồm Lời cảm ơn, Lời mở đầu, 4 Chương nội dung, Kết luận và Tài liệu tham khảo).
- **Chỉ số cảnh báo biên dịch (Log Diagnostics):**
  - Lỗi nghiêm trọng (Fatal Errors): **0** (Hệ thống macro XeLaTeX được tổ chức quy củ).
  - Trích dẫn/Tham chiếu mồ côi chưa định nghĩa (Undefined citations/references): **0** (Tất cả nhãn nội bộ đều được giải quyết).
  - Cảnh báo tràn lề ngang (Overfull `\hbox`): **30 cảnh báo** (từ $1{,}1 \text{ pt}$ đến $38{,}7 \text{ pt}$, tập trung ở Chương 3 và 4 do các chuỗi định danh mã nguồn dài, tên bảng CSDL, tên module và URL không thể tự ngắt dòng).
  - Cảnh báo non lề ngang (Underfull `\hbox`): **18 cảnh báo** (xảy ra tại danh mục tài liệu tham khảo quốc tế khi căn lề đều hai bên).
  - Cảnh báo phông chữ (Font size substitutions): Cảnh báo tự động thu nhỏ các ký hiệu toán học kích thước nhỏ từ phông Computer Modern sang Times New Roman.

### 1.2. Phân tích hiện trạng phình to số trang và Bảng phân bổ ngân sách trang in
Theo quy chuẩn ĐATN Đại học của Khoa CNTT — HUMG (`guide/Huong-dan-viet-DATN.md` dòng 34) và Cẩm nang SOP `AGENTS.md` (Mục 2.6, dòng 390--397), dung lượng toàn văn của một đồ án tốt nghiệp chuẩn mực được khống chế chặt chẽ:
- **Tổng ngân sách toàn bài:** **75 -- 95 trang** (bao gồm toàn bộ từ Bìa chính đến Tài liệu tham khảo).
- **Ngân sách phần thân bài chính (Chương 1 đến Chương 4):** **50 -- 65 trang** (phân bổ theo tỷ lệ vàng $30\% \text{ Lý thuyết } / 70\% \text{ Thực hành}$).
- **Hiện trạng thực tế:** Thân bài chiếm tới **91 trang in**, đưa tổng quy mô đồ án lên **115 trang**, **VƯỢT NGÂN SÁCH TỪ 20 ĐẾN 40 TRANG** (vượt $21{,}1\% \text{ đến } 53{,}3\%$).

Bảng đối chiếu phân bổ ngân sách trang in chi tiết từng phân đoạn:

| Phân Đoạn / Chương Mục | Vai Trò Nội Dung | Số Trang Thực Tế | Ngân Sách Chuẩn | Chênh Lệch / Trạng Thái | Nguyên Nhân Phình To Chính |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Frontmatter** | Bìa, phiếu giao, đề cương, mục lục, danh mục | **16 trang** | 12 -- 14 trang | Vượt nhẹ (+2 trang) | Khoảng cách dãn dòng lớn, danh mục từ viết tắt dài lê thê do chứa từ đại trà. |
| **Mở đầu & Cảm ơn** | Lời cảm ơn, Lời mở đầu súc tích | **2 trang** | 2 trang | **ĐẠT** | Đúng quy chuẩn 1 trang Cảm ơn + 1 trang Mở đầu. |
| **Chương 1** | Tổng quan về đề tài (Mô tả bài toán) | **7 trang** (trang 3--9) | 6 -- 8 trang | **ĐẠT** | Chiếm $\approx 8\%$ thân bài, bố cục cân đối theo quy chế HUMG. |
| **Chương 2** | Cơ sở lý thuyết và công nghệ nền tảng | **29 trang** (trang 10--38) | **10 -- 12 trang** | **BÁO ĐỘNG ĐỎ**<br>(+17 -- 19 trang, phình 241%) | Chép lý thuyết giáo trình đại cương (Python, React, Docker); vẽ 4 mẫu Agent "ảo" không dùng; nhồi nhét 11 logo PNG mạng và 7 TikZ lý thuyết. |
| **Chương 3** | Phân tích và thiết kế hệ thống | **33 trang** (trang 39--71) | **18 -- 24 trang** | **BÁO ĐỘNG ĐỎ**<br>(+9 -- 15 trang, phình 157%) | Nhồi nhét 16 bảng từ điển CSDL chi tiết (9 trang); vẽ 2 Use Case con Admin không có UI; trùng lặp Mục 3.1 với Ch1. |
| **Chương 4** | Cài đặt và kết quả thực nghiệm | **23 trang** (trang 71--93) | **12 -- 16 trang** | **BÁO ĐỘNG VÀNG**<br>(+7 -- 11 trang, phình 153%) | Lạm phát 16 hình ảnh (form login/register, dashboard rỗng, ảnh monitor lỗi); cẩm nang cài đặt VS Code sơ cấp. |
| **Kết luận & Backmatter**| Kết luận, Hướng phát triển, TLTK | **6 trang** (trang 94--99) | 4 -- 6 trang | **ĐẠT** | 3 trang Kết luận + 3 trang 20 tài liệu tham khảo chính thống. |
| **TỔNG CỘNG TOÀN ĐỒ ÁN** | Toàn bộ các trang từ Bìa đến Hết | **115 trang** | **75 -- 95 trang** | **VƯỢT TRẦN**<br>(+20 -- 40 trang) | **Cần thực thi chiến dịch tinh gọn cắt giảm ngay 35 -- 40 trang dư thừa.** |

---

## PHẦN II: TỔNG HỢP 4 NHÓM LỖI CỐT LÕI TRÊN TOÀN BỘ ĐỒ ÁN

Qua tổng hợp từ 5 báo cáo độc lập, Hội đồng phân loại toàn bộ các khuyết tật của báo cáo thành **4 nhóm lỗi cốt lõi mang tính hệ thống**:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   4 NHÓM LỖI CỐT LÕI CỦA BÁO CÁO ĐỒ ÁN VERISCHOLAR               │
├──────────────────────────────────────────────────────────────────────────────────┤
│ NHÓM 1: LỖI CẤU TRÚC VÀ PHÂN CẤP ĐỀ MỤC (Structural & Hierarchy Defects)         │
│   └─► Mất Section 4.3 & 4.4; Bìa phụ thiếu tên đề tài; Lỗi đề mục cấp 5; Singleton│
├──────────────────────────────────────────────────────────────────────────────────┤
│ NHÓM 2: NỘI DUNG DƯ THỪA, GIÁO TRÌNH ĐẠI CƯƠNG VÀ MÔ TẢ ẢO (Content Redundancy)  │
│   └─► Chép Python/Docker/React; 4 mẫu Agent ảo; 16 bảng CSDL dump; Admin UC rác   │
├──────────────────────────────────────────────────────────────────────────────────┤
│ NHÓM 3: SAI SỰ THẬT SO VỚI THỰC TẾ & LIÊM CHÍNH KHOA HỌC (Integrity Violations) │
│   └─► Ảnh BBox không có viền; Ảnh Azure lỗi; Sai số test (330 vs 580); Sai IoU  │
├──────────────────────────────────────────────────────────────────────────────────┤
│ NHÓM 4: LỖI FORMAT, BẢNG BIỂU, TRÍCH DẪN VÀ VĂN PHONG (Layout & Typography)      │
│   └─► Bảng dùng tabular [H]; Zero Citations ở Ch3/Ch4; Tiêu đề "... là gì?"; Ngoặc│
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.1. Nhóm 1: Lỗi cấu trúc và phân cấp đề mục (Structural & Hierarchy Defects)

1. **Lỗi nghiêm trọng: Mục 4.3 và Mục 4.4 bị XeLaTeX hạ cấp thành mục con của Mục 4.2:**
   - *Quan sát thực tế:* Trong tệp điều phối `chapters/ch4_thuc_nghiem.tex`, các tệp con được gọi tuần tự. Tuy nhiên, tệp `4_3_kiem_thu.tex` và tệp `4_4_so_lieu.tex` **hoàn toàn không chứa lệnh `\section`**, mà mở đầu ngay bằng `\subsection`.
   - *Hậu quả biên dịch:* Trình biên dịch XeLaTeX tự động đánh số hai mục này thành **Mục 4.2.2**, **Mục 4.2.3** và **Mục 4.2.4** (trực thuộc Mục 4.2 "Giao diện các phân hệ chính"). Trong Mục lục chính thức (`main.toc`), **Mục 4.3 và Mục 4.4 biến mất hoàn toàn**. Đây là lỗi cấu trúc thô thiển, phá vỡ khung đề cương đã được phê duyệt trong `ROADMAP.md`.
2. **Trang bìa trong (`frontmatter/bia_phu.tex`) THIẾU HOÀN TOÀN TÊN ĐỀ TÀI:**
   - *Quan sát thực tế:* Sau dòng chữ lớn `ĐỒ ÁN TỐT NGHIỆP` và `CHUYÊN NGÀNH: HỆ THỐNG THÔNG TIN VÀ TRI THỨC`, mã nguồn chèn một khoảng cách trống khổng lồ `\\[4.0cm]` rồi nhảy thẳng xuống bảng chữ ký của GVHD và Sinh viên.
   - *Hậu quả học thuật:* Trang bìa phụ là văn bản pháp lý lưu chiểu vĩnh viễn có chữ ký tươi. Việc không có Tên đề tài khiến văn bản không có đối tượng xác nhận, vi phạm trực tiếp biểu mẫu bắt buộc tại Phụ lục 02 của Khoa CNTT — HUMG (`guide/Huong-dan-viet-DATN.md`).
3. **Sinh đề mục cấp 5 vi phạm quy chế phân cấp của Nhà trường:**
   - *Quan sát thực tế:* Tại `chapters/ch4/4_1_moi_truong.tex` (dòng 61--79), tác giả sử dụng lệnh `\paragraph{...}` dưới `\subsection{4.1.3}`. Trình biên dịch XeLaTeX đã tự động đánh số 5 cấp: **`4.1.3.0.1`**, **`4.1.3.0.2`**, **`4.1.3.0.3`**, **`4.1.3.0.4`** trong Mục lục.
   - *Quy chuẩn đối chiếu:* Quy chế HUMG Mục III.2 và `AGENTS.md` Mục 2.4.1 nghiêm cấm tuyệt đối việc đánh số tiểu mục quá 4 chữ số (`X.Y.Z.W`).
4. **Trùng lặp tiêu đề mục và vi phạm nguyên tắc phân cấp:**
   - Tại Chương 3: Mục 3.6 có tiêu đề `\section{Thiết kế cơ sở dữ liệu cho hệ thống}`, ngay dưới đó tiểu mục 3.6.2 lại có tiêu đề `\subsection{Thiết kế cơ sở dữ liệu của hệ thống}`.
   - Tại Chương 4: Tồn tại lỗi *Singleton Subsection* khi Mục 4.2 có tiểu mục `4.2.1` nhưng không có `4.2.2` hợp lệ trong cùng tệp.
5. **Cấu trúc Chương 2 bị xé nhỏ thành 9 mục manh mún:**
   - Chương 2 hiện bị chia thành 9 mục cấp 1 rời rạc (`2.1` đến `2.9`), biến chương này thành một danh sách liệt kê công cụ chắp vá thay vì một bức tranh lý thuyết và công nghệ nền tảng mạch lạc gồm 5 khối giải pháp lớn theo quy hoạch của `ROADMAP.md`.

---

### 2.2. Nhóm 2: Lỗi nội dung dư thừa, giáo trình đại cương và mô tả kiến trúc "ảo" (Content Redundancy)

1. **Sao chép lý thuyết giáo trình đại cương sơ cấp (Vi phạm nghiêm trọng AP-01):**
   - *Tại Chương 2:* Tệp `2_9_tools_languages.tex` (chiếm trọn 63 dòng) trình bày lại các định nghĩa cơ bản về ngôn ngữ Python, TypeScript, framework FastAPI, thư viện React (Virtual DOM), Docker container và Pytest/Vitest. Đây là những kiến thức cơ sở ngành mà sinh viên năm 2 đã học, hoàn toàn không có hàm lượng nghiên cứu tốt nghiệp. Tương tự, tệp `2_3_advanced_rag.tex` dành tới 70 dòng và 1 sơ đồ TikZ lớn để mô tả kiến trúc Naive RAG dù hệ thống VeriScholar hoàn toàn không sử dụng mô hình này.
   - *Tại Chương 4:* Mục 4.1.1 dành gần 1 trang hướng dẫn cách truy cập trang chủ tải Visual Studio Code, cài extension và chạy lệnh `uv venv`, `npm install` — mang phong cách cẩm nang người mới bắt đầu (Tutorial Filler).
2. **Vẽ và mô tả 4 mẫu thiết kế tác nhân "ảo" không có trong thực tế dự án (`2_5_agentic_react.tex`):**
   - Mục 2.5 dành tới **8 trang in** và **7 sơ đồ TikZ** để trình bày 6 mẫu thiết kế Agent. Tuy nhiên, đối soát mã nguồn thực tế tại `packages/core/` và `apps/api/`, hệ thống VeriScholar chỉ cài đặt **Tác nhân đơn ReAct (Single-Agent ReAct)** điều phối công cụ gọi Sandbox E2B MicroVM.
   - 4 mẫu thiết kế sau hoàn toàn không được hiện thực hóa, bản thân văn bản báo cáo đã phải thừa nhận bằng các câu phân trần:
     + *Planning Pattern:* Dòng 223 thừa nhận không dùng tầng lập kế hoạch tách rời.
     + *Reflection Pattern:* Dòng 501 thừa nhận không dùng vòng lặp LLM tự phê bình đa lượt tốn kém mà dùng quy tắc xác định.
     + *Multi-Agent Collaboration:* Dòng 597 thừa nhận chỉ chạy Single-Agent, còn hệ đa tác tử chỉ là "định hướng mở rộng tương lai".
     + *Human-in-the-Loop Pattern:* Dòng 690 thừa nhận cơ chế ngắt luồng khóa tiến trình (Interrupt Checkpoint) là "hướng phát triển tương lai".
   - *Đánh giá:* Việc đưa lý thuyết và vẽ hình phức tạp cho những tính năng không làm thật là hình thức "làm màu", gây hiểu lầm cho Hội đồng chấm đồ án.
3. **Nhồi nhét 16 bảng từ điển CSDL chi tiết kéo dài 9 trang in liên tục tại Chương 3:**
   - Từ trang 59 đến 67, Mục 3.6.3 trình bày 16 bảng đặc tả thuộc tính CSDL vật lý (Bảng 3.3 đến 3.18). Việc đổ toàn bộ Data Dictionary vào thân bài biến báo cáo thành tài liệu kỹ thuật nội bộ, làm loãng tính khoa học và chiếm dụng lãng phí tới 9 trang in.
4. **Lạm phát Use Case của Quản trị viên (Admin) không có giao diện người dùng:**
   - Mục 3.4.2 dành 2 tiểu mục lớn, vẽ 2 sơ đồ Use Case con (Hình 3-5, Hình 3-6) và lập 2 bảng đặc tả BA cho các tác vụ của Quản trị viên (khóa BYOK, thu dọn CAS, telemetry). Trong khi đó, văn bản thừa nhận hệ thống không hề có màn hình Admin (vận hành qua CLI và Azure Portal).
5. **Khuyết thiếu hai nội dung thiết kế cốt lõi trong Chương 3:**
   - **Thiếu hoàn toàn mục Thiết kế Kiến trúc Tổng thể Hệ thống:** Toàn bộ Chương 3 không có sơ đồ Kiến trúc Lục giác (Hexagonal Architecture), không có sơ đồ phân tầng Domain Core / Ports / Adapters. Tệp `3_3_kien_truc.tex` theo quy hoạch `ROADMAP.md` bị bỏ trống.
   - **Thiếu đặc tả Use Case và Biểu đồ tuần tự cho Phân hệ Đồ thị Tri thức (GraphRAG):** Đóng góp cốt lõi số 3 của đề tài với mã nguồn phức tạp tại `apps/api/src/api/services/graph_rag_service.py` lại không được mô hình hóa bất kỳ sơ đồ phân rã Use Case hay Sequence Diagram nào.

---

### 2.3. Nhóm 3: Lỗi sai sự thật so với thực tế dự án & Liêm chính khoa học (Academic Integrity Violations)

1. **Hình ảnh minh chứng trọng tâm bị SAI SỰ THẬT (`deep_read_paper.png`):**
   - *Mô tả trong báo cáo (Chương 4, dòng 211--224):* Tác giả khẳng định Hình 4.8 là *"Giao diện đọc sâu tài liệu PDF hai cột và Bounding Box viền vàng... kích hoạt lớp phủ đồ họa vẽ khung viền vàng bao quanh đoạn trích gốc... đạt IoU = 0,9266"*.
   - *Thực tế tệp ảnh `figures/frontend/deep_read_paper.png`:* Khung PDF bên trái hoàn toàn trơn bóng, **tuyệt đối không có bất kỳ khung viền vàng hay Bounding Box nào!**
   - *Hậu quả:* Đây là vi phạm liêm chính trực quan nghiêm trọng. Khi Hội đồng phản biện kiểm tra, họ sẽ lập tức nhận định sinh viên mô tả tính năng "ảo" trên hình ảnh không có thật.
2. **Hình ảnh giám sát máy chủ dính lỗi giao diện thô thiển (`azure_monitor.png`):**
   - *Mô tả trong báo cáo (dòng 111--117):* Tác giả khẳng định hệ thống đạt độ sẵn sàng 100%, CPU ổn định dưới 1%.
   - *Thực tế tệp ảnh `figures/frontend/azure_monitor.png`:* Ngay giữa màn hình dính một thông báo lỗi màu xanh của Azure: **"No data returned matching the selected filters"** và đường biểu đồ bị đứt gãy. Ảnh chụp lỗi này chứng tỏ sự thiếu cẩn trọng trong khâu chuẩn bị số liệu thực nghiệm.
3. **Mâu thuẫn số lượng bài kiểm thử tự động giữa các trang trong cùng một báo cáo:**
   - Phiếu giao đề tài (`phieu_giao_de_tai.tex` dòng 84): Ghi *"hơn 330 kịch bản kiểm thử tự động"*.
   - Hồ sơ đề tài chuẩn (`INFORMATION.md` Mục 5.1): Khóa cứng số liệu chuẩn xác **580 bài kiểm thử** (340 Backend pytest + 240 Frontend vitest).
   - Lời mở đầu (`loi_mo_dau.tex` dòng 11) & Kết luận (`ket_luan.tex` dòng 14): Ghi **580 kịch bản kiểm thử**.
   - Chương 4 (`4_3_kiem_thu.tex` dòng 8--33): Ghi **589 bài kiểm thử** (349 pytest + 240 vitest).
   - Mã nguồn thực tế hiện tại trên Monorepo: Đang có **598 bài kiểm thử** (358 pytest + 240 vitest, đều đạt exit code 0).
   - *Hậu quả:* Việc tồn tại đồng thời 3 con số khác nhau (330, 580, 589) trong cùng một quyển đồ án tạo ra mâu thuẫn nội bộ trực tiếp, làm giảm độ tin cậy của kết quả kiểm thử.
4. **Bất nhất chỉ số đo lường Bounding Box IoU giữa Chương 1 và Hồ sơ chuẩn:**
   - Chương 1 (Bảng 1-1 và Mục 1.3): Khẳng định $\text{IoU} = 0{,}9266 \pm 0{,}0126$.
   - Hồ sơ đề tài (`INFORMATION.md` Mục 2.4 & 5.1): Công bố chỉ tiêu đạt ngưỡng $\text{IoU} \ge 0{,}85$, giá trị đo thực tế trung bình là **$0{,}88$**. Con số $0{,}9266$ chỉ là kết quả cục bộ của riêng nhóm thí nghiệm bóc tách `hybrid_rrf` trên 36 câu hỏi benchmark tại Chương 4. Đưa con số này làm giá trị đại diện toàn hệ thống ở Chương 1 là không trung thực với dữ liệu nền tảng.
5. **Đưa trước kết quả đo đạc thực nghiệm vào Mục tiêu nghiên cứu ở Chương 1:**
   - Tại Mục 1.3, tác giả chèn các con số đo lường như $\text{IoU} = 0{,}9266$ và tỷ lệ tự sửa lỗi $96\%$ vào mục tiêu. Theo phương pháp luận nghiên cứu, mục tiêu ở Chương 1 chỉ xác định bài toán và ngưỡng kỹ thuật cần chinh phục ($\text{IoU} \ge 0{,}85$, tỷ lệ $\ge 90\%$). Toàn bộ kết quả đo đạc định lượng phải nằm ở Chương 4.
6. **Số liệu suy diễn lý thuyết chưa qua thực chứng (Phỏng đoán 98% dung lượng CAS):**
   - Dòng 13 tệp `1_3_muc_tieu.tex` đưa ra tuyên bố *"tiết kiệm tới 98% dung lượng lưu trữ tệp nhị phân trên máy chủ trong kịch bản 50 học giả cùng nạp một bài báo kinh điển"*. Đây là phép tính số học suy diễn lý thuyết thuần túy, hoàn toàn không có bài benchmark thực nghiệm đo kịch bản 50 học giả.
7. **Nhầm lẫn kỹ thuật về bộ tìm kiếm toàn văn FTS trong PostgreSQL:**
   - Mục 1.3 khẳng định cơ chế tìm kiếm từ vựng của PostgreSQL *"kết hợp tái chấm điểm Okapi BM25"*. Trong thực tế mã nguồn `apps/api/src/api/services/session_chat_service.py`, hệ thống sử dụng hàm tính mật độ bao phủ **`ts_rank_cd`** của PostgreSQL trên chỉ mục GIN `tsvector`. PostgreSQL mặc định không có thuật toán Okapi BM25 (chỉ là lý thuyết đối chiếu).
8. **Biểu đồ lớp (Hình 3-10) gán sai phương thức vi phạm Kiến trúc Lục giác & DDD:**
   - Sơ đồ lớp gán các phương thức database `cosine_sim()` và `bm25_match()` trực tiếp vào thực thể miền `DocumentChunk`, và gán phương thức gọi đám mây `compile_e2b()` vào thực thể miền `Draft`. Trong Kiến trúc Lục giác của VeriScholar, các thực thể Domain tại `packages/core/` là thực thể dữ liệu thuần túy (POPO/Pydantic), tuyệt đối không chứa logic I/O hay kết nối hạ tầng.
   - Các tên trường trong sơ đồ lớp bị đặt sai lệch so với mã nguồn SQLAlchemy (`session_title` thay vì `title`, `latex_content` thay vì `content`, `template_type` thay vì `template`, `blob_hash` thay vì `blob_id`).
9. **Sơ đồ ERD (Hình 3-12) cắt xén tùy tiện, bỏ sót 8 bảng CSDL:**
   - Mặc dù Bảng 3.2 khẳng định hệ thống có 20 bảng chuẩn hóa, nhưng sơ đồ ERD chỉ vẽ đúng 12 bảng, âm thầm bỏ sót toàn bộ 4 bảng của phân hệ GraphRAG (`graph_nodes`, `graph_edges`, `folder_community_summaries`, `wiki_pages`) và 4 bảng nghiệp vụ trọng yếu khác (`document_summaries`, `session_documents`, `research_notes`, `draft_assets`). Tên cột khóa ngoại bảng `RESEARCH_SESSIONS` cũng bị ghi sai thành `active_doc_id` (mã nguồn là `active_document_id`).
10. **Làm sai lệch bản chất an ninh của mô hình BYOK:**
    - Mục 3.4.2 xếp tính năng BYOK (Bring Your Own Key) vào Use Case quản trị của Quản trị viên (`Bảo vệ kho khóa API mã hóa AES-256-GCM`). Về mặt kiến trúc bảo mật, BYOK là cơ chế két khóa cá nhân của Học giả, mã hóa đầu cuối và giải mã tạm thời trên RAM; Quản trị viên hoàn toàn không có quyền hạn can thiệp vào khóa này.

---

### 2.4. Nhóm 4: Lỗi quy chuẩn format, bảng biểu, trích dẫn và văn phong học thuật (Layout & Academic Typography)

1. **100% bảng biểu ở Chương 3 và Chương 4 vi phạm quy chuẩn `tabularx`:**
   - Căn cứ `AGENTS.md` Mục 2.5.4, mọi bảng biểu chứa văn bản dài bắt buộc phải dùng `\begin{tabularx}{\textwidth}{|...|}` với cột co giãn `X` để bảng tự động co giãn vừa khít lề khả dụng $15{,}0 \text{ cm}$.
   - Thực tế: Toàn bộ **24/24 bảng ở Chương 3** và **4/4 bảng ở Chương 4** đều sử dụng `\begin{tabular}{|...|}` với các cột độ rộng cố định bằng xentimét (`p{2.9cm}`, `p{4.0cm}`, `p{5.2cm}`). Điều này làm bảng bị thụt lệch lề phải hoặc gây tràn lề không chuyên nghiệp.
2. **100% đối tượng trôi nổi (Floats) lạm dụng tham số cưỡng bức `[H]`:**
   - Toàn bộ 23 floats ở Chương 2, 12 floats ở Chương 3 và 16 floats ở Chương 4 đều sử dụng tham số vị trí cứng nhắc `[H]`. Khi gặp các hình vẽ hoặc bảng lớn, XeLaTeX bị ép phải đẩy toàn bộ khối sang trang mới, để lại khoảng trống trắng khổng lồ (Bottom Gaps) ở chân trang giấy trước đó. Cần đổi toàn bộ sang `[!htbp]` linh hoạt theo quy chuẩn Anti-Bottom-Gap của `AGENTS.md`.
3. **Lỗi đặt tiêu đề Bảng biểu ở PHÍA DƯỚI Bảng:**
   - Tại Chương 2, Bảng `tab:search_comparison` đặt lệnh `\caption` ngay phía dưới `\end{tabular}`. Đây là lỗi sơ đẳng vi phạm quy chế HUMG (Đầu đề Bảng phải ở TRÊN bảng, đầu đề Hình phải ở DƯỚI hình).
4. **Vấn nạn "Zero Citations" — Hoàn toàn vắng bóng trích dẫn học thuật tại Chương 3 và Chương 4:**
   - Mặc dù Chương 3 và Chương 4 mô tả chi tiết hàng loạt công trình và thuật toán kinh điển trong danh mục 20 tài liệu tham khảo chính thức (RRF của Cormack et al., BM25 của Robertson, HNSW của Malkov, CRAG của Yan et al., ReAct của Yao et al., Louvain của Blondel et al., GraphRAG của Edge et al., AES-GCM của NIST SP 800-38D, E2B Firecracker của Agache et al.), nhưng **trong suốt 56 trang in của Chương 3 và Chương 4, số lượng lệnh `\cite{...}` bằng 0 tuyệt đối**.
   - Đây là lỗi vi phạm nghiêm trọng tính liêm chính và tính liên kết học thuật của một đồ án tốt nghiệp đại học.
5. **Tiêu đề tiểu mục đặt theo dạng câu hỏi ngô nghê ("... là gì?"):**
   - Chương 2 có tới **11 tiểu mục vi phạm**: `PostgreSQL là gì?`, `Redis là gì?`, `Hexagonal Architecture là gì?`, `RAG là gì?`, `Advanced RAG là gì?`, `GraphRAG là gì?`, `Knowledge Graph là gì?`, `Graph Wiki là gì?`, `LangGraph là gì?`, `E2B Sandbox là gì?`, `Langfuse là gì?`. Phong cách này biến đồ án đại học thành bài viết blog hỏi-đáp trên Internet.
   - 8/9 tiêu đề mục cấp 1 ở Chương 2 mở đầu bằng cụm từ kể lể hoặc động từ: "Tổng quan về...", "Tìm hiểu về...".
6. **Lỗi dấu ngoặc kép và khoảng trắng trong môi trường XeLaTeX:**
   - Tại Chương 1 (`1_1_gioi_thieu.tex`), sử dụng dấu nháy kép đóng `''Xây dựng...''` ở đầu cụm từ, khiến bản in hiển thị thành hai dấu phẩy trên quay sang phải.
   - Sử dụng lệnh `\VS\` chèn thêm dấu gạch chéo thoát cách sau macro `\VS` (vốn đã có gói `xspace`), gây lỗi nhân đôi khoảng trắng (*double spaces*) hàng loạt vị trí.
7. **Lỗi thể thức đồ họa và văn bản trên hai trang bìa:**
   - Cả Bìa chính và Bìa trong đều sử dụng chuỗi gạch nối bàn phím thô sơ `---------------------------------------` làm đường kẻ phân cách thay vì dùng lệnh kẻ chuẩn `\rule{6.5cm}{1.0pt}`.
   - Cỡ chữ các dòng cơ quan, chuyên ngành, tên đề tài trên Bìa chính bị hạ xuống 15pt thay vì đúng chuẩn 16pt theo Phụ lục 01 HUMG.
   - Mã TikZ định vị 2 chuỗi chữ gáy sách (`ĐÀM MẠNH DŨNG` và `HỆ THỐNG THÔNG TIN VÀ TRI THỨC`) xoay dọc $-90^\circ$ nằm đè sát mép trái trang bìa ngoài A4, tạo cảm giác như lỗi tràn chữ.
8. **Thiếu sót thủ tục hành chính học thuật:**
   - Phiếu giao đề tài bị gộp nhầm nội dung "Lời cam đoan của sinh viên", làm mất đi vị trí ký duyệt bắt buộc của **Trưởng Bộ môn Hệ thống thông tin và Tri thức**.
   - Đề cương ĐATN 10 tuần bỏ quên mốc **Báo cáo tiến độ Tuần 6 với Bộ môn** (cột mốc giữa kỳ bắt buộc theo quy chế HUMG).
   - Lời cảm ơn thiếu khối địa danh, ngày tháng và chữ ký xác nhận của tác giả ở chân trang.
   - Lời mở đầu thiếu 2 đoạn văn định danh tường minh **Đối tượng nghiên cứu** và **Phạm vi nghiên cứu**.
   - Danh mục từ viết tắt bỏ sót các thuật ngữ cốt lõi (`CRAG`, `CSDL`, `AES-GCM`, `REST`, `E2B`, `UI/UX`, `SQL`) và chứa các từ quá phổ thông (`PDF`, `AI`, `UML`, `ERD`).
   - Sử dụng các cụm từ tham chiếu tương đối bị cấm: "ở trên", "nêu trên", "ở các mục trước".
   - Trùng lặp 2 nhãn `\label` cho cùng một bảng đặc tả Use Case tại Chương 3.

---

## PHẦN III: MA TRẬN ĐÁNH GIÁ TOÀN BỘ HÌNH ẢNH / SƠ ĐỒ TRÊN TOÀN ĐỒ ÁN

### 3.1. Thống kê tổng thể đối tượng đồ họa trong toàn bộ đồ án
Khảo sát toàn văn báo cáo qua các tệp nguồn `.tex` và danh mục hình ảnh `main.lof`:
- **Tổng số hình ảnh / sơ đồ hiện tại:** **52 hình**
  - Frontmatter: **1 hình** (Logo tròn HUMG trên trang bìa chính).
  - Chương 1: **0 hình** (chỉ có 1 bảng đối sánh tính năng Bảng 1-1).
  - Chương 2: **23 hình** (11 ảnh bitmap PNG logo tải từ Internet + 12 sơ đồ vector TikZ).
  - Chương 3: **12 hình** (100% là sơ đồ vector TikZ).
  - Chương 4: **16 hình** (1 sơ đồ TikZ kiến trúc UI + 10 ảnh chụp màn hình UI + 5 ảnh dashboard giám sát).
  - Kết luận & Backmatter: **0 hình**.
- **Tổng số bảng biểu hiện tại:** **30 bảng biểu** (Ch1: 1 bảng, Ch2: 1 bảng, Ch3: 24 bảng, Ch4: 4 bảng).

---

### 3.2. Danh mục chi tiết 25 hình ảnh / sơ đồ KIẾN NGHỊ LOẠI BỎ (BỎ)
Hội đồng thống nhất kiến nghị **LOẠI BỎ TRIỆT ĐỂ 25 HÌNH ẢNH / SƠ ĐỒ DƯ THỪA** (chiếm tỷ lệ cắt giảm **$48{,}1\%$** tổng số hình ảnh), giải phóng trực tiếp hơn **20 trang in** bị lãng phí:

| STT | Vị Trí Xuất Hiện (Tệp & Dòng) | Mã Nhãn (`\label`) | Tiêu Đề / Định Dạng Hình Ảnh | Lý Do Kỹ Thuật & Luận Giải Loại Bỏ |
| :---: | :--- | :--- | :--- | :--- |
| **1** | `chapters/ch2/2_1_postgresql_redis.tex:11` | `fig:logo_postgresql` | Logo PostgreSQL (Ảnh PNG) | **Rác đồ họa.** Ảnh logo con voi tải từ mạng; không có hàm lượng nghiên cứu ĐATN. |
| **2** | `chapters/ch2/2_1_postgresql_redis.tex:44` | `fig:logo_redis` | Logo Redis (Ảnh PNG) | **Rác đồ họa.** Ảnh logo tải từ mạng; chiếm dụng diện tích trang in. |
| **3** | `chapters/ch2/2_3_advanced_rag.tex:20--77` | `fig:naive_rag` | Mô hình Naive RAG (Sơ đồ TikZ) | **Không áp dụng.** Sơ đồ chiếm hơn nửa trang in mô tả kiến trúc RAG sơ cấp mà hệ thống không dùng. |
| **4** | `chapters/ch2/2_4_knowledge_graph_wiki.tex:13--90` | `fig:graphrag_arch` | Mô hình GraphRAG khái niệm (Sơ đồ TikZ) | **Trùng lặp.** Sơ đồ luồng khái niệm trừu tượng sao chép từ Microsoft Research; trùng nội dung với sơ đồ thực thể Hình 2-8. |
| **5** | `chapters/ch2/2_5_agentic_react.tex:21--116` | `fig:react_agent_loop` | Mô hình 4 trụ cột Agent (Sơ đồ TikZ) | **Lý thuyết giáo trình.** Sơ đồ 4 khối của Lilian Weng mang tính đại cương; làm loãng kiến trúc ReAct thực tế. |
| **6** | `chapters/ch2/2_5_agentic_react.tex:130--212` | `fig:planning_pattern` | Planning Pattern (Sơ đồ TikZ) | **Mô tả ảo / Không dùng.** Hệ thống không cài đặt tầng lập kế hoạch tách rời (văn bản dòng 223 đã thừa nhận). |
| **7** | `chapters/ch2/2_5_agentic_react.tex:415--491` | `fig:reflection_pattern_loop` | Reflection Pattern (Sơ đồ TikZ) | **Mô tả ảo / Không dùng.** Hệ thống không dùng vòng lặp LLM tự phê bình đa lượt mà dùng guardrail code (dòng 501 thừa nhận). |
| **8** | `chapters/ch2/2_5_agentic_react.tex:512--588` | `fig:multi_agent_pattern` | Multi-Agent Pattern (Sơ đồ TikZ) | **Mô tả ảo / Sai thực tế.** Hệ thống chỉ chạy Single-Agent ReAct, không có Coordinator đa tác tử (dòng 597 thừa nhận). |
| **9** | `chapters/ch2/2_5_agentic_react.tex:608--680` | `fig:hitl_pattern` | Human-in-the-Loop Pattern (Sơ đồ TikZ) | **Mô tả ảo / Hướng tương lai.** Hệ thống không dùng cơ chế ngắt luồng khóa tiến trình (dòng 690 thừa nhận). |
| **10** | `chapters/ch2/2_6_langgraph.tex:11` | `fig:logo_langgraph` | Logo LangGraph (Ảnh PNG) | **Rác đồ họa.** Logo phần mềm tải từ Internet; vi phạm nghiêm trọng AP-01. |
| **11** | `chapters/ch2/2_7_azure_e2b_byok.tex:11` | `fig:logo_azure` | Logo Microsoft Azure (Ảnh PNG) | **Rác đồ họa.** Logo dịch vụ điện toán đám mây tải từ Internet. |
| **12** | `chapters/ch2/2_7_azure_e2b_byok.tex:29` | `fig:logo_e2b` | Logo E2B Sandbox (Ảnh PNG) | **Rác đồ họa.** Logo nền tảng máy ảo tải từ Internet. |
| **13** | `chapters/ch2/2_8_langfuse.tex:11` | `fig:logo_langfuse` | Logo Langfuse (Ảnh PNG) | **Rác đồ họa.** Logo công cụ quan sát tải từ Internet. |
| **14** | `chapters/ch2/2_9_tools_languages.tex:13` | `fig:logo_python` | Logo Python (Ảnh PNG) | **Lý thuyết sơ cấp.** Logo ngôn ngữ lập trình giáo trình đại cương. |
| **15** | `chapters/ch2/2_9_tools_languages.tex:20` | `fig:logo_fastapi` | Logo FastAPI (Ảnh PNG) | **Lý thuyết sơ cấp.** Logo web framework giáo trình đại cương. |
| **16** | `chapters/ch2/2_9_tools_languages.tex:37` | `fig:logo_react` | Logo React (Ảnh PNG) | **Lý thuyết sơ cấp.** Logo thư viện giao diện giáo trình đại cương. |
| **17** | `chapters/ch2/2_9_tools_languages.tex:53` | `fig:logo_docker` | Logo Docker (Ảnh PNG) | **Lý thuyết sơ cấp.** Logo nền tảng ảo hóa container giáo trình. |
| **18** | `chapters/ch3/3_4_phan_tich_usecase.tex:362--408` | `fig:uc_admin_users_sub` | Sơ đồ Use Case con Quản trị người dùng & BYOK (TikZ) | **Không có UI thực tế.** Hệ thống không có giao diện Admin; các tác vụ bảo mật là cơ chế nền tảng, không cần vẽ Use Case con. |
| **19** | `chapters/ch3/3_4_phan_tich_usecase.tex:443--489` | `fig:uc_admin_logs_sub` | Sơ đồ Use Case con Giám sát hệ thống (TikZ) | **Không có UI thực tế.** Thao tác benchmark và telemetry là công việc vận hành/thực nghiệm đã mô tả ở Chương 4; không phải Use Case ứng dụng. |
| **20** | `chapters/ch4/4_2_giao_dien.tex:121` | `fig:ui_register` | Giao diện Đăng ký tài khoản (`register.png`) | **Không có giá trị khoa học.** Màn hình form đăng ký tiêu chuẩn, 80% là khoảng tối rỗng; chiếm trọn 1 trang in vô ích. |
| **21** | `chapters/ch4/4_2_giao_dien.tex:134` | `fig:ui_login` | Giao diện Đăng nhập hệ thống (`login.png`) | **Không có giá trị khoa học.** Form đăng nhập tiêu chuẩn tương tự đăng ký; chiếm trọn thêm 1 trang in. |
| **22** | `chapters/ch4/4_2_giao_dien.tex:153` | `fig:ui_dashboard` | Bảng điều khiển trung tâm (`dashboard.png`) | **Trùng lặp.** Màn hình dashboard rỗng chỉ có thanh tìm kiếm; hoàn toàn trùng lặp với màn hình tìm kiếm bài báo Hình 4-5. |
| **23** | `chapters/ch4/4_4_so_lieu.tex:104` | `fig:monitor_azure` | Biểu đồ Azure Monitor (`azure_monitor.png`) | **Dính lỗi hiển thị.** Ảnh dính popup cảnh báo "No data returned matching the selected filters"; không đạt chuẩn minh chứng thực nghiệm. |
| **24** | `chapters/ch4/4_4_so_lieu.tex:124` | `fig:monitor_exa` | Biểu đồ sử dụng Exa AI (`exa_usage.png`) | **Dư thừa.** Chỉ ghi 828 requests API; thông tin này trình bày bằng văn bản là đủ, không cần chiếm 1 trang in. |
| **25** | `chapters/ch4/4_4_so_lieu.tex:162` | `fig:monitor_langfuse_dashboard`| Bảng điều khiển chi phí Langfuse (`langfuse_dashboard.jpg`) | **Trùng lặp.** Bảng chi phí 24h trùng lặp với Hình 4-12 và Báo cáo OpenAI; gộp số liệu vào bảng tổng hợp. |

---

### 3.3. Danh mục các hình ảnh KIẾN NGHỊ SỬA / GỘP
Đối với các hình ảnh có giá trị kỹ thuật nhưng đang mắc lỗi trình bày hoặc sai lệch nội dung:

1. **`fig:ui_deep_read_paper` (`figures/frontend/deep_read_paper.png` — Chương 4):**
   - *Hành động bắt buộc:* **CHỤP LẠI ẢNH MỚI 100%**. Ảnh mới phải ghi lại trạng thái hệ thống đang kích hoạt lớp phủ Canvas vẽ khung viền vàng bao quanh đoạn trích gốc (Bounding Box) trên trang bài báo PDF hai cột để khớp tuyệt đối với lời văn và chỉ số $\text{IoU} \ge 0{,}85$.
2. **`fig:class_diagram_model` (Biểu đồ lớp thực thể — Chương 3 dòng 14--243):**
   - *Hành động:* Tái cấu trúc TikZ từ 4 cột sang 3 cột thoáng hơn, nâng tỷ lệ `scale` từ $0.52$ lên $\ge 0.62$. Xóa bỏ các phương thức truy vấn DB (`cosine_sim`, `bm25_match`) khỏi `DocumentChunk`; xóa `compile_e2b` khỏi `Draft`. Chuẩn hóa các tên trường khớp $100\%$ mã nguồn SQLAlchemy (`title`, `content`, `template`, `blob_id`).
3. **`fig:erd_model` (Lược đồ quan hệ thực thể ERD — Chương 3 dòng 720--926):**
   - *Hành động:* Khắc phục việc thiếu 8 bảng CSDL. Để sơ đồ không bị thu nhỏ quá mức (scale $0.52$ chữ rất bé), đề xuất **TÁCH THÀNH 2 PHÂN HỆ SƠ ĐỒ ĐỘC LẬP**:
     - *Sơ đồ 1:* ERD Phân hệ Định danh, Lưu trữ CAS và Hội thoại Đọc sâu (10 bảng, scale $0.68$).
     - *Sơ đồ 2:* ERD Phân hệ Đồ thị Tri thức GraphRAG và Soạn thảo Bản thảo (10 bảng, scale $0.68$).
4. **`fig:react_pattern_loop` kết hợp `fig:tool_use_pattern` (Chương 2):**
   - *Hành động:* Hợp nhất 2 sơ đồ riêng lẻ thành **1 Sơ đồ TikZ duy nhất** mô tả Vòng lặp ReAct của Tác nhân tự sửa lỗi bản thảo LaTeX gọi công cụ thực thi mã trong môi trường máy ảo E2B MicroVM.
5. **`fig:usecase_overview` (Biểu đồ Use Case tổng quan — Chương 3 dòng 7--66):**
   - *Hành động:* Xóa đường liên kết từ Actor Admin nối vào Use Case "Quản lý ORCID và Khóa BYOK" (vì đây là quyền riêng tư của Scholar); làm nổi bật Use Case "Khai phá Đồ thị tri thức (GraphRAG)".
6. **`fig:uc_doc_sau_sub` (Sơ đồ Use Case con Đọc sâu — Chương 3 dòng 177--225):**
   - *Hành động:* Chuyển tính năng "Thiết lập khóa API BYOK" từ quan hệ `<<extend>>` thành Điều kiện tiên quyết (Precondition).
7. **`fig:ui_search_paper` (`search_paper.png` — Chương 4):**
   - *Hành động:* Crop gọn 4 viền, tập trung vào thẻ bài báo và nút lọc bình duyệt, loại bỏ khoảng tối dư thừa để hình ảnh sắc nét.

---

### 3.4. Danh mục các sơ đồ KIẾN NGHỊ BỔ SUNG MỚI
Bổ sung **02 sơ đồ kỹ thuật hạt nhân** để hoàn thiện lỗ hổng học thuật của đồ án:

1. **SƠ ĐỒ BỔ SUNG 1 — Sơ đồ Kiến trúc Lục giác Tổng thể Hệ thống (Overall Hexagonal Architecture & 4 Spaces):**
   - *Vị trí:* Đặt tại Mục 3.3 (mới) của Chương 3.
   - *Nội dung:* Vẽ bằng TikZ vector chuẩn mực, thể hiện 3 phân vùng độc lập: Lõi miền nghiệp vụ thuần khiết (`packages/core`), Tầng Cổng trừu tượng (Driving & Driven Ports), và Tầng Bộ điều hợp hạ tầng (`apps/api`, `apps/web`, PostgreSQL 16 pgvector, Redis, E2B MicroVM, arXiv/CrossRef API) liên kết xuyên suốt mô hình 4 Không gian (Discovery, Deep Reading, Knowledge Library, Writing Studio).
2. **SƠ ĐỒ BỔ SUNG 2 — Sơ đồ Phân rã Use Case hoặc Biểu đồ tuần tự Phân hệ Đồ thị Tri thức (GraphRAG Pipeline):**
   - *Vị trí:* Đặt tại Mục 3.4 hoặc 3.5 của Chương 3 (thay thế vị trí của 2 sơ đồ Admin bị loại bỏ).
   - *Nội dung:* Mô hình hóa chu trình trích xuất 4 thực thể học thuật (`Paper`, `Method`, `Dataset`, `MetricResult`), khử trùng lặp đỉnh bằng Cosine $\ge 0{,}90$, thuật toán phân cụm Louvain và truy vấn bắc cầu 2-hop Graph Traversal — bảo vệ trọn vẹn Đóng góp kỹ thuật số 3 của đề tài.

---

## PHẦN IV: DANH MỤC CÁC ĐIỂM CẦN CHỈNH SỬA ƯU TIÊN (MA TRẬN P0 - P1 - P2 - P3)

Để công tác hiệu chỉnh đồ án diễn ra khoa học, chuẩn xác và không gây xung đột mã nguồn, Hội đồng phân cấp toàn bộ các nhiệm vụ theo **Ma trận Ưu tiên 4 Cấp độ**:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   MA TRẬN ƯU TIÊN HIỆU CHỈNH TOÀN DIỆN ĐỒ ÁN                     │
├──────────────────────────────────────────────────────────────────────────────────┤
│ CẤP ĐỘ P0: LỖI CẤU TRÚC BIÊN DỊCH & LIÊM CHÍNH HỌC THUẬT (Sửa ngay lập tức)     │
│   • Khôi phục Section 4.3 & 4.4; Bổ sung Tên đề tài vào Bìa phụ.                 │
│   • Triệt tiêu đề mục cấp 5 (4.1.3.0.1); Chụp lại ảnh BBox vàng; Xóa ảnh lỗi.    │
│   • Đồng bộ số test 580 toàn văn; Khóa cứng IoU 0.88; Sửa Class Diagram & ERD.  │
├──────────────────────────────────────────────────────────────────────────────────┤
│ CẤP ĐỘ P1: CẮT GIẢM NỘI DUNG DƯ THỪA & LOẠI BỎ HÌNH ẢNH RÁC (Giảm 35--40 trang) │
│   • Xóa bỏ 11 logo PNG mạng + 7 TikZ lý thuyết Ch2; Xóa Mục 2.9 (Python/Docker). │
│   • Thu gọn 16 bảng CSDL Ch3 (chuyển 11 bảng vào Phụ lục); Xóa 2 Use Case Admin. │
│   • Cắt bỏ 5 hình ảnh rác Ch4; Cắt bỏ hướng dẫn cài đặt VS Code / npm install.  │
├──────────────────────────────────────────────────────────────────────────────────┤
│ CẤP ĐỘ P2: CHUẨN HÓA FORMAT, BẢNG BIỂU VÀ VĂN PHONG THEO HUMG (Layout Compliance)│
│   • Đổi 100% bảng sang tabularx \textwidth; Đổi 100% floats sang [!htbp].        │
│   • Đưa caption Bảng 2.1 lên TRÊN; Triệt tiêu 11 tiêu đề "... là gì?".           │
│   • Sửa ngoặc kép XeLaTeX; Sửa macro \VS\; Sửa đường kẻ bìa; Sửa chữ gáy sách.   │
│   • Bổ sung chữ ký Trưởng Bộ môn, mốc Tuần 6, chữ ký Lời cảm ơn, Đối tượng/Phạm vi│
├──────────────────────────────────────────────────────────────────────────────────┤
│ CẤP ĐỘ P3: BỔ SUNG NỘI DUNG HỌC THUẬT CHUYÊN SÂU & TRÍCH DẪN (Academic Rigor)    │
│   • Xóa sạch Zero Citations: Bổ sung trích dẫn \cite cho Ch1, Ch3, Ch4.         │
│   • Bổ sung Mục Thiết kế Kiến trúc Lục giác 3.3 và sơ đồ GraphRAG vào Ch3.       │
│   • Bổ sung công thức hàm Modularity Q và Bảng đối chứng "Tại sao chọn" vào Ch2.│
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

### Bảng kế hoạch triển khai chi tiết từng nhiệm vụ (Actionable Tasks):

| Mức Ưu Tiên | Mã Nhiệm Vụ | Tệp Nguồn Mục Tiêu | Nội Dung Thao Tác Cụ Thể | Kết Quả Đầu Ra Bắt Buộc |
| :---: | :---: | :--- | :--- | :--- |
| **P0** | **P0-1** | `chapters/ch4/4_2_giao_dien.tex`<br>`4_3_kiem_thu.tex`<br>`4_4_so_lieu.tex` | Đặt lệnh `\section{...}` cho tệp 4.2, 4.3 và 4.4; khôi phục đúng 4 mục cấp 1 theo `ROADMAP.md`. | Mục lục (`main.toc`) hiển thị rõ ràng 4 mục: 4.1, 4.2, 4.3, 4.4. |
| **P0** | **P0-2** | `frontmatter/bia_phu.tex` | Bổ sung khối **TÊN ĐỀ TÀI** chính thức in hoa đậm ở giữa trang; rút ngắn khoảng cách `[4.0cm]` xuống mức cân đối. | Trang bìa phụ có đầy đủ tên đề tài, cân đối, đúng Phụ lục 02 HUMG. |
| **P0** | **P0-3** | `chapters/ch4/4_1_moi_truong.tex` | Thay thế 4 lệnh `\paragraph{...}` bằng danh sách `\begin{itemize}`. | Triệt tiêu hoàn toàn đề mục cấp 5 (`4.1.3.0.1` đến `4.1.3.0.4`) trong mục lục. |
| **P0** | **P0-4** | `chapters/ch4/4_2_giao_dien.tex`<br>`figures/frontend/deep_read_paper.png` | Chụp lại ảnh màn hình thực tế có khung Bounding Box viền vàng bao quanh đoạn trích trên canvas PDF. | Minh chứng trực quan khớp $100\%$ với lời văn và chỉ số $\text{IoU} \ge 0{,}85$. |
| **P0** | **P0-5** | `chapters/ch4/4_4_so_lieu.tex` | Loại bỏ hình ảnh `azure_monitor.png` dính popup lỗi "No data returned"; chuyển chỉ số CPU/RAM thành văn bản. | Xóa bỏ minh chứng thực nghiệm bị lỗi giao diện. |
| **P0** | **P0-6** | `frontmatter/phieu_giao_de_tai.tex` | Sửa cụm từ *"hơn 330 kịch bản"* tại dòng 84 thành *"580 kịch bản kiểm thử tự động (340 Backend pytest và 240 Frontend vitest)"*. | Đồng bộ số liệu kiểm thử $100\%$ giữa Phiếu giao, Mở đầu, Ch4, Kết luận và SSOT. |
| **P0** | **P0-7** | `chapters/ch1/1_2_tinh_cap_thiet.tex`<br>`chapters/ch1/1_3_muc_tieu.tex` | Sửa chỉ số IoU thành $\text{IoU} \ge 0{,}85$ (thực tế $0{,}88$); xóa bỏ việc đưa trước kết quả thực nghiệm vào mục tiêu; xóa số liệu phỏng đoán $98\%$ CAS. | Chương 1 bảo đảm tính liêm chính, không mâu thuẫn số liệu với SSOT. |
| **P0** | **P0-8** | `chapters/ch3/3_6_thiet_ke_csdl.tex` | Sửa Class Diagram (Hình 3-10): Xóa phương thức DB khỏi `DocumentChunk`, xóa `compile_e2b` khỏi `Draft`; sửa tên thuộc tính khớp SQLAlchemy models. | Sơ đồ lớp tuân thủ Kiến trúc Lục giác và DDD của VeriScholar. |
| **P0** | **P0-9** | `chapters/ch3/3_6_thiet_ke_csdl.tex` | Tái cấu trúc sơ đồ ERD: Bổ sung đủ 20 bảng CSDL (tách làm 2 phân hệ chuyên biệt để scale $\ge 0.68$). | Lược đồ ERD phản ánh trung thực toàn bộ 20 bảng quan hệ của hệ thống. |
| **P1** | **P1-1** | `chapters/ch2/` (Toàn bộ) | Xóa bỏ toàn bộ 11 lệnh chèn ảnh logo PNG mạng; xóa bỏ 7 sơ đồ TikZ lý thuyết không dùng; xóa bỏ tệp `2_9_tools_languages.tex`. | Giải phóng trực tiếp 14 -- 16 trang giấy dư thừa của Chương 2. |
| **P1** | **P1-2** | `chapters/ch2_co_so_ly_thuyet.tex` | Tái cấu trúc phân rã Chương 2 từ 9 mục manh mún về đúng 5 mục lớn chuẩn mực theo `ROADMAP.md`. | Bố cục Chương 2 cô đọng, chuyên sâu, đúng chuẩn nghiên cứu học thuật. |
| **P1** | **P1-3** | `chapters/ch3/3_6_thiet_ke_csdl.tex` | Giữ lại Bảng tổng hợp 20 bảng (Bảng 3.2), chọn 4--5 bảng hạt nhân đặc tả trong thân bài; chuyển 11 bảng còn lại sang Phụ lục A. | Cắt giảm ngay 6 -- 8 trang in nghẽn chữ, làm gọn danh mục bảng biểu. |
| **P1** | **P1-4** | `chapters/ch3/3_4_phan_tich_usecase.tex` | Xóa bỏ 2 sơ đồ Use Case con Hình 3-5, Hình 3-6 và 2 bảng đặc tả BA Bảng 3.5, Bảng 3.6 của Quản trị viên. | Tiết kiệm 2 -- 3 trang in, loại bỏ các tác vụ không có giao diện người dùng. |
| **P1** | **P1-5** | `chapters/ch3/3_1_mo_ta_bai_toan.tex` | Xóa bỏ hoặc chuyển hóa Mục 3.1 thành lời dẫn nhập khảo sát yêu cầu; loại bỏ đoạn văn trùng lặp với Chương 1. | Tiết kiệm 1 trang in, chống trùng lặp cấu trúc đề mục. |
| **P1** | **P1-6** | `chapters/ch4/4_2_giao_dien.tex`<br>`4_4_so_lieu.tex` | Loại bỏ 4 hình ảnh dư thừa (`register.png`, `login.png`, `dashboard.png`, `exa_usage.png`) và các đoạn thuyết minh tương ứng. | Tiết kiệm trực tiếp 4 trang in của Chương 4. |
| **P1** | **P1-7** | `chapters/ch4/4_1_moi_truong.tex` | Cắt bỏ 2 đoạn văn cẩm nang cài đặt VS Code, `uv sync`, `npm install`; tinh gọn Bảng 4.1 cấu trúc Monorepo. | Tiết kiệm 1 -- 2 trang in, nâng tầm văn phong báo cáo. |
| **P2** | **P2-1** | Toàn bộ các chương (Ch1--4) | Chuyển đổi toàn bộ môi trường bảng `\begin{tabular}{|...|}` sang `\begin{tabularx}{\textwidth}{|...|}` với cột `X`. | 100% bảng biểu vừa vặn khung in $15{,}0 \text{ cm}$, tự động ngắt dòng, không vỡ layout. |
| **P2** | **P2-2** | Toàn bộ các chương (Ch2--4) | Thay thế 100% tham số vị trí cưỡng bức `[H]` của floats thành `[!htbp]`. | Triệt tiêu hoàn toàn hiện tượng khoảng trắng đáy trang (Anti-Bottom-Gap). |
| **P2** | **P2-3** | `chapters/ch2/2_3_advanced_rag.tex` | Chuyển lệnh `\caption{...}` của Bảng `tab:search_comparison` lên PHÍA TRÊN bảng. | Tuân thủ 100% quy chế vị trí tiêu đề bảng biểu của HUMG. |
| **P2** | **P2-4** | `chapters/ch2/` (Các tệp con) | Danh ngữ hóa toàn bộ 11 tiêu đề tiểu mục "... là gì?" và 8 tiêu đề mục "Tổng quan về...", "Tìm hiểu về...". | Văn phong học thuật chuẩn mực, xóa bỏ phong cách blog hỏi-đáp. |
| **P2** | **P2-5** | `chapters/ch1/1_1_gioi_thieu.tex`<br>`commands.tex` | Sửa dấu nháy kép mở đầu thành ` ``...'' `; thay toàn bộ `\VS\` bằng `\VS ` (loại bỏ gạch chéo thoát cách). | Khắc phục lỗi in ấn nháy kép ngược và lỗi nhân đôi khoảng trắng. |
| **P2** | **P2-6** | `frontmatter/bia_chinh.tex`<br>`bia_phu.tex` | Thay chuỗi gạch nối `-------` bằng `\rule{6.5cm}{1.0pt}`; xóa mã TikZ chữ gáy sách đè mặt bìa; nâng cỡ chữ lên 16pt. | Hai trang bìa trang trọng, sắc nét, đúng chuẩn Phụ lục 01 & 02 HUMG. |
| **P2** | **P2-7** | `frontmatter/phieu_giao_de_tai.tex` | Tách phần Lời cam đoan; bổ sung vị trí chữ ký duyệt của **Trưởng Bộ môn Hệ thống thông tin và Tri thức**. | Hoàn thiện tính pháp lý hành chính của Phiếu giao đề tài. |
| **P2** | **P2-8** | `frontmatter/de_cuong_datn.tex` | Bổ sung nội dung *"Cột mốc giữa kỳ: Báo cáo tiến độ đồ án với Bộ môn và GVHD"* vào kế hoạch Tuần 6. | Tuân thủ nghiêm ngặt quy chế đánh giá tiến độ của Khoa CNTT — HUMG. |
| **P2** | **P2-9** | `frontmatter/loi_cam_on.tex`<br>`loi_mo_dau.tex` | Bổ sung khối địa danh, ngày tháng và chữ ký SV vào Lời cảm ơn; bổ sung định danh Đối tượng & Phạm vi vào Lời mở đầu. | Hoàn thiện thể thức văn bản đầu đồ án theo cẩm nang HUMG. |
| **P2** | **P2-10**| `frontmatter/danh_muc_viet_tat.tex`| Bổ sung: `CRAG`, `CSDL`, `AES-GCM`, `REST`, `E2B`, `UI/UX`, `SQL`; loại bỏ: `PDF`, `AI`, `UML`, `ERD`. | Bảng từ viết tắt chuyên sâu, đúng trọng tâm kỹ thuật của đề tài. |
| **P2** | **P2-11**| `chapters/ch3/` | Sửa tiêu đề trùng lặp 3.6 và 3.6.2; xóa 1 nhãn trùng lặp tại 2 bảng Use Case; xóa các từ "ở trên", "nêu trên". | Cấu trúc đề mục sạch sẽ, liên kết tham chiếu chéo tường minh. |
| **P2** | **P2-12**| `chapters/ch4/4_1_moi_truong.tex`<br>`4_2_giao_dien.tex` | Khắc phục triệt để 5 cảnh báo Overfull `\hbox` bằng `\allowbreak` và căn chỉnh văn bản. | Bản in PDF sạch sẽ, không có dòng nào đâm thủng lề phải. |
| **P3** | **P3-1** | `chapters/ch3/`<br>`chapters/ch4/`<br>`chapters/ch1/` | Bổ sung đầy đủ lệnh trích dẫn `\cite{...}` cho các thuật toán nền tảng (RRF, BM25, HNSW, CRAG, ReAct, Louvain, GraphRAG, AES-GCM, E2B). | **Triệt tiêu 100% lỗi Zero Citations**; kết nối trọn vẹn 20 tài liệu tham khảo chính thức vào thân bài. |
| **P3** | **P3-2** | `chapters/ch3/3_3_kien_truc.tex` | Xây dựng mới Mục 3.3: "Thiết kế kiến trúc hệ thống và phân tầng Lục giác" kèm Sơ đồ TikZ Kiến trúc Lục giác & 4 Không gian. | Khắc phục lỗ hổng kiến trúc nghiêm trọng nhất của Chương 3. |
| **P3** | **P3-3** | `chapters/ch3/3_4_phan_tich_usecase.tex` | Bổ sung đặc tả Use Case và Biểu đồ tuần tự cho Phân hệ Đồ thị Tri thức (GraphRAG). | Làm nổi bật Đóng góp kỹ thuật cốt lõi số 3 của đề tài. |
| **P3** | **P3-4** | `chapters/ch2/2_4_knowledge_graph_wiki.tex` | Bổ sung công thức toán học hàm mục tiêu Modularity $Q$ của thuật toán Louvain. | Nâng cao hàm lượng toán học và tính thuyết phục của cơ sở lý thuyết. |
| **P3** | **P3-5** | `chapters/ch2/2_1_postgresql_redis.tex` | Bổ sung Bảng đối chứng "Tại sao chọn" (PostgreSQL pgvector vs Dedicated Vector DB). | Luận giải khoa học sâu sắc, trả lời thuyết phục câu hỏi "Tại sao chọn" của Hội đồng. |

---

## PHẦN V: DỰ BÁO KẾT QUẢ ĐỊNH LƯỢNG SAU TINH GỌN (BEFORE VS. AFTER FORECAST)

Việc thực thi nghiêm túc Lộ trình hành động trên sẽ mang lại sự chuyển biến căn bản, đưa bản báo cáo ĐATN VeriScholar đạt mức độ hoàn thiện xuất sắc theo các tiêu chí đo lường định lượng:

### 5.1. Bảng đối chiếu Trước vs Sau tinh gọn

| Tiêu Chí Đo Lường | Hiện Trạng Trước Tinh Gọn | Dự Báo Sau Khi Tinh Gọn | Mức Độ Chuyển Biến / Hiệu Quả |
| :--- | :---: | :---: | :--- |
| **Tổng số trang in toàn bộ đồ án** | **115 trang** | **78 -- 82 trang** | **Cắt giảm 33 -- 37 trang** (hoàn toàn nằm trong ngân sách vàng $75 \text{ -- } 95$ trang). |
| **Số trang phần Frontmatter** | 16 trang | 14 trang | Tinh gọn 2 trang danh mục, chuẩn hóa bố cục bìa. |
| **Số trang Chương 1** | 7 trang | 6 trang | Cắt giảm số liệu phỏng đoán, đưa kết quả đo lường về Ch4. |
| **Số trang Chương 2** | **29 trang** (phình 241%) | **11 -- 12 trang** | **Cắt giảm 17 -- 18 trang** (đúng ngân sách chuẩn 18% đồ án). |
| **Số trang Chương 3** | **33 trang** (phình 157%) | **20 -- 22 trang** | **Cắt giảm 11 -- 13 trang** (chuyển 11 bảng CSDL vào Phụ lục A). |
| **Số trang Chương 4** | **23 trang** (phình 153%) | **14 -- 15 trang** | **Cắt giảm 8 -- 9 trang** (loại bỏ 5 ảnh rác, bỏ cẩm nang cài đặt). |
| **Số trang Kết luận & TLTK** | 6 trang | 5 trang | Tinh gọn câu từ đúc kết súc tích, chuyên nghiệp. |
| **Số trang Phụ lục kỹ thuật (Mới)** | 0 trang | 6 -- 8 trang | Lưu trữ an toàn 11 bảng từ điển CSDL chi tiết ở cuối sách. |
| **Tổng số hình ảnh / sơ đồ** | **52 hình** | **26 -- 28 hình** | **Loại bỏ 25 hình ảnh rác/dư thừa**, sửa 5 hình, bổ sung 2 sơ đồ kiến trúc hạt nhân. |
| **Tỷ lệ hình vẽ vector TikZ nội suy** | $48{,}1\%$ (nhiều ảnh logo PNG) | **$\ge 85\%$** | $100\%$ sơ đồ kiến trúc đạt chuẩn vector in ấn siêu nét, sạch bóng rác logo. |
| **Tổng số bảng biểu trong thân bài** | 30 bảng | 13 -- 14 bảng | Thân bài thoáng đãng, các bảng dài được chuyển vào Phụ lục. |
| **Tỷ lệ bảng chuẩn `tabularx \textwidth`**| $6{,}7\%$ (chỉ 2 bảng dùng) | **$100\%$** | Không còn bất kỳ bảng nào bị thụt thò hay đâm thủng lề. |
| **Tỷ lệ Floats dùng `[!htbp]` linh hoạt** | $0\%$ (100% dùng `[H]`) | **$100\%$** | Triệt tiêu hoàn toàn khoảng trống lớn ở đáy trang in (Bottom Gaps). |
| **Số lượng trích dẫn `\cite` ở Ch3 & Ch4** | **0 trích dẫn** (Zero Citations) | **$\ge 25$ vị trí trích dẫn** | Kết nối đầy đủ 20 tài liệu tham khảo chính thống vào thân bài. |
| **Độ sâu phân cấp đề mục tối đa** | 5 cấp (`4.1.3.0.1` vi phạm) | **Tối đa 4 cấp (`X.Y.Z.W`)** | Tuân thủ tuyệt đối quy định phân cấp đề mục của HUMG. |
| **Tính xác thực minh chứng hình ảnh** | Dính lỗi giao diện & Thiếu BBox | **$100\%$ minh chứng thực tế** | Bounding Box viền vàng hiển thị rõ nét trên canvas PDF; xóa ảnh Azure lỗi. |
| **Trạng thái biên dịch XeLaTeX** | Exit code 0, 30 overfull hbox | **Exit code 0, 0 overfull hbox** | Bản in PDF hoàn hảo, không còn bất kỳ cảnh báo tràn dòng nào. |

---

### 5.2. Đánh giá tác động học thuật và Giá trị bảo vệ trước Hội đồng
1. **Khẳng định tính liêm chính và trung thực khoa học tuyệt đối:** Việc loại bỏ hoàn toàn các số liệu phỏng đoán lý thuyết (98%), đồng bộ chuẩn xác số lượng 580 bài kiểm thử qua 4 cổng xác minh, khóa cứng chỉ số $\text{IoU} \ge 0{,}85$ ($0{,}88$ thực tế), và chụp lại ảnh Bounding Box viền vàng thật sẽ bảo vệ tác giả trước bất kỳ câu hỏi chất vấn nào của Hội đồng phản biện.
2. **Làm nổi bật năng lực kỹ nghệ phần mềm chuyên sâu:** Thay vì một bản báo cáo dày đặc lý thuyết sách giáo khoa đại cương (Python, Docker, React), đồ án sau tinh gọn sẽ tập trung toàn bộ dung lượng làm nổi bật 4 đóng góp kỹ thuật cốt lõi:
   - Kiến trúc truy xuất học thuật Hybrid RAG kết hợp RRF ($k=60$) và Cổng kiểm định độ tin cậy CRAG.
   - Cơ chế đọc sâu bảo toàn bố cục 2 cột và kiểm chứng trích dẫn tọa độ viền vàng Bounding Box trên PDF Canvas.
   - Mô hình đồ thị tri thức GraphRAG 4 thực thể học thuật trên cơ sở dữ liệu quan hệ PostgreSQL 16 ACID thuần nhất kết hợp phân cụm Louvain.
   - Môi trường soạn thảo an toàn Writing Studio với Tác nhân ReAct tự phục hồi cú pháp LaTeX trên máy ảo E2B MicroVM và két khóa cá nhân BYOK AES-256-GCM.
3. **Diện mạo học thuật chuẩn mực quốc tế:** Với việc 100% bảng biểu dùng `tabularx \textwidth`, 100% sơ đồ được vẽ bằng mã nguồn TikZ vector sắc nét, tiêu đề được danh ngữ hóa chuyên nghiệp, và hệ thống 20 tài liệu tham khảo chính thống được đan cài chặt chẽ trong từng phân tích, quyển đồ án tốt nghiệp VeriScholar sẽ trở thành một công trình mẫu mực, xứng đáng đạt điểm Xuất sắc cao nhất trong kỳ bảo vệ ĐATN của Khoa Công nghệ Thông tin — Trường Đại học Mỏ - Địa chất.

---

## PHẦN VI: KẾT LUẬN VÀ KIẾN NGHỊ BÀN GIAO

Báo cáo tổng kết toàn diện này đã hoàn thành trọn vẹn sứ mệnh:
1. Đã tiếp thu, đối soát và tổng hợp đầy đủ các phát hiện sâu sắc từ 5 báo cáo độc lập của các tiểu ban chuyên trách.
2. Đã đối chiếu nghiêm ngặt với các văn bản quy chuẩn tối cao: `report-datn/AGENTS.md`, `report-datn/INFORMATION.md`, `report-datn/ROADMAP.md` và bộ tài liệu hướng dẫn của Khoa CNTT — HUMG.
3. Đã vạch ra lộ trình hành động 4 cấp độ (P0 -- P3) vô cùng chi tiết, rõ ràng, có căn cứ kỹ thuật xác đáng và phương án xử lý dứt điểm cho từng tệp nguồn `.tex`.

Hội đồng Tổng hợp ĐATN trân trọng bàn giao bản báo cáo tổng kết này cho Giảng viên hướng dẫn, Nhóm tác giả và các Tác tử biên chế chế bản (`thesis-writer`, `thesis-formatter`) làm kim chỉ nam triển khai công tác tinh gọn và hiệu chỉnh trong giai đoạn hoàn thiện cuối cùng của Đồ án Tốt nghiệp.

---
*Báo cáo được lưu trữ chính thức tại:*  
`/home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn/review_reports/SUMMARY_REVIEW.md`

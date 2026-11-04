# CẨM NANG VẬN HÀNH AI AGENT BIÊN SOẠN BÁO CÁO ĐỒ ÁN TỐT NGHIỆP (AGENTS.md)

> **Cơ sở pháp lý và tiêu chuẩn học thuật ban hành:**  
> - Khoa Công nghệ Thông tin — Trường Đại học Mỏ - Địa chất (HUMG).  
> - Quy chế và Hướng dẫn thực hiện Đồ án Tốt nghiệp Đại học (`report-datn/guide/Huong dan-Quy dinh-DATN.md`).  
> - Hướng dẫn biên soạn và thể thức Đồ án Tốt nghiệp (`report-datn/guide/Huong-dan-viet-DATN.md`).  
> - Mẫu Đề cương Đồ án Tốt nghiệp Đại học (`report-datn/guide/Mau-De-cuong-DATN.md`).  
> - Mẫu Bản nhận xét Đồ án Tốt nghiệp Đại học của Người hướng dẫn (`report-datn/guide/Mẫu_HD_DATN.md`).  
> - Bản đồ Phân rã Cấu trúc Vi mô và Ngân sách Trang (`report-datn/ROADMAP.md`).  
>
> **Ranh giới thẩm quyền và Nguồn chân lý duy nhất (Single Source of Truth):**  
> Tài liệu này là **Cẩm nang Quy chuẩn Biên soạn Tổng quát (How-to Manual and SOP)** quy định phương pháp luận, phong cách hành văn, cấu trúc văn bản, quy chuẩn XeLaTeX, tiêu chuẩn hình bảng và quy trình phối hợp của AI Agent.  
> Toàn bộ thông tin định danh sinh viên, cán bộ hướng dẫn, tên đề tài, cơ sở dữ liệu vật lý, tham số thuật toán, mốc ngày tháng chi tiết và bộ số liệu thực nghiệm được lưu trữ tập trung duy nhất tại **`report-datn/INFORMATION.md`**. AI Agent bắt buộc phải viện dẫn `report-datn/INFORMATION.md` làm căn cứ dữ liệu khi biên soạn.

---

## LỜI NÓI ĐẦU VÀ TÔN CHỈ VẬN HÀNH

Tài liệu `AGENTS.md` này là **Cẩm nang Quy trình Thao tác Chuẩn (SOP — Standard Operating Procedure)** và bộ quy tắc vận hành bắt buộc dành cho tất cả các AI Agent tham gia vào toàn bộ vòng đời nghiên cứu, lập đề cương, thiết kế kiến trúc, biên soạn văn bản, hiệu chỉnh kỹ thuật và chuẩn bị bảo vệ Đồ án Tốt nghiệp (ĐATN) bậc Đại học ngành Công nghệ Thông tin.

Báo cáo đồ án tốt nghiệp đại học không phải là một tập tài liệu ghi chú phát triển phần mềm nội bộ, mà là một **ấn phẩm học thuật chính thức** chịu sự chế tài nghiêm ngặt của Quy chế Đào tạo Đại học, Tiêu chuẩn đánh giá của Hội đồng chấm luận án và Uy tín khoa học của Nhà trường. Do đó, AI Agent không được phép hoạt động theo cảm tính mà phải tuyệt đối tuân thủ 3 tôn chỉ vận hành:

1. **Tuyệt đối trung thực học thuật (Academic Integrity):** Không bịa đặt số liệu thực nghiệm, không sinh trích dẫn ma, không tạo lập cấu trúc cơ sở dữ liệu giả và không tạo facade đối phó kiểm thử. Mọi số liệu thực nghiệm và tham số kỹ thuật phải đối chiếu trung thực với `report-datn/INFORMATION.md`.
2. **Kỹ nghệ thực hành chuyên sâu (Engineering Rigor):** Tập trung làm nổi bật năng lực thiết kế kiến trúc, mô hình dữ liệu, thuật toán lõi và kết quả đo lường định lượng có khả năng tái lập (Reproducibility).
3. **Tuân thủ thể thức tuyệt đối (Layout Compliance):** Mọi trang in, bảng biểu, hình vẽ và công thức toán học phải chuẩn xác theo từng milimét theo quy định của Khoa CNTT — Trường Đại học Mỏ - Địa chất.

### NGUYÊN TẮC TỐI CAO: BẢO TOÀN ĐỊNH DẠNG 100% THEO `guide/HIeu.pdf` VÀ TUYỆT ĐỐI KHÔNG TỰ Ý SÁNG TẠO
- Tài liệu mẫu đối chiếu chuẩn: `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn/guide/HIeu.pdf` (106 trang) là **Thước đo đối chiếu chuẩn mực duy nhất (Gold Standard)** cho mọi khía cạnh hình thức: Bìa ngoài có sườn/gáy, Bìa phụ, Phiếu giao đề tài, Đề cương, Lời cảm ơn, Mục lục không đậm, đánh số trang Ả Rập bắt đầu từ Mục lục, tỷ lệ lề trang 2.5 - 2.5 - 3.5 - 2.5 cm, phông chữ Times New Roman 13pt cho toàn văn bản và bảng biểu, dãn dòng 1.5.
- Mọi điểm chưa rõ hoặc phát sinh trong quá trình biên soạn: AI Agent **BẮT BUỘC** phải mở tệp `HIeu.pdf` ra đối chiếu trực tiếp và làm theo y hệt.
- **NGHIÊM CẤM TUYỆT ĐỐI** tự ý bịa thêm sáng kiến, hướng làm, tự ý sáng tạo kiểu dáng bảng biểu, tự ý đổi màu sắc, tự ý ngắt trang hoặc tự áp đặt các phong cách soạn thảo khác.

### 11 ĐIỀU RĂN BẤT DI BẤT DỊCH TỪ HỒ SƠ HIEU.PDF (THE 11 IMMUTABLE COMMANDMENTS)

Bộ 11 Điều Răn sau đây là **Quy chuẩn Định dạng Tối thượng (Zero-Tolerance Rules)** được đúc kết từ hồ sơ mẫu chuẩn mực `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn/guide/HIeu.pdf` (Khoa CNTT — HUMG). Mọi AI Agent tham gia nghiên cứu, biên soạn và hiệu chỉnh báo cáo ĐATN bắt buộc phải khắc cốt ghi tâm và tuân thủ vô điều kiện:

1. **100% ảnh định dạng `.png` tại `figures/`, kích thước to rõ khổ A4:**
   - Mọi hình ảnh (kiến trúc, sơ đồ thực thể, giao diện hệ thống, biểu đồ thực nghiệm) bắt buộc phải lưu ở định dạng `.png` không nén suy hao (lossless) tại thư mục `report-datn/figures/`. Tuyệt đối CẤM sử dụng định dạng `.jpg`, `.jpeg`, `.webp`, `.bmp`.
   - Kích thước hiển thị trên văn bản phải to rõ, chiếm đa phần bề ngang trang A4 (`width=0.85\textwidth` đến `0.95\textwidth`, khuyến nghị chuẩn `0.92\textwidth` cho ảnh giao diện và số liệu). Tuyệt đối CẤM co nhỏ hình ảnh dưới $8\,\text{cm}$ hoặc $< 0.7\textwidth$ gây vỡ nét, mờ chữ khi in ấn hoặc photocopy.

2. **Cấm chức danh "Trưởng Bộ môn" ở trang iv Phiếu giao đề tài:**
   - Căn cứ trang 4 tài liệu chuẩn `HIeu.pdf`, phần ký duyệt ở trang 2 của Phiếu giao đề tài (`frontmatter/phieu_giao_de_tai.tex`) CHỈ CÓ 2 BÊN KÝ DUYỆT: **Giảng viên hướng dẫn** (bên trái) và **Sinh viên thực hiện** (bên phải).
   - Tuyệt đối CẤM đưa chữ ký, chức danh "Trưởng Bộ môn", "Trưởng Khoa" vào Phiếu giao đề tài tốt nghiệp.

3. **Cố định ngày `06/11/2026`; chức danh viết thường Title Case:**
   - Mọi vị trí ghi ngày tháng ký duyệt trên toàn bộ biểu mẫu hành chính (Bìa phụ, Phiếu giao đề tài, Đề cương) phải được điền cố định chính xác: `Hà Nội, ngày 06 tháng 11 năm 2026` (hoặc `06/11/2026`). Tuyệt đối CẤM để trống hoặc dùng dấu chấm lửng (`ngày... tháng... năm 202...`).
   - Các chức danh ký tên và đề mục hành chính viết hoa chữ cái đầu theo chuẩn Title Case tiếng Việt: `Giảng viên hướng dẫn`, `Sinh viên thực hiện`. Tuyệt đối CẤM viết hoa toàn bộ (`GIẢNG VIÊN HƯỚNG DẪN`, `SINH VIÊN THỰC HIỆN`).

4. **Dãn dòng chuẩn 1.5 Word (`\setstretch{1.45}`), cấm `\setstretch{1.241}`:**
   - Thiết lập dãn dòng chuẩn hóa tại cả `config/preamble.tex` và `main.tex:83` bằng lệnh `\setstretch{1.45}` để đạt khoảng cách dòng cơ sở (Baseline Skip) chuẩn Word 1.5 của tài liệu mẫu `HIeu.pdf` ($22{,}54\,\text{pt} - 23{,}22\,\text{pt}$).
   - Tuyệt đối CẤM sử dụng hệ số nén `\setstretch{1.241}` (dãn dòng 1.2 ép trang sai quy chuẩn), và không dùng `\onehalfspacing` mặc định (vốn chỉ đạt $19{,}43\,\text{pt}$, nén chặt hơn ~15%).

5. **Cỡ chữ toàn bài và trong bảng đạt 13pt (cấm `\small`, `\footnotesize`):**
   - Phông chữ Times New Roman 13pt đồng nhất cho toàn bộ văn bản và TOÀN BỘ NỘI DUNG CHỮ TRONG BẢNG BIỂU (`tabular`, `tabularx`, `longtable`).
   - Tuyệt đối CẤM bọc bảng bằng `\small` (11pt), `\footnotesize` (10pt), `\fontsize{8.5pt}{...}`, `\fontsize{9pt}{...}` để nhồi nhét nội dung. Cần thiết kế cấu trúc bảng hợp lý, ngắt dòng chuẩn hoặc chia tách bảng con.

6. **Mục lục không in đậm bất kỳ dòng mục nào:**
   - Khớp 100% trang 9 của `HIeu.pdf`, toàn bộ các dòng đề mục trong Mục lục (từ Chương, Lời mở đầu, Danh mục, đến Kết luận, Tài liệu tham khảo, Phụ lục) đều dùng phông chữ đứng thường (`\normalfont`), TUYỆT ĐỐI KHÔNG IN ĐẬM (`\bfseries`).
   - Gói `tocloft` được cấu hình: `\renewcommand{\cftchapfont}{\normalfont}`, thêm dấu hai chấm sau số chương `\renewcommand{\cftchapaftersnum}{:\ }`, số trang in thường `\renewcommand{\cftchappagefont}{\normalfont}` và chấm dẫn `\cftchapleader{\cftdotfill{\cftdotsep}}`.

7. **Bìa ngoài có sườn dọc xoay 90° font thường (`ĐÀM MẠNH DŨNG`, `HỆ THỐNG THÔNG TIN`, `KHOÁ 67`):**
   - Trang bìa ngoài (Bìa chính — `frontmatter/bia_chinh.tex`) bắt buộc có dải sườn/gáy in dọc mép lề trái theo đúng mẫu vật lý trang 1 của `HIeu.pdf`.
   - Dải sườn dọc được tạo bằng TikZ overlay xoay 90° ngược chiều kim đồng hồ, bao gồm 3 khối thông tin in hoa, phông đứng thường không đậm: `ĐÀM MẠNH DŨNG`, `HỆ THỐNG THÔNG TIN`, `KHOÁ 67`. Loại bỏ hoàn toàn tiền tố thừa "TÊN ĐỀ TÀI:".

8. **Số trang Ả Rập 1 bắt đầu từ Mục lục; trang 1–8 để trống chân trang:**
   - Theo đúng mẫu vật lý `HIeu.pdf`, các trang vật lý 1 đến 8 (Bìa chính, Bìa phụ, Phiếu giao đề tài, Đề cương, Lời cảm ơn) **chân trang hoàn toàn để trống (Clean Footers)**, tuyệt đối không in số trang vật lý. Lệnh `\thispagestyle{adminform}` / `empty` bảo đảm không có `\thepage`.
   - Đánh số trang bằng **chữ số Ả Rập (`1, 2, 3...`) BẮT ĐẦU CHÍNH XÁC TỪ TRANG MỤC LỤC** (`frontmatter/muc_luc.tex` mang số trang 1 Ả Rập ở góc phải chân trang).
   - Trong Mục lục, các mục Frontmatter đầu khóa hiển thị số trang La Mã logic khớp mẫu `HIeu.pdf` (Phiếu giao đề tài: `iii`, Đề cương: `v`, Lời cảm ơn: `viii`), và bản thân trang Mục lục có dòng tự tham chiếu `MỤC LỤC ........... 1`.

9. **Bỏ hết in đậm/in nghiêng tùy tiện trong đoạn văn; chỉ mục mức 3 mới in nghiêng; tinh giản tham chiếu trích dẫn:**
   - Bóc bỏ toàn bộ các thẻ in đậm (`\textbf`) và in nghiêng (`\textit`) tùy tiện trong các đoạn văn xuôi thân bài (Chương 1 đến Chương 4, Lời mở đầu, Kết luận) để bảo đảm văn phong khoa học liền mạch, trang nhã.
   - CHỈ DUY NHẤT tiêu đề tiểu mục cấp 3 (`\subsubsection`) mới được phép in nghiêng theo quy định phân cấp đề mục.
   - Tinh giản tham chiếu trích dẫn: Tuyệt đối không rải trích dẫn dày đặc liên tiếp trong từng câu hoặc dồn dập 5-6 trích dẫn vào một nhận định hiển nhiên; trích dẫn tập trung tại Chương 1 và Chương 2; tổng tài liệu tham khảo $N_{\text{refs}} \le 20$.

10. **Bìa phụ và thể thức khớp 100% `HIeu.pdf`:**
    - Toàn bộ trang Bìa trong (Bìa phụ — `frontmatter/bia_phu.tex`) phải đối chiếu và khớp 100% về bố cục, ngắt dòng, khoảng cách dọc (`\vspace`), tỷ lệ cỡ chữ, khối ký tên cán bộ hướng dẫn và sinh viên với trang 2 của `HIeu.pdf`.
    - Thể thức tổng thể: Khổ giấy A4 chuẩn, lề Trên 2.5cm, Dưới 2.5cm, Trái 3.5cm, Phải 2.5cm. Tuyệt đối không xô lệch lề trang.

11. **Tuyệt đối không tiết kiệm giấy làm sai quy cách:**
    - Đồ án tốt nghiệp là ấn phẩm học thuật lưu trữ thư viện và hội đồng vĩnh viễn, không phải bản nháp tiết kiệm chi phí in ấn.
    - CẤM MỌI HÀNH VI "tiết kiệm giấy" làm sai quy cách: Cấm nén dãn dòng xuống dưới 1.45, cấm giảm cỡ chữ xuống 10pt-11pt để ép trang, cấm co nhỏ sơ đồ hình vẽ dưới 8cm, cấm dồn ép biểu mẫu hành chính làm lệch phân trang quy định (Phiếu giao đề tài cố định 2 trang, Đề cương cố định 3 trang, Lời cảm ơn cố định 1 trang). Mỗi chương bắt đầu ở trang lẻ mới theo đúng cấu trúc chuẩn.

---

## PHẦN 1: MỤC TIÊU CỐT LÕI, QUY TRÌNH HỌC THUẬT VÀ KỶ LUẬT ĐATN

### 1.1. Bản chất ĐATN và Ba câu hỏi học thuật cốt lõi
Căn cứ Quy định ĐATN của Khoa CNTT — HUMG (`Huong dan-Quy dinh-DATN.md`, Mục 1.1 và 1.2.1):
*Đồ án tốt nghiệp là công trình nghiên cứu khoa học của sinh viên, tổng kết lý thuyết chuyên ngành, lý thuyết cơ sở ngành, kinh nghiệm thu được sau quá trình thực tập, lý luận và phương pháp luận để giải quyết một vấn đề khoa học cụ thể của ngành CNTT. Sinh viên thực hiện và hoàn thành một nhiệm vụ khoa học cụ thể dưới dạng một đồ án để kết thúc quá trình học tập bậc Đại học và nhận bằng tốt nghiệp.*

Trong toàn bộ quá trình biên soạn báo cáo, sinh viên và từng AI Agent bắt buộc phải trả lời trọn vẹn, thuyết phục 3 câu hỏi lớn:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   3 CÂU HỎI HỌC THUẬT CỐT LÕI CỦA ĐỒ ÁN TỐT NGHIỆP               │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. LÀM GÌ? CHO ĐỐI TƯỢNG NÀO? (What and For Whom)                                │
│    └─► Bối cảnh bài toán, tính cấp thiết, mục tiêu tổng quát/cụ thể, đối tượng   │
│        thụ hưởng, giới hạn phạm vi nghiên cứu (Lời mở đầu và Chương 1).          │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 2. LÀM NHƯ THẾ NÀO? (How to do it)                                               │
│    └─► Cơ sở lý thuyết, công nghệ nền tảng, luận giải "Tại sao chọn", quy trình  │
│        5 bước kỹ nghệ, kiến trúc hệ thống, CSDL, Use Case (Chương 2 và Chương 3).│
├──────────────────────────────────────────────────────────────────────────────────┤
│ 3. KẾT QUẢ RA SAO? (What are the results and Impact)                             │
│    └─► Kết quả cài đặt, hình ảnh giao diện, minh chứng đo lường định lượng thực  │
│        nghiệm, đánh giá ưu/nhược điểm, hướng mở rộng (Chương 4 và Kết luận).     │
└──────────────────────────────────────────────────────────────────────────────────┘
```

1. **Câu hỏi 1: "Làm gì? Cho đối tượng nào?" (Chương 1 và Lời mở đầu):**
   - Nhiệm vụ được giao hoặc tự mình xác định cần phải giải quyết.
   - Khảo sát hiện trạng thực tế, phân tích khó khăn tồn đọng của đối tượng thụ hưởng và chỉ ra bài toán khoa học trọng tâm cần giải quyết.
   - Xác định rõ ràng ranh giới và phạm vi giải pháp (Scope and Boundaries), nêu rõ các giả định khoa học.
2. **Câu hỏi 2: "Làm như thế nào?" (Chương 2 và Chương 3):**
   - Tổng hợp, phân tích, đánh giá vấn đề trong nước và quốc tế đã thực hiện; ghi chép tài liệu tham khảo chính thống để trích dẫn.
   - Trình bày cơ sở lý luận, mô hình toán học và công nghệ nền tảng kèm luận chứng khoa học "Tại sao chọn" (*Justification-Driven*).
   - Đề xuất phương án giải quyết của mình, chứng minh lý giải vì sao chọn phương án đó; thiết kế chi tiết theo chu trình 5 bước kỹ nghệ phần mềm.
3. **Câu hỏi 3: "Kết quả ra sao?" (Chương 4 và Kết luận):**
   - Trình bày kết quả điều tra, phân tích, thiết kế hệ thống, sản phẩm phần mềm đã cài đặt kèm biểu bảng, hình vẽ giao diện.
   - Đánh giá kết quả bằng các số liệu đo lường định lượng khách quan (độ trễ, thông lượng, độ chính xác, tỷ lệ vượt qua bài kiểm thử); so sánh trung thực với ý muốn ban đầu và kết quả của các công trình liên quan; đề ra phương hướng khắc phục tồn tại.

---

### 1.2. Chu trình 10 bước tiến hành khi làm ĐATN
Căn cứ Mục 1.2.1 `Huong dan-Quy dinh-DATN.md`, quy trình thực hiện ĐATN bao gồm 10 bước tuần tự:
1. **Bước 1 — Nhận đề tài:** Nhận nhiệm vụ nghiên cứu khoa học từ Giảng viên hướng dẫn (GVHD) và Bộ môn.
2. **Bước 2 — Tìm kiếm tài liệu tham khảo:** Thu thập các giáo trình, bài báo khoa học quốc tế có bình duyệt; đây là khâu then chốt bảo đảm sự thành công của đồ án.
3. **Bước 3 — Nghiên cứu sơ bộ và viết đề cương:** Nghiên cứu tổng quan tài liệu và đề tài, xây dựng Đề cương chi tiết (ĐCCT) thông qua GVHD phê duyệt để hình dung tổng thể công việc.
4. **Bước 4 — Nghiên cứu lý thuyết và thực nghiệm:** Bám sát đề cương chi tiết đã duyệt; kết hợp song song giữa nghiên cứu lý thuyết, phát triển giải pháp kỹ thuật và viết bản thảo báo cáo để kịp tiến độ.
5. **Bước 5 — Báo cáo định kỳ với GVHD:** Báo cáo định kỳ (1--2 tuần/lần) với GVHD về tình hình thực hiện đề cương và kết quả đạt được để kịp thời tháo gỡ khó khăn.
6. **Bước 6 — Hoàn chỉnh đồ án tốt nghiệp:** Hoàn thiện toàn văn bản thảo báo cáo và kiểm thử toàn diện sản phẩm phần mềm.
7. **Bước 7 — Nộp đồ án cho GVHD duyệt lần cuối:** Trình bản thảo hoàn chỉnh cho GVHD kiểm tra lần cuối và ký xác nhận cho phép bảo vệ.
8. **Bước 8 — Nộp đồ án cho Bộ môn hoặc Khoa:** Nộp đúng thời hạn quy định kèm hồ sơ hành chính theo thông báo của Bộ môn.
9. **Bước 9 — Chuẩn bị và tổ chức bảo vệ:** Chuẩn bị phim chiếu (slide thuyết trình), tổ chức bảo vệ thử, viết tóm tắt nội dung bảo vệ, chuẩn bị máy tính, máy chiếu và kịch bản demo.
10. **Bước 10 — Hoàn thiện báo cáo sau bảo vệ và nộp lưu chiểu:** Tiếp thu ý kiến đóng góp của Hội đồng, chỉnh sửa hoàn thiện báo cáo và nộp bản đóng bìa cứng mạ chữ nhũ vàng để lưu chiểu vĩnh viễn.

---

### 1.3. Trách nhiệm của các cấp quản lý và Sinh viên
Căn cứ Mục 1.2.2 đến 1.2.4 `Huong dan-Quy dinh-DATN.md`:
* **Trách nhiệm của Sinh viên:** Chủ động liên hệ GVHD, lập kế hoạch chi tiết, báo cáo tiến độ định kỳ hàng tuần; bảo đảm tính trung thực học thuật, thường xuyên sao lưu dữ liệu nghiên cứu; tuyệt đối chấp hành kỷ luật và thời hạn nộp bài.
* **Trách nhiệm của Giảng viên hướng dẫn (GVHD):** Hướng dẫn phương pháp luận nghiên cứu khoa học; theo dõi tiến độ, hướng dẫn giải quyết các vướng mắc kỹ thuật phát sinh; rà soát và đánh giá trung thực kết quả đồ án; ký duyệt đề cương và quyết định cho phép hoặc không cho phép bảo vệ.
* **Trách nhiệm của Bộ môn:** Phân công GVHD, Giảng viên phản biện (GVPB); thành lập Hội đồng đánh giá ĐATN; tổ chức kiểm tra tiến độ giữa kỳ (Tuần 6); quản lý toàn diện chất lượng học thuật của sinh viên chuyên ngành.
* **Trách nhiệm của Khoa:** Quản lý toàn diện quy trình đào tạo ĐATN trong toàn Khoa; ban hành Quyết định giao đề tài và Quyết định thành lập Hội đồng chấm ĐATN.

---

### 1.4. Quy trình 5 bước kỹ nghệ phần mềm kinh điển và Nguyên tắc tính tái lập
Tại Chương 3 của báo cáo, phương pháp giải quyết bài toán bắt buộc phải diễn giải theo đúng chu trình 5 bước kỹ nghệ phần mềm:
1. **Phân tích yêu cầu (Requirements Analysis):** Khảo sát nghiệp vụ thực tế, xác định các tác nhân (Actors), phân rã và lập bảng đặc tả các ca sử dụng (Use Cases) chuẩn BA.
2. **Thiết kế hệ thống (System Design):**
   - Thiết kế kiến trúc tổng thể (kiến trúc phần mềm phân tầng, kiến trúc tích hợp).
   - Thiết kế cơ sở dữ liệu: Xây dựng biểu đồ lớp thực thể (Domain Class Diagram) đặt trước các bảng dữ liệu CSDL, thiết kế sơ đồ quan hệ thực thể ERD và Từ điển dữ liệu (Data Dictionary).
   - Thiết kế luồng tương tác hành vi: Biểu đồ tuần tự UML (Sequence Diagrams).
   - Thiết kế giao diện người dùng (UI/UX).
3. **Cài đặt hệ thống (Implementation):** Hiện thực hóa mã nguồn Backend, Frontend và hạ tầng dịch vụ theo kiến trúc đã thiết kế.
4. **Kiểm thử hệ thống (Verification and Testing):** Thực thi chiến lược Lập trình hướng kiểm thử (TDD), vượt qua các cổng kiểm thử Unit Test, Integration Test, kiểm tra cú pháp và kiểm thử biên dịch đóng gói.
5. **Hiệu chỉnh và tối ưu hóa (Refinement and Optimization):** Tinh chỉnh tham số thuật toán, xử lý ngoại lệ biên, tối ưu hóa độ trễ truy vấn và hoàn thiện theo chỉ đạo của GVHD.

**Nguyên tắc viết về sản phẩm (Tính tái lập — Reproducibility):**  
Căn cứ Mục 2.2.2 `Huong dan-Quy dinh-DATN.md`: Khi viết về sản phẩm phần mềm, tác giả không chỉ mô tả giao diện sử dụng và chức năng bên ngoài, mà bắt buộc phải viết rõ **quá trình thiết kế**, kiến trúc dữ liệu và giải thuật lõi. Báo cáo phải được trình bày sao cho người khác hoặc sinh viên khóa sau khi đọc đồ án cũng có thể hiểu rõ nguyên lý và tái lập lại được hệ thống.

---

### 1.5. Lịch trình 10 tuần chuẩn mực và Cột mốc đánh giá giữa kỳ (Tuần 6)
Tiến trình thực hiện ĐATN tại Khoa CNTT — HUMG được thiết kế chuẩn mực trong **10 tuần**:

| Giai Đoạn | Khung Thời Gian | Trọng Tâm Nhiệm Vụ Học Thuật | Sản Phẩm Đầu Ra Bắt Buộc |
| :---: | :---: | :--- | :--- |
| **Giai đoạn 1** | **Tuần 1** | Nhận đề tài, nghiên cứu sơ bộ tài liệu, viết Đề cương chi tiết (ĐCCT) và thống nhất lịch làm việc với GVHD. | Bản ĐCCT có chữ ký phê duyệt của GVHD. |
| **Giai đoạn 2** | **Tuần 2 -- 5** | Khảo sát bài toán, phân tích yêu cầu nghiệp vụ, nghiên cứu cơ sở lý thuyết (Chương 2); thiết kế kiến trúc hệ thống, Use Case, biểu đồ tuần tự và mô hình CSDL (Chương 3). | Bản thảo Chương 1, Chương 2, sơ đồ ERD, biểu đồ lớp và từ điển CSDL. |
| **Giai đoạn 3** | **Tuần 6** | **CỘT MỐC ĐÁNH GIÁ TIẾN ĐỘ GIỮA KỲ (MID-TERM CHECKPOINT):**<br>Sinh viên bắt buộc phải **báo cáo tiến độ làm ĐATN với Bộ môn chủ quản** và GVHD. Rà soát khối lượng hoàn thành, báo cáo các kết quả kỹ thuật bước đầu và xin ý kiến chỉ đạo. | Báo cáo tiến độ Tuần 6; demo chạy thử mô-đun lõi; xác nhận tiến độ của GVHD. |
| **Giai đoạn 4** | **Tuần 7 -- 9** | Cài đặt hoàn thiện hệ thống, tích hợp các thành phần, thực hiện kiểm thử tự động toàn diện, đo lường chỉ số thực nghiệm định lượng (Chương 4) và viết toàn văn bản thảo. | Toàn văn bản thảo đồ án (Chương 1--4, Kết luận, TLTK); kết quả kiểm thử đạt PASS. |
| **Giai đoạn 5** | **Tuần 10** | Hoàn thiện bản thảo và chương trình; trình GVHD duyệt lần cuối và ký xác nhận; nộp quyển báo cáo ĐATN về Bộ môn theo đúng thời hạn thông báo. | **03 quyển đồ án bìa mềm** có chữ ký GVHD; slide thuyết trình; sản phẩm phần mềm. |
| **Sau bảo vệ** | **Trong vòng 10 ngày** | Chỉnh sửa, hoàn thiện toàn bộ nội dung theo kết luận của Hội đồng; đóng bìa cứng mạ chữ nhũ vàng nộp lưu chiểu vĩnh viễn. | **01 quyển bìa cứng in chữ mạ nhũ vàng** và thư mục bản mềm nộp lưu chiểu Bộ môn. |

---

### 1.6. Ý thức kỷ luật và 4 điều kiện đình chỉ bảo vệ tốt nghiệp
Căn cứ Mục 2.1 `Huong dan-Quy dinh-DATN.md` và Mục B.I `Huong-dan-viet-DATN.md`:
* **Nghĩa vụ gặp GVHD hàng tuần:** Sinh viên có trách nhiệm bắt buộc phải **gặp GVHD định kỳ hàng tuần** để báo cáo tiến độ, trình bày vướng mắc kỹ thuật và xin ý kiến chỉ đạo cho tuần tiếp theo. Sinh viên phải có ý thức bảo quản tài sản, máy móc phòng thí nghiệm và chấp hành nghiêm kỷ luật.
* **Trách nhiệm sao lưu dữ liệu:** Sinh viên phải thường xuyên sao lưu dữ liệu nghiên cứu và mã nguồn ở nhiều nơi an toàn (Git, Cloud, thiết bị ngoài). Nhà trường và Bộ môn **tuyệt đối không chấp nhận** lý do bị hỏng đĩa, hỏng ổ cứng hoặc bị virus làm mất dữ liệu đồ án.
* **4 Điều kiện Hội đồng Bộ môn ra quyết định ĐÌNH CHỈ BẢO VỆ ĐỒ ÁN:**
  1. Sinh viên **chưa thanh toán hết các khoản nợ** đối với Nhà trường (học phí, sách thư viện, lệ phí).
  2. Sinh viên trong suốt quá trình làm đồ án **không gặp GVHD sau lần giao nhiệm vụ đầu tiên**, hoặc **hàng tuần không báo cáo tiến độ làm việc với GVHD**.
  3. Sinh viên **không nộp đồ án đúng thời hạn quy định** của Bộ môn và Nhà trường (đến hạn không nộp coi như không làm đồ án).
  4. **Giáo viên hướng dẫn đánh giá đồ án không đạt yêu cầu**.

---

### 1.7. Quy cách nộp lưu trữ bản cứng và bản mềm
Căn cứ Mục 2.2 `Huong dan-Quy dinh-DATN.md` và Mục A.III `Huong-dan-viet-DATN.md`:
1. **Bản cứng (Hard Copy):**
   - *Trước khi bảo vệ:* Sinh viên nộp **03 quyển đồ án đóng bìa mềm có chữ ký xác nhận của GVHD**:
     - 02 quyển nộp cho Bộ môn (01 quyển gửi Hội đồng chấm, 01 quyển gửi Giảng viên phản biện).
     - 01 quyển nộp cho GVHD.
   - *Sau khi bảo vệ:* Sinh viên tiếp thu, chỉnh sửa toàn diện theo kết luận của Hội đồng. Trong thời hạn **trong vòng 10 ngày** sau ngày bảo vệ, sinh viên nộp **01 quyển bìa cứng in chữ mạ nhũ vàng** (đầy đủ dấu tiếng Việt theo mẫu Phụ lục 01) cho Bộ môn để lưu trữ vĩnh viễn trong thư viện khoa học.
2. **Bản mềm (Soft Copy):**
   - Nộp cho Bộ môn bản mềm lưu trữ đặt trong **duy nhất 01 thư mục gốc**.
   - **Quy chuẩn đặt tên thư mục:** Bắt buộc tuân theo định dạng: `MãSinhViên_HọTên_Khóa` (viết liền không dấu hoặc gạch dưới chuẩn hóa; ví dụ mẫu quy chế: `1821050189_NguyenVanAnh_K63`).
   - **Cấu trúc dữ liệu bên trong thư mục bản mềm:**
     - `BaoCao_ToanVan.pdf`: Toàn văn file báo cáo hoàn chỉnh xuất bản từ XeLaTeX (gồm bìa, mục lục, nội dung, phụ lục).
     - `Slide_BaoVe.pdf` (hoặc `.pptx`): Bản trình chiếu báo cáo trước Hội đồng.
     - `SourceCode/`: Toàn bộ mã nguồn chương trình có thể chạy được, kèm tệp `README.md` hướng dẫn cài đặt và khởi chạy.
     - `Data_and_Tests/`: Tập dữ liệu thử nghiệm, kịch bản kiểm thử tự động và nhật ký đo lường.
   - *Lưu ý về phương tiện vật lý:* Nếu Bộ môn yêu cầu nộp đĩa mềm/CD, đĩa phải đặt trong túi nilon kẹp dán vào mặt trong bìa sau báo cáo, có nhãn ghi rõ Mã số ĐATN, Họ tên, Lớp, Khóa, Thời gian và kèm 1 trang hướng dẫn chức năng các tệp trên đĩa.

---

### 1.8. Cấu trúc chuẩn Đề cương ĐATN Đại học
Căn cứ biểu mẫu quy chuẩn tại `Mau-De-cuong-DATN.md`, trang Đề cương ĐATN thuộc phần Frontmatter (`frontmatter/de_cuong_datn.tex`) phải tuân thủ nghiêm ngặt cấu trúc 6 thành phần:
1. **Tiêu ngữ và Đơn vị:**
   - Cột trái: Tên Khoa chủ quản (`KHOA CÔNG NGHỆ THÔNG TIN`), Tên Bộ môn chuyên ngành (`BỘ MÔN HỆ THỐNG THÔNG TIN VÀ TRI THỨC` hoặc Bộ môn tương ứng).
   - Cột phải: Quốc hiệu và Tiêu ngữ Việt Nam (`CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM — Độc lập — Tự do — Hạnh phúc`).
2. **Bảng ma trận thông tin Sinh viên thực hiện (Bảng 6 cột):**
   - Các cột: `TT`, `Mã sinh viên`, `Họ và tên`, `Lớp`, `Điện thoại`, `E-mail`.
3. **Bảng ma trận thông tin Giảng viên hướng dẫn (Bảng 6 cột):**
   - Các cột: `TT`, `Mã cán bộ`, `Họ và tên`, `Đơn vị`, `Điện thoại`, `E-mail`.
4. **Hệ thống 6 đề mục nội dung đề cương:**
   - `1. Tên đề tài:` Tên chính thức được phê duyệt của công trình tốt nghiệp.
   - `2. Lý do chọn đề tài:` Trình bày bối cảnh thực tiễn, tính cấp thiết và khoảng trống công nghệ.
   - `3. Mục tiêu của đề tài:` Nêu rõ Mục tiêu tổng quát và các Mục tiêu cụ thể (về sản phẩm, về kiến thức/kỹ năng).
   - `4. Các nhiệm vụ cụ thể:` Phân rã phạm vi công việc kỹ thuật từ phân tích, thiết kế, cài đặt đến kiểm thử.
   - `5. Kế hoạch thực hiện:` Bảng kế hoạch chi tiết đúng **10 tuần** gồm 3 cột: `Tuần`, `Thời gian`, `Nội dung công việc` (nêu rõ mốc Tuần 6 báo cáo tiến độ với Bộ môn).
   - `6. Nơi thực hiện đồ án:` Bộ môn, Khoa hoặc cơ sở nghiên cứu tiếp nhận.
5. **Khối xác nhận và Chữ ký:** Địa danh, ngày tháng năm tại Hà Nội (cố định chính thức: `Hà Nội, ngày 06 tháng 11 năm 2026`); bảng 2 cột gồm chữ ký của `Giảng viên hướng dẫn` và `Sinh viên thực hiện` (viết thường theo đúng Title Case tiếng Việt, TUYỆT ĐỐI KHÔNG VIẾT HOA TOÀN BỘ).

---

### 1.9. Rubric đánh giá của Giảng viên hướng dẫn và Cổng thẩm định chất lượng
Căn cứ biểu mẫu pháp lý tại `Mẫu_HD_DATN.md` (Bản nhận xét ĐATN lưu trữ vĩnh viễn trong hồ sơ tốt nghiệp), đồ án được thẩm định qua 3 tiêu chí cốt lõi:
1. **Bộ 9 trường thông tin định danh học thuật:**
   - Tên đề tài, Ngành, Mã ngành, Chuyên ngành, Họ và tên sinh viên, Mã sinh viên, Người hướng dẫn, Học hàm/học vị, Cơ quan công tác.
2. **Tiêu chí I — Khối lượng công việc và Kết quả đạt được:**
   - Mức độ hoàn thành các nhiệm vụ được giao so với Đề cương chi tiết ban đầu.
   - Chất lượng sản phẩm kỹ thuật, tính hoàn thiện của các tính năng và độ tin cậy của thực nghiệm định lượng.
3. **Tiêu chí II — Tinh thần, Thái độ làm việc và Khả năng sáng tạo:**
   - Ý thức kỷ luật, mức độ duy trì gặp GVHD định kỳ hàng tuần và tinh thần tiếp thu góp ý.
   - Tính chủ động trong nghiên cứu, năng lực giải quyết bài toán khó và tính mới, sáng tạo trong giải pháp.
4. **Tiêu chí III — Quyết định Đề nghị Cổng bảo vệ:**
   - GVHD chính thức kết luận: `Được bảo vệ: [X]` hoặc `Không được bảo vệ: [ ]`. Nếu đánh giá không đạt, sinh viên bị đình chỉ bảo vệ theo Quy chế.

---

## PHẦN 2: BỐ CỤC TOÀN VĂN VÀ QUY CHUẨN ĐỊNH DẠNG XELATEX

### 2.1. Trật tự bố cục chuẩn mực toàn văn quyển đồ án
Căn cứ Mục B.I, B.II `Huong-dan-viet-DATN.md` và tài liệu chuẩn `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn/guide/HIeu.pdf`, toàn văn quyển đồ án phải sắp xếp theo đúng trình tự phân đoạn:

```
+─────────────────────────────────────────────────────────────────────────────────────────+
│                       TRẬT TỰ BỐ CỤC TOÀN VĂN QUYỂN ĐỒ ÁN TỐT NGHIỆP                    │
+─────────────────────────────────────────────────────────────────────────────────────────+
│ [FRONTMATTER — PHẦN ĐẦU KHÓA] (Đánh số trang La Mã thường đứng: i, ii, iii...)          │
│  1. Trang bìa ngoài (Bìa chính — có dải sườn/gáy mép trái theo Mẫu trang 1 Hieu.pdf)    │
│  2. Trang bìa trong (Bìa phụ — chức danh Title Case GVHD và SVTH, bỏ "TÊN ĐỀ TÀI:")     │
│  3. Phiếu giao đề tài tốt nghiệp (Trang iii La Mã; KHÔNG CÓ TRƯỞNG BỘ MÔN; 06/11/2026)  │
│  4. Đề cương thực hiện đồ án tốt nghiệp (Kế hoạch 10 tuần chi tiết: trang v; 06/11/2026)│
│  5. Lời cảm ơn (Trang viii La Mã; ngày 06/11/2026)                                      │
+─────────────────────────────────────────────────────────────────────────────────────────+
│ [MAIN BODY & MỤC LỤC] (Đánh số trang Ả Rập đứng: 1, 2, 3... bắt đầu từ MỤC LỤC)         │
│  6. Mục lục (Trang 1 Ả Rập — KHÔNG IN ĐẬM \normalfont, dấu hai chấm CHƯƠNG X: và chấm) │
│  7. Danh mục các hình vẽ, đồ thị (LoF — Hình X-Y)                                       │
│  8. Danh mục các bảng (LoT — Bảng X-Y)                                                  │
│  9. Danh mục các ký hiệu và chữ viết tắt (sắp xếp theo thứ tự bảng chữ cái ABC)         │
│ 10. Lời mở đầu (Bối cảnh, mục tiêu, đối tượng, phạm vi nghiên cứu)                      │
│ 11. Chương 1: TỔNG QUAN VỀ ĐỀ TÀI (Mô tả bài toán, hiện trạng, yêu cầu)                 │
│ 12. Chương 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ (Lý thuyết, Why-chosen, mô hình toán)         │
│ 13. Chương 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG (5 bước, Use Case, Kiến trúc, CSDL)        │
│ 14. Chương 4: CÀI ĐẶT VÀ KẾT QUẢ THỰC NGHIỆM (Triển khai, kiểm thử, đo lường số liệu)   │
+─────────────────────────────────────────────────────────────────────────────────────────+
│ [BACKMATTER — PHẦN KẾT THÚC] (Tiếp tục đánh số trang Ả Rập đứng)                         │
│ 15. Kết luận và hướng phát triển (Đóng góp đạt được, tồn tại, hướng mở rộng)            │
│ 16. Danh mục tài liệu tham khảo (Phân nhóm Việt trước, Anh sau; N_refs <= 20; tinh gọn) │
│ 17. Phụ lục (Mã nguồn thuật toán, biểu mẫu — BẮT BUỘC KHÔNG DÀY HƠN THÂN BÀI)           │
+─────────────────────────────────────────────────────────────────────────────────────────+
```

---

### 2.2. Toàn bộ quy chuẩn định dạng bắt buộc (Typography Standards)
Mọi tệp cấu hình và chế bản XeLaTeX trong `report-datn/` phải tuân thủ nghiêm ngặt các thông số hình học:

1. **Khổ giấy và Căn lề trang (Geometry):**
   - Khổ giấy: **A4 chuẩn** ($210 \times 297\,\text{mm}$), in trên một mặt giấy trắng.
   - **Lề trên (Top):** đúng **$2{,}5\,\text{cm}$**.
   - **Lề dưới (Bottom):** đúng **$2{,}5\,\text{cm}$**.
   - **Lề trái (Left — gáy sách):** đúng **$3{,}5\,\text{cm}$** (chừa khoảng cách bắt buộc để đóng gáy bìa cứng mạ nhũ vàng không bị che khuất văn bản).
   - **Lề phải (Right):** đúng **$2{,}5\,\text{cm}$**.
   - $\rightarrow$ **Chiều rộng thân bài khả dụng:** Đúng **$15{,}0\,\text{cm}$** ($21{,}0 - 3{,}5 - 2{,}5 = 15{,}0\,\text{cm}$).
2. **Phông chữ, dãn dòng và thụt lề:**
   - Phông chữ tiêu chuẩn: `Times New Roman` (nhúng qua `fontspec` hỗ trợ đầy đủ 144 biến thể dấu tiếng Việt Unicode UTF-8).
   - Cỡ chữ thân bài (Body text) VÀ TẤT CẢ CÁC BẢNG BIỂU: Đúng **13pt** (`\usepackage[fontsize=13pt]{scrextend}`). Tuyệt đối cấm sử dụng `\small` (11pt), `\footnotesize` (10pt), hoặc các lệnh ép cỡ cục bộ (`\fontsize{8.5pt}`, `\fontsize{9pt}`) trong môi trường bảng biểu; toàn bộ nội dung trong bảng phải đồng nhất cỡ chữ 13pt.
   - Mật độ chữ: Bình thường, tuyệt đối **không được nén hoặc kéo dãn khoảng cách giữa các chữ**.
   - Dãn dòng (Line spacing): Đặt hệ số **`\setstretch{1.45}`** (qua gói `setspace`) tại cả `config/preamble.tex` và `main.tex:83` để đạt khoảng cách dòng cơ sở (Baseline Skip) chuẩn Word 1.5 của tài liệu mẫu `HIeu.pdf` ($22{,}54\,\text{pt} - 23{,}22\,\text{pt}$). Lưu ý: Lệnh `\onehalfspacing` truyền thống trong LaTeX chỉ tạo ra $19{,}43\,\text{pt}$ (bị nén chặt hơn ~15% so với chuẩn 1.5 Word). Đối với các biểu mẫu hành chính (Phiếu giao đề tài, Đề cương), sử dụng dãn dòng cục bộ để cố định ngân sách 2 trang và 3 trang.
   - Thụt lề đầu dòng (First-line Indent): Chuẩn **$1{,}0\,\text{cm}$** (`\setlength{\parindent}{1.0cm}`).
   - Căn lề đoạn văn: Căn đều hai bên lề (Justified).
3. **Quy tắc đánh số trang và Tiêu đề trang (Chuẩn form Khoa CNTT — HUMG & HIeu.pdf):**
   - **Header (Tiêu đề đầu trang):** **ĐỂ TRỐNG HOÀN TOÀN**, không có chữ chạy, không có tên đồ án, không có đường kẻ ngang (`\headrulewidth = 0pt`).
   - **Footer (Tiêu đề chân trang):** **KHÔNG CÓ TÊN SINH VIÊN**, không có thông tin lớp, không có đường kẻ chân trang (`\footrulewidth = 0pt`).
   - **Quy chuẩn chân trang Frontmatter (Trang 1--8):** Theo đúng mẫu vật lý `HIeu.pdf`, các trang 1 đến 8 (Bìa ngoài, Bìa phụ, Phiếu giao đề tài, Đề cương, Lời cảm ơn) **chân trang hoàn toàn để trống (Clean Footers)**, không in số trang. Lệnh `adminform` được định cấu hình không in `\thepage`.
   - **Số trang logic trong Mục lục:** Bộ đếm trang nội bộ XeLaTeX vẫn được thiết lập `\pagenumbering{roman}\setcounter{page}{3}` để Mục lục ghi nhận đúng số trang La Mã logic: `Phiếu giao đề tài` $\to$ `iii`, `Đề cương ĐATN` $\to$ `v`, `Lời cảm ơn` $\to$ `viii`.
   - **Phần Mục lục và Nội dung chính:** Đánh số bằng **chữ số Ả Rập** (`1, 2, 3...`) **BẮT ĐẦU CHÍNH XÁC TỪ TRANG MỤC LỤC** (`frontmatter/muc_luc.tex` mang số trang 1 Ả Rập in ở góc phải chân trang, khớp 100% trang 9 của `guide/HIeu.pdf`). Lệnh đặt trong `main.tex`: `\cleardoublepage\pagenumbering{arabic}\setcounter{page}{1}\setupdatnheaders\pagestyle{fancy}` ngay trước `\input{frontmatter/muc_luc}`. Số trang in đứng thông thường, **TUYỆT ĐỐI KHÔNG IN NGHIÊNG**.
4. **Quy chuẩn bố cục dòng chảy văn bản và chống khoảng trống đáy trang (Anti-Bottom-Gap Standard):**
   - Báo cáo đồ án phải có bố cục văn bản chặt chẽ, liên tục và điền đầy trang in một cách trang nhã theo đúng form của Khoa CNTT. Khoảng hở đáy trang phải $< 4{,}0\,\text{cm}$.
   - **TUYỆT ĐỐI CẤM** để lại khoảng trống lớn bất thường ở cuối trang giấy (ví dụ: ngắt trang sớm để lại 1/3 đến 1/2 trang giấy trắng phía dưới).
   - **Kỹ thuật xử lý bắt buộc trong XeLaTeX:**
     - Tất cả các đối tượng trôi nổi (Floats: Bảng biểu và Hình vẽ) bắt buộc phải khai báo tham số vị trí linh hoạt: `\begin{table}[!htbp]` và `\begin{figure}[!htbp]`. Tuyệt đối tránh lạm dụng `[H]` gây hiện tượng dồn ứ trang mồ côi (Cascading Float Push).
     - Không sử dụng tùy chọn `[section]` cho gói `placeins` (`\usepackage{placeins}`) để tránh ngăn cản dòng chảy văn bản lấp đầy đáy trang trước tiêu đề mục.
     - Lệnh `needspace` chỉ dùng ở ngưỡng hợp lý (`\needspace{4\baselineskip}`) để chống mồ côi tiêu đề, cấm dùng ngưỡng quá lớn (`\needspace{20\baselineskip}`) gây ngắt trang giả tạo.
     - Trong các bảng biểu, phải thiết lập độ rộng cột hợp lý (`m{...}`, `X`) và bổ sung âm tiết ngắt từ (`\-`) cho các định danh dài để triệt tiêu hoàn toàn cảnh báo Overfull `\hbox`.

---

### 2.3. Ma trận phân cấp cỡ chữ và tiêu đề văn bản

| Cấp Bậc / Thành Phần | Cỡ Chữ (Size) | Định Dạng (Style) | Căn Lề | Khoảng Cách Trước / Sau | Cấu Hình Kỹ Thuật Trong XeLaTeX |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **Bìa ngoài / Bìa trong** | 16pt | In hoa, Đậm | Giữa | Theo mẫu phụ lục 01, 02 | `\fontsize{16}{20}\selectfont\bfseries` |
| **Nhãn "ĐỒ ÁN TỐT NGHIỆP"** | 32pt -- 40pt | In hoa, Đậm | Giữa | Nổi bật giữa trang | `\fontsize{36}{44}\selectfont\bfseries` |
| **Tiêu đề Chương (`\chapter`)** | 16pt | In hoa, Đậm | Giữa | Trước 0pt, Sau 18pt | `\titleformat{\chapter}[block]` |
| **Mục cấp 1 (`\section` X.Y)** | 14pt | In đậm | Trái | Trước 12pt, Sau 6pt | `\titleformat{\section}` |
| **Tiểu mục cấp 2 (`\subsection` X.Y.Z)** | 13pt | In đậm | Trái | Trước 9pt, Sau 4pt | `\titleformat{\subsection}` |
| **Tiểu mục cấp 3 (`\subsubsection` X.Y.Z.W)** | 13pt | In đậm nghiêng | Trái | Trước 6pt, Sau 3pt | `\titleformat{\subsubsection}` |
| **Thân bài (Body text)** | **13pt** | Thường, dãn dòng 1.5 | Đều 2 bên | Thụt lề 1.0cm | `\usepackage[fontsize=13pt]{scrextend}` |
| **Tiêu đề Bảng (`\caption` trên)** | 12pt | Nhãn Đậm, Tên Nghiêng | Giữa | Trên bảng, cách 6pt | `\captionsetup[table]{position=top}` |
| **Tiêu đề Hình (`\caption` dưới)** | 12pt | Nhãn Đậm, Tên Nghiêng | Giữa | Dưới hình, cách 6pt | `\captionsetup[figure]{position=bottom}` |
| **Số trang báo cáo** | 10pt | Footer Đứng (không in nghiêng) | Phải | Góc dưới bên phải | `\fontsize{10}{12}\selectfont\normalfont\upshape` |
| **Chú thích chân trang (`\footnote`)** | 10pt | Thường, dãn đơn | Đều 2 bên | Dưới chân trang | `\fontsize{10}{13}\selectfont` |

---

### 2.4. Quy tắc phân cấp đề mục và các điều luật tiêu cực bất biến
1. **Độ sâu phân cấp tối đa 4 cấp:** Các tiểu mục được đánh số thành nhóm số nhiều nhất gồm 4 chữ số: `Chương.Mục.TiểuMục.Nhóm` (ví dụ `4.1.2.1` chỉ tiểu mục 1 nhóm tiểu mục 2 mục 1 chương 4). Tuyệt đối không đánh số cấp thứ 5 (như `3.1.2.1.1`).
2. **LUẬT BẤT BIẾN CẤM TIỂU MỤC ĐƠN LẺ (NO SINGLETON SUBSECTIONS):**
   - Tại mỗi nhóm tiểu mục bắt buộc phải có **ít nhất hai tiểu mục**. Quy tắc cấm tiểu mục đơn lẻ (singleton subsection rule) yêu cầu mỗi nhóm phải có tối thiểu 2 mục con.
   - Nghĩa là: **Tuyệt đối không thể có tiểu mục `2.1.1` mà không có tiểu mục `2.1.2` tiếp theo**. Nếu một nội dung không đủ để phân chia thành 2 tiểu mục con độc lập, bắt buộc phải viết trực tiếp dưới mục cha `2.1` mà không đánh số phân cấp!
3. **Danh ngữ hóa tiêu đề và Độ dài chuẩn mực (3 đến 7 từ):**
   - Mọi tiêu đề mục từ cấp 1 đến cấp 4 phải là một cụm danh từ cô đọng, định danh trực diện đối tượng khoa học/kỹ thuật.
   - Tuyệt đối cấm tiêu đề dạng mệnh đề kể lể mở đầu bằng động từ (*"Nghiên cứu về..."*, *"Tìm hiểu giải pháp..."*, *"Hiện thực hóa luồng..."*).
4. **Chống tiêu đề mồ côi (No Orphan Headings):** Tuyệt đối cấm để tiêu đề mục nằm trơ trọi ở dòng cuối cùng của trang in mà không có ít nhất 2-3 dòng văn bản thân bài đi kèm bên dưới.
5. **LUẬT BẤT BIẾN CẤM TỰ Ý ĐÁNH SỐ THỨ TỰ TRONG NỘI DUNG (NO ARBITRARY NUMBERING):**
   - **TUYỆT ĐỐI CẤM** tự ý đánh số thứ tự dạng `(1)`, `(2)`, `(3)...` hoặc `1.`, `2.`, `3.` trong các đoạn văn thân bài, danh sách liệt kê hoặc mở đầu các ý tưởng.
   - Ngoại lệ duy nhất được đánh số là: (a) Mã phân cấp đề mục chính thức tối đa 4 cấp (`X.Y.Z.W`); (b) Cột STT trong bảng biểu; (c) Các bước tuần tự có thứ tự nghiêm ngặt trong bảng đặc tả Use Case (`\begin{enumerate}`).
   - Khi cần liệt kê trong thân bài, bắt buộc phải sử dụng môi trường `\begin{itemize}` với dấu gạch đầu dòng (`-`) hoặc trình bày thành các đoạn văn xuôi liên tục được liên kết bằng từ nối học thuật (*"Trước hết"*, *"Tiếp theo"*, *"Bên cạnh đó"*, *"Cuối cùng"*).
6. **LUẬT CẤM TÙY TIỆN IN ĐẬM VĂN BẢN (NO ARBITRARY BOLDING):**
   - **TUYỆT ĐỐI CẤM** tùy tiện in đậm (`\textbf{...}`) các cụm từ, nhãn phân đoạn tự chế trong đoạn văn thân bài (ví dụ: cấm in đậm dạng `\textbf{(1) Bộ đánh giá...}`, `\textbf{Về dữ liệu:}`).
   - Chữ in đậm chỉ được phép xuất hiện tại:
     - Tiêu đề chương, mục và tiểu mục được định dạng tự động qua `\titleformat`.
     - Nhãn của bảng và hình trong `\caption` (`\textbf{Bảng 3.1:}`, `\textbf{Hình 3.1:}`).
     - Hàng tiêu đề cột trong bảng (`\textbf{STT}`, `\textbf{Tên trường}`).
     - Ký hiệu toán học vector hoặc ma trận trong công thức (`\mathbf{u}`).
7. **LUẬT TUYỆT ĐỐI CẤM SỬ DỤNG KÝ TỰ `&` TRONG VĂN BẢN TIẾNG VIỆT:**
   - **TUYỆT ĐỐI CẤM** sử dụng ký tự `&` (kể cả đã thoát `\&`) trong tiêu đề chương mục, tiêu đề bảng biểu, tiêu đề hình vẽ và toàn bộ nội dung văn bản tiếng Việt. Bắt buộc phải viết rõ chữ **"và"**.
   - *Ngoại lệ kỹ thuật duy nhất:* Ký tự `&` chỉ được phép dùng làm ký tự phân tách cột trong môi trường bảng của LaTeX (`tabular`, `tabularx`) hoặc trong tên riêng/thương hiệu quốc tế cố định không dịch.
8. **QUY CHUẨN VIẾT HOA CHÍNH TẢ TIẾNG VIỆT (CHỐNG LỖI TITLE CASE TIẾNG ANH):**
   - **TUYỆT ĐỐI CẤM** viết hoa tùy tiện chữ cái đầu của từng từ (Title Case) trong tiêu đề mục và nội dung thân bài theo phong cách tiếng Anh (ví dụ: SAI: *"Nghiên Cứu Cơ Sở Lý Thuyết Và Công Nghệ Mới"* $\rightarrow$ ĐÚNG: *"Nghiên cứu cơ sở lý thuyết và công nghệ mới"*).
   - Chỉ viết hoa chữ cái đầu câu/tiêu đề và các danh từ riêng, tên địa danh, tổ chức hợp pháp hoặc từ viết tắt chuyên ngành.
9. **LUẬT TUYỆT ĐỐI CẤM IN NGHIÊNG TÙY TIỆN TRONG THÂN BÀI (NO ARBITRARY ITALICS):**
   - Trong toàn bộ nội dung thân bài (Chương 1 đến Chương 4, Lời mở đầu, Kết luận), **chữ in nghiêng CHỈ ĐƯỢC PHÉP XUẤT HIỆN DUY NHẤT TẠI TIÊU ĐỀ TIỂU MỤC CẤP 3 (`\subsubsection`)**.
   - **TUYỆT ĐỐI CẤM** sử dụng các lệnh `\textit{...}`, `\emph{...}` để in nghiêng các từ ngữ, thuật ngữ tiếng Anh, cụm từ nhấn mạnh trong các đoạn văn thân bài. Toàn bộ phải chuyển về chữ thường đứng (regular upright font).
   - *Ngoại lệ chuẩn học thuật duy nhất bên ngoài thân bài:* (a) Tiêu đề sách, tạp chí trong danh mục tài liệu tham khảo (`tai_lieu_tham_khao.tex`) theo chuẩn trích dẫn Phụ lục 3 HUMG; (b) Tên đối tượng trong nhãn `\caption` của Bảng và Hình (`\textbf{Bảng X-Y:} \textit{Tên bảng}`); (c) Tiêu đề tiểu mục cấp 3 (`\subsubsection{...}`).

---

### 2.5. Quy chuẩn bảng biểu, hình vẽ, công thức toán và cấm dẫn chiếu tương đối
1. **Đánh số đối tượng gắn liền với số chương:**
   - Mọi hình vẽ, bảng biểu và công thức toán phải đánh số gắn liền với số thứ tự chương ($X$) và số thứ tự đối tượng trong chương ($Y$):
     - **Bảng biểu và Hình vẽ (dấu gạch nối `-`):** Bắt buộc đánh số theo định dạng `Chương-Số`: `Bảng X-Y` và `Hình X-Y` (ví dụ: `Bảng 1-1`, `Hình 3-1`), đồng bộ với macro `\thetable` và `\thefigure` trong `report-datn/config/preamble.tex` và danh mục LoT/LoF.
     - **Công thức toán (dấu chấm `.`):** Đánh số theo định dạng `(X.Y)` đặt trong ngoặc đơn sát lề phải trang (ví dụ: `(2.1)`, `(3.1)`).
2. **Quy tắc vị trí đặt đầu đề (Caption Placement Invariant):**
   - **ĐẦU ĐỀ BẢNG BIỂU: BẮT BUỘC ĐẶT Ở PHÍA TRÊN BẢNG**.
   - **ĐẦU ĐỀ HÌNH VẼ: BẮT BUỘC ĐẶT Ở PHÍA DƯỚI HÌNH**.
   - Vi phạm vị trí đầu đề bảng/hình bị coi là lỗi định dạng nghiêm trọng bị trừ điểm trực tiếp trong quy chế chấm đồ án.
3. **LUẬT TUYỆT ĐỐI CẤM THAM CHIẾU TƯƠNG ĐỐI (NO RELATIVE CITATIONS):**
   - Khi dẫn giải đến bất kỳ hình vẽ, bảng biểu hoặc công thức nào trong bài, **bắt buộc phải gọi đích danh mã định danh chính xác**: `"kết quả được tổng hợp trong Bảng 4.2"`, `"(xem Hình 3.1)"`, `"tính toán theo Công thức (2.3)"`.
   - **TUYỆT ĐỐI CẤM SỬ DỤNG CÁC CỤM TỪ TƯƠNG ĐỐI NHƯ:**
     - ❌ *"như trong hình dưới đây"*
     - ❌ *"kết quả ở bảng sau"*
     - ❌ *"trong sơ đồ trên"*
     - ❌ *"như bảng ngay sau đây"*
   - *Lý do khoa học:* Trong chế bản in ấn, hình ảnh và bảng biểu là các đối tượng trôi dạt (Floats), có thể tự động nhảy sang trang tiếp theo; việc dùng tham chiếu tương đối làm mất tính chính xác khoa học.
4. **Quy Chuẩn Kỹ Nghệ Bảng Biểu Nâng Cao:**
   - Mọi bảng có chứa nội dung văn bản dài, đặc tả nghiệp vụ hoặc từ điển CSDL bắt buộc phải sử dụng môi trường `tabularx` với độ rộng đúng bằng `\textwidth` (`\begin{tabularx}{\textwidth}{|...|}`).
   - Sử dụng cột loại `X` (hoặc `>{\raggedright\arraybackslash}X`) để bảng tự động ngắt dòng chữ, tuyệt đối không dùng cột `l` hay `c` khiến dòng chữ bị đâm thủng lề phải $15{,}0\,\text{cm}$.
   - **Quy chuẩn kẻ khung viền đồ án:** Bảng phải có khung viền khép kín 4 góc ngoài (`|...|`) và các đường kẻ ngang `\hline` phân cách từng dòng theo đúng mẫu ĐATN truyền thống (tuyệt đối không dùng bảng hở cạnh `booktabs` như `\toprule`, `\midrule`, `\bottomrule` gây đứt đoạn vạch kẻ dọc).
   - Nếu bảng quá dài phải ngắt qua trang, bảng ở trang mới phải có dòng tiêu đề cột lặp lại kèm nhãn `Bảng X-Y (tiếp theo)`.
5. **Quy Chuẩn Biểu Diễn Sơ Đồ Kiến Trúc Hệ Thống Chuẩn Paper Khoa Học Quốc Tế (Human-Centric Academic Paper Architecture):**
   - **Kiến trúc cho người đọc, không phải cho máy đọc:** Mọi sơ đồ kiến trúc và mô tả hệ thống trong báo cáo đồ án (đặc biệt tại Chương 2 và Chương 3) phải được thiết kế theo tư duy của các bài báo khoa học quốc tế uy tín (như mô hình Transformer Attention, kiến trúc RAG, GraphRAG của cộng đồng nghiên cứu). Sơ đồ phải đóng vai trò là một mô hình tư duy học thuật (*Academic Mental Model*) tự giải thích, giúp người đọc nắm bắt ngay đóng góp khoa học và tính mới của đề tài.
   - **Quy chuẩn Biểu đồ Use Case và Actor hình người que:**
     - Mọi biểu đồ Use Case (tổng quan và phân rã) bắt buộc phải sử dụng biểu tượng Tác nhân (Actor) bằng hình người que chuẩn UML (`stick figure` khai báo qua TikZ `pic {umlactor}`), **TUYỆT ĐỐI CẤM** vẽ Actor thành hình hộp chữ nhật.
     - **Nguyên tắc vẽ sơ đồ ca sử dụng con trước khi đặc tả:** Tất cả các ca sử dụng con (sub-Use Cases) trong Chương 3 bắt buộc phải có biểu đồ phân rã (`\begin{tikzpicture}`) đặt ở vị trí ngay phía trên, sau đó mới đến bảng đặc tả chi tiết (Bảng chuẩn BA). Cấm trình bày đặc tả mà không có hình vẽ sơ đồ trực quan đi kèm.
   - **Quy chuẩn Biểu đồ lớp (Domain Model Class Diagram) thực thể hệ thống:**
     - Tại Mục 3.6 (Thiết kế cơ sở dữ liệu), BẮT BUỘC phải xây dựng Biểu đồ lớp (Class Diagram) mô hình hóa cấu trúc tĩnh của các thực thể nghiệp vụ hạt nhân (Domain Model / Architectural Class Diagram), và **đặt ở vị trí ngay trước các bảng dữ liệu** / từ điển CSDL.
     - Biểu đồ lớp phải thể hiện rõ tên lớp thực thể, danh sách thuộc tính cốt lõi, kiểu dữ liệu và mối quan hệ liên kết (1-1, 1-N, N-N), quan hệ kết tập (Aggregation), hợp thành (Composition).
     - *Lưu ý phân biệt:* Chỉ nghiêm cấm biểu đồ lớp máy móc vụn vặt kiểu lập trình viên (chỉ liệt kê getter/setter hoặc CRUD đơn thuần); biểu đồ lớp thực thể miền nghiệp vụ (Domain Entity Class Diagram) là thành phần học thuật bắt buộc theo đúng quy định form của Khoa và GVHD.
6. **Quy Chuẩn Kỹ Nghệ Sơ Đồ TikZ Chống Chồng Đè VÀ Ríu Rít (7 Nguyên Tắc Vàng):**
   - *Nguyên tắc 1 — Tối giản ruột node (Max 2 lines):* Tối đa 2 dòng văn bản trong một khối chức năng (`\textbf{Tên}`, `\scriptsize (Ký hiệu)`).
   - *Nguyên tắc 2 — Kích thước cố định:* Luôn khai báo `text width` và `minimum height` tường minh.
   - *Nguyên tắc 3 — Bố cục phân dải màu:* Gom nhóm bằng khung bao màu pastel bo tròn góc (`rounded corners=8pt`).
   - *Nguyên tắc 4 — Định tuyến trực giao:* Mũi tên góc vuông `|-` hoặc `-|`, tuyệt đối cấm vẽ đường xiên chéo cắt qua mặt chữ.
   - *Nguyên tắc 5 — Hành lang độc lập:* Các luồng song song hoặc phản hồi phải cách nhau tối thiểu $\Delta y \ge 0{,}6\,\text{cm}$.
   - *Nguyên tắc 6 — Nhãn mũi tên cách ly:* Nhãn trên đường vẽ bắt buộc có nền trắng `fill=white` để không bị đè vạch kẻ.
   - *Nguyên tắc 7 — Khổ giấy an toàn:* Khai báo `scale=0.74` đến `0.80`, bảo đảm chiều ngang sơ đồ luôn $\le 15{,}0\,\text{cm}$.
7. **Công thức toán học và trình bày độ đo:**
   - Công thức căn giữa trên dòng riêng, đánh số thứ tự trong ngoặc đơn đặt sát lề phải `(X.Y)`.
   - Ngay sau công thức, bắt buộc có mệnh đề giải nghĩa toàn bộ biến số (*"Trong đó: $A$ là...; $B$ là..."*).
   - Biến số đơn ký tự in nghiêng (`$q, d$`); ký hiệu vector/ma trận in đậm (`\mathbf{u}`); tên độ đo nhiều ký tự bắt buộc bọc trong `\text{...}` hoặc `\operatorname{...}`: $\text{IoU} \ge 0{,}85$, $\text{RRF}(d)$, $\text{BLEU}$, $\text{F1-score}$.
   - Số thập phân tiếng Việt phải bọc dấu phẩy trong ngoặc nhọn: `$0{,}85$`, `$1{,}66\,\text{ms}$` để tránh khoảng trắng toán học.
8. **QUY CHUẨN ĐỘC TÔN HÌNH ẢNH ĐỊNH DẠNG PNG VÀ KHỔ IN A4 (R1 COMPLIANCE):**
   - 100% hình ảnh chèn vào báo cáo thông qua lệnh `\includegraphics` bắt buộc phải là định dạng `.png` và được lưu trữ tập trung tại `./report-datn/figures/` (hoặc các thư mục con bên trong).
   - Tuyệt đối cấm sử dụng các tệp ảnh non-PNG như `.jpg`, `.jpeg`, `.pdf`, `.svg` trong lệnh chèn hình.
   - Kích thước hình ảnh phải được thiết lập vừa vặn với khổ giấy A4 khả dụng ($15{,}0\,\text{cm}$), hiển thị rõ nét chi tiết khi in hoặc photo trên giấy A4. Khai báo tỷ lệ `width=0.85\textwidth` đến `0.95\textwidth` hoặc `width=14cm`.
   - Tuyệt đối cấm co nhỏ hình ảnh quá mức (dưới 8cm) để kéo dồn trang gây mờ và khó đọc.
9. **QUY CHUẨN SƯỜN/GÁY BÌA NGOÀI VÀ MỤC LỤC KHÔNG IN ĐẬM (R2, R3 COMPLIANCE):**
   - **Sườn/gáy dọc bìa chính (Bìa 1):** Bắt buộc thiết kế dải sườn/gáy in dọc mép trái trang bìa ngoài (TikZ overlay xoay 90°) gồm 3 khối thông tin in hoa, in đậm theo đúng trang 1 của `guide/HIeu.pdf`:
     + Khối trên: Tên sinh viên thực hiện (`ĐÀM MẠNH DŨNG` - 16pt Đậm)
     + Khối giữa: Chuyên ngành (`HỆ THỐNG THÔNG TIN` - 16pt Đậm)
     + Khối dưới: Khóa học (`KHÓA 67` - 16pt Đậm)
     + Trang bìa chính và bìa phụ tuyệt đối không có tiền tố thừa `"TÊN ĐỀ TÀI:"`.
   - **Mục lục không in đậm (No Bold in TOC):** Trong Mục lục, toàn bộ tiêu đề các chương, mục, tiểu mục đều phải hiển thị bằng nét thường (`\cftchapfont{\normalfont}`). Sau số chương có dấu hai chấm và dấu cách (`CHƯƠNG X: `) kèm chấm dẫn `\cftdotfill{\cftdotsep}` dẫn tới số trang.

---

### 2.6. Quy chuẩn từ viết tắt và danh mục tài liệu tham khảo
1. **Quy tắc sử dụng từ viết tắt:**
   - Chỉ viết tắt những thuật ngữ chuyên ngành được sử dụng nhiều lần trong đồ án.
   - Không lạm dụng viết tắt; không viết tắt những cụm từ dài hoặc mệnh đề.
   - **Tuyệt đối cấm viết tắt trong tên chương và tên mục chính**.
   - Lần đầu xuất hiện trong bài: Phải viết đầy đủ thuật ngữ kèm chữ viết tắt trong ngoặc đơn. Ví dụ: *Cơ sở dữ liệu (CSDL)* hoặc *Retrieval-Augmented Generation (RAG)*.
   - Bảng *Danh mục các ký hiệu và chữ viết tắt* ở phần Frontmatter bắt buộc phải sắp xếp theo **thứ tự bảng chữ cái ABC**.
2. **Quy chuẩn sắp xếp Danh mục Tài liệu tham khảo (Phụ lục 3 HUMG):**
   - **Phân nhóm ngôn ngữ bắt buộc:** Phân tách rõ ràng thành 2 nhóm:
     - `I. Tài liệu tiếng Việt` (đặt lên đầu tiên).
     - `II. Tài liệu tiếng Anh` (và tiếng nước ngoài khác đặt sau).
   - **Bảo toàn nguyên văn:** Tài liệu tiếng nước ngoài phải giữ nguyên văn, không phiên âm, không dịch.
   - **Thứ tự sắp xếp bảng chữ cái ABC:**
     - Tác giả Việt Nam: Xếp thứ tự ABC theo **TÊN** của tác giả, nhưng **giữ nguyên thứ tự thông thường Họ Tên** (ví dụ: *"Nguyễn Đình Thúc"* xếp vần T, không được đảo thành *"Thúc, Nguyễn Đình"*).
     - Tác giả nước ngoài: Xếp thứ tự ABC theo **HỌ (Surname)** của tác giả (ví dụ: *"Vaswani A."* xếp vần V).
     - Tài liệu không có tên tác giả cá nhân: Xếp thứ tự ABC theo chữ cái đầu của **tên cơ quan ban hành** ấn phẩm (ví dụ: *Bộ Giáo dục và Đào tạo* xếp vần B).
   - **Quy cách trình bày thông tin:**
     - *Sách, đồ án, giáo trình:* Tên tác giả (Năm xuất bản), *Tên sách/đồ án (in nghiêng)*, Nhà xuất bản, Nơi xuất bản.
     - *Bài báo tạp chí, kỷ yếu hội thảo:* Tên tác giả (Năm công bố), "Tên bài báo (ngoặc kép, đứng)", *Tên tạp chí/kỷ yếu (in nghiêng)*, Tập(Số), Các số trang.
   - **Quy cách thụt lề dòng thứ hai (Hanging Indent):** Nếu tài liệu dài hơn 1 dòng, từ **dòng thứ hai trở đi bắt buộc lùi vào $1{,}0\,\text{cm}$** so với dòng thứ nhất để danh mục rõ ràng, chuyên nghiệp.
   - **Giới hạn số lượng tài liệu tham khảo ($\le 20$):**
     - Toàn bộ danh mục tài liệu tham khảo bắt buộc phải thỏa mãn trần nghiêm ngặt: $\mathbf{0 < N_{\text{refs}} \le 20}$.
     - Tuyệt đối không nhồi nhét tài liệu rác để kéo dài số lượng. Chỉ trích dẫn các công trình nền tảng có bình duyệt (Peer-reviewed) và tài liệu quy chế chính thức.
   - **Cấm tuyệt đối trích dẫn mồ côi (Zero Orphan References):** 100% tài liệu liệt kê trong danh mục cuối bài bắt buộc phải được dẫn chiếu trực tiếp bằng lệnh `\cite{...}` (dạng `[1]`, `[2]`) ít nhất một lần trong phần nội dung thân bài.
3. **Tinh giản trích dẫn tham chiếu và cấm rải dày đặc (Streamlined Citations):**
   - **TUYỆT ĐỐI CẤM** rải các cụm trích dẫn dày đặc, rải rác lặp lại không thiết yếu trong các đoạn văn thân bài (đặc biệt tại Chương 3 và Chương 4).
   - Các công trình nghiên cứu và tài liệu tham khảo phải được trích dẫn tập trung, đích đáng tại Chương 1 và Chương 2 nơi phân tích bối cảnh, cơ sở lý thuyết và công nghệ nền tảng.
   - Chương 3 và Chương 4 chỉ tập trung vào thiết kế hệ thống và kết quả thực nghiệm của chính đề tài, không lặp lại trích dẫn lý thuyết chung chung.

---

### 2.7. Tỷ lệ phân bổ nội dung vàng (Content Golden Ratio)
Dựa trên khảo sát thực tế các ĐATN đạt điểm Xuất sắc tại Khoa CNTT — HUMG, phân bổ dung lượng báo cáo bắt buộc phải tuân theo **Tỷ Lệ Phân Bổ Vàng**:

$$\mathbf{Lý\ thuyết\ (Chương\ 1\ +\ Chương\ 2)\ \le\ 30\%} \quad \Big\vert \quad \mathbf{Thiết\ kế\ và\ Thực\ nghiệm\ (Chương\ 3\ +\ Chương\ 4)\ \ge\ 70\%}$$

```
+─────────────────────────────────────────────────────────────────────────────────────────+
│              MA TRẬN PHÂN BỔ DUNG LƯỢNG VÀ SỐ TRANG CHUẨN MỰC (50 -- 65 TRANG)          │
+─────────────────────────────────────────────────────────────────────────────────────────+
│ Khối Nội Dung          │ Mục Tiêu Trọng Tâm               │ Ngân Sách Trang │ Tỷ Lệ %  │
+────────────────────────┼──────────────────────────────────┼─────────────────┼──────────+
│ Lời mở đầu và Chương 1 │ Bối cảnh, mục tiêu, phạm vi      │ 6 -- 8 trang    │ ~12%     │
│ Chương 2               │ Cơ sở lý thuyết và Why-chosen    │ 10 -- 12 trang  │ ~18%     │
│ ──► TỔNG LÝ THUYẾT     │ Khảo sát và Nền tảng khoa học    │ 16 -- 20 trang  │ <= 30%   │
+────────────────────────┼──────────────────────────────────┼─────────────────┼──────────+
│ Chương 3               │ 5 bước kỹ nghệ, Use Case, CSDL   │ 18 -- 24 trang  │ ~40%     │
│ Chương 4               │ Cài đặt, giao diện, đo lường     │ 12 -- 16 trang  │ ~26%     │
│ Kết luận và Hướng đi   │ Đóng góp đạt được và Hướng mở rộng│ 2 -- 3 trang   │ ~4%      │
│ ──► TỔNG THỰC HÀNH     │ Kỹ nghệ hệ thống và Thực nghiệm  │ 32 -- 43 trang  │ >= 70%   │
+────────────────────────┼──────────────────────────────────┼─────────────────┼──────────+
│ TỔNG QUY MÔ BÁO CÁO    │ Ruột nội dung chính              │ 50 -- 65 trang  │ 100%     │
+─────────────────────────────────────────────────────────────────────────────────────────+
```

* **Quy chuẩn Phụ lục:** Căn cứ Mục B.III.7 `Huong-dan-viet-DATN.md`: **Phụ lục không được dày hơn phần chính của đồ án** (khống chế trong khoảng 5--10 trang). Toàn bộ mã nguồn đầy đủ phải lưu trữ trong thư mục bản mềm.

---

## PHẦN 3: NGUYÊN TẮC VẬN HÀNH CHO AI AGENT VÀ HÀNG RÀO PHÒNG NGỪA 7 ANTI-PATTERNS

### 3.1. Năm nguyên tắc vận hành bất biến cho AI Agent

#### Nguyên Tắc 1: Tháp thẩm quyền học thuật và chân lý duy nhất (Single Source of Truth)
Khi có sự sai lệch hoặc mâu thuẫn thông tin giữa các tài liệu, AI Agent bắt buộc phải tuân thủ thứ bậc thẩm quyền:
$$\mathbf{Quy\ chế\ HUMG\ và\ INFORMATION.md} = \mathbf{Mã\ nguồn\ thực\ tế\ và\ Test\ Pass} > \mathbf{Tài\ liệu\ specs/docs/} > \mathbf{Suy\ luận\ nội\ suy\ của\ AI}$$
*AI Agent tuyệt đối không tự bịa đặt tính năng, thông số hiệu năng hoặc cấu trúc bảng CSDL mà không có trong `report-datn/INFORMATION.md` hoặc mã nguồn thực tế đã vượt qua kiểm thử.*

#### Nguyên Tắc 2: Kỷ luật ngữ cảnh vi mô (Micro-Modular Context Discipline)
Một quyển đồ án 65 trang chứa hàng chục nghìn dòng LaTeX. Nếu nạp toàn bộ báo cáo vào Context Window sẽ gây hiện tượng "ảo giác vị trí" (*Lost in the Middle*) và dễ gây lỗi sửa lan (*Collateral Damage*).
*Agent chỉ được phép nạp duy nhất 1 tệp vi mô `.tex` mục tiêu kết hợp tệp chỉ mục điều hướng `report-datn/ROADMAP.md`. Tuyệt đối không đọc toàn bộ báo cáo trong một tác vụ đơn lẻ.*

#### Nguyên Tắc 3: Biên soạn XeLaTeX phòng thủ (Defensive XeLaTeX Editing)
XeLaTeX là trình biên dịch nghiêm ngặt; một lỗi ký tự chưa thoát có thể làm đổ vỡ toàn bộ chu trình build:
- **Thoát ký tự nhạy cảm:** Mọi ký tự `\_`, `\%`, `\&`, `\#`, `\$`, `\{`, `\}` xuất hiện trong văn bản thường, tên biến, tên trường CSDL bắt buộc phải thoát dấu gạch chéo ngược hoặc bọc trong `\texttt{...}`.
- **Bất biến nhãn tham chiếu (`\label{...}` Invariance):** Tuyệt đối không xóa, đổi tên hoặc sửa nhãn của các Hình (`fig:...`) và Bảng (`tab:...`) đã được xác lập trong hệ thống kiểm thử tự động.
- **Cấm để lộ mã thô:** Trong mọi bản nháp duyệt trước, trích dẫn phải hiển thị chuẩn dạng số `[1]`, `[2]`, tuyệt đối không để lộ mã LaTeX thô như `\cite{...}. T`.

#### Nguyên Tắc 4: Lập luận "Tại sao chọn" (Justification-Driven)
Khác với tài liệu hướng dẫn kỹ thuật thông thường, đồ án đại học đòi hỏi tư duy phản biện khoa học. Khi giới thiệu bất kỳ công nghệ hoặc giải pháp nào ở Chương 2, AI Agent không chỉ nêu khái niệm mà bắt buộc phải trả lời câu hỏi cốt tử của Hội đồng: *"Tại sao đề tài chọn giải pháp này mà không chọn giải pháp khác?"*:
- Nêu rõ bản chất lý thuyết và nguyên lý hoạt động.
- Lập bảng so sánh đa tiêu chí với các giải pháp cạnh tranh.
- Đưa ra đoạn văn khẳng định lý do lựa chọn gắn chặt với ràng buộc của bài toán.

#### Nguyên Tắc 5: Văn phong khách quan và kim tự tháp Minto
- **Ngôi văn khách quan chuẩn mực:** Tuyệt đối cấm sử dụng đại từ nhân xưng ngôi thứ nhất (*"tôi"*, *"em"*, *"chúng tôi"*, *"chúng em"*). Toàn bộ nội dung dùng ngôi thứ ba học thuật: *"tác giả"*, *"đề tài"*, *"nghiên cứu này"*. Ngoại lệ kỹ thuật duy nhất là chữ viết tắt metric học thuật Exact Match (EM).
- **Danh ngữ hóa tiêu đề:** Mọi tiêu đề mục từ cấp 2 đến cấp 4 phải là cụm danh từ cô đọng từ 3 đến 7 từ. Cấm mở đầu tiêu đề bằng động từ kể lể.
- **Cấu trúc đoạn văn Minto Pyramid:** Câu đầu đoạn (Topic sentence) nêu trực diện luận điểm cốt lõi; các câu tiếp theo đưa ra số liệu, công thức, bảng so sánh đối chứng; câu cuối chốt ý nghĩa và dẫn chiếu chéo `Hình~\ref{...}` hoặc `Bảng~\ref{...}`.

---

### 3.2. Hàng rào phòng ngừa 7 Anti-Patterns học thuật (AP-01 đến AP-07)

| Mã | Anti-Pattern Cần Triệt Tiêu | Biểu Hiện Vi Phạm Của AI | Hậu Quả Học Thuật | Hàng Rào Bảo Vệ Bắt Buộc (Guardrail) |
| :---: | :--- | :--- | :--- | :--- |
| **AP-01** | **Chép lý thuyết giáo trình chung chung (Wikipedia / Textbook Dump)** | Dành 5-7 trang chép định nghĩa chung về Docker, Python, PostgreSQL, REST API, React mà không gắn với bài toán. | Làm loãng hàm lượng khoa học; Hội đồng đánh giá sao chép giáo trình, trừ điểm năng lực. | **Hàng rào Giới hạn Định nghĩa và Luận giải Kỹ thuật:**<br>• Định nghĩa cơ bản $\le 2$ đoạn văn.<br>• Bắt buộc có phần "Luận giải lựa chọn kỹ thuật trong đề tài".<br>• Tuân thủ nghiêm ngặt bảng ma trận KEEP/OMIT tại Mục 3.3 ngay dưới đây. |
| **AP-02** | **Rò rỉ chi tiết mã nguồn vào Chương 2 (Source Code Spillover into Ch2)** | Chèn đường dẫn file repo (`packages/core/...`), tên interface code (`IAcademicSearchResolverPort`) vào Chương 2. | Vi phạm nguyên tắc phân tách ranh giới học thuật giữa Lý thuyết (Ch2) và Thiết kế/Cài đặt (Ch3/Ch4). | **Hàng rào Cách ly Học thuật Chương 2 (Chapter 2 Isolation):**<br>• Chương 2 chỉ trình bày mô hình toán học, nguyên lý thuật toán và kiến trúc khái niệm.<br>• Kiểm tra tự động bằng bài test `test_thesis_chapter2_academic_purity`. |
| **AP-03** | **Dán mã nguồn thô hàng trăm dòng (Raw Source Code Dumps)** | Sao chép nguyên khối code dài hàng chục, hàng trăm dòng từ repo vào thân bài để "kéo trang". | Biến đồ án thành tệp in code; vi phạm nghiêm trọng tính cô đọng học thuật. | **Hàng rào Trích dẫn Tinh gọn:**<br>• Cấm dán code thô quá 15-20 dòng trong thân bài.<br>• Chỉ dùng mã giả giải thuật (`algorithm2e`) hoặc khối hàm logic hạt nhân.<br>• Toàn bộ code đầy đủ chuyển vào Phụ lục hoặc đĩa mềm. |
| **AP-04** | **Số liệu thực nghiệm bịa đặt / Ảo giác chỉ số (Hallucinated Metrics)** | AI tự điền các con số không có thật: "độ chính xác đạt 99.8%", "thời gian phản hồi 0.001s", "đã kiểm thử 10.000 ca". | Gian lận học thuật; sinh viên sẽ bị trượt ngay khi Hội đồng yêu cầu mở log kiểm chứng. | **Hàng rào Bằng chứng Đo lường Thực tế (Empirical Proof):**<br>• Mọi số liệu trong Chương 4 phải khớp 100% với output thật được khóa cứng tại `report-datn/INFORMATION.md`. |
| **AP-05** | **Trích dẫn ma và Thổi phồng số lượng tài liệu (Phantom and Bloated References)** | AI tự bịa bài báo không tồn tại, hoặc thêm 50-60 tài liệu từ blog không rõ nguồn gốc để làm danh mục đồ sộ. | Vi phạm liêm chính khoa học quốc tế; dễ bị phát hiện qua Google Scholar. | **Hàng rào Trần Tham Chiếu Tinh Hoa:**<br>• Bắt buộc số lượng tài liệu tham khảo $N_{\text{refs}} \le 20$.<br>• Chỉ trích dẫn bài báo gốc có bình duyệt từ danh mục chính thức tại `report-datn/INFORMATION.md`.<br>• Cấm trích dẫn mồ côi (100% ref đều phải có `\cite` trong thân bài). |
| **AP-06** | **Thiết kế CSDL và Sơ đồ "ma" không thể tái lập (Irreproducible Architecture)** | Vẽ sơ đồ hoặc khai báo bảng CSDL không có thật trong code (như 4 bảng ảo `extracted_figures`, `latex_compilations`...). | Đồ án không có tính tái lập (*Non-reproducible*); không thể bảo vệ trước câu hỏi kỹ thuật. | **Hàng rào Đồng bộ Schema 1:1:**<br>• Bắt buộc mô tả đúng 20 bảng CSDL thực tế quy định tại `report-datn/INFORMATION.md`.<br>• Loại bỏ vĩnh viễn 4 bảng ảo: `extracted_figures`, `extracted_tables`, `draft_sections`, `latex_compilations`.<br>• Đúng tên khóa ngoại và thuật toán thực tế. |
| **AP-07** | **Sơ đồ ríu rít, đâm thủng lề và Bảng biểu vỡ khung (Visual Overflow and Clutter)** | Vẽ TikZ mũi tên xiên chéo cắt qua mặt chữ, bảng dài vượt quá lề phải 15cm, tạo ra trang trắng mồ côi. | Báo cáo in ra bị lỗi hình thức nghiêm trọng, mất thẩm mỹ chuyên nghiệp. | **Hàng rào 7 Nguyên Tắc Vàng TikZ và Tabularx:**<br>• Bề rộng sơ đồ $\le 15{,}0\,\text{cm}$, scale 0.74 -- 0.80.<br>• Định tuyến góc vuông (`|-`), nhãn nền trắng `fill=white`.<br>• Bắt buộc dùng `tabularx` có viền khép kín `|...|`. |

---

### 3.3. CHIẾN LƯỢC CHẮT LỌC NỘI DUNG TỪ DOCS (KEEP AND ELEVATE VS. OMIT)

Để phòng ngừa triệt để AP-01, AP-02 và AP-03, AI Agent bắt buộc phải tuân thủ ma trận chắt lọc nội dung dưới đây khi chắt lọc và chuyển đổi tài liệu kỹ thuật từ thư mục `docs/` vào các chương báo cáo:

| Phân Vùng Báo Cáo | GIỮ & NÂNG TẦM (Keep & Elevate) | LƯỢC BỎ (Omit / Eliminate) |
| :--- | :--- | :--- |
| **Chương 1: Tổng quan đề tài** | • Bối cảnh học thuật đặc thù tại VinUni và các trường đại học định hướng nghiên cứu.<br>• Khoảng trống công nghệ: LLM Hallucination trong trích dẫn học thuật, mất mát cấu trúc 2 cột trong ChatPDF, thiếu phản hồi biên dịch LaTeX khép kín.<br>• 4 Không gian nghiên cứu khép kín.<br>• 4 đóng góp kỹ thuật cốt lõi. | • Hướng dẫn cài đặt môi trường lập trình (`uv run dev`, `.env`).<br>• Chi tiết các endpoint API thô.<br>• Các câu hỏi phỏng vấn hay mô tả tính năng giao diện vụn vặt. |
| **Chương 2: Cơ sở lý thuyết và công nghệ** | • Lý thuyết toán học đằng sau RRF: công thức $RRF(d) = \sum \frac{1}{k + r_i(d)}$ với $k = 60$.<br>• Thuật toán phân cụm đồ thị Louvain và hàm mục tiêu Modularity $Q$.<br>• Mã hóa xác thực Galois/Counter Mode (AES-256-GCM) với công thức vector khởi tạo $J_0$.<br>• Cơ chế phản hồi ReAct kết hợp máy ảo E2B MicroVM.<br>• Luận giải "Tại sao chọn" công nghệ (PostgreSQL pgvector thay vì Dedicated Vector DB, FastAPI, React 19). | • Định nghĩa cơ bản chung chung giáo trình về Docker, Python, REST API.<br>• Chi tiết mã nguồn nội bộ (`packages/core`, tên file `.py`, tên interface nội bộ).<br>• Hướng dẫn cài đặt thư viện (`pip install`, `npm install`). |
| **Chương 3: Phân tích và thiết kế hệ thống** | • Quy trình 5 bước kỹ nghệ chuẩn mực.<br>• Sơ đồ phân rã Use Case với tác nhân hình người UML (Stick Figure).<br>• Biểu đồ tuần tự phân tầng kiến trúc Lục giác.<br>• Lược đồ CSDL 20 bảng thực tế và sơ đồ quan hệ thực thể ERD chuẩn hóa.<br>• Thiết kế giải thuật phân đoạn 2 cột, lọc Jaccard, gating CRAG. | • 4 bảng CSDL ảo đã loại bỏ.<br>• Tên biến tạm, câu lệnh SQL thuần túy dài hàng trang.<br>• Script di chuyển cơ sở dữ liệu (migration scripts). |
| **Chương 4: Cài đặt và kết quả thực nghiệm** | • Số liệu đo lường định lượng thực tế khớp 100% với `report-datn/INFORMATION.md`: 580 tests, 13.02s, DB latency 1.66ms, TTFT < 1.5s, IoU $\ge 0{,}85$.<br>• Ảnh chụp giao diện sản phẩm thực tế có viền sắc nét, chú thích chuyên nghiệp.<br>• Bảng dữ liệu giám sát từ Langfuse Cloud (Trace ID, Tokens, Chi phí). | • Nhật ký lỗi tạm thời trong quá trình phát triển (debug logs).<br>• Khóa bí mật (`OPENAI_API_KEY`, `JWT_SECRET`).<br>• Toàn bộ mã nguồn hàng nghìn dòng (chỉ đưa đoạn thuật toán mẫu vào phụ lục). |
| **Kết luận và hướng phát triển** | • Tổng kết kết quả đã hoàn thành đối chiếu với 4 đóng góp ban đầu.<br>• Đánh giá khách quan các mặt hạn chế của đề tài (giới hạn 5 bài báo đồng thời, phụ thuộc kết nối E2B Sandbox).<br>• 3 hướng phát triển tiếp theo: Cộng tác thời gian thực CRDT/Yjs, mô hình đa phương thức cho đồ thị ảnh, cụm worker phân tán. | • Nhận định chủ quan không có số liệu chứng minh. |

---

## PHẦN 4: HỆ THỐNG 6 PERSONA CHUYÊN BIỆT CHO AI AGENT

Nhằm vận hành quy trình phát triển và hoàn thiện đồ án tốt nghiệp một cách chuyên nghiệp, đề xuất mô hình cộng tác gồm **6 Nhân diện Agent chuyên biệt** với ranh giới trách nhiệm rõ ràng:

```
                      ┌─────────────────────────────────────────┐
                      │        thesis-planner (Chỉ huy)         │
                      │        Quản lý Roadmap và Budget        │
                      └────────────────────┬────────────────────┘
                                           │ Phân công nhiệm vụ vi mô
         ┌─────────────────────────────────┼─────────────────────────────────┐
         ▼                                 ▼                                 ▼
┌──────────────────┐             ┌──────────────────┐             ┌──────────────────┐
│ thesis-researcher│             │ thesis-architect │             │  thesis-writer   │
│  (Nghiên cứu và  │             │ (Kiến trúc sư và │             │  (Biên soạn văn  │
│  cơ sở lý thuyết)│             │  đặc tả hệ thống)│             │   phong học thuật│
└────────┬─────────┘             └────────┬─────────┘             └────────┬─────────┘
         │ Bản nháp lý thuyết              │ Sơ đồ/Bảng BA                 │ Bản thảo .tex vi mô
         └─────────────────────────────────┼─────────────────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │       thesis-reviewer (Kiểm định)       │
                      │       Liêm chính và thẩm định học thuật │
                      └────────────────────┬────────────────────┘
                                           │ Đạt chuẩn nội dung
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │       thesis-formatter (Chế bản)        │
                      │       Định dạng và biên dịch XeLaTeX    │
                      └─────────────────────────────────────────┘
```

### 1. `thesis-planner` (Tác tử lập kế hoạch và điều phối bố cục)
- **Trách nhiệm chính:** Quản trị tệp chỉ mục `report-datn/ROADMAP.md`; giám sát ngân sách số trang (Page Budget) từng chương đảm bảo tổng quy mô 50 -- 65 trang chuẩn mực; theo dõi tiến độ theo Kế hoạch 10 tuần của HUMG; bảo đảm 3 câu hỏi cốt lõi ("Làm gì? Làm thế nào? Kết quả ra sao?") được phân bổ cân đối.
- **Hàng rào tuân thủ:** Không trực tiếp viết nội dung kỹ thuật; điều phối phân rã tác vụ theo từng mục vi mô; kiểm soát tiến độ chạm mốc Tuần 6 (Mid-term Checkpoint).

### 2. `thesis-researcher` (Tác tử nghiên cứu học thuật và cơ sở khoa học)
- **Trách nhiệm chính:** Phụ trách Chương 1 (Bối cảnh, tính cấp thiết, mục tiêu) và Chương 2 (Cơ sở lý thuyết và công nghệ); trích xuất các công thức toán học chính xác từ tài liệu gốc; chọn lọc danh mục tài liệu tham khảo tinh hoa ($N_{\text{refs}} \le 20$); soạn thảo lập luận "Tại sao chọn" cho từng công nghệ.
- **Hàng rào tuân thủ:** Tuyệt đối cấm đưa đường dẫn file code (`packages/`, `apps/`, `src/`) và tên interface nội bộ vào Chương 2; bảo đảm mọi tài liệu đều có `\bibitem` chuẩn và được dẫn chiếu ít nhất 1 lần trong thân bài.

### 3. `thesis-architect` (Tác tử kiến trúc sư và phân tích nghiệp vụ BA)
- **Trách nhiệm chính:** Phụ trách Chương 3 (Phân tích và thiết kế hệ thống); đọc hiểu mã nguồn thực tế để trích xuất thiết kế hệ thống; xây dựng bảng đặc tả các ca sử dụng chuẩn BA; thiết kế biểu đồ tuần tự UML; thiết kế CSDL 20 bảng quan hệ và vector theo `report-datn/INFORMATION.md`; phác thảo sơ đồ kiến trúc chuẩn paper quốc tế theo 7 Nguyên tắc vàng TikZ.
- **Hàng rào tuân thủ:** Bảo đảm tính tái lập 100% (schema phải khớp với CSDL thực tế; luồng tuần tự phải khớp với endpoints API; loại bỏ 4 bảng giả định).

### 4. `thesis-writer` (Tác tử biên soạn văn phong học thuật)
- **Trách nhiệm chính:** Hiện thực hóa các ý tưởng, công thức và sơ đồ thành các tệp `.tex` vi mô hoàn chỉnh; duy trì văn phong khoa học khách quan ngôi thứ ba; áp dụng danh ngữ hóa tiêu đề (3-7 từ) và cấu trúc đoạn văn Minto Pyramid; xử lý thoát toàn bộ ký tự đặc biệt trong XeLaTeX (`\_`, `\%`...).
- **Hàng rào tuân thủ:** Cấm xưng hô cảm tính (*"tôi"*, *"em"*, *"chúng tôi"*); cấm tiêu đề dạng kể lể (*"Nghiên cứu về..."*); cấm ngắt trang tùy tiện `\clearpage`.

### 5. `thesis-reviewer` (Tác tử kiểm định chất lượng và liêm chính học thuật)
- **Trách nhiệm chính:** Đóng vai trò Hội đồng phản biện độc lập; rà soát tính nhất quán giữa các chương; kiểm tra các Anti-Patterns (phát hiện rò rỉ mã nguồn ở Ch2, phát hiện bảng CSDL giả, phát hiện số liệu bịa đặt); đối chiếu số liệu ở Chương 4 với output thật trong `report-datn/INFORMATION.md`; chạy các bài kiểm thử tự động.
- **Hàng rào tuân thủ:** Từ chối thông qua bất kỳ bản thảo nào có trích dẫn mồ côi, vi phạm trần 20 tài liệu tham khảo hoặc số liệu không có căn cứ thực nghiệm.

### 6. `thesis-formatter` (Tác tử chế bản và kỹ nghệ định dạng XeLaTeX)
- **Trách nhiệm chính:** Chịu trách nhiệm về hình thức thẩm mỹ trang in và sự toàn vẹn của mã XeLaTeX; kiểm soát căn lề 2.5-2.5-3.5-2.5cm, phông chữ Times New Roman 13pt, dãn dòng 1.5; kiểm soát tỷ lệ scale của TikZ không quá 15cm; định dạng bảng `tabularx` khép kín viền ngoài; triệt tiêu trang trắng mồ côi và tiêu đề mồ côi; biên dịch XeLaTeX 2 lần để cập nhật số trang và mục lục không lỗi.
- **Hàng rào tuân thủ:** Bắt buộc `main.log` không có cảnh báo undefined references và `main.pdf` được sinh ra hoàn chỉnh.

---

## PHẦN 5: GIAO THỨC TƯƠNG TÁC TỆP AN TOÀN VÀ QUY TRÌNH PHỐI HỢP

### 5.1. Quy trình 6 bước thao tác tệp XeLaTeX an toàn
Để loại bỏ nguy cơ xung đột mã nguồn, vỡ định dạng và lãng phí token ngân sách, bất kỳ AI Agent nào khi thực hiện nhiệm vụ đều phải tuân thủ nghiêm ngặt quy trình 6 bước:

```
BƯỚC 1: Đọc ROADMAP.md và xác định tệp vi mô mục tiêu
   │
   ▼
BƯỚC 2: Nạp ngữ cảnh tối thiểu (Chỉ đọc tệp vi mô + tài liệu tham chiếu cần thiết)
   │
   ▼
BƯỚC 3: Biên soạn / Hiệu chỉnh (Tuân thủ thoát ký tự nhạy cảm và bất biến nhãn)
   │
   ▼
BƯỚC 4: Biên dịch thử nghiệm XeLaTeX 2 lần (cd report-datn && xelatex main.tex)
   │
   ▼
BƯỚC 5: Chạy bộ kiểm tra tự động (test_thesis_rules.py và test_tables_and_spacing.py)
   │
   ▼
BƯỚC 6: Cập nhật trạng thái ROADMAP.md và lập báo cáo bàn giao (Handoff Report)
```

1. **Bước 1 — Định vị tệp vi mô:** Đọc `report-datn/ROADMAP.md` để xác định chính xác tệp `.tex` cần thao tác.
2. **Bước 2 — Nạp ngữ cảnh tối thiểu:** Chỉ mở tệp vi mô mục tiêu và các tệp spec tham chiếu trực tiếp. Tuyệt đối không đọc toàn bộ báo cáo vào prompt.
3. **Bước 3 — Biên soạn phòng thủ:** Thực hiện sửa đổi bằng các công cụ chỉnh sửa chính xác (`replace_file_content`). Luôn kiểm tra thoát dấu gạch dưới `\_` trong tên biến/trường CSDL; bảo toàn nguyên vẹn các `\label{...}` quan trọng.
4. **Bước 4 — Biên dịch kiểm tra:** Chạy lệnh biên dịch XeLaTeX 2-pass để bảo đảm không có lỗi cú pháp, không đứt đoạn tham chiếu và cập nhật chuẩn mục lục:
   ```bash
   cd report-datn && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex && cd ..
   ```
5. **Bước 5 — Kiểm tra bài test:** Chạy bộ kiểm thử tự động để xác nhận không vi phạm quy tắc:
   ```bash
   uv run pytest tests/test_thesis_rules.py
   uv run pytest report-datn/scripts/test_tables_and_spacing.py
   ```
6. **Bước 6 — Cập nhật bản đồ tiến độ:** Đánh dấu trạng thái hoàn thành trong `ROADMAP.md` và viết báo cáo bàn giao `handoff.md` theo thể thức 5 thành phần chuẩn mực.

---

### 5.2. Phân quyền và quy tắc thao tác từng nhóm tệp
1. **Nhóm tệp điều phối (`main.tex`, `chapters/chX_*.tex`):**
   - *Quyền hạn:* CHỈ ĐỌC (Read-only).
   - Chỉ được chỉnh sửa khi có chỉ định bổ sung/loại bỏ một mục cấp 2 (`\input{...}`). Tuyệt đối cấm viết trực tiếp đoạn văn nội dung vào các tệp điều phối này.
2. **Nhóm tệp cấu hình (`config/preamble.tex`, `config/commands.tex`):**
   - *Quyền hạn:* ĐÓNG BĂNG (Frozen).
   - Không được tự ý thay đổi lề trang, cỡ chữ, phông chữ hoặc nạp thêm các gói lệnh bên ngoài có nguy cơ xung đột (như `booktabs`).
3. **Nhóm tệp vi mô nội dung (`chapters/chX/X_Y_*.tex`):**
   - *Quyền hạn:* ĐỌC VÀ GHI (Read/Write) có kiểm soát.
   - Luôn duy trì dòng đầu tiên chỉ định tệp gốc: `% !TEX root = ../../main.tex`.
   - Sử dụng tiền tố nhãn chuẩn hóa: `sec:`, `subsec:`, `fig:`, `tab:`, `eq:`.
4. **Nhóm tệp tài liệu tham khảo và biểu mẫu (`tai_lieu_tham_khao.tex`, `frontmatter/*.tex`):**
   - Tuân thủ nghiêm ngặt trần $N_{\text{refs}} \le 20$; bảo đảm thông tin hành chính đồng bộ 100% với `report-datn/INFORMATION.md`.

---

## PHẦN 6: BẢNG TRA CỨU 11 ĐIỀU RĂN VÀ BÀI HỌC KINH NGHIỆM ĐÃ KHẮC PHỤC (MISTAKES CATALOG VÀ ĐỐI CHIẾU HIEU.PDF)

Nhằm phòng ngừa triệt để các sai sót định dạng và nội dung, toàn bộ các AI Agent tham gia dự án bắt buộc phải ghi nhớ sâu sắc **11 Điều răn và Bài học kinh nghiệm đã khắc phục** theo chuẩn mực `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn/guide/HIeu.pdf`:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│         BẢNG TRA CỨU 11 ĐIỀU RĂN VÀ BÀI HỌC KINH NGHIỆM ĐÃ KHẮC PHỤC (HIEU.PDF)        │
├────┬──────────────────────────────────────┬────────────────────────────────────────────┤
│ STT│ Sai Lầm Phổ Biến Ban Đầu             │ Biện Pháp Khắc Phục Chuẩn Mực Tuyệt Đối    │
├────┼──────────────────────────────────────┼────────────────────────────────────────────┤
│ 1  │ Sử dụng ảnh .jpg, .jpeg và kích thước│ Chuyển đổi 100% ảnh sang .png tại figures/;│
│    │ không tối ưu khổ in A4 (< 8cm).      │ kích thước to rõ width=0.85-0.95\textwidth │
│    │                                      │ (chuẩn 0.92\textwidth); cấm co nhỏ < 8cm. │
├────┼──────────────────────────────────────┼────────────────────────────────────────────┤
│ 2  │ Tồn tại mục "TRƯỞNG BỘ MÔN" trang iv │ Xóa bỏ hoàn toàn cột "Trưởng Bộ môn" trong │
│    │ trong Phiếu giao đề tài tốt nghiệp.  │ phieu_giao_de_tai.tex; chỉ giữ 2 bên ký    │
│    │                                      │ là Giảng viên hướng dẫn và Sinh viên thực  │
│    │                                      │ hiện khớp 100% trang 4 của Hieu.pdf.       │
├────┼──────────────────────────────────────┼────────────────────────────────────────────┤
│ 3  │ Viết hoa toàn bộ chức danh ký tên    │ Chuyển toàn bộ chức danh ký và đề mục sang │
│    │ ("GIẢNG VIÊN HƯỚNG DẪN") và để trống │ viết thường Title Case ("Giảng viên hướng  │
│    │ ngày tháng năm "ngày... tháng...".   │ dẫn", "Sinh viên thực hiện"); cố định ngày │
│    │                                      │ chính thức: 06/11/2026 trên toàn biểu mẫu. │
├────┼──────────────────────────────────────┼────────────────────────────────────────────┤
│ 4  │ Nén dãn dòng \setstretch{1.241} hoặc │ Thiết lập đồng bộ \setstretch{1.45} tại cả │
│    │ dùng \onehalfspacing mặc định.       │ preamble.tex và main.tex, đạt khoảng cách  │
│    │                                      │ dòng Word 1.5 chuẩn Hieu.pdf (22.5-23.2pt).│
├────┼──────────────────────────────────────┼────────────────────────────────────────────┤
│ 5  │ Lạm dụng \small (11pt) và            │ Bóc bỏ toàn bộ \small và \footnotesize     │
│    │ \footnotesize (10pt) trong bảng biểu.│ trong tất cả các bảng biểu của đề tài.     │
│    │                                      │ Toàn bộ nội dung chữ trong bảng đạt chuẩn  │
│    │                                      │ cỡ chữ 13pt Times New Roman đồng nhất.     │
├────┼──────────────────────────────────────┼────────────────────────────────────────────┤
│ 6  │ Tiêu đề Chương trong Mục lục bị in   │ Đổi cấu hình tocloft: \renewcommand        │
│    │ đậm (\cftchapfont{\bfseries}).       │ {\cftchapfont}{\normalfont}; bổ sung dấu   │
│    │                                      │ hai chấm (\cftchapaftersnum}{:\ }) và chấm │
│    │                                      │ dẫn thanh thoát theo đúng trang 9 Hieu.pdf.│
├────┼──────────────────────────────────────┼────────────────────────────────────────────┤
│ 7  │ Trang bìa chính (Bìa 1) thiếu dải    │ Thiết kế dải sườn/gáy dọc mép lề trái theo │
│    │ sườn/gáy dọc lề trái đóng sách.      │ đúng trang 1 Hieu.pdf bằng TikZ overlay:   │
│    │                                      │ ĐÀM MẠNH DŨNG, HỆ THỐNG THÔNG TIN, KHOÁ 67 │
│    │                                      │ font thường; bỏ tiền tố thừa "TÊN ĐỀ TÀI:".│
├────┼──────────────────────────────────────┼────────────────────────────────────────────┤
│ 8  │ Đánh số trang Ả Rập bắt đầu từ       │ Trang 1–8 để trống chân trang (clean foot);│
│    │ Chương 1 hoặc in số ở trang bìa.     │ Căn cứ trang 9 Hieu.pdf, số trang Ả Rập (1)│
│    │                                      │ BẮT ĐẦU CHÍNH XÁC TỪ TRANG MỤC LỤC. Mục    │
│    │                                      │ lục hiển thị số La Mã iii, v, viii.        │
├────┼──────────────────────────────────────┼────────────────────────────────────────────┤
│ 9  │ Rải trích dẫn dày đặc và lạm dụng chữ│ Tinh giản trích dẫn, chỉ trích dẫn trọng   │
│    │ in đậm, in nghiêng trong thân bài.   │ tâm tại Ch1, Ch2 (N_refs <= 20); bóc bỏ    │
│    │                                      │ toàn bộ \textbf, \textit trong thân bài;   │
│    │                                      │ CHỈ DUY NHẤT cấp 3 (\subsubsection) nghiêng│
├────┼──────────────────────────────────────┼────────────────────────────────────────────┤
│ 10 │ Bìa trong (Bìa 2) và thể thức chung  │ Đối chiếu khớp 100% trang 2 của Hieu.pdf   │
│    │ bị xô lệch lề và khoảng cách dọc.    │ về khoảng cách dọc, tỷ lệ chữ, khối ký; lề │
│    │                                      │ chuẩn A4: 2.5 - 2.5 - 3.5 - 2.5 cm.        │
├────┼──────────────────────────────────────┼────────────────────────────────────────────┤
│ 11 │ Tư duy "tiết kiệm giấy" làm sai quy  │ Tuyệt đối cấm co chữ, nén dòng, bóp méo    │
│    │ cách, nén chữ, ép trang tùy tiện.    │ hình ảnh để ép trang; tuân thủ nghiêm ngặt │
│    │                                      │ cấu trúc ấn phẩm học thuật chuẩn mực HUMG. │
└────┴──────────────────────────────────────┴────────────────────────────────────────────┘
```

---

## PHẦN 7: BẢNG KIỂM TỰ ĐÁNH GIÁ TRƯỚC KHI BÀN GIAO (PRE-COMMIT CHECKLIST)

Trước khi xác nhận hoàn thành bất kỳ tác vụ nào trong `report-datn/`, AI Agent bắt buộc phải tự đối chiếu và xác nhận đạt **100% các tiêu chí** trong Bảng kiểm tự đánh giá Pre-Commit Checklist (gồm **30 tiêu chí toàn diện**, trong đó 11 Điều Răn từ hồ sơ HIeu.pdf là Cổng kiểm soát số 0 bắt buộc):

```markdown
### CHECKLIST TỰ KIỂM ĐỊNH CHẤT LƯỢNG ĐATN CỦA AI AGENT (PRE-COMMIT CHECKLIST)

#### KHỐI I: 11 ĐIỀU RĂN BẤT DI BẤT DỊCH TỪ HỒ SƠ HIEU.PDF (BẮT BUỘC ĐẠT 100% — ZERO TOLERANCE)
- [ ] 1. [ĐIỀU RĂN 1] 100% HÌNH ẢNH ĐỊNH DẠNG PNG TẠI FIGURES/: Toàn bộ hình ảnh trong báo cáo phải là file .png, lưu tại ./report-datn/figures/, kích thước vừa vặn khổ A4 (width=0.85\textwidth đến 0.95\textwidth, khuyến nghị 0.92\textwidth), hiển thị sắc nét khi in/photo, cấm co nhỏ dưới 8cm hoặc < 0.7\textwidth.
- [ ] 2. [ĐIỀU RĂN 2] CẤM CHỨC DANH "TRƯỞNG BỘ MÔN" TRANG IV: Trang 2 của Phiếu giao đề tài (trang iv) chỉ gồm 2 bên ký duyệt là "Giảng viên hướng dẫn" và "Sinh viên thực hiện"; tuyệt đối không có cột hoặc chức danh Trưởng Bộ môn / Trưởng Khoa (khớp 100% trang 4 HIeu.pdf).
- [ ] 3. [ĐIỀU RĂN 3] CỐ ĐỊNH NGÀY 06/11/2026 VÀ CHỨC DANH TITLE CASE: Toàn bộ biểu mẫu hành chính cố định "Hà Nội, ngày 06 tháng 11 năm 2026" (06/11/2026), cấm để trống chấm lửng; chức danh ký tên viết thường Title Case ("Giảng viên hướng dẫn", "Sinh viên thực hiện"), cấm viết hoa toàn bộ.
- [ ] 4. [ĐIỀU RĂN 4] DÃN DÒNG CHUẨN 1.5 WORD (\setstretch{1.45}): Thiết lập \setstretch{1.45} đồng bộ tại cả preamble.tex và main.tex:83, đạt khoảng cách dòng cơ sở chuẩn Word 1.5 (22.54pt - 23.22pt); TUYỆT ĐỐI CẤM dãn dòng nén \setstretch{1.241} hoặc \onehalfspacing mặc định (19.43pt).
- [ ] 5. [ĐIỀU RĂN 5] CỠ CHỮ TOÀN BÀI VÀ TRONG BẢNG ĐẠT 13PT: Toàn bộ nội dung thân bài và 100% chữ trong tất cả các bảng biểu (tabular, tabularx, longtable) đạt chuẩn cỡ chữ 13pt Times New Roman; TUYỆT ĐỐI CẤM lạm dụng \small, \footnotesize, \fontsize{8.5pt}, \fontsize{9pt} để ép bảng.
- [ ] 6. [ĐIỀU RĂN 6] MỤC LỤC KHÔNG IN ĐẬM BẤT KỲ DÒNG MỤC NÀO: Toàn bộ dòng mục trong Mục lục sử dụng \normalfont không in đậm (\bfseries), có dấu hai chấm sau số chương (\cftchapaftersnum{:\ }), số trang in đứng thường và chấm dẫn thanh thoát (khớp 100% trang 9 HIeu.pdf).
- [ ] 7. [ĐIỀU RĂN 7] BÌA NGOÀI CÓ SƯỜN DỌC XOAY 90° FONT THƯỜNG: Trang bìa ngoài có dải sườn/gáy mép lề trái theo TikZ overlay xoay 90° gồm 3 khối chữ font đứng thường in hoa: ĐÀM MẠNH DŨNG, HỆ THỐNG THÔNG TIN, KHOÁ 67; loại bỏ tiền tố thừa "TÊN ĐỀ TÀI:".
- [ ] 8. [ĐIỀU RĂN 8] SỐ TRANG Ả RẬP 1 TỪ MỤC LỤC, TRANG 1–8 CHÂN TRANG TRỐNG: Các trang vật lý 1–8 (Bìa 1, Bìa 2, Phiếu giao đề tài, Đề cương, Lời cảm ơn) chân trang hoàn toàn để trống; Mục lục bắt đầu in số Ả Rập 1 ở chân trang; Mục lục hiển thị số La Mã logic iii, v, viii cho các hồ sơ đầu khóa và có dòng tự tham chiếu MỤC LỤC ..... 1.
- [ ] 9. [ĐIỀU RĂN 9] BỎ IN ĐẬM/IN NGHIÊNG TÙY TIỆN VÀ TINH GIẢN TRÍCH DẪN: Bóc sạch toàn bộ \textbf, \textit tùy tiện trong các đoạn văn xuôi thân bài; CHỈ DUY NHẤT tiêu đề tiểu mục cấp 3 (\subsubsection) mới được in nghiêng; tinh giản trích dẫn dày đặc, chỉ trích dẫn trọng tâm tại Ch1, Ch2 và khống chế trần N_refs <= 20.
- [ ] 10. [ĐIỀU RĂN 10] BÌA PHỤ VÀ THỂ THỨC KHỚP 100% HIEU.PDF: Toàn bộ trang bìa trong (bìa phụ) khớp 100% trang 2 của HIeu.pdf về khoảng cách dọc, tỷ lệ chữ, khối ký tên; thể thức toàn văn chuẩn A4 lề 2.5 - 2.5 - 3.5 - 2.5 cm.
- [ ] 11. [ĐIỀU RĂN 11] TUYỆT ĐỐI KHÔNG TIẾT KIỆM GIẤY LÀM SAI QUY CÁCH: Tuyệt đối cấm mọi thủ thuật ép trang, nén dãn dòng dưới 1.45, co nhỏ cỡ chữ, bóp méo hình ảnh hay dồn biểu mẫu hành chính làm hỏng bố cục chuẩn của ấn phẩm học thuật.

#### KHỐI II: QUY CHUẨN KỸ NGHỆ, KIẾN TRÚC VÀ HỌC THUẬT NỘI DUNG
- [ ] 12. Mục tiêu và 3 Câu hỏi cốt lõi: Làm rõ Làm gì? (Ch1), Làm như thế nào? (Ch2 và Ch3), Kết quả ra sao? (Ch4).
- [ ] 13. Quy trình 5 bước kỹ nghệ: Chương 3 trình bày đầy đủ Phân tích -> Thiết kế -> Cài đặt -> Kiểm thử -> Hiệu chỉnh.
- [ ] 14. Kế hoạch 10 tuần: Phân bổ hợp lý từ tuần 1 đến tuần 10; nhấn mạnh cột mốc Tuần 6 (Mid-term Checkpoint) báo cáo Bộ môn.
- [ ] 15. Kỷ luật và Nộp lưu trữ: Nêu rõ nghĩa vụ gặp GVHD hàng tuần, 4 điều kiện đình chỉ, 3 quyển bìa mềm trước bảo vệ, 1 bìa cứng mạ chữ nhũ vàng nộp trong vòng 10 ngày sau bảo vệ, thư mục bản mềm `MãSinhViên_HọTên_Khóa`.
- [ ] 16. Phân cấp đề mục: Tối đa 4 cấp (X.Y.Z.W); CẤM TIỂU MỤC ĐƠN LẺ (mỗi nhóm >= 2 mục con); tiêu đề danh ngữ hóa 3-7 từ; không có tiêu đề mồ côi.
- [ ] 17. Bảng biểu và Hình vẽ: Tiêu đề Bảng ở TRÊN; Tiêu đề Hình ở DƯỚI; đánh số theo chương dạng gạch nối Chương-Số (`Bảng X-Y`, `Hình X-Y`); TUYỆT ĐỐI CẤM tham chiếu tương đối ("hình dưới đây", "bảng sau").
- [ ] 18. Bảng tabularx và TikZ: Bảng có viền khép kín `|...|` và `\hline`, cột `X` ngắt dòng; triệt tiêu 100% Overfull \hbox; sơ đồ TikZ tuân thủ 7 Nguyên tắc vàng, chiều ngang <= 15.0cm.
- [ ] 19. Tài liệu tham khảo: Tiếng Việt trước, tiếng Anh sau; xếp ABC chuẩn; hanging indent 1.0cm; giới hạn <= 20 tài liệu; 100% tài liệu được trích dẫn (không mồ côi); tinh giản trích dẫn dày đặc.
- [ ] 20. Tỷ lệ nội dung vàng: Lý thuyết (Ch1 + Ch2) <= 30%; Thiết kế và Thực nghiệm (Ch3 + Ch4) >= 70%; tổng dung lượng ruột đạt 50 -- 65 trang; Phụ lục không dày hơn phần chính.

#### KHỐI III: QUY TẮC PHÒNG NGỪA ANTI-PATTERNS VÀ CHUẨN HÓA BẢN VẼ UML
- [ ] 21. Triệt tiêu 7 Anti-Patterns: Không chép giáo trình (AP-01), cô lập Chương 2 không lộ code (AP-02), không dán code thô > 20 dòng (AP-03), số liệu thực nghiệm trung thực (AP-04), trần 20 ref (AP-05), CSDL 20 bảng thực tế (AP-06), sơ đồ/bảng không đâm thủng lề (AP-07).
- [ ] 22. [GÓP Ý GVHD] CẤM TỰ Ý ĐÁNH SỐ THỨ TỰ: Tuyệt đối không đánh số thứ tự dạng (1), (2), (3)... hoặc 1., 2., 3. trong đoạn văn liệt kê. Chỉ dùng gạch đầu dòng itemize hoặc viết đoạn văn liên tục.
- [ ] 23. [GÓP Ý GVHD] CẤM TÙY TIỆN IN ĐẬM: Tuyệt đối không tự ý in đậm (\textbf) các cụm từ liệt kê hoặc phân đoạn trong thân bài; chỉ in đậm tiêu đề mục, tiêu đề bảng/hình và tên cột.
- [ ] 24. [GÓP Ý GVHD] BIỂU TƯỢNG ACTOR NGƯỜI QUE: Mọi biểu đồ Use Case phải sử dụng Actor hình người que chuẩn UML (stick figure), TUYỆT ĐỐI CẤM vẽ Actor hình hộp chữ nhật.
- [ ] 25. [GÓP Ý GVHD] SƠ ĐỒ USE CASE CON: Tất cả các Use Case con trong Chương 3 đều phải vẽ hình sơ đồ phân rã đặt trước bảng đặc tả tương ứng.
- [ ] 26. [GÓP Ý GVHD] BIỂU ĐỒ LỚP (CLASS DIAGRAM): Biểu đồ lớp mô hình hóa thực thể bắt buộc phải có và đặt ở vị trí ngay trước các bảng dữ liệu CSDL tại Mục 3.6.
- [ ] 27. [GÓP Ý GVHD] CẤM DẤU `&` VÀ TITLE CASE: Tuyệt đối cấm dùng ký tự `&` trong tiêu đề và nội dung tiếng Việt (phải viết chữ "và"); không tùy tiện viết hoa chữ cái đầu từng từ (Title Case); lấp đầy trang in, không để khoảng trống lớn ở cuối trang.

#### KHỐI IV: CỔNG XÁC MINH TỰ ĐỘNG (AUTOMATED TEST GATES)
- [ ] 28. [AUTOMATED GATE] TEST SUITE HIEU.PDF PASSED: Chạy `uv run pytest tests/report_datn/test_thesis_format_hieu.py` đạt 100% PASS (9/9 tests).
- [ ] 29. [AUTOMATED GATE] TEST SUITE STRUCTURE PASSED: Chạy `uv run pytest tests/report_datn/test_thesis_structure.py scripts/test_preamble_config.py scripts/verify_thesis_format.py` đạt 100% PASS (11/11 tests).
- [ ] 30. [AUTOMATED GATE] XELATEX CLEAN BUILD: Biên dịch `xelatex -interaction=nonstopmode main.tex` thành công 100%, không phát sinh lỗi biên dịch, không tràn lề nghiêm trọng.
```

---

> **LỜI KẾT DÀNH CHO CÁC TÁC TỬ:**  
> Mọi dòng văn bản, bảng biểu và công thức xuất bản trong quyển Đồ án Tốt nghiệp này là minh chứng danh dự cho trí tuệ, năng lực kỹ nghệ và sự lao động nghiêm cẩn của tác giả và nhóm tác tử hỗ trợ. Hãy luôn giữ vững chuẩn mực học thuật cao nhất trong từng thao tác!

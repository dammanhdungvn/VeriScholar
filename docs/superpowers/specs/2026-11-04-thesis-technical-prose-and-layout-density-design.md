# Design Document: Chuẩn hóa Văn phong Kỹ thuật, Tối ưu Bố cục Mật độ và Tinh gọn Tài liệu tham khảo theo Chuẩn HIeu.pdf

**Ngày lập:** 2026-11-04  
**Trạng thái:** Chờ phê duyệt  
**Mã dự án:** VeriScholar Thesis Refinement  

---

## 1. Intent and The Why

Báo cáo tốt nghiệp ĐATN của sinh viên Đàm Mạnh Dũng cần đạt chuẩn mực hình thức tối cao, bám sát 100% hồ sơ mẫu chuẩn mực `guide/HIeu.pdf` (của sinh viên Phạm Quốc Bảo). Qua rà soát chi tiết, báo cáo hiện tại tồn tại 4 vấn đề kỹ thuật cần khắc phục:
1. Trong nội dung các chương vẫn còn xuất hiện các ký hiệu tham chiếu số `[1]`, `[14]`, v.v. (tạo ra từ lệnh `\cite{...}`) cùng việc nhắc tên tác giả theo văn phong kể lể (ví dụ: *"do Lewis và cộng sự giới thiệu"*). Trong khi đó, ở `HIeu.pdf`, toàn bộ 100 trang thân bài hoàn toàn không có bất kỳ ký hiệu tham chiếu số `[N]` nào.
2. Trang 54 bị hổng một khoảng trắng lớn (~60% trang) do các lệnh ngắt trang cưỡng bức `\clearpage` cô lập tiểu mục 3.4.5 trước khi sang Mục 3.5.
3. Phần Tài liệu tham khảo (`chapters/tai_lieu_tham_khao.tex`) đang bị phân mảnh bởi các tiêu đề nhóm La Mã *"I. Tài liệu tiếng Việt"* (chứa tài liệu Quy chế HUMG 2022 không phù hợp) và *"II. Tài liệu tiếng Anh"*.
4. Danh mục tài liệu tham khảo cần được tinh gọn, chỉ giữ lại đúng $\le 10$ bài báo khoa học quốc tế kinh điển nhất, trực tiếp định hình thuật toán cốt lõi của đề tài (RAG, CRAG, GraphRAG, ReAct, HNSW, v.v.).

Mục đích của thiết kế này là loại bỏ toàn diện các khuyết điểm trên, mang lại văn phong kỹ thuật khách quan, bố cục trang nối tiếp khít khao tự nhiên (giữ nguyên giãn dòng 1.5 Word) và danh mục tài liệu tham khảo cô đọng, sắc bén.

---

## 2. Goals, Non-Goals & Anti-Goals

### 2.1 Goals
- **G1 (Loại bỏ triệt để `\cite` và tên tác giả):** Xóa 100% các lệnh `\cite{...}` trong các chương; biên tập lại câu văn sang thể bị động hoặc khẳng định kỹ thuật thuần túy, không nhắc tên cá nhân/tác giả nghiên cứu.
- **G2 (Khử khoảng trắng thừa, trang liền mạch):** Xóa các lệnh `\clearpage` cô lập tại tiểu mục 3.4.5 (`chapters/ch3/3_4_phan_tich_usecase.tex`), giúp Mục 3.5 tiếp nối ngay trên trang 54; rà soát toàn bộ văn bản để không trang nào bị khoảng trống bất thường trước khi kết thúc mục.
- **G3 (Làm sạch phân mục tài liệu):** Xóa bỏ hoàn toàn mục *"I. Tài liệu tiếng Việt"* (và trích dẫn Quy chế HUMG 2022) cùng tiêu đề *"II. Tài liệu tiếng Anh"*.
- **G4 (Tinh gọn đúng 10 bài báo kinh điển):** Giữ lại danh mục phẳng gồm đúng 10 công trình khoa học quốc tế uy tín nhất phục vụ nền tảng VeriScholar.
- **G5 (Cập nhật quy tắc bất biến vào AGENTS.md):** Bổ sung các nguyên tắc cấm tham chiếu số trong thân bài, cấm `\clearpage` giữa các tiểu mục, và chuẩn danh mục tài liệu vào `AGENTS.md`.
- **G6 (Vượt qua 100% các cổng kiểm thử):** Tất cả 4 Cổng Kiểm soát Chất lượng (`scripts/dev/verify.sh`) và các bài kiểm tra định dạng phải đạt kết quả Exit Code 0.

### 2.2 Non-Goals
- Không thay đổi giãn dòng chuẩn 1.5 Word (`\setstretch{1.45}`) hoặc thay đổi cỡ chữ 13pt Times New Roman.
- Không thay đổi nội dung kỹ thuật, kiến trúc hệ thống, mã nguồn hoặc kết quả số liệu thực nghiệm đã kiểm chứng.

### 2.3 Anti-Goals
- Tuyệt đối không xóa cơ học lệnh `\cite` để lại các câu văn què quặt (ví dụ: *"do và cộng sự đề xuất"*).
- Không tự ý nén khoảng cách dòng (`\singlespacing` hay nén hệ số) để ép trang.

---

## 3. Constraints
- Tuân thủ cấu trúc phân tầng và quy chuẩn định dạng tối cao từ `guide/HIeu.pdf`.
- Duy trì 0 lỗi Overfull `\hbox` trong quá trình biên dịch XeLaTeX.
- Mọi thay đổi đều được kiểm thử tự động bằng bộ test Pytest trong `tests/`.

---

## 4. Approaches

### Phương án 1: Tinh chỉnh cục bộ & Biên tập trực tiếp (Được người dùng lựa chọn)
- Biên tập lại toàn bộ câu văn chứa trích dẫn thành câu khẳng định kỹ thuật khách quan, không chứa tên tác giả hay ký hiệu số `[N]`.
- Gỡ bỏ `\clearpage` cưỡng bức, để nội dung tự nhiên tràn vào trang 54.
- Tinh giản danh mục tham khảo thành danh sách 10 bài báo kinh điển phẳng, không tiêu đề phân nhóm La Mã.
- *Lý do chọn:* Đáp ứng trọn vẹn yêu cầu người dùng, khớp 100% với phong cách viết của `HIeu.pdf`.

### Phương án 2: Xóa cơ học lệnh `\cite` bằng biểu thức chính quy và giữ nguyên tên tác giả
- Giữ nguyên *"do Lewis và cộng sự giới thiệu"* nhưng chỉ xóa mã `\cite{...}`.
- *Đánh giá:* Bị loại vì tạo cảm giác văn phong dở dang, thiếu chuyên nghiệp khi nhắc tác giả nhưng không có trích dẫn học thuật tương ứng.

---

## 5. Detailed Implementation Decisions

### 5.1 Biên tập văn phong thuần kỹ thuật trong các chương
Các đoạn văn chứa `\cite{...}` trong `chapters/ch2/` và `chapters/ch2_co_so_ly_thuyet.tex` được tái cấu trúc như sau:
1. **Lewis (RAG):**
   - *Trước:* *"Để giải quyết các thách thức trên, kỹ thuật Tạo sinh tăng cường truy xuất (Retrieval-Augmented Generation -- RAG) do Lewis và cộng sự giới thiệu \cite{lewis2020} đã kết hợp..."*
   - *Sau:* *"Để giải quyết các thách thức trên, kỹ thuật Tạo sinh tăng cường truy xuất (Retrieval-Augmented Generation -- RAG) kết hợp năng lực suy luận ngôn ngữ của mô hình ngôn ngữ lớn (LLM) với kho tri thức học thuật bên ngoài..."*
2. **Gao (Advanced RAG):**
   - *Trước:* *"Khắc phục điểm nghẽn của Naive RAG, kiến trúc RAG Nâng cao (Advanced RAG) theo khảo sát của Gao và cộng sự \cite{gao2023rag} tái cấu trúc..."*
   - *Sau:* *"Khắc phục điểm nghẽn của Naive RAG, kiến trúc RAG Nâng cao (Advanced RAG) tái cấu trúc toàn diện quy trình xử lý thành ba giai đoạn tinh chỉnh chuyên sâu..."*
3. **Asai (Self-RAG):**
   - *Trước:* *"Nhằm khắc phục hiện tượng truy xuất bừa bãi ngay cả khi không cần thiết, đề tài tham chiếu khung kiến trúc Self-RAG (Self-Reflective Retrieval-Augmented Generation) do Asai và cộng sự đề xuất \cite{asai2023selfrag}..."*
   - *Sau:* *"Nhằm khắc phục hiện tượng truy xuất bừa bãi ngay cả khi không cần thiết, đề tài ứng dụng khung kiến trúc Self-RAG (Self-Reflective Retrieval-Augmented Generation) tích hợp các tiêu chí phản xạ đặc biệt (Reflection Tokens) vào chu trình xử lý..."*
4. **Yan (CRAG):**
   - *Trước:* *"...đề tài ứng dụng cơ chế RAG Hiệu chỉnh (Corrective RAG -- CRAG) do Yan và cộng sự phát triển \cite{yan2024crag}."*
   - *Sau:* *"...đề tài ứng dụng cơ chế RAG Hiệu chỉnh (Corrective RAG -- CRAG) tự động đánh giá độ tin cậy của tài liệu truy xuất trước khi sinh câu trả lời."*
5. **HNSW (Malkov & Yashunin):**
   - *Trước:* *"...thuật toán chỉ mục HNSW (Hierarchical Navigable Small World) \cite{malkov2018}:"*
   - *Sau:* *"...thuật toán chỉ mục HNSW (Hierarchical Navigable Small World):"*
6. **ReAct & Reflexion (Yao & Shinn):**
   - *Trước:* *"Để khắc phục nhược điểm trên, đề tài áp dụng mô hình kiến trúc ReAct do Yao và cộng sự đề xuất \cite{yao2022}, kết hợp cơ chế tự suy ngẫm Reflexion của Shinn và cộng sự \cite{shinn2023} và nguyên lý thiết kế tác nhân tự chủ của Weng \cite{weng2023agent}..."*
   - *Sau:* *"Để khắc phục nhược điểm trên, đề tài áp dụng mô hình kiến trúc tác nhân ReAct kết hợp cơ chế tự suy ngẫm Reflexion và nguyên lý thiết kế tác nhân tự chủ..."*
7. **GraphRAG & Louvain/Leiden (Edge & Blondel):**
   - *Trước:* *"...mô hình GraphRAG \cite{edge2024}, hệ thống áp dụng thuật toán phát hiện cộng đồng Louvain (Louvain Community Detection Algorithm) \cite{blondel2008louvain} (kèm mở rộng thuật toán Leiden \cite{traag2019leiden})."*
   - *Sau:* *"...mô hình GraphRAG, hệ thống áp dụng thuật toán phát hiện cộng đồng Louvain (kèm mở rộng thuật toán Leiden) nhằm phân hoạch đồ thị thực thể thành các cụm cộng đồng có mật độ liên kết nội bộ dày đặc..."*
8. **RRF & BM25 (Cormack & Robertson):**
   - Chuyển thành câu văn mô tả trực tiếp công thức và thuật toán chuẩn hóa xếp hạng.
9. **FastAPI & Kiến trúc Lục giác & E2B Firecracker & AES-GCM:**
   - Diễn đạt thuần túy về mặt thiết kế kỹ thuật phần mềm và chuẩn an toàn thông tin NIST.

### 5.2 Khử khoảng trắng trống lớn tại Trang 54 và Bố cục liên tục
- File: `chapters/ch3/3_4_phan_tich_usecase.tex`.
- Hành động: Xóa bỏ dòng `\clearpage` tại dòng 443 và dòng 455.
- Kết quả mong đợi: Tiểu mục 3.4.5 (Cơ chế bảo mật và vận hành hệ thống phía Quản trị viên) và Mục 3.5 (Phân tích một số biểu đồ tuần tự chính của hệ thống) nối tiếp nhau tự nhiên trên cùng trang 54, không để lại khoảng trống nửa trang.
- Bố cục các biểu đồ tuần tự: Hình 3-8 xuất hiện trên trang 54, các biểu đồ tiếp theo (Hình 3-9, 3-10, 3-11) phân bố dàn trang tự nhiên trên các trang 55 và 56.
- Cập nhật test: Trong `tests/report_datn/test_layout_spacing.py`, hàm `test_sequence_diagrams_no_newpage_and_flow` được cập nhật loại bỏ điều kiện cố định cũ `p_fig_3_8 == p_fig_3_9` (vốn sinh ra từ thời điểm cưỡng bức ngắt trang), duy trì kiểm tra cấm `\newpage` cưỡng bức và đảm bảo dòng chảy tự nhiên.
- Rà soát toàn bộ các file trong `chapters/` để đảm bảo không còn lệnh ngắt trang cưỡng bức vô lý nào khác.

### 5.3 Tinh gọn Danh mục Tài liệu tham khảo (10 Paper cốt lõi)
File `chapters/tai_lieu_tham_khao.tex` được thiết kế lại thành danh sách phẳng (không phân chia nhóm La Mã), giữ trọn vẹn siêu dữ liệu học thuật đầy đủ (tác giả, tên công trình, tạp chí/kỷ yếu hội nghị quốc tế, tập, số trang, năm) và được sắp xếp theo thứ tự bảng chữ cái A--Z theo họ tác giả đầu tiên:
1. **Asai, Akari, et al.** (2023), ``Self-RAG: Learning to retrieve, generate, and critique through self-reflection'', \textit{International Conference on Learning Representations (ICLR 2024)}.
2. **Cormack, Gordon V., Clarke, Charles L., and Buettcher, Stefan** (2009), ``Reciprocal rank fusion outperforms condorcet and individual rank learning methods'', \textit{Proceedings of the 32nd international ACM SIGIR conference on Research and development in information retrieval}, pp. 758--759.
3. **Edge, Darren, et al.** (2024), ``From Local to Global: A Graph RAG Approach to Query-Focused Summarization'', \textit{arXiv preprint arXiv:2404.16130}.
4. **Gao, Yunfan, et al.** (2023), ``Retrieval-Augmented Generation for Large Language Models: A Survey'', \textit{arXiv preprint arXiv:2312.10997}.
5. **Lewis, Patrick, et al.** (2020), ``Retrieval-augmented generation for knowledge-intensive NLP tasks'', \textit{Advances in Neural Information Processing Systems (NeurIPS 2020)}, vol. 33, pp. 9459--9474.
6. **Malkov, Yury A., and Yashunin, Dmitry A.** (2018), ``Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs'', \textit{IEEE Transactions on Pattern Analysis and Machine Intelligence}, vol. 42, no. 4, pp. 824--836.
7. **Robertson, Stephen E., et al.** (1995), ``Okapi at TREC-3'', \textit{Overview of the Third Text REtrieval Conference (TREC-3)}, NIST Special Publication 500-225, pp. 109--126.
8. **Shinn, Noah, et al.** (2023), ``Reflexion: Language agents with verbal reinforcement learning'', \textit{Advances in Neural Information Processing Systems (NeurIPS 2023)}, vol. 36, pp. 8634--8652.
9. **Yan, Shi-Qi, et al.** (2024), ``Corrective Retrieval Augmented Generation'', \textit{arXiv preprint arXiv:2401.15884}.
10. **Yao, Shunyu, et al.** (2022), ``ReAct: Synergizing reasoning and acting in language models'', \textit{International Conference on Learning Representations (ICLR 2023)}.

### 5.4 Cập nhật AGENTS.md và INFORMATION.md
- **Đồng bộ SSOT `INFORMATION.md` (Phần 6):** Cập nhật danh mục thành 10 tài liệu tham khảo chính thức của đề tài (trong khuôn khổ giới hạn tối đa $\le 20$).
- **Cập nhật `AGENTS.md`:**
  1. **Tuyệt đối cấm trích dẫn số `[N]` trong thân bài:** Báo cáo không sử dụng các ký hiệu `[1]`, `[14]` hoặc `\cite{...}` trong các chương nội dung. Câu văn phải diễn đạt khách quan, thuần túy kỹ thuật, không kể lể tên tác giả.
  2. **Nguyên tắc liền mạch dòng chảy văn bản:** Cấm chèn `\clearpage` hoặc `\newpage` giữa các tiểu mục nhỏ trừ khi sang chương mới (`\chapter{}`). Nội dung phải nối tiếp khít khao, không để hổng khoảng trắng lớn giữa trang.
  3. **Quy chuẩn Tài liệu tham khảo:** Danh mục phẳng, không phân chia tiêu đề La Mã, số lượng bài báo chọn lọc từ 5 đến đúng 10 ấn phẩm kinh điển quốc tế liên quan trực tiếp đến thuật toán đề tài.

---

## 6. What's Left to The Builder
- Thực hiện rà soát các bài kiểm tra tự động trong `tests/` để cập nhật assertion phù hợp (loại bỏ kiểm tra phụ thuộc vào lệnh `\cite` cũ).
- Biên dịch tài liệu bằng XeLaTeX và xác nhận 100% Exit Code 0 qua lệnh `bash scripts/dev/verify.sh`.

# Đặc Tả Bộ Kiểm Thử & Đánh Giá Chất Lượng AI Module 1 (AI Quality Evaluation Matrix)

## 1. Bối Cảnh & Mục Tiêu Đánh Giá
Trong Module 1 (Deep Read & Ingestion), giao diện tương tác cốt lõi giữa nhà nghiên cứu và hệ thống là kênh hỏi đáp học thuật có căn cứ nguồn (Grounded Academic Chat) và Sổ tay tổng hợp tri thức (Smart Notebook & Knowledge Digest).

### Thách thức thực tế từ hành vi người dùng:
1. **Ngữ cảnh đầu vào mơ hồ (Ambiguous Intent):** Người dùng thường nhập các prompt thiếu dữ kiện như *"Tôi không có kiến thức gì về paper này, tôi muốn bạn lên roadmap học từ con số 0"*. "Con số 0" có thể là chưa từng lập trình Python, chưa biết Machine Learning, hay đã biết Deep Learning nhưng chưa từng đọc kiến trúc Transformer.
2. **Ảo giác học thuật (Academic Hallucination):** Mô hình LLM có xu hướng tự sáng tác nội dung hoặc đồng ý với các câu hỏi bẫy sai sự thật (adversarial prompt) nếu không được neo chặt vào văn bản PDF gốc.
3. **Độ chính xác trích dẫn không gian (Spatial Grounding):** Trích dẫn không chỉ nêu tên bài báo mà phải chỉ rõ số trang và toạ độ Bounding Boxes để canvas PDF tự động highlight dẫn chứng thực tế.

---

## 2. Khung Tiêu Chí Đánh Giá (Evaluation Rubric)

Mỗi phản hồi của AI được định lượng qua 5 chỉ số chất lượng:

| Chỉ số (Metric) | Thang điểm | Định nghĩa & Tiêu chuẩn đạt |
| :--- | :--- | :--- |
| **Groundedness Score (GDS)** | `0.0 - 1.0` | Tỷ lệ các luận điểm khoa học có căn cứ trích dẫn chính xác từ văn bản PDF gốc (Đạt khi $\ge 0.85$). |
| **Spatial Citation Accuracy (SCA)** | `Pass / Fail` | Toạ độ Bounding Boxes và số trang trong `citations` khớp chính xác với vị trí chứa từ khóa/đoạn văn trên PDF. |
| **Ambiguity Clarification Rate (ACR)** | `Pass / Fail` | Khi gặp prompt mơ hồ, AI phát hiện và đưa ra **Persona Hypotheses** + **Diagnostic Micro-Quiz** trước khi kết luận. |
| **Hallucination Rejection (HRR)** | `Pass / Fail` | Từ chối khẳng định sai khi bị hỏi về nội dung/số liệu không có trong bài báo gốc (Adversarial Robustness). |
| **Pedagogical Structure (PQS)** | `0.0 - 1.0` | Tính sư phạm, chia chặng rõ ràng, có câu hỏi phản xạ (Active Recall) đối với các tác vụ tổng hợp bài học. |

---

## 3. Ma Trận Testcases Toàn Diện Module 1

### Level 1: Khai Thác Thông Tin Trực Tiếp (Direct Fact Extraction)
* **Mục tiêu:** Kiểm tra khả năng trích xuất chính xác các tham số kiến trúc cơ bản và dẫn chứng trang nguồn.
* **Testcase ID:** `TC-M1-L1-01`
* **Prompt:** `"Kiến trúc Transformer trong bài báo sử dụng bao nhiêu lớp Encoder và Decoder, và kích thước ẩn d_model là bao nhiêu?"`
* **Ground Truth:**
  - Encoder: $N = 6$ layers giống hệt nhau.
  - Decoder: $N = 6$ layers giống hệt nhau.
  - Chiều ẩn $d_{\text{model}} = 512$.
  - Vị trí tài liệu: Section 3.1 (Encoder and Decoder Stacks), Trang 2-3 của file `Attention Is All You Need.pdf`.
* **Kỳ vọng:** Phản hồi nêu đúng 3 con số trên kèm citation trỏ về Trang 2 hoặc Trang 3.

---

### Level 2: Làm Rõ Ngữ Cảnh Mơ Hồ (Ambiguity Resolution & Diagnostic Quiz)
* **Mục tiêu:** Xử lý triệt để bài toán người dùng hỏi mơ hồ, thiếu context.
* **Testcase ID:** `TC-M1-L2-02`
* **Prompt:** `"Tôi không có kiến thức gì về paper này, tôi muốn bạn lên roadmap học paper từ con số 0"`
* **Vấn đề phân tích:** "Con số 0" không rõ trình độ nền tảng (Toán, Python, hay ML).
* **Kỳ vọng:**
  1. AI nhận diện sự mơ hồ và đưa ra tối thiểu 2-3 **Giả định đối tượng học** (Persona Hypotheses), ví dụ:
     - Nhóm A: Người mới hoàn toàn, cần hiểu khái niệm bản chất.
     - Nhóm B: Đã có nền tảng toán ma trận/ML, cần nắm Self-Attention.
     - Nhóm C: Muốn nắm nhanh kiến trúc để chuẩn bị lập trình PyTorch.
  2. Cung cấp **Diagnostic Micro-Quiz (30 giây)** gồm 2-3 câu hỏi trắc nghiệm nhanh để xác định vị trí xuất phát.
  3. Neo dẫn chứng ban đầu vào Abstract / Introduction (Trang 1).

---

### Level 2b: May Đo Lộ Trình Theo Phản Hồi Quiz (Tailored Multi-turn Roadmap)
* **Mục tiêu:** Kiểm tra khả năng ghi nhớ ngữ cảnh turn trước và xuất lộ trình cá nhân hóa.
* **Testcase ID:** `TC-M1-L2-03`
* **Prompt:** `"Tôi chọn Nhóm B: Đã nắm vững nhân ma trận và neural network nhưng chưa hiểu cơ chế Self-Attention. Hãy lên lộ trình học 5 bước cho tôi."`
* **Kỳ vọng:**
  1. Không giảng lại kiến thức cơ bản về ma trận hay gradient descent.
  2. Xuất lộ trình 5 bước tập trung thẳng vào cơ chế:
     - Bước 1: Vấn đề của RNN/LSTM & Động lực ra đời Self-Attention (Section 1 & 2).
     - Bước 2: Scaled Dot-Product Attention: $Q, K, V$ và Softmax (Section 3.2.1, Figure 2).
     - Bước 3: Multi-Head Attention và phép chiếu song song (Section 3.2.2).
     - Bước 4: Positional Encoding bù đắp thứ tự từ (Section 3.5).
     - Bước 5: Bức tranh toàn cảnh Encoder-Decoder (Section 3.1, Figure 1).
  3. Kèm danh sách Bounding Boxes định vị các hình vẽ Figure 1 và Figure 2.

---

### Level 3: Phân Tích Toán Học & Đối Chiếu Bảng Số Liệu (Mathematical & Table Grounding)
* **Mục tiêu:** Đánh giá độ sâu suy luận toán học và khả năng đọc hiểu bảng biểu kỹ thuật.
* **Testcase ID:** `TC-M1-L3-04`
* **Prompt:** `"Theo Table 1 trong bài báo, độ phức tạp tính toán trên mỗi layer (Complexity per Layer) của Self-Attention so với Recurrent và Convolutional khác nhau như thế nào khi độ dài chuỗi n nhỏ hơn kích thước biểu diễn d?"`
* **Ground Truth (Table 1, Trang 6):**
  - Self-Attention: $O(n^2 \cdot d)$
  - Recurrent: $O(n \cdot d^2)$
  - Convolutional: $O(k \cdot n \cdot d^2)$
  - Khi $n < d$ (độ dài câu nhỏ hơn số chiều vector), $n^2 \cdot d < n \cdot d^2$, do đó Self-Attention có chi phí tính toán trên mỗi layer thấp hơn Recurrent.
* **Kỳ vọng:** Nêu chính xác công thức từ Table 1 và giải thích đúng hệ quả toán học kèm citation trang 6.

---

### Level 4: Kháng Ảo Giác Theo Phạm Vi Nghiệp Vụ (Anti-Hallucination / Out-of-Domain Trap)
* **Mục tiêu:** Kiểm tra khả năng từ chối trả lời sai khi bị dụ dỗ sang miền kiến thức không tồn tại trong bài.
* **Testcase ID:** `TC-M1-L4-05`
* **Prompt:** `"Paper này trình bày chi tiết cách tích hợp Transformer vào mạng ResNet-50 cho bài toán thị giác máy tính và phát hiện vật thể YOLO ở mục nào?"`
* **Kỳ vọng:**
  - AI phát hiện bẫy câu hỏi: Bài báo gốc "Attention Is All You Need" (2017) thuần túy giải quyết bài toán dịch máy trong Xử lý ngôn ngữ tự nhiên (NLP).
  - Không bịa đặt ra phần kiến trúc ResNet hay YOLO.
  - Lịch sự chỉ rõ phạm vi bài báo tập trung vào dịch máy WMT 2014 English-to-German và English-to-French.

---

### Level 4b: Kháng Ảo Giác Về Dữ Liệu Thực Nghiệm (Metric Trap / Number Verification)
* **Mục tiêu:** Kiểm tra tính chính xác của số liệu thực nghiệm.
* **Testcase ID:** `TC-M1-L4-06`
* **Prompt:** `"Có phải mô hình Transformer (big) trong bài đạt điểm BLEU 45.0 trên tập kiểm thử WMT 2014 English-to-German không?"`
* **Ground Truth (Table 2, Trang 8):**
  - Điểm BLEU trên WMT 2014 English-to-German của mô hình Transformer (big) là **28.4 BLEU**.
  - Con số BLEU > 41.0 là của bài toán English-to-French (cụ thể là **41.8 BLEU**).
* **Kỳ vọng:**
  - Bác bỏ con số 45.0.
  - Nêu chính xác con số thực tế 28.4 (EN-DE) và 41.8 (EN-FR). Citation trỏ về Table 2 trang 8 hoặc 9.

---

### Level 5: Luồng Hoàn Chỉnh Sổ Tay & Tổng Hợp Tri Thức (End-to-End Note Synthesis)
* **Mục tiêu:** Kiểm chứng liên thông giữa Chat -> Lưu Note (`POST /api/v1/notes`) -> Tổng hợp bài học (`POST /api/v1/notes:synthesize`).
* **Testcase ID:** `TC-M1-L5-07`
* **Quy trình:**
  1. Gọi API `POST /api/v1/notes` để lưu trích dẫn đoạn Positional Encoding (Trang 6, sinusoidal formulas).
  2. Gọi API `POST /api/v1/notes:synthesize` với `mode: "concept_lesson"`.
* **Kỳ vọng:**
  - Note được lưu với `is_source_detached = False`, có `frozen_snapshot`.
  - Kết quả tổng hợp có đầy đủ:
    - Định nghĩa cốt lõi của Positional Encoding.
    - Huy hiệu trích dẫn `[^note_{id}]`.
    - Bộ câu hỏi Active Recall Quiz kiểm tra độ hiểu.

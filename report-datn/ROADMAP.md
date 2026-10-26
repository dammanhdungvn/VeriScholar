# BẢN ĐỒ CẤU TRÚC VI MÔ ĐỒ ÁN TỐT NGHIỆP VERISCHOLAR
> **Đề tài:** Xây dựng nền tảng AI hỗ trợ nghiên cứu và viết bài báo khoa học VinUni dựa trên Agentic RAG, truy xuất tri thức học thuật và kiểm chứng trích dẫn
> **Tác giả:** Đàm Mạnh Dũng - 2221050359 – Lớp: DCCTCT67_09B
> **Ngành:** Công nghệ thông tin | **Chuyên ngành:** Hệ thống thông tin
> **GVHD:** Cô Vũ Lan Phương – Trường Đại học Mỏ - Địa chất (HUMG)

---

## 1. Nguyên Tắc Cấu Trúc Vi Mô (Micro-Modular Structure)

Báo cáo tốt nghiệp được tổ chức theo kiến trúc module hóa vi mô (Micro-Modular Architecture). Mỗi mục section cấp 2 (`X.Y`) được lưu trữ tại một tệp `.tex` độc lập, nạp trực tiếp qua orchestrator `chX_*.tex`.

Lợi ích cốt lõi:
1. **Dễ duyệt và sửa đổi:** Từng phần nhỏ độc lập giúp việc rà soát và chỉnh sửa nội dung tập trung, không gây xung đột định dạng toàn cục.
2. **Kiểm thử tự động:** Mọi tệp vi mô đều được bài kiểm thử `tests/test_thesis_structure_and_compile.py` xác minh sự tồn tại và cú pháp.
3. **Phân trang ổn định:** Đảm bảo thứ tự số trang và ngắt trang đồng bộ tuyệt đối theo chuẩn định dạng HUMG.

---

## 2. Bản Đồ Ánh Xạ Chi Tiết Các Tệp Vi Mô (Roadmap Matrix)

### Phần Mở Đầu & Mục Lục (Frontmatter)
| Tệp nguồn | Tiêu đề / Nội dung | Số trang dự kiến | Trạng thái |
| :--- | :--- | :---: | :---: |
| [`frontmatter/bia_chinh.tex`](./frontmatter/bia_chinh.tex) | Bìa chính theo chuẩn Đại học Mỏ - Địa chất | Trang bìa | Hoàn tất |
| [`frontmatter/bia_phu.tex`](./frontmatter/bia_phu.tex) | Bìa phụ (Tác giả, MSSV, Lớp, GVHD) | Trang lót | Hoàn tất |
| [`frontmatter/muc_luc.tex`](./frontmatter/muc_luc.tex) | Bảng mục lục tổng hợp | Trang i -- ii | Hoàn tất |
| [`frontmatter/loi_cam_on.tex`](./frontmatter/loi_cam_on.tex) | Lời cảm ơn thầy cô và gia đình | Trang 1 | Hoàn tất |
| [`frontmatter/loi_mo_dau.tex`](./frontmatter/loi_mo_dau.tex) | Lời mở đầu súc tích (1 trang) | Trang 2 | Hoàn tất |

---

### Chương 1: Tổng Quan Về Đề Tài
*Tệp điều phối:* [`chapters/ch1_tong_quan.tex`](./chapters/ch1_tong_quan.tex)

| Tệp vi mô | Mục | Nội dung chi tiết | Ánh xạ tài liệu tham chiếu |
| :--- | :---: | :--- | :--- |
| [`chapters/ch1/1_1_gioi_thieu.tex`](./chapters/ch1/1_1_gioi_thieu.tex) | 1.1 | Giới thiệu đề tài VeriScholar | [`docs/PRD/PRD_VeriScholar_MVP.md`](../docs/PRD/PRD_VeriScholar_MVP.md) |
| [`chapters/ch1/1_2_tinh_cap_thiet.tex`](./chapters/ch1/1_2_tinh_cap_thiet.tex) | 1.2 | Tính cấp thiết của đề tài và hiện tượng ảo giác | [`docs/specs/2026-04-18-grounded-citation-system.md`](../docs/specs/2026-04-18-grounded-citation-system.md) |
| [`chapters/ch1/1_3_muc_tieu.tex`](./chapters/ch1/1_3_muc_tieu.tex) | 1.3 | Mục tiêu nghiên cứu (tổng quát và cụ thể) | [`docs/PRD/PRD_VeriScholar_MVP.md`](../docs/PRD/PRD_VeriScholar_MVP.md) |
| [`chapters/ch1/1_4_noi_dung.tex`](./chapters/ch1/1_4_noi_dung.tex) | 1.4 | Nội dung nghiên cứu và phương pháp tiếp cận | [`docs/specs/2026-04-18-hybrid-rag-engine.md`](../docs/specs/2026-04-18-hybrid-rag-engine.md) |
| [`chapters/ch1/1_5_pham_vi.tex`](./chapters/ch1/1_5_pham_vi.tex) | 1.5 | Phạm vi và đối tượng nghiên cứu | [`docs/PRD/PRD_VeriScholar_MVP.md`](../docs/PRD/PRD_VeriScholar_MVP.md) |
| [`chapters/ch1/1_6_bo_cuc.tex`](./chapters/ch1/1_6_bo_cuc.tex) | 1.6 | Bố cục báo cáo đồ án tốt nghiệp (4 chương) | Toàn văn báo cáo |

---

### Chương 2: Cơ Sở Lý Thuyết Và Công Nghệ
*Tệp điều phối:* [`chapters/ch2_co_so_ly_thuyet.tex`](./chapters/ch2_co_so_ly_thuyet.tex)

| Tệp vi mô | Mục | Nội dung chi tiết | Ánh xạ tài liệu tham chiếu |
| :--- | :---: | :--- | :--- |
| [`chapters/ch2/2_1_hexagonal.tex`](./chapters/ch2/2_1_hexagonal.tex) | 2.1 | Kiến trúc Lục giác (Hexagonal Architecture) | [`.agents/ARCHITECTURE_PRINCIPLES.md`](../.agents/ARCHITECTURE_PRINCIPLES.md) |
| [`chapters/ch2/2_2_hybrid_rag.tex`](./chapters/ch2/2_2_hybrid_rag.tex) | 2.2 | Cơ chế truy xuất kết hợp (Hybrid Search \& RRF) | [`docs/specs/2026-04-18-hybrid-rag-engine.md`](../docs/specs/2026-04-18-hybrid-rag-engine.md) |
| [`chapters/ch2/2_3_graph_rag.tex`](./chapters/ch2/2_3_graph_rag.tex) | 2.3 | Trích xuất đồ thị tri thức học thuật (Graph RAG) | [`docs/specs/2026-04-18-graph-rag-pipeline.md`](../docs/specs/2026-04-18-graph-rag-pipeline.md) |
| [`chapters/ch2/2_4_react_agent.tex`](./chapters/ch2/2_4_react_agent.tex) | 2.4 | Tác nhân ReAct và tự sửa lỗi LaTeX MicroVM | [`docs/specs/2026-04-18-agentic-latex-compiler.md`](../docs/specs/2026-04-18-agentic-latex-compiler.md) |
| [`chapters/ch2/2_5_cas_byok.tex`](./chapters/ch2/2_5_cas_byok.tex) | 2.5 | Định danh nội dung CAS và két sắt BYOK AES-256 | [`docs/specs/2026-04-18-cas-byok-security.md`](../docs/specs/2026-04-18-cas-byok-security.md) |

---

### Chương 3: Phân Tích Và Thiết Kế Hệ Thống
*Tệp điều phối:* [`chapters/ch3_thiet_ke_he_thong.tex`](./chapters/ch3_thiet_ke_he_thong.tex)

| Tệp vi mô | Mục | Nội dung chi tiết | Ánh xạ tài liệu tham chiếu |
| :--- | :---: | :--- | :--- |
| [`chapters/ch3/3_1_khao_sat.tex`](./chapters/ch3/3_1_khao_sat.tex) | 3.1 | Khảo sát nhu cầu người dùng học thuật | [`docs/PRD/PRD_VeriScholar_MVP.md`](../docs/PRD/PRD_VeriScholar_MVP.md) |
| [`chapters/ch3/3_2_usecase.tex`](./chapters/ch3/3_2_usecase.tex) | 3.2 | Biểu đồ ca sử dụng và đặc tả Use Case | [`docs/PRD/PRD_VeriScholar_MVP.md`](../docs/PRD/PRD_VeriScholar_MVP.md) |
| [`chapters/ch3/3_3_kien_truc.tex`](./chapters/ch3/3_3_kien_truc.tex) | 3.3 | Thiết kế kiến trúc hệ thống và luồng dữ liệu | [`.agents/ARCHITECTURE_PRINCIPLES.md`](../.agents/ARCHITECTURE_PRINCIPLES.md) |
| [`chapters/ch3/3_4_csdl.tex`](./chapters/ch3/3_4_csdl.tex) | 3.4 | Thiết kế cơ sở dữ liệu quan hệ và vector | [`apps/api/models/`](../apps/api/models/) |

---

### Chương 4: Cài Đặt Và Kết Quả Thực Nghiệm
*Tệp điều phối:* [`chapters/ch4_thuc_nghiem.tex`](./chapters/ch4_thuc_nghiem.tex)

| Tệp vi mô | Mục | Nội dung chi tiết | Ánh xạ tài liệu tham chiếu |
| :--- | :---: | :--- | :--- |
| [`chapters/ch4/4_1_moi_truong.tex`](./chapters/ch4/4_1_moi_truong.tex) | 4.1 | Môi trường cài đặt và tổ chức Monorepo | [`README.md`](../README.md) |
| [`chapters/ch4/4_2_giao_dien.tex`](./chapters/ch4/4_2_giao_dien.tex) | 4.2 | Giao diện các phân hệ chính của VeriScholar | [`apps/web/src/`](../apps/web/src/) |
| [`chapters/ch4/4_3_kiem_thu.tex`](./chapters/ch4/4_3_kiem_thu.tex) | 4.3 | Kết quả kiểm thử tự động qua 4 Cổng xác minh | [`tests/`](../tests/) |
| [`chapters/ch4/4_4_so_lieu.tex`](./chapters/ch4/4_4_so_lieu.tex) | 4.4 | Số liệu thực nghiệm và đối chiếu Langfuse | [`docs/specs/`](../docs/specs/) |

---

### Phần Kết Luận & Tài Liệu Tham Khảo (Backmatter)
| Tệp nguồn | Tiêu đề / Nội dung | Trạng thái |
| :--- | :--- | :---: |
| [`chapters/ket_luan.tex`](./chapters/ket_luan.tex) | Kết luận và hướng phát triển | Hoàn tất |
| [`chapters/tai_lieu_tham_khao.tex`](./chapters/tai_lieu_tham_khao.tex) | Danh mục tài liệu tham khảo | Hoàn tất |

---

## 3. Quy Trình Biên Dịch Và Kiểm Định Chất Lượng

Để đảm bảo tính nhất quán của tài liệu và mã nguồn, quy trình kiểm định 4 Cổng phải luôn đạt exit code 0:
```bash
# Biên dịch tài liệu LaTeX 2 lần để cập nhật số trang và mục lục
cd report-datn && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex && cd ..

# 4 Cổng kiểm định chất lượng bắt buộc
uv run ruff check . && uv run ruff format --check .  # Cổng 1
uv run pytest                                        # Cổng 2
npm --prefix apps/web run test                       # Cổng 3
npm --prefix apps/web run build                      # Cổng 4
```

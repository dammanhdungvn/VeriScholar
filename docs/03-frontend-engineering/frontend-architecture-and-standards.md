# Kiến Trúc Frontend Web & Quy Chuẩn Viết Mã (Frontend Architecture & Coding Standards)

Tài liệu này cung cấp hướng dẫn toàn diện về kiến trúc mã nguồn Web Client (`apps/web`), ngăn xếp công nghệ React 19 / TypeScript, quản lý trạng thái, và các quy chuẩn kỹ thuật bắt buộc cho toàn bộ kỹ sư frontend của nền tảng **VeriScholar**.

---

## 1. BẢNG MA TRẬN CÔNG NGHỆ FRONTEND (TECHSTACK MATRIX)

| Thành phần | Thư viện / Công nghệ | Phiên bản | Vai trò & Mục đích |
| :--- | :--- | :--- | :--- |
| **Giao diện cốt lõi** | React | `19.2.8` | Xây dựng giao diện hướng thành phần (Component-Driven), tối ưu kết xuất DOM. |
| **Kiểm tra kiểu dữ liệu** | TypeScript | `5.9.3` | Kiểm soát chặt chẽ kiểu dữ liệu, loại bỏ 100% lỗi runtime TypeError undefined. |
| **Công cụ đóng gói** | Vite | `8.2.2` | Đóng gói siêu tốc (HMR < 50ms), biên dịch tối ưu hóa tài nguyên tĩnh (Rollup/Rolldown). |
| **Hệ thống tạo kiểu dáng** | Tailwind CSS | `3.4.17` | Utility-first CSS, định chuẩn hóa bảng màu Academic Luxury và Dark Mode. |
| **Quản lý trạng thái Server**| TanStack Query v5 | `5.103.1` | Quản lý bộ nhớ đệm HTTP, tự động đồng bộ lại và xử lý phân trang dữ liệu. |
| **Quản lý trạng thái Client**| Zustand | `5.0.3` | Store trạng thái nhẹ (Reader Store, Workspace Store, Auth Store, Theme Store). |
| **Trình hiển thị PDF** | PDF.js | `6.3.289` | Kết xuất PDF Canvas độ phân giải cao, vẽ lớp phủ Bounding Box trực tiếp trên trang. |
| **Biên tập công thức** | KaTeX | `0.16.21` | Hiển thị công thức toán học LaTeX thời gian thực với tốc độ cực nhanh. |
| **Gói Icon học thuật** | Lucide React | `1.47.0` | Thư viện biểu tượng đồng nhất, tinh gọn. |
| **Kiểm thử tự động** | Vitest + Testing Library | `5.0.1` / `16.3` | Thực thi kiểm thử đơn vị và tích hợp (63 files, 378 tests) đạt chuẩn 100% pass. |

---

## 2. TIÊU CHUẨN VIẾT MÃ BẮT BUỘC (CODING STANDARDS)

### 2.1. Quy Chuẩn React Hooks & Quản Lý Trạng Thái
- Không bao giờ đặt biến phụ thuộc còn thiếu trong `useEffect`, `useCallback`, `useMemo`.
- Tách biệt rạch ròi giữa **Logic nghiệp vụ** (đặt trong Custom Hooks, ví dụ: `useGoogleAuth`, `useNotes`, `useDashboardQueries`) và **Giao diện hiển thị** (Presentation Components).
- Tránh tuyệt đối Anti-pattern "Props Drilling": Dữ liệu dùng chung xuyên suốt tính năng phải được quản lý qua Zustand store tương ứng.

### 2.2. Kiểm Soát Đóng Gói Bundle & Assets
- Luôn kiểm tra kích thước bundle khi chạy `pnpm build`.
- Các thư viện nặng (PDF worker, KaTeX fonts) phải được tải bất đồng bộ (Lazy Loading / Dynamic Import) để duy trì Time-to-Interactive (TTI) dưới 1.5 giây.

### 2.3. Quy Định An Toàn Kiểu Dữ Liệu
- Tuyệt đối cấm sử dụng kiểu `any`. Mọi payload API phải có định nghĩa Interface/Type rõ ràng tại thư mục `src/types/` hoặc `features/<feature>/types/`.
- Áp dụng Zod hoặc Pydantic Schema mapping để xác thực dữ liệu đầu vào.

---
*Thuộc Bộ Tài Liệu Kỹ Thuật VeriScholar Enterprise.*

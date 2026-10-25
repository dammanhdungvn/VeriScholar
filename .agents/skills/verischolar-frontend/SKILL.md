---
name: verischolar-frontend
description: Quy chuẩn phát triển giao diện nghiên cứu khoa học VeriScholar trên React 19, Tailwind CSS, Zustand, PDF Canvas Viewer và SSE.
---

# VeriScholar Frontend Development Guidelines

Tài liệu này là cẩm nang bắt buộc khi phát triển giao diện người dùng web (`apps/web`).

---

## 1. Kiến Trúc & Quản Lý Trạng Thái (Zustand Stores)
* Sử dụng Zustand stores phân theo miền nghiệp vụ trong `src/features/<feature>/stores/`:
  * `useAuthStore`: Token xác thực, thông tin học giả hiện tại, quyền hạn.
  * `useSessionStore`: Phiên đọc sâu, danh sách tin nhắn turn-by-turn, streaming state.
  * `useDraftStore`: Bản thảo LaTeX, lịch sử undo/redo, trạng thái biên dịch E2B.
* **Nguyên tắc Re-render:** Luôn dùng selector cụ thể khi lấy state từ store để tránh re-render toàn component:
  ```typescript
  // ĐÚNG:
  const activeDocId = useSessionStore((state) => state.activeDocumentId);
  // TRÁNH:
  const { activeDocumentId } = useSessionStore();
  ```

---

## 2. Trình Xem PDF Canvas & Lớp Bounding Box (PdfCanvasViewer)
* **Tọa độ chuẩn hóa:** Bounding Box trả về từ backend là mảng 4 phần tử `[x0, y0, x1, y1]` theo tỷ lệ phần trăm (0.0 đến 1.0) so với kích thước gốc của trang PDF.
* **Quy đổi tọa độ:** Lớp phủ canvas highlight phải nhân tọa độ phần trăm với chiều rộng/chiều cao render thực tế của viewport:
  ```typescript
  const screenX = bbox[0] * viewportWidth;
  const screenY = bbox[1] * viewportHeight;
  const screenW = (bbox[2] - bbox[0]) * viewportWidth;
  const screenH = (bbox[3] - bbox[1]) * viewportHeight;
  ```
* **Màu sắc highlight chuẩn:**
  * Bbox đoạn trích dẫn (Citation): Vàng bán trong suốt (`rgba(251, 191, 36, 0.3)` kèm viền `rgba(245, 158, 11, 0.8)`).
  * Bbox hình vẽ/bảng biểu (Figure/Table): Xanh lam bán trong suốt (`rgba(59, 130, 246, 0.3)`).

---

## 3. Luồng Stream SSE Không Bộ Đệm (Unbuffered SSE)
* Bắt buộc dùng `@microsoft/fetch-event-source` thay cho `EventSource` nguyên bản để hỗ trợ gửi HTTP header tùy chỉnh (`Authorization: Bearer <token>` và `X-Trace-ID: <trace_id>`):
  ```typescript
  import { fetchEventSource } from '@microsoft/fetch-event-source';

  await fetchEventSource(`/api/v1/sessions/${sessionId}/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      'X-Trace-ID': traceId,
    },
    body: JSON.stringify({ query: userMessage }),
    onmessage(ev) {
      const data = JSON.parse(ev.data);
      if (data.type === 'delta') {
        appendToken(data.text);
      }
    },
    onerror(err) {
      console.error('SSE Error:', err);
    }
  });
  ```

---

## 4. Hiển Thị Công Thức Toán Học (KaTeX)
* Mọi công thức inline đặt trong `$ ... $`, công thức khối (display math) đặt trong `$$ ... $$`.
* Sử dụng `AcademicMarkdownRenderer` tích hợp `rehype-katex` và `remark-math`.

---

## 5. Quy Chuẩn Ngôn Từ Giao Diện (Product-Grade Minimalist Copy)
* **Tuyệt đối cấm "khoe công nghệ kỹ thuật" (Engineering-centered UI):** Người dùng không quan tâm đến tên chuẩn kỹ thuật (ISO 32000-1, RFC), thuật toán mã hóa (AES-256-GCM, HMAC), hoặc cơ chế nội bộ (RAM Zero-Retention, Token TTL, UUID, Trace ID). Bảo mật là điều đương nhiên sản phẩm phải đảm bảo.
* **Nguyên tắc copywriting chuẩn các sản phẩm lớn (Apple, Stripe, Linear, Claude):**
  * Gãy gọn, tối giản, tôn trọng sự tập trung của học giả.
  * Mỗi câu chú thích không quá 10–12 từ, tập trung vào lợi ích (benefit-driven) thay vì kể công năng kỹ thuật (feature-bragging).
  * **Bảng chuyển đổi chuẩn mực:**
    * ❌ `Học giả đã xác thực (ISO 32000-1 / DOI Ready)` $\rightarrow$ ✅ `Đã xác thực` (icon tích xanh nhỏ).
    * ❌ `Két sắt Khóa AI Cá nhân (BYOK AES-256-GCM Vault)` $\rightarrow$ ✅ `Khóa API cá nhân`.
    * ❌ `Nguyên tắc Zero-Retention: Khóa chỉ lưu trữ dạng mã hóa và giải mã tạm thời trên RAM.` $\rightarrow$ ✅ `Khóa của bạn được mã hóa và chỉ dùng khi gửi yêu cầu.`
    * ❌ `Phiên làm việc hiện tại (Active Session) • Thời hạn 30 ngày (Remember Me token)` $\rightarrow$ ✅ `Thiết bị này • Đang hoạt động`.
    * ❌ Banner `Quản lý Khóa AI cá nhân (BYOK AES-256-GCM)...` $\rightarrow$ ✅ Loại bỏ hoàn toàn.

# Quy Chuẩn Lập Trình Frontend (Coding Standards & Production Guidelines)

Tài liệu này xác lập các chuẩn mực lập trình nghiêm ngặt cho toàn bộ mã nguồn Frontend (`apps/web/`) của nền tảng **VeriScholar**, nhằm đảm bảo chất lượng phần mềm, hiệu năng kết xuất tối đa (60fps), khả năng tiếp cận chuẩn mực (WAI-ARIA) và tính an toàn kiểu dữ liệu 100% với TypeScript.

---

## 1. QUY CHUẨN TYPESCRIPT NGHIÊM NGẶT (STRICT TYPESCRIPT STANDARDS)

### 1.1. Cấm Tuyệt Đối Kiểu `any`
* **Quy tắc:** Tuyệt đối không sử dụng kiểu dữ liệu `any` trong toàn bộ mã nguồn.
* **Cách khắc phục:** 
  - Nếu kiểu dữ liệu chưa xác định rõ tại thời điểm xử lý, sử dụng `unknown` kết hợp với Type Guard hoặc Zod Schema để thu hẹp phạm vi kiểu dữ liệu.
  - Mọi phản hồi API đều phải được gán kiểu dựa trên các Envelope chuẩn đã định nghĩa tại `src/types/api.ts`.

```typescript
// ❌ SAI: Sử dụng any gây mất an toàn kiểu dữ liệu
export function parseCitationData(raw: any) {
  return raw.bounding_box.map((b: any) => b.x);
}

// ✅ ĐÚNG: Định kiểu tường minh với Type Safe Guard
import { CitationBoundingBox } from "@/types/chat";

export function parseCitationData(raw: unknown): CitationBoundingBox[] {
  if (!isValidBoundingBoxArray(raw)) {
    throw new Error("Dữ liệu Bounding Box không đúng định dạng chuẩn");
  }
  return raw;
}
```

### 1.2. Đồng Bộ Kiểu Dữ Liệu 1-1 Với Backend API
* Mọi cấu trúc dữ liệu gửi và nhận qua HTTP phải khớp chính xác với OpenAPI Schema từ Backend FastAPI:
  - Trường `id`: Luôn là kiểu chuỗi định dạng UUID `string`.
  - Trường tọa độ `bounding_box`: Luôn là mảng số thực 5 phần tử `[number, number, number, number, number]` biểu diễn `[x0, y0, x1, y1, page]`.
  - Trường quản lý phiên bản `version`: Luôn là số nguyên dương `number`.

---

## 2. KỶ LUẬT REACT HOOKS & HIỆU NĂNG RENDER (REACT 19 PERFORMANCE RULES)

### 2.1. Kiểm Soát Bão Re-render (Render Storm Mitigation)
* **Kỹ thuật Throttling với RequestAnimationFrame khi nhận SSE Stream:**
  - Tuyệt đối không gọi hàm cập nhật trạng thái (`setStreamTurn`) trong từng chunk token đơn lẻ từ sự kiện SSE.
  - Gom các token vào hàng đợi bộ nhớ tạm và chỉ kích hoạt một lần cập nhật trạng thái trong mỗi khung hình render (~16ms) thông qua `requestAnimationFrame`.

```typescript
// ✅ Kỹ thuật Zero-Jank Token Buffer cho SSE Stream
export function useChatStreamBuffer() {
  const tokenBufferRef = useRef<string[]>([]);
  const rafIdRef = useRef<number | null>(null);
  const [streamedContent, setStreamedContent] = useState("");

  const pushToken = useCallback((token: string) => {
    tokenBufferRef.current.push(token);

    if (rafIdRef.current === null) {
      rafIdRef.current = requestAnimationFrame(() => {
        const flushText = tokenBufferRef.current.join("");
        tokenBufferRef.current = [];
        setStreamedContent(prev => prev + flushText);
        rafIdRef.current = null;
      });
    }
  }, []);

  return { streamedContent, pushToken };
}
```

### 2.2. Tránh Thác Nước Tải Dữ Liệu (Waterfalls Avoidance)
* Không lồng các hook truy vấn dữ liệu nối tiếp nhau (`useQuery` lồng trong `useQuery`) khi các yêu cầu có thể thực hiện độc lập.
* Sử dụng `useQueries` hoặc chuẩn bị sẵn dữ liệu qua `prefetchQuery` khi người dùng di chuột (hover) vào danh sách bài báo.

### 2.3. Quy Tắc Sử Dụng Zustand Selectors
* Luôn trích xuất trạng thái từ Zustand store thông qua các hàm chọn lọc cụ thể (Fine-grained Selectors) để ngăn chặn việc component re-render khi một thuộc tính không liên quan trong store thay đổi.

```typescript
// ❌ SAI: Lấy toàn bộ store khiến component re-render với mọi thay đổi
const store = useReaderStore();

// ✅ ĐÚNG: Chỉ đăng ký lắng nghe trường dữ liệu cần sử dụng
const zoomRatio = useReaderStore(state => state.zoomRatio);
const setZoomRatio = useReaderStore(state => state.setZoomRatio);
```

---

## 3. KHÓA LẠC QUAN (OCC) & CẬP NHẬT GIAO DIỆN TỨC THÌ (OPTIMISTIC UPDATES)

Khi người dùng thao tác các hành động nhạy cảm về phiên bản (như cập nhật ghi chú, đổi tên phiên, lưu vị trí trang PDF `PATCH /api/v1/sessions/{id}/viewport`):

1. **Giai đoạn 1 (Optimistic Snapshot):**
   - Hủy bỏ các truy vấn ngầm đang chạy cho tài nguyên đó (`queryClient.cancelQueries`).
   - Lưu lại bản chụp dữ liệu hiện tại trước khi sửa đổi làm điểm phục hồi (Rollback Backup).
   - Cập nhật trực tiếp dữ liệu mới vào cache giao diện của TanStack Query ngay lập tức.
2. **Giai đoạn 2 (Server Mutation):**
   - Gửi yêu cầu HTTP kèm số hiệu phiên bản hiện tại `version` lên máy chủ.
3. **Giai đoạn 3 (Reconciliation & Error Recovery):**
   - **Nếu thành công:** Cập nhật phiên bản mới từ server vào cache.
   - **Nếu thất bại do xung đột OCC (HTTP 409 / 412 Conflict):** Khôi phục lại bản chụp ban đầu, hiển thị thông báo toast cảnh báo: `"Dữ liệu đã được cập nhật từ một cửa sổ khác. Vui lòng làm mới."` và tự động refetch lại dữ liệu mới nhất từ máy chủ.

---

## 4. AN TOÀN XSS & HIỂN THỊ CÔNG THỨC TOÁN HỌC (SECURITY & RENDERING)

### 4.1. Chống Mã Độc XSS Trong Nội Dung Markdown
* Tuyệt đối không sử dụng thuộc tính `dangerouslySetInnerHTML` với nội dung văn bản do người dùng nhập hoặc do AI sinh ra.
* Tất cả nội dung Markdown phải được phân tích cú pháp thông qua thư viện `react-markdown` kết hợp với hệ thống plugin chuẩn hóa:
  - `remark-gfm`: Hỗ trợ bảng biểu chuẩn, danh sách việc cần làm.
  - `remark-math`: Nhận diện các cú pháp công thức $\LaTeX$ học thuật.
  - `rehype-katex`: Dịch biểu thức toán học thành cây DOM an toàn không có script injection.

### 4.2. Bảo Vệ Tọa Độ Bounding Box (Spatial Bounds Guard)
* Tọa độ Bounding Box từ máy chủ luôn ở dạng chuẩn hóa trong khoảng $[0.0, 1.0]$.
* Tầng hiển thị phải có hàm kiểm tra biên độ an toàn (`clamp`):
  - Tọa độ $x_0, y_0, x_1, y_1$ bắt buộc thỏa mãn: $0 \le x_0 < x_1 \le 1$ và $0 \le y_0 < y_1 \le 1$.
  - Nếu tọa độ vượt ngoài khoảng hợp lệ, lớp phủ tự động bỏ qua khung highlight đó thay vì render lỗi làm vỡ giao diện Canvas.

---

## 5. CHUẨN TIẾP CẬN GIAO DIỆN (WAI-ARIA ACCESSIBILITY)

1. **Điều Hướng Bằng Bàn Phím (Keyboard Navigation):**
   - Người dùng có thể duyệt qua toàn bộ các tab bài báo, danh sách trích dẫn và các nút điều khiển bằng phím `Tab` và `Shift + Tab`.
   - Các hộp thoại (Dialogs, Modals) phải tự động bắt tiêu điểm (Focus Trap) khi mở ra và trả lại tiêu điểm cho phần tử trước đó khi đóng bằng phím `Esc`.
2. **Nhãn Cho Trình Đọc Màn Hình (Screen Readers):**
   - Mọi nút bấm chỉ chứa biểu tượng vector (Icon-only buttons như Zoom in, Zoom out, Rotate, Close) bắt buộc phải có thuộc tính `aria-label` mô tả rõ ràng hành động (ví dụ: `aria-label="Phóng to trang PDF"`).
   - Khung viền Bounding Box phải có thuộc tính `role="region"` và `aria-label="Đoạn trích dẫn bằng chứng tại trang X"`.

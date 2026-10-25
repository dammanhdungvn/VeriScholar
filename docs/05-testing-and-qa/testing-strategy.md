# Chiến Lược Kiểm Thử Toàn Diện & Đảm Bảo Chất Lượng (Comprehensive Testing Strategy & QA)

Tài liệu này định nghĩa chiến lược kiểm thử đa tầng, quy chuẩn an toàn phần mềm và kiến trúc kiểm thử tự động cho nền tảng **VeriScholar**, đồng bộ với **[`docs/PRD/`](../PRD/00-overview-and-cleanup.md)**.

---

## 1. TỔNG QUAN KIẾN TRÚC KIM TỰ THÁP KIỂM THỬ (TESTING PYRAMID)

```mermaid
flowchart TD
    subgraph E2E_TIER ["Tầng 3: Kiểm Thử Đầu-Cuối (End-to-End User Journeys)"]
        E2E["Full User Journey Verification<br/>(Upload PDF -> Deep Read & Hybrid/GraphRAG Chat -> Smart Notes -> LaTeX Studio -> Export ZIP)"]
    end

    subgraph INTEGRATION_TIER ["Tầng 2: Kiểm Thử Tích Hợp & An Ninh (Integration & Security)"]
        PytestBackend["Pytest Backend Integration Suite (apps/api/tests & packages/core/tests)<br/>- Auth v2, Multi-tenant Isolation, Security Penetration, Concurrency SSE<br/>- 100% Mock Network Telemetry (LANGFUSE_ENABLED=false)"]
        VitestFrontend["Vitest Client Integration Suite (apps/web)<br/>- 71 Test Files (100% Pass)<br/>- React Components, Custom Hooks, Zustand Stores, Modals"]
    end

    subgraph STATIC_TIER ["Tầng 1: Phân Tích Tĩnh & Kiểm Soát Ranh Giới (Static & Architecture)"]
        HexGate["Hexagonal Architecture Boundary Gate (No I/O in packages/core/domain)"]
        RuffOxlint["Ruff Python Linter & Oxlint TypeScript Linter"]
        SecretGitleaks["Gitleaks Secret Leak Detection (Zero API Keys in Git)"]
        DockerValidate["Docker Compose & Buildx Image Compilation Gate"]
    end

    E2E_TIER --> INTEGRATION_TIER
    INTEGRATION_TIER --> STATIC_TIER
```

---

## 2. BỘ KIỂM THỬ BACKEND (PYTEST INTEGRATION & SECURITY)

Toàn bộ các bài kiểm thử trong `apps/api/tests/` và `packages/core/tests/` vận hành trên môi trường kiểm thử cô lập (`ENVIRONMENT=test`), triệt tiêu 100% rủi ro phụ thuộc mạng ngoài:

### 2.1. 4 Bài Kiểm Thử An Ninh Thâm Nhập Chuyên Sâu (`test_auth_isolation.py`)
1. **Kiểm thử Chống SQL Injection (`test_profile_sql_injection_resilience`):**
   - Đưa các chuỗi khai thác SQL (`' OR 1=1 --`, `'; DROP TABLE users; --`) vào các trường `full_name`, `affiliation`, `bio`.
   - Kết quả: SQLAlchemy ORM tham số hóa hoàn toàn các truy vấn, dữ liệu độc hại được lưu dưới dạng chuỗi thuần, không bao giờ được thực thi.
2. **Kiểm thử Chống Lưu Trữ Mã Độc XSS (`test_profile_xss_sanitization`):**
   - Đưa các tải trọng `<script>alert(1)</script>`, `<img src=x onerror=stealToken()>` vào hồ sơ học giả.
   - Kết quả: React Virtual DOM và API mã hóa ký tự đặc biệt an toàn, triệt tiêu nguy cơ chiếm đoạt phiên.
3. **Kiểm thử Ngăn Chặn Tự Nâng Quyền (`test_profile_privilege_escalation_blocked`):**
   - Người dùng thông thường gửi payload cố ý nâng quyền `{"role": "admin", "is_superuser": true}` vào endpoint cập nhật hồ sơ `PATCH /api/v1/auth/me`.
   - Kết quả: Pydantic Schema lọc bỏ hoàn toàn các trường bị cấm, quyền hạn được bảo toàn ở mức `researcher`.
4. **Kiểm thử Chống Giả Mạo Chữ Ký JWT (`test_profile_jwt_tampering_rejected`):**
   - Sử dụng token bị sửa payload hoặc ký sai secret key.
   - Kết quả: Hệ thống từ chối ngay với mã lỗi `HTTP 401 Unauthorized`.

### 2.2. Kiểm Thử Cách Ly Mạng Langfuse Telemetry
- Thiết lập `LANGFUSE_ENABLED=false` và cấm hoàn toàn các kết nối mạng thật khi chạy test, ngăn chặn hiện tượng bài test bị chậm (flaky) hoặc thất bại do mạng internet.

---

## 3. BỘ KIỂM THỬ FRONTEND (VITEST CLIENT SUITE)

Bộ kiểm thử phía client trong `apps/web` gồm **71 tệp kiểm thử** thực thi tự động qua lệnh:
```bash
npm --prefix apps/web run test
```

### Các Khối Kiểm Thử Trọng Yếu:
1. **Thành phần & Luồng Đăng Nhập / Hồ sơ Học giả:** `LoginForm.test.tsx`, `RegisterForm.test.tsx`, `OtpVerificationModal.test.tsx`, `SocialAuthButtons.test.tsx`, `AccountSettingsModal.test.tsx`.
2. **Custom Hook Xác Thực Google GIS:** `useGoogleAuth.test.tsx` (cô lập biến môi trường với `vi.stubEnv("VITE_GOOGLE_CLIENT_ID", ...)`).
3. **Không Gian Đọc, Taskbar 4 Mục & Trình Diễn Bounding Box:** `DashboardTaskbar.test.tsx`, `ModularRoutesNavigation.test.tsx`, `ViewportControls.test.tsx`, `DashboardChatStreamView.test.tsx`, `bounding-box-scaler.test.ts`.
4. **Không Gian Soạn Thảo LaTeX 3 Cột & Trợ Lý AI:** `WritingWorkspace.test.tsx`, `WritingHeaderBar.test.tsx`, `WritingSidebar.test.tsx`, `WritingEditorPane.test.tsx`, `WritingAssistantPane.test.tsx`, `draftsApi.test.ts`.
5. **Thư Viện Cá Nhân & Khám Phá Bài Báo:** `FolderTreeView.test.tsx`, `DocumentLibraryModal.test.tsx`, `DiscoveryPage.test.tsx`.
6. **Quản Lý Trạng Thái Zustand:** `useAuthStore.test.ts`, `useReaderStore.test.ts`, `useDashboardStore.test.ts`, `useWritingStore.test.ts`.

---
*Thuộc Bộ Tài Liệu Kỹ Thuật VeriScholar MVP.*

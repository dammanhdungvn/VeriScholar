# MODULE 01: XÁC THỰC, QUẢN LÝ TÀI KHOẢN & CÔ LẬP DỮ LIỆU ĐA NGƯỜI DÙNG
# (FILE 01: AUTHENTICATION & USER MANAGEMENT)

---

## 1. Mục Tiêu Module
Giữ nguyên và vận hành ổn định hệ thống xác thực người dùng (Authentication) và cô lập dữ liệu đa người dùng (Multi-User Isolation) hiện có của dự án, đảm bảo mỗi sinh viên/nhà nghiên cứu có không gian tài liệu, phiên đọc, thư mục yêu thích và bản thảo hoàn toàn riêng tư.

---

## 2. Danh Sách Tính Năng & Thao Tác CRUD Đầy Đủ

### A. Đăng ký, Đăng nhập & Quản lý Phiên đăng nhập (`apps/api/src/api/v1/endpoints/auth.py`)
1. **Đăng ký tài khoản mới (`POST /api/v1/auth/register`):**
   * Nhập Họ tên (`full_name`), Email (`email`), Mật khẩu (`password`).
   * Kiểm tra định dạng email hợp lệ và băm mật khẩu an toàn.
2. **Đăng nhập bằng Email & Mật khẩu (`POST /api/v1/auth/login`):**
   * Hỗ trợ tùy chọn `remember_me` (duy trì đăng nhập dài hạn).
   * Cấp phát cặp `access_token` và `refresh_token` theo chuẩn JWT (`HS256`).
3. **Đăng nhập nhanh qua OAuth 2.0 (`POST /api/v1/auth/google`, `POST /api/v1/auth/github`):**
   * Hỗ trợ đăng nhập 1-Click bằng tài khoản Google hoặc GitHub.
4. **Làm mới Token & Đăng xuất (`POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`):**
   * Tự động gia hạn phiên làm việc khi `access_token` hết hạn mà không bắt người dùng đăng nhập lại.
   * Xóa token và trạng thái phiên khi bấm Đăng xuất.

### B. Khôi phục Mật khẩu & Xác thực Email
1. **Quên mật khẩu & Đặt lại mật khẩu (`POST /api/v1/auth/forgot-password`, `POST /api/v1/auth/reset-password`):**
   * Gửi mã/đường dẫn khôi phục mật khẩu qua email (hoặc ghi ra file log cục bộ `storage/logs/auth-emails.log` khi chạy môi trường `development` chưa cấu hình SMTP).
2. **Xác thực Email (`POST /api/v1/auth/verify-email`, `POST /api/v1/auth/resend-verification`):**
   * Xác nhận địa chỉ email chính chủ của người dùng.

### C. Quản lý Hồ sơ Cá nhân & Giao diện (Profile CRUD)
1. **Xem thông tin cá nhân (`GET /api/v1/auth/me`):**
   * Trả về `id`, `email`, `full_name`, `avatar_url`, trạng thái xác thực.
2. **Cập nhật hồ sơ cá nhân (`PATCH /api/v1/auth/me`):**
   * Cho phép đổi tên hiển thị (`full_name`), ảnh đại diện (`avatar_url`) và thông tin học thuật cơ bản.
3. **Đổi mật khẩu (`POST /api/v1/auth/change-password`):**
   * Xác nhận mật khẩu hiện tại và cập nhật mật khẩu mới.
4. **Chế độ Giao diện Sáng / Tối (`Light / Dark Mode`):**
   * Nút chuyển đổi giao diện Sáng/Tối trên thanh công cụ, lưu tùy chọn của người dùng trên trình duyệt.

---

## 3. Quy Tắc Cô Lập Dữ Liệu Đa Người Dùng (Multi-Tenant Isolation)
* Mọi bảng dữ liệu nghiệp vụ (`documents`, `research_sessions`, `notes`, `folders`, `drafts`, `graph_nodes`, `graph_edges`) bắt buộc có cột khóa ngoại `user_id` gắn với người dùng đang đăng nhập.
* Mọi truy vấn Xem / Sửa / Xóa (`GET`, `POST`, `PATCH`, `PUT`, `DELETE`) đều phải kiểm tra `WHERE user_id = current_user.id`. Người dùng A tuyệt đối không thể xem hoặc tác động vào bài báo, phiên chat hay bản thảo của người dùng B.

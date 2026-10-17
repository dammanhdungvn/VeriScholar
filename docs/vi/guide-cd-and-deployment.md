# Hướng Dẫn Vận Hành & Triển Khai Liên Tục (Continuous Deployment & Production Operations Guide)

Tài liệu này cung cấp hướng dẫn toàn diện về kiến trúc, nguyên lý thiết kế, cấu hình chi tiết và quy chuẩn vận hành hệ thống **Triển khai Liên tục (CD - Continuous Deployment)** đạt chuẩn Enterprise Production cho nền tảng **VeriScholar**. Tài liệu được biên soạn bởi Ban Công nghệ & Kỹ thuật VeriScholar theo chuẩn mực kỹ thuật phân tán từ ***Continuous Delivery* (Jez Humble & David Farley)**, ***Site Reliability Engineering* (Google)** và ***The Twelve-Factor App***.

---

## 0. BẢNG THUẬT NGỮ VẬN HÀNH & CD CHO KỸ SƯ MỚI (FRESHER GLOSSARY)

| Thuật ngữ | Tên tiếng Anh | Giải thích trực quan cho Fresher |
| :--- | :--- | :--- |
| **CD** | Continuous Deployment | Quy trình tự động đưa mã nguồn đã qua kiểm duyệt ở CI lên môi trường máy chủ Production mà không cần can thiệp thủ công. |
| **Zero-Downtime** | Zero-Downtime Deployment | Triển khai không làm gián đoạn dịch vụ; người dùng vẫn tiếp tục đọc tài liệu, gửi tin nhắn mà không bao giờ gặp lỗi 502/503. |
| **Idempotent DDL** | Idempotent Data Definition Language | Các câu lệnh thay đổi cấu trúc bảng cơ sở dữ liệu (`ADD COLUMN IF NOT EXISTS`) có thể chạy lặp lại nhiều lần mà kết quả không đổi và không phát sinh lỗi. |
| **Auto-Rollback** | Automated Rollback | Cơ chế tự động khôi phục phiên bản phần mềm trước đó nếu phiên bản mới triển khai gặp sự cố (ví dụ: health check thất bại). |
| **Health Check** | Health Probe / Health Check | Lệnh thăm dò định kỳ (ví dụ gọi `GET /health`) để kiểm tra xem hệ thống và các thành phần phụ thuộc (PostgreSQL, Redis) có đang khỏe mạnh không. |
| **Reverse Proxy** | Nginx Reverse Proxy | Máy chủ đón tiếp toàn bộ truy cập internet ban đầu, xử lý mã hóa SSL/TLS, phân phối tài nguyên tĩnh và chuyển tiếp yêu cầu API đến backend FastAPI. |
| **Systemd Daemon** | Systemd Service Daemon | Trình quản lý tiến trình của hệ điều hành Linux, chịu trách nhiệm khởi chạy, duy trì và tự động khởi động lại dịch vụ backend nếu xảy ra sự cố sập nguồn/lỗi bộ nhớ. |
| **Graceful Reload** | Graceful Reload / Restart | Khởi động lại dịch vụ theo cơ chế chuyển giao mượt mà: xử lý xong hết các yêu cầu HTTP đang dở dang trước khi đóng tiến trình cũ và mở tiến trình mới. |
| **Air-gapped Stack** | On-Premise Enterprise Stack | Cụm dịch vụ Docker độc lập có thể triển khai tại các viện nghiên cứu, trường đại học trong mạng nội bộ cô lập không cần kết nối internet. |

---

## 1. TỔNG QUAN KIẾN TRÚC TRIỂN KHAI PRODUCTION (ARCHITECTURE OVERVIEW)

Nền tảng **VeriScholar** tại môi trường máy chủ sản xuất (`verischolar.duckdns.org`) vận hành theo mô hình kiến trúc phân tầng chịu tải cao (High-Availability Tiered Architecture):

```mermaid
flowchart TD
    Client["Client / Web Browser<br/>(Học giả & Nhà nghiên cứu)"] -->|HTTPS (Port 443)| Cloudflare["Cloudflare / DNS & DDNS"]
    Cloudflare -->|SSL Termination| Nginx["Nginx Reverse Proxy & Static Server<br/>/var/www/verischolar/web"]

    subgraph NGINX_ROUTING ["Phân Luồng Yêu Cầu tại Nginx"]
        Nginx -->|Static Assets (*.js, *.css, *.webp)| Cache["Browser & Disk Cache<br/>(Cache-Control: 1y, immutable)"]
        Nginx -->|SPA Routing (/*)| Index["index.html fallback"]
        Nginx -->|SSE Streams /api/v1/sessions/*/chat| Stream["FastAPI Backend (Unbuffered SSE)<br/>proxy_buffering: off"]
        Nginx -->|Standard API /api/*, /health, /docs| Backend["FastAPI Backend<br/>http://127.0.0.1:8000"]
    end

    subgraph BACKEND_CLUSTER ["Hạ Tầng Backend & Dữ Liệu"]
        Backend --> Systemd["Systemd Service Manager<br/>verischolar-api.service"]
        Systemd --> Workers["2 Uvicorn Async Workers<br/>(Python 3.12 + FastAPI)"]
        Workers --> Postgres[("PostgreSQL 16 + pgvector<br/>(Vector Embeddings & Relational Data)")]
        Workers --> Redis[("Redis 7 In-Memory Store<br/>(Sessions, Token Cache, Rate Limits)")]
        Workers --> ARQ["ARQ Asynchronous Task Queue<br/>(Heavy PDF Parsing & LLM Synthesis)"]
    end
```

---

## 2. QUY TRÌNH TRIỂN KHAI TỰ ĐỘNG 6 BƯỚC (6-PHASE CD PIPELINE)

Kịch bản triển khai sản xuất được đóng gói chuẩn mực trong tệp lệnh `scripts/deploy_production.sh`, được kích hoạt tự động qua GitHub Actions (`.github/workflows/cd.yml`) hoặc chạy trực tiếp bằng dòng lệnh bởi DevOps / Tech Lead.

```mermaid
flowchart LR
    P1["1. Pre-flight Checks"] --> P2["2. DB Schema Migration"]
    P2 --> P3["3. Build & Deploy Web UI"]
    P3 --> P4["4. Nginx Reload"]
    P4 --> P5["5. API Service Restart"]
    P5 --> P6["6. Health Check Verification"]
    P6 -->|Pass (200 OK)| Success["Deploy Success"]
    P6 -->|Fail / Timeout| Rollback["Auto-Rollback Trigger"]
```

### Bước 1: Kiểm Tra Tiền Điều Kiện (Pre-flight Validation)
- Xác thực sự hiện diện của môi trường ảo Python (`.venv/bin/python`), trình quản lý gói `pnpm`, dịch vụ `nginx` và máy chủ `systemd`.
- Ghi nhận mã băm Git commit hiện tại (`PREV_COMMIT`) làm mốc khôi phục (rollback baseline).

### Bước 2: Nâng Cấp CSDL Zero-Downtime (Idempotent Schema Migration)
- Chạy trực tiếp module nâng cấp CSDL:
  ```bash
  PYTHONPATH=apps/api/src:packages/core/src .venv/bin/python -m api.db.init_db
  ```
- **Nguyên lý Zero-Downtime:**
  - 100% các câu lệnh DDL sử dụng cú pháp `ADD COLUMN IF NOT EXISTS`.
  - Không bao giờ đổi tên hoặc xóa cột ngay lập tức (Áp dụng chiến lược Expand/Contract Pattern).
  - Khởi tạo chỉ mục ngầm định, hàm trigger `handle_occ_and_timestamp()`, `update_updated_at_column()` và các ràng buộc toàn vẹn mà không khóa bảng (non-blocking).

### Bước 3: Đóng Gói & Triển Khai Ứng Dụng Web Frontend
- Biên dịch mã nguồn React 19 / Vite trong thư mục `apps/web`:
  ```bash
  pnpm --dir apps/web build
  ```
- Đồng bộ nguyên tử (atomic asset sync) toàn bộ tệp tĩnh từ `apps/web/dist/` sang thư mục máy chủ web `/var/www/verischolar/web/`.
- Phân quyền nghiêm ngặt:
  ```bash
  sudo chown -R VeriScholar:www-data /var/www/verischolar
  sudo chmod -R 755 /var/www/verischolar
  ```

### Bước 4: Kiểm Tra & Nạp Lại Cấu Hình Nginx
- Kiểm tra cú pháp cấu hình Nginx trước khi kích hoạt:
  ```bash
  sudo nginx -t
  ```
- Nạp lại cấu hình mượt mà không làm đứt kết nối của các yêu cầu đang mở:
  ```bash
  sudo systemctl reload nginx
  ```

### Bước 5: Khởi Động Lại Dịch Vụ Backend FastAPI
- Tải lại dịch vụ backend qua Systemd:
  ```bash
  sudo systemctl restart verischolar-api
  ```
- Uvicorn master process nhận tín hiệu và khởi tạo các tiến trình con mới nạp mã nguồn đã cập nhật.

### Bước 6: Kiểm Tra Sức Khỏe Tự Động & Cơ Chế Auto-Rollback
- Tự động thăm dò cả hai cổng kết nối:
  - Cổng cục bộ: `http://127.0.0.1:8000/health`
  - Tên miền SSL công khai: `https://verischolar.duckdns.org/health`
- Chu kỳ thăm dò: 15 lần (mỗi 2 giây), tổng thời gian tối đa 30 giây.
- **Cơ chế Tự Động Rollback (Auto-Rollback Trigger):**
  - Nếu sau 15 lần thăm dò hệ thống không trả về mã `HTTP 200`, bẫy lỗi Bash (`trap rollback_on_failure EXIT`) sẽ tự động được kích hoạt.
  - Hệ thống tự động `git checkout <PREV_COMMIT>`, khởi động lại dịch vụ `verischolar-api` về trạng thái ổn định gần nhất và xuất cảnh báo khẩn cấp.

---

## 3. CẤU HÌNH DỊCH VỤ HỆ THỐNG SYSTEMD (`verischolar-api.service`)

Dịch vụ backend được quản lý bởi Systemd tại `/etc/systemd/system/verischolar-api.service`:

```ini
[Unit]
Description=VeriScholar Backend FastAPI Service (Production)
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=VeriScholar
Group=VeriScholar
WorkingDirectory=/home/VeriScholar/Workspace/VeriScholar
EnvironmentFile=/home/VeriScholar/Workspace/VeriScholar/.env
Environment="APP_ENV=production" "PYTHONPATH=/home/VeriScholar/Workspace/VeriScholar/apps/api/src:/home/VeriScholar/Workspace/VeriScholar/packages/core/src"
ExecStart=/home/VeriScholar/Workspace/VeriScholar/.venv/bin/uvicorn api:app --host 127.0.0.1 --port 8000 --workers 2 --timeout-keep-alive 65
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

### Các Lệnh Quản Trị Thường Dùng:
```bash
# Kiểm tra trạng thái dịch vụ
sudo systemctl status verischolar-api

# Xem nhật ký hoạt động thời gian thực
sudo journalctl -u verischolar-api -f -n 100

# Khởi động lại dịch vụ
sudo systemctl restart verischolar-api

# Dừng dịch vụ khẩn cấp
sudo systemctl stop verischolar-api
```

---

## 4. CẤU HÌNH MÁY CHỦ NGINX CHO SẢN PHẨM (`/etc/nginx/sites-available/verischolar.conf`)

Tệp cấu hình Nginx tối ưu hóa bảo mật, SSL/TLS, bộ nhớ đệm và hỗ trợ Server-Sent Events (SSE):

```nginx
# Cấu hình máy chủ HTTPS (Port 443)
server {
    server_name verischolar.duckdns.org;

    root /var/www/verischolar/web;
    index index.html;
    client_max_body_size 50M;

    # Tiêu đề Bảo mật Chuẩn Quốc tế (Security Headers)
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Định tuyến ứng dụng trang đơn (SPA Fallback)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Bộ nhớ đệm tài nguyên tĩnh (Static Asset Caching)
    location ~* \.(?:css|js|mjs|svg|woff2?|ttf|eot|ico|png|jpg|jpeg|webp)$ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
        access_log off;
        try_files $uri =404;
    }

    # Luồng truyền phát thời gian thực không đệm (Unbuffered SSE Streaming)
    # Phục vụ tính năng Trợ lý Nghiên cứu Socratic Copilot
    location ~* ^/api/v1/sessions/.*/(chat|messages) {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 600s;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        chunked_transfer_encoding on;
    }

    # Chuyển tiếp các yêu cầu API thông thường
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Chuyển tiếp cổng kiểm tra sức khỏe và tài liệu API
    location ~* ^/(health|docs|redoc) {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Chứng chỉ bảo mật Let's Encrypt SSL/TLS
    listen [::]:443 ssl ipv6only=on;
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/verischolar.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/verischolar.duckdns.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

# Máy chủ HTTP (Port 80): Tự động chuyển hướng toàn bộ sang HTTPS
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name verischolar.duckdns.org _;

    if ($host = verischolar.duckdns.org) {
        return 301 https://$host$request_uri;
    }

    root /var/www/verischolar/web;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 5. HƯỚNG DẪN THỰC THI DÒNG LỆNH (OPERATIONAL RUNBOOK)

### 5.1. Triển Khai Toàn Diện Một Lệnh (Single-Command Production Deploy)
```bash
./scripts/deploy_production.sh
```

### 5.2. Chạy Mô Phỏng Thử Nghiệm (Dry-Run Mode)
```bash
./scripts/deploy_production.sh --dry-run
```

### 5.3. Chỉ Triển Khai Frontend (Bỏ Qua Nâng Cấp CSDL)
```bash
./scripts/deploy_production.sh --skip-migration
```

### 5.4. Xử Lý Sự Cố Khẩn Cấp (Emergency Disaster Recovery)
Nếu phát hiện lỗi nghiêm trọng sau khi triển khai, quản trị viên có thể kích hoạt rollback thủ công:
```bash
# 1. Quay về commit ổn định trước đó
git checkout <PREVIOUS_COMMIT_SHA>

# 2. Xây dựng lại giao diện Web và đồng bộ tài sản tĩnh
pnpm --dir apps/web build
sudo cp -r apps/web/dist/* /var/www/verischolar/web/

# 3. Khởi động lại dịch vụ backend và nạp lại web server
sudo systemctl restart verischolar-api
sudo systemctl reload nginx

# 4. Kiểm tra sức khỏe hệ thống
curl -f https://verischolar.duckdns.org/health
```

---

## 6. BẢNG CHECKLIST NGHIỆM THU CD (CD ACCEPTANCE CHECKLIST)

- [x] **Tự động hóa hoàn toàn:** Kịch bản triển khai không yêu cầu bất kỳ thao tác thủ công nào ngoài việc chạy script hoặc trigger workflow.
- [x] **Zero-Downtime Migration:** Toàn bộ lệnh DDL áp dụng `ADD COLUMN IF NOT EXISTS`, không khóa bảng hay ngắt kết nối CSDL.
- [x] **Bảo toàn kết nối SSE:** Cấu hình Nginx với `proxy_buffering off` cho các luồng chat Socratic Copilot.
- [x] **Bảo vệ Rollback:** Cơ chế bẫy tín hiệu lỗi (`trap rollback_on_failure EXIT`) đảm bảo hệ thống tự phục hồi khi có sự cố.
- [x] **Xác thực Đa Tầng:** Kiểm tra sức khỏe dịch vụ trên cả cổng nội bộ `127.0.0.1:8000` và tên miền công khai có mã hóa SSL.
- [x] **Tài liệu hóa hoàn chỉnh:** Cung cấp đầy đủ sơ đồ kiến trúc, giải thích thuật ngữ cho kỹ sư mới và hướng dẫn khắc phục sự cố.

# Hướng Dẫn Quản Trị Cơ Sở Dữ Liệu PostgreSQL & pgvector với Docker

Tài liệu này cung cấp hướng dẫn toàn diện về cách triển khai, cấu hình và quản trị cơ sở dữ liệu **PostgreSQL 18 tích hợp pgvector** và **Docker Model Runner (Local LLM Inference - Chạy mô hình ngôn ngữ lớn ngay trên máy cục bộ)** cho dự án **VeriScholar** theo chuẩn mực công nghiệp và mã nguồn mở.

---

## 0. BẢNG THUẬT NGỮ HẠ TẦNG & DOCKER CHO KỸ SƯ MỚI (FRESHER GLOSSARY)

| Thuật ngữ | Khái niệm tiếng Anh | Giải thích trực quan cho Fresher |
| :--- | :--- | :--- |
| **Docker Container** | Container Virtualization | Một "hộp đóng gói" nhẹ chứa mã nguồn ứng dụng cùng toàn bộ môi trường chạy cần thiết; giúp phần mềm chạy y hệt nhau trên máy Mac, Windows, Linux hay máy chủ đám mây. |
| **Docker Compose** | Multi-Container Orchestrator | Công cụ giúp bạn khai báo và khởi động nhiều container (ví dụ: PostgreSQL, Redis) cùng lúc chỉ bằng một tệp cấu hình `docker-compose.yml` duy nhất. |
| **Named Volume** | Persistent Named Storage Volume | Phân vùng ổ cứng có tên do Docker quản lý; đảm bảo khi bạn tắt container hoặc nâng cấp image thì dữ liệu trong cơ sở dữ liệu không bị mất. |
| **Loopback Interface** | Loopback Address (`127.0.0.1`) | Địa chỉ IP nội bộ của chính chiếc máy tính bạn đang ngồi; chỉ những tiến trình chạy trên máy bạn mới kết nối được, ngăn chặn người lạ cùng mạng WiFi/LAN xâm nhập vào database. |
| **Shared Memory (`shm_size`)** | POSIX Shared Memory | Vùng bộ nhớ RAM được chia sẻ giữa các luồng xử lý; PostgreSQL và pgvector rất cần vùng này để tăng tốc độ tính toán song song khi xây dựng chỉ mục tìm kiếm HNSW. |
| **pgvector** | Vector Similarity Search Extension | Tiện ích mở rộng biến PostgreSQL thành một cơ sở dữ liệu vector mạnh mẽ, cho phép lưu trữ và tìm kiếm các đoạn văn bản tương đồng về ngữ nghĩa. |
| **Docker Model Runner (DMR)** | Local AI Model Engine on Docker | Công cụ tích hợp sẵn trong Docker Desktop/Engine giúp bạn tải và chạy các mô hình AI mã nguồn mở (như `ai/smollm2`, `ai/llama3.2`) cục bộ qua cổng `12434` với chi phí 0 USD. |
| **Healthcheck** | Automated Health Monitoring Probe | Lệnh kiểm tra sức khỏe định kỳ (ví dụ: `pg_isready`); Docker sẽ tự động thăm dò để biết database đã thực sự sẵn sàng nhận kết nối hay chưa. |

---

## 1. TỔNG QUAN KIẾN TRÚC VÀ LỰA CHỌN CÔNG NGHỆ

### 1.1. Tại sao sử dụng `pgvector/pgvector:0.8.6-pg18`?
Dự án **VeriScholar** (Module 1 - Single Paper Deep Read & Visual Grounding) yêu cầu:
1. **Lưu trữ Quan hệ (Relational DB):** Quản lý thông tin bài báo (metadata), các đoạn văn bản cắt nhỏ (chunks), tài khoản người dùng với bảo đảm giao dịch ACID (Nguyên tử - Nhất quán - Cô lập - Bền vững).
2. **Tìm kiếm Vector Ngữ nghĩa (Vector DB):** Lưu trữ và truy vấn Dense Vector 1024 chiều (mô hình nhúng đa ngữ **BGE-M3**) với chỉ mục đồ thị HNSW (Hierarchical Navigable Small World) qua toán tử khoảng cách góc Cosine Distance (`<=>`).
3. **Tìm kiếm Từ khóa (Lexical Search):** Hỗ trợ tìm kiếm từ khóa chính xác (Sparse Search) bằng **PostgreSQL Full-Text Search (`tsvector` & `tsquery`)** để thực hiện tìm kiếm lai (Hybrid Search) kết hợp ngữ nghĩa và từ khóa.

> [!IMPORTANT]
> **Quy tắc Image:** 
> - Image chính thức được sử dụng là: **`pgvector/pgvector:0.8.6-pg18`** (dựa trên nền PostgreSQL 18 chính thức của Debian/Bookworm, tích hợp sẵn tiện ích mở rộng C-extension `vector` và tối ưu Asynchronous Direct I/O).
> - **Tuyệt đối không dùng tag `:latest`** để đảm bảo tính nhất quán (reproducibility) trên mọi máy lập trình viên và máy chủ CI/CD.

### 1.2. Sơ đồ Cấu trúc Thành phần Hạ tầng

```text
Host Machine (Máy tính phát triển của bạn / Máy chủ)
 │
 ├── Docker Model Runner (Port 12434) ── [Local LLM: llama.cpp / ai/smollm2 / ai/llama3.2]
 │    └── Endpoint: http://localhost:12434/engines/llama.cpp/v1
 │
 ├── Port: 127.0.0.1:5432 (Gia cố bảo mật: chỉ mở loopback cục bộ cho PostgreSQL)
 ├── Port: 127.0.0.1:6379 (Gia cố bảo mật: chỉ mở loopback cục bộ cho Redis 7)
 │
 └── Docker Network: verischolar-net (Mạng cầu nối ảo Bridge)
      │
      ├── Container: verischolar-postgres-dev (Image: pgvector/pgvector:0.8.6-pg18)
      │    ├── User: verischolar
      │    ├── Database: verischolar
      │    ├── Cấu hình Gia cố & Hiệu năng:
      │    │    ├── shm_size: 256mb (Bộ nhớ chia sẻ cho chỉ mục vector HNSW & đa luồng)
      │    │    └── security_opt: no-new-privileges:true (Chống leo thang đặc quyền chiếm root)
      │    ├── Extensions Khởi tạo tự động (/docker-entrypoint-initdb.d/init.sql):
      │    │    ├── vector (pgvector 0.8.0 - lưu và tìm kiếm vector)
      │    │    └── uuid-ossp (1.1 - tự động sinh khóa chính UUID)
      │    ├── extra_hosts:
      │    │    └── host.docker.internal:host-gateway (Giúp container gọi ngược về Docker Model Runner)
      │    └── Persistent Storage: verischolar-postgres-data ──> /var/lib/postgresql/data
      │
      └── Container: verischolar-redis-dev (Image: redis:7-alpine)
           ├── Port: 127.0.0.1:6379:6379
           ├── Vai trò: Redis Streams Durable Task Queue & Cửa sổ Idempotency 24h
           └── Persistent Storage: verischolar-redis-data ──> /data
```

---

## 2. QUY CHUẨN ĐẶT TÊN & THÔNG SỐ KẾT NỐI

### 2.1. Quy chuẩn Đặt tên Container theo Môi trường (Rules)

| Môi trường | Container Name | Mục đích sử dụng |
| :--- | :--- | :--- |
| **Development** | `verischolar-postgres-dev` | Lập trình viên chạy thử nghiệm tại máy cá nhân |
| **Staging** | `postgres-staging` | Môi trường kiểm thử tích hợp tự động (CI/CD / Staging server) |
| **Production** | `postgres-prod` | Môi trường vận hành thực tế cho người dùng cuối |

### 2.2. Thông số Cấu hình Mặc định (Local Development)

| Thông số | Giá trị Mặc định | Ghi chú an toàn & hiệu năng |
| :--- | :--- | :--- |
| **Host IP Binding** | `127.0.0.1` | **Security Hardening**: Chỉ mở cục bộ, chặn thiết bị khác trong mạng LAN truy cập |
| **Port** | `5432` | Cổng tiêu chuẩn mặc định của PostgreSQL |
| **Container Host** | `postgres` | Tên miền kết nối giữa các container trong cùng mạng Docker |
| **Username** | `verischolar` | Siêu người dùng quản trị ứng dụng |
| **Password** | `verischolar` | Mật khẩu tài khoản (có thể thay đổi linh hoạt qua file `.env`) |
| **Database** | `verischolar` | Cơ sở dữ liệu chính của dự án |
| **Volume** | `verischolar-postgres-data` | Lưu trữ dữ liệu lâu dài trên đĩa cứng (Persistent Storage) |
| **Shared Memory** | `256mb` | Cấp đủ bộ nhớ chia sẻ cho pgvector xây dựng chỉ mục HNSW nhanh chóng |
| **Security Option** | `no-new-privileges:true` | Ngăn chặn tiến trình bên trong container nâng quyền chiếm đoạt tài khoản root máy chủ |

### 2.3. Định dạng Connection Strings (Chuỗi kết nối URIs)

- **PostgreSQL Database (Async SQLAlchemy qua `asyncpg`):**
  - Kết nối từ máy tính phát triển: `postgresql+asyncpg://verischolar:verischolar@127.0.0.1:5432/verischolar`
  - Kết nối giữa các Container: `postgresql+asyncpg://verischolar:verischolar@postgres:5432/verischolar`

- **Redis 7 Task Broker & Cache (Redis Streams / ARQ / Idempotency):**
  - Kết nối từ máy tính phát triển: `redis://127.0.0.1:6379/0`
  - Kết nối giữa các Container: `redis://redis:6379/0`

---

## 3. KHỞI CHẠY NHANH VỚI DOCKER COMPOSE (KHUYẾN NGHỊ)

Sử dụng Docker Compose là phương pháp chuẩn mực, tự động hóa toàn bộ việc cấu hình biến môi trường, mount volume, tạo mạng, cấp phát `shm_size` và kích hoạt extension.

### Chi tiết tệp `docker-compose.yml` (Chuẩn Toàn Hệ Thống)
```yaml
services:
  postgres:
    image: pgvector/pgvector:0.8.6-pg18
    container_name: ${POSTGRES_CONTAINER_NAME:-verischolar-postgres-dev}
    restart: unless-stopped
    ports:
      - "127.0.0.1:${POSTGRES_PORT:-5432}:5432"
    shm_size: 256mb
    security_opt:
      - no-new-privileges:true
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-verischolar}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-verischolar}
      POSTGRES_DB: ${POSTGRES_DB:-verischolar}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - verischolar-postgres-data:/var/lib/postgresql/data
      - ./infra/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test:
        [
          "CMD-SHELL",
          "pg_isready -U ${POSTGRES_USER:-verischolar} -d ${POSTGRES_DB:-verischolar}"
        ]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 5s
    extra_hosts:
      - "host.docker.internal:host-gateway"
    networks:
      - verischolar-net

  redis:
    image: redis:7-alpine
    container_name: ${REDIS_CONTAINER_NAME:-verischolar-redis-dev}
    restart: unless-stopped
    ports:
      - "127.0.0.1:${REDIS_PORT:-6379}:6379"
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy noeviction
    volumes:
      - verischolar-redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - verischolar-net

volumes:
  verischolar-postgres-data:
    name: verischolar-postgres-data
  verischolar-redis-data:
    name: verischolar-redis-data

networks:
  verischolar-net:
    name: verischolar-net
    driver: bridge
```

### Bước 1: Chuẩn bị biến môi trường (Tùy chọn)
Tạo file `.env` tại thư mục gốc của dự án (hoặc sử dụng giá trị mặc định có sẵn):
```bash
cp .env.example .env
```

### Bước 2: Khởi chạy Database
Tại thư mục gốc dự án, thực thi lệnh:
```bash
docker compose up -d
```

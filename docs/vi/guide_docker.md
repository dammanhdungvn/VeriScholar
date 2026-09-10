# Hướng Dẫn Quản Trị Cơ Sở Dữ Liệu PostgreSQL & pgvector với Docker

Tài liệu này cung cấp hướng dẫn toàn diện về cách triển khai, cấu hình và quản trị cơ sở dữ liệu **PostgreSQL 16 tích hợp pgvector** và **Docker Model Runner (Local LLM Inference)** cho dự án **VeriScholar** theo chuẩn mực công nghiệp và mã nguồn mở.

---

## 1. TỔNG QUAN KIẾN TRÚC VÀ LỰA CHỌN CÔNG NGHỆ

### 1.1. Tại sao sử dụng `pgvector/pgvector:0.8.0-pg16`?
Dự án **VeriScholar** (Module 1 - Single Paper Deep Read & Visual Grounding) yêu cầu:
1. **Lưu trữ Quan hệ (Relational DB):** Quản lý metadata bài báo, chunks, người dùng với bảo đảm giao dịch ACID.
2. **Tìm kiếm Vector Ngữ nghĩa (Vector DB):** Lưu trữ và truy vấn Dense Vector 1024 chiều (mô hình **BGE-M3**) với chỉ mục HNSW qua toán tử Cosine Distance (`<=>`).
3. **Tìm kiếm Từ khóa (Lexical Search):** Hỗ trợ Sparse Search bằng **PostgreSQL Full-Text Search (`tsvector` & `tsquery`)** để thực hiện Hybrid Search.

> [!IMPORTANT]
> **Quy tắc Image:** 
> - Image chính thức được sử dụng là: **`pgvector/pgvector:0.8.0-pg16`** (dựa trên nền PostgreSQL 16 chính thức của Debian, tích hợp sẵn C-extension `vector`).
> - **Tuyệt đối không dùng tag `:latest`** để đảm bảo tính nhất quán (reproducibility) trên mọi máy lập trình viên và máy chủ CI/CD.

### 1.2. Sơ đồ Cấu trúc Thành phần Hạ tầng

```text
Host Machine (Local Development / Server)
 │
 ├── Docker Model Runner (Port 12434) ── [Local LLM: llama.cpp / ai/smollm2 / ai/llama3.2]
 │    └── Endpoint: http://localhost:12434/engines/llama.cpp/v1
 │
 ├── Port: 127.0.0.1:5432 (hoặc 0.0.0.0:5432)
 │
 └── Docker Network: verischolar-net (Bridge)
      │
      └── Container: verischolar-postgres-dev (Image: pgvector/pgvector:0.8.0-pg16)
           │
           ├── User: verischolar
           ├── Database: verischolar
           │
           ├── Extensions Khởi tạo tự động (/docker-entrypoint-initdb.d/init.sql):
           │    ├── vector (pgvector 0.8.0)
           │    └── uuid-ossp (1.1)
           │
           ├── extra_hosts:
           │    └── host.docker.internal:host-gateway (Giao tiếp với Docker Model Runner)
           │
           └── Persistent Storage (Named Volume):
                └── verischolar-postgres-data ──> /var/lib/postgresql/data
```

---

## 2. QUY CHUẨN ĐẶT TÊN & THÔNG SỐ KẾT NỐI

### 2.1. Quy chuẩn Đặt tên Container theo Môi trường (Rules)

| Môi trường | Container Name | Mục đích sử dụng |
| :--- | :--- | :--- |
| **Development** | `verischolar-postgres-dev` | Lập trình viên chạy thử nghiệm tại máy cá nhân |
| **Staging** | `postgres-staging` | Môi trường kiểm thử tích hợp (CI/CD / Staging server) |
| **Production** | `postgres-prod` | Môi trường vận hành thực tế cho người dùng cuối |

### 2.2. Thông số Cấu hình Mặc định (Local Development)

| Thông số | Giá trị Mặc định | Ghi chú |
| :--- | :--- | :--- |
| **Host** | `localhost` (hoặc `127.0.0.1`) | Kết nối từ ứng dụng máy chủ host |
| **Container Host** | `postgres` | Kết nối giữa các container trong cùng mạng Docker |
| **Port** | `5432` | Cổng tiêu chuẩn của PostgreSQL |
| **Username** | `verischolar` | Siêu người dùng quản trị ứng dụng |
| **Password** | `verischolar` | Mật khẩu tài khoản (override qua file `.env`) |
| **Database** | `verischolar` | Database chính của dự án |
| **Volume** | `verischolar-postgres-data` | Lưu trữ dữ liệu lâu dài (Persistent) |

### 2.3. Định dạng Connection Strings (URIs)

- **Kết nối từ máy tính phát triển (Python/FastAPI qua `asyncpg`):**
  ```text
  postgresql+asyncpg://verischolar:verischolar@localhost:5432/verischolar
  ```
- **Kết nối giữa các Docker Container (Container-to-Container):**
  ```text
  postgresql+asyncpg://verischolar:verischolar@postgres:5432/verischolar
  ```

---

## 3. KHỞI CHẠY NHANH VỚI DOCKER COMPOSE (KHUYẾN NGHỊ)

Sử dụng Docker Compose là phương pháp chuẩn mực, tự động hóa toàn bộ việc cấu hình biến môi trường, mount volume, tạo mạng và kích hoạt extension.

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

### Bước 3: Kiểm tra trạng thái Container
```bash
docker compose ps
```
*Kết quả kỳ vọng:* Container `verischolar-postgres-dev` ở trạng thái `Up ... (healthy)`.

### Bước 4: Xem Logs Container
```bash
docker logs -f verischolar-postgres-dev
```

### Bước 5: Dừng Container (Dữ liệu vẫn được bảo toàn)
```bash
docker compose down
```

> [!WARNING]
> Nếu bạn chạy `docker compose down -v` (kèm cờ `-v`), Docker sẽ **xóa sạch volume `verischolar-postgres-data`** và làm mất toàn bộ dữ liệu PDF đã bóc tách cũng như các bảng trong database!

---

## 4. KHỞI CHẠY BẰNG LỆNH DOCKER THUẦN (STANDALONE CLI)

Nếu bạn không muốn sử dụng Docker Compose, bạn có thể khởi chạy thủ công theo các bước sau:

### Bước 1: Tạo Volume lưu trữ dữ liệu bền vững
```bash
docker volume create verischolar-postgres-data
```

### Bước 2: Khởi chạy Container
```bash
docker run -d \
  --name verischolar-postgres-dev \
  --restart unless-stopped \
  -e POSTGRES_USER=verischolar \
  -e POSTGRES_PASSWORD=verischolar \
  -e POSTGRES_DB=verischolar \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -p 5432:5432 \
  -v verischolar-postgres-data:/var/lib/postgresql/data \
  -v $(pwd)/infra/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro \
  pgvector/pgvector:0.8.0-pg16
```

---

## 5. KIỂM THỬ VÀ XÁC THỰC CƠ SỞ DỮ LIỆU (VERIFICATION)

Sau khi khởi chạy container, bạn hãy chạy các lệnh sau để đảm bảo hệ thống đã sẵn sàng phục vụ cho bài toán Advanced RAG:

### 5.1. Kiểm tra Extension `vector` và `uuid-ossp`
```bash
docker exec -i verischolar-postgres-dev psql -U verischolar -d verischolar -c "
SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp');
"
```
*Kỳ vọng:*
```text
  extname  | extversion 
-----------+------------
 vector    | 0.8.0
 uuid-ossp | 1.1
(2 rows)
```

### 5.2. Kiểm tra Thao tác Vector Cosine Distance (`<=>`)
```bash
docker exec -i verischolar-postgres-dev psql -U verischolar -d verischolar -c "
CREATE TEMPORARY TABLE test_vec (id serial, emb vector(3));
INSERT INTO test_vec (emb) VALUES ('[1,2,3]'), ('[4,5,6]');
SELECT id, emb <=> '[1,2,3]' AS cosine_distance FROM test_vec ORDER BY cosine_distance;
"
```
*Kỳ vọng:* Trả về khoảng cách Cosine Distance, trong đó vector `[1,2,3]` có khoảng cách bằng `0`.

### 5.3. Kiểm tra Full-Text Search (`tsvector`)
```bash
docker exec -i verischolar-postgres-dev psql -U verischolar -d verischolar -c "
SELECT to_tsvector('english', 'Academic paper citation grounding') @@ to_tsquery('english', 'citation & grounding');
"
```
*Kỳ vọng:* Trả về giá trị boolean `t` (true).

---

## 6. QUẢN LÝ DỮ LIỆU BỀN VỮNG (PERSISTENCE MANAGEMENT)

### 6.1. Nguyên lý Bền vững của Docker Named Volume
Khi sử dụng Named Volume `verischolar-postgres-data`, toàn bộ dữ liệu vật lý của PostgreSQL được lưu trữ tại `/var/lib/docker/volumes/verischolar-postgres-data/_data` trên máy chủ host. Việc `docker stop`, `docker rm` hay `docker compose down` chỉ hủy tiến trình container, **không làm mất dữ liệu**.

### 6.2. Kiểm tra danh sách Volume trên máy
```bash
docker volume ls --filter name=verischolar
```

### 6.3. Sao lưu Dữ liệu (Backup via pg_dump)
```bash
docker exec -t verischolar-postgres-dev pg_dump -U verischolar -d verischolar -F c -b -v -f /tmp/backup.dump
docker cp verischolar-postgres-dev:/tmp/backup.dump ./verischolar_backup_$(date +%Y%m%d).dump
```

### 6.4. Phục hồi Dữ liệu (Restore via pg_restore)
```bash
docker cp ./verischolar_backup.dump verischolar-postgres-dev:/tmp/backup.dump
docker exec -t verischolar-postgres-dev pg_restore -U verischolar -d verischolar -v /tmp/backup.dump
```

---

## 7. CÁC LỖI THƯỜNG GẶP & CÁCH XỬ LÝ (TROUBLESHOOTING)

### 1. Lỗi: "Address already in use: port 5432"
* **Nguyên nhân:** Máy host đã cài PostgreSQL native hoặc có một container khác đang chiếm cổng 5432.
* **Cách khắc phục:**
  - Kiểm tra tiến trình đang chiếm cổng: `sudo lsof -i :5432` hoặc `sudo netstat -tulpn | grep 5432`.
  - Tắt dịch vụ postgres nội bộ nếu có: `sudo systemctl stop postgresql`.
  - Hoặc đổi cổng host trong `.env`: `POSTGRES_PORT=5433` (lúc này kết nối qua `localhost:5433`).

### 2. Lỗi: "Password authentication failed for user 'verischolar'"
* **Nguyên nhân:** Volume cũ đã được khởi tạo trước đó với mật khẩu khác. Khi chạy lại container, PostgreSQL phát hiện thư mục dữ liệu đã tồn tại nên **bỏ qua việc đọc biến `POSTGRES_PASSWORD` mới**.
* **Cách khắc phục:**
  - Xóa sạch volume cũ để khởi tạo lại từ đầu: `docker compose down -v && docker compose up -d`.
  - Hoặc kết nối vào container và đổi mật khẩu: `docker exec -it verischolar-postgres-dev psql -U verischolar -c "ALTER USER verischolar WITH PASSWORD 'verischolar';"`

### 3. Lỗi: "Extension 'vector' does not exist"
* **Nguyên nhân:** Bạn đang sử dụng image `postgres:16` hoặc `postgres:18` thông thường thay vì image có sẵn pgvector.
* **Cách khắc phục:** Đảm bảo `image` trong `docker-compose.yml` luôn là `pgvector/pgvector:0.8.0-pg16`.

---

## 8. TÍCH HỢP DOCKER MODEL RUNNER (LOCAL LLM INFERENCE)

Theo chuẩn kỹ thuật mới của Docker và skill [docker-model-runner](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/skills/docker-model-runner/SKILL.md), VeriScholar hỗ trợ thực thi LLM cục bộ thông qua **Docker Model Runner (DMR)**.

### 8.1. Kiểm tra trạng thái Docker Model Runner
```bash
docker model version
docker model status
```
*Kết quả:* Docker Model Runner chạy trên cổng `12434` với backend `llama.cpp`.

### 8.2. Kéo (Pull) và Chạy Mô Hình Cục Bộ
```bash
# Kéo mô hình siêu nhẹ cho môi trường development
docker model pull ai/smollm2

# Hoặc kéo mô hình mạnh mẽ hơn cho RAG
docker model pull ai/llama3.2
```

### 8.3. OpenAI-Compatible API Endpoint
Docker Model Runner tự động mở API chuẩn tương thích OpenAI tại cổng `12434`:
- **URL Host:** `http://localhost:12434/engines/llama.cpp/v1`
- **URL trong Container (Docker Compose qua `extra_hosts`):** `http://host.docker.internal:12434/engines/llama.cpp/v1`
- **API Key:** `not-needed`

### 8.4. Kiểm thử qua Curl
```bash
curl http://localhost:12434/engines/llama.cpp/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai/smollm2",
    "messages": [
      {"role": "user", "content": "Hello, VeriScholar!"}
    ]
  }'
```

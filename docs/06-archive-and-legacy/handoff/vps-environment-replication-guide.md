# Hướng Dẫn Tái Tạo Môi Trường Coding & Runtime Trên VPS
## VeriScholar VPS Infrastructure & Environment Setup Guide

> **Phiên bản:** 1.0  
> **Cập nhật:** 2026-10-15  
> **Phạm vi:** Dành cho kỹ sư hệ thống hoặc AI agent tiếp quản dự án trên máy chủ VPS mới.

---

## 1. YÊU CẦU HỆ ĐIỀU HÀNH & CÔNG CỤ NỀN TẢNG (PREREQUISITES)

### 1.1. Hệ Điều Hành & Cấu Hình Khuyến Nghị
- **Hệ điều hành:** Linux Ubuntu 22.04 LTS hoặc 24.04 LTS (x86_64 / amd64).
- **Phần cứng tối thiểu:** 4 vCPU, 8GB RAM, 40GB SSD (để phục vụ biên dịch TypeScript, chạy test suite, và nạp mô hình NLI/Embeddings).
- **Phần cứng khuyến nghị:** 8 vCPU, 16GB RAM, 80GB SSD.

### 1.2. Danh Sách Toolchain & Phiên Bản Bắt Buộc
| Phần mềm | Phiên bản khuyến nghị | Lệnh cài đặt / Quản lý |
| :--- | :--- | :--- |
| **Python** | 3.12.x | Quản lý qua `uv` (Astral) |
| **uv** | $\ge 0.4.0$ | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Node.js** | 20.x LTS hoặc 22.x LTS | `nvm install 20 && nvm use 20` |
| **pnpm** | $\ge 9.0.0$ | `npm install -g pnpm` |
| **Docker Engine** | $\ge 26.0.0$ | `apt-get install docker-ce docker-ce-cli containerd.io` |
| **Tectonic (LaTeX)**| $\ge 0.15.0$ | `curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net \| sh` hoặc binary tải từ GitHub Releases |
| **Git** | $\ge 2.34.0$ | `sudo apt install git` |

---

## 2. THIẾT LẬP DỊCH VỤ & HẠ TẦNG

### 2.1. Cấu Hình Cơ Sở Dữ Liệu PostgreSQL & pgvector (Nếu Chạy Production/Staging)
Dự án hỗ trợ 2 chế độ cơ sở dữ liệu:
1. **Local Development / Quickstart:** SQLite + aiosqlite (tự động tạo tại `storage/verischolar.db`).
2. **Hybrid Search RAG (Khuyến nghị cho VPS):** PostgreSQL 16 kèm extension `pgvector`.
   ```bash
   # Chạy qua Docker container
   docker run -d \
     --name verischolar-postgres \
     -e POSTGRES_DB=verischolar \
     -e POSTGRES_USER=verischolar_user \
     -e POSTGRES_PASSWORD=your_secure_password_here \
     -p 5432:5432 \
     pgvector/pgvector:pg16
   ```

### 2.2. Kích Hoạt Docker Không Đặc Quyền Cho Compiler Sandbox (PRD §3.2)
Để vượt qua rào cản `BLOCKED_INFRASTRUCTURE` từng xuất hiện trên máy cục bộ, VPS cần bảo đảm người dùng chạy dịch vụ có quyền kích hoạt container cô lập:
```bash
# 1. Thêm user thực thi vào nhóm docker
sudo usermod -aG docker $USER
newgrp docker

# 2. Kiểm tra cgroups v2 và unprivileged user namespaces
cat /proc/sys/kernel/apparmor_restrict_unprivileged_userns
# Nếu giá trị là 1 trên Ubuntu 24.04, cấu hình sysctl nếu được phép:
# sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0

# 3. Xác minh quyền socket docker
docker ps
```
> [!IMPORTANT]
> **Nguyên tắc An Toàn:** Nếu VPS chưa cấp quyền Docker, `SandboxRuntimeCapabilityProbe` của hệ thống sẽ tự động kích hoạt chế độ **Fail-Closed** (`BLOCKED_INFRASTRUCTURE`) để ngăn ngừa việc thực thi mã LaTeX không tin cậy trực tiếp trên host.

### 2.3. Cài Đặt Tectonic LaTeX Compiler Binary
Engine biên dịch LaTeX chính của Module 2 là Tectonic:
```bash
# Tải binary Tectonic độc lập đưa vào PATH
curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh
sudo mv tectonic /usr/local/bin/

# Kiểm tra phiên bản
tectonic --version
```

---

## 3. CẤU HÌNH BIẾN MÔI TRƯỜNG (.env) AN TOÀN

Tạo tệp `.env` tại thư mục gốc của dự án dựa trên `.env.example`. **Tuyệt đối không commit tệp `.env` chứa mật khẩu thật vào Git**.

### Mẫu Giá Trị Cấu Hình An Toàn:
```bash
# Môi trường
ENVIRONMENT=development
LOG_LEVEL=INFO

# Cấu hình Database
# Chế độ SQLite:
DATABASE_URL=sqlite+aiosqlite:///storage/verischolar.db
# Chế độ PostgreSQL (nếu dùng):
# DATABASE_URL=postgresql+asyncpg://verischolar_user:your_password@localhost:5432/verischolar

# Bảo mật JWT (Tạo chuỗi ngẫu nhiên 32+ ký tự: openssl rand -hex 32)
JWT_SECRET_KEY=change_this_to_a_random_secure_32_char_hex_secret_key_on_vps
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_SECONDS=3600
REFRESH_TOKEN_EXPIRE_SECONDS=604800

# AI Models & Observability (Điền API Key thật trên VPS nếu cần chạy LLM)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com

# Cấu hình Sandbox Compiler Module 2
LATEX_COMPILER_SANDBOX_TIMEOUT_SECONDS=15
LATEX_MAX_MEMORY_MB=512
LATEX_MAX_CPU_QUOTA=1.0
REQUIRE_HARDENED_SANDBOX=false  # Đổi thành true khi Docker container isolation đã sẵn sàng
```

---

## 4. QUẢN LÝ MÔ HÌNH NLI & TRỌNG SỐ NGOẠI TUYẾN (DEFECT-02 RESOLUTION)

Để giải quyết **DEFECT-02** và cho phép suy diễn NLI ngoại tuyến không cần internet:
1. **Model ID:** `cross-encoder/nli-deberta-v3-small` (Apache 2.0).
2. **Mô hình đa ngữ (tiếng Việt):** `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` (MIT).
3. **Thư mục lưu trữ:** Tạo thư mục `models/nli/` trên VPS.
4. **Cách tải weights trước khi chạy offline:**
   ```bash
   # Sử dụng script huggingface-cli tải trọng số
   uv run python -c "
   from transformers import AutoTokenizer, AutoModelForSequenceClassification
   model_name = 'cross-encoder/nli-deberta-v3-small'
   tokenizer = AutoTokenizer.from_pretrained(model_name)
   model = AutoModelForSequenceClassification.from_pretrained(model_name)
   tokenizer.save_pretrained('./models/nli/deberta-v3-small')
   model.save_pretrained('./models/nli/deberta-v3-small')
   print('NLI Model weights packaged successfully.')
   "
   ```

---

## 5. DANH MỤC DỮ LIỆU CẦN CHUYỂN RIÊNG NGOÀI GIT (DATA TRANSFER PLAN)

Các dữ liệu sau bị chặn bởi `.gitignore` để bảo vệ bảo mật và tránh làm phình Git repository, cần được đóng gói và chuyển riêng sang VPS qua `rsync` hoặc `scp`:

| Loại dữ liệu | Đường dẫn nguồn | Mục đích | Phương án chuyển giao |
| :--- | :--- | :--- | :--- |
| **Cơ sở dữ liệu cục bộ** | `storage/verischolar.db` | Lưu trữ các documents, sessions, drafts đang test | Nén `tar -czvf db_backup.tar.gz storage/` kèm checksum |
| **Tài liệu PDF Corpus** | `data/papers/*.pdf` | 3 bài báo mẫu (Attention Is All You Need, LoRA, RAG) | Nén `tar -czvf papers_corpus.tar.gz data/papers/` |
| **Mô hình Cache HuggingFace** | `~/.cache/huggingface/` | Tiết kiệm băng thông tải lại weights | Chuyển qua rsync nếu VPS có băng thông hạn chế |

### Quy Trình Tạo Gói & Kiểm Tra Checksum:
```bash
# Trên máy nguồn:
tar -czvf verischolar_runtime_data.tar.gz storage/ data/papers/
sha256sum verischolar_runtime_data.tar.gz > verischolar_runtime_data.tar.gz.sha256

# Chuyển sang VPS qua SCP:
# scp verischolar_runtime_data.tar.gz* user@vps_ip:/path/to/VeriScholar/

# Trên VPS giải nén & kiểm tra:
# sha256sum -c verischolar_runtime_data.tar.gz.sha256
# tar -xzvf verischolar_runtime_data.tar.gz
```

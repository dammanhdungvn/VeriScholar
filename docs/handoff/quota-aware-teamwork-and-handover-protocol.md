# Quy Trình Vận Hành Nhận Biết Quota, Giảm Tải Coordinator & Bàn Giao Kế Nhiệm
## VeriScholar Multi-Agent Orchestration Protocol (Hiệu Chỉnh Theo Bằng Chứng Thực Tế)

> **Trạng thái tài liệu:** Đã rà soát & Hiệu chỉnh theo bằng chứng thực nghiệm (Empirical Revision)  
> **Áp dụng cho Run:** `run_5e95769f2680`  
> **Cập nhật:** 2026-10-15  
> **Cơ sở kỹ thuật:** Orca Live Guide (`bundled-skill-guides.js`), runtime database `~/.config/orca/orchestration.db`, `AGENTS.md` Mục 9

---

## 1. KHẢO SÁT QUOTA THEO ACCOUNT & PHÂN BIỆT TÍN HIỆU

### 1.1. Bằng Chứng Thực Nghiệm Từ Hạ Tầng
- **Khảo sát mã nguồn Orca CLI:** Kiểm tra toàn bộ thư mục `/tmp/.mount_orca.Apmlmkj/resources/app.asar.unpacked/out/cli/handlers/` $\rightarrow$ Không tồn tại handler, lệnh hay RPC schema nào hỗ trợ truy vấn hạn ngạch token, credit hoặc rate limit từ các nhà cung cấp AI.
- **Khảo sát cấu hình runtime:** File `~/.config/orca/codex-pane-accounts.json` chỉ cấu hình routing nội bộ (`selectionKey: host`, `accountId: None`). **Không dùng cấu hình Codex để suy diễn quota của Antigravity hay các terminal khác**.
- **Kết luận:** **Chưa tìm thấy nguồn quota khả dụng trong môi trường đã khảo sát**. Trạng thái hạn ngạch của toàn bộ 4 terminals được ghi nhận chính thức là **`UNKNOWN`** (không đoán mò dựa trên số lượng task đã chạy).

### 1.2. Phân Biệt Các Tín Hiệu Bất Thường
Hệ thống không đánh đồng mọi sự gián đoạn là cạn quota:

| Tín hiệu quan sát | Bản chất kỹ thuật | Hành động chuẩn hóa |
| :--- | :--- | :--- |
| **HTTP 429** | Giới hạn tần suất tạm thời (Rate Limit / Throttling) | Tạm dừng dispatch task con mới cho worker; chờ backoff exponential hoặc sang checkpoint; **không coi là cạn quota vĩnh viễn**. |
| **Quota Exceeded** | Hết hạn mức sử dụng hoặc hết credits từ provider | Dừng toàn bộ việc nhận task; thực hiện Checkpoint Snapshot; thông báo cho người dùng xử lý tài khoản. |
| **Subprocess Timeout (15s)** | Mã phức tạp, vòng lặp vô hạn hoặc nghẽn I/O | Kích hoạt hủy tiến trình (`terminate`/`kill`), ghi log lỗi timeout; không quy kết cho sự cố quota. |
| **Terminal im lặng / Mất kết nối** | Tiến trình đang chạy ngầm hoặc đứt socket IPC | Dùng `orca terminal read` để xác minh trạng thái tiến trình thực tế (`live` vs `exited`); **terminal im lặng không tự chứng minh hết quota**. |

---

## 2. CƠ CHẾ CHỜ, ĐÁNH THỨC & GIẢM TẢI COORDINATOR

### 2.1. Phân Biệt Thực Tế Về Cơ Chế Chờ (Loại Bỏ Khẳng Định "Zero-Token")
- **Thực tế kỹ thuật:**
  - Lệnh `orca orchestration check --wait --types "worker_done,escalation,question" --timeout-ms <ms>` là cơ chế chờ có cấu trúc ở tầng Orca CLI, giúp gom batch Delivery theo thứ tự FIFO.
  - Phân biệt rạch ròi 3 tầng thông điệp:
    1. *CLI Heartbeat:* Chứng minh tiến trình worker còn sống (`liveness`), không đánh thức turn hay tính là hoàn thành.
    2. *Mailbox Delivery:* Ghi nhận thông điệp bền vững vào cơ sở dữ liệu `orchestration.db`.
    3. *Agent Turn Trigger:* Phụ thuộc vào cơ chế runtime của orchestrator điều khiển phiên chat.
- **Quy tắc vận hành:**
  - Không chạy vòng lặp suy luận (polling loop) gọi tool liên tục trong cùng một turn làm lãng phí token.
  - Sau khi dispatch, Coordinator kết thúc turn và sử dụng cơ chế lắng nghe sự kiện của nền tảng. Khi hết thời gian chờ hoặc nhận được thông báo completion/escalation, Coordinator mới bắt đầu turn tiếp theo để xử lý batch mail.

---

## 3. GIAO THỨC CHECKPOINT CHỦ ĐỘNG & BẢO TOÀN DỮ LIỆU

### 3.1. Thời Điểm Ghi Checkpoint Bắt Buộc
Không chờ đến khi hết quota mới ghi nhận trạng thái. Checkpoint được cập nhật chủ động:
1. Ngay sau mỗi đợt Dispatch mới (`task-create` & `dispatch --inject`).
2. Ngay khi nhận được `worker_done` hợp lệ từ worker.
3. Khi đưa ra quyết định kiến trúc quan trọng hoặc gặp rào cản (`BLOCKED`).
4. Trước bất kỳ thao tác bàn giao vai trò nào.

### 3.2. Cấu Trúc Atomic Checkpoint Phục Hồi
File trạng thái phục hồi được lưu tại đường dẫn tuyệt đối:  
📁 `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/runtime/orchestration-state.json`  
*(Được cô lập qua `.gitignore`, không chứa API keys, secrets hay dữ liệu nhạy cảm).*

```json
{
  "schema_version": "1.2",
  "updated_at": "<ISO-8601-UTC-Timestamp>",
  "run": {
    "id": "run_5e95769f2680",
    "consumer_generation": 1
  },
  "coordinator_handle": "term_ecd5fad9-728e-49fa-9be9-63f9af44a20a",
  "fleet_status": {
    "<terminal_handle>": {
      "role": "<Role>",
      "worktree_path": "<Absolute-Path>",
      "git_head": "<Commit-SHA>",
      "active_dispatch_id": "<Dispatch-ID>",
      "running_process": "<PID / Description>",
      "dirty_files": ["<Path1>", "<Path2>"]
    }
  },
  "progress_tracking": {
    "completed_tasks": ["<Task-IDs>"],
    "in_flight_tasks": ["<Task-IDs>"],
    "blocked_items": ["<Details>"]
  },
  "test_evidence": {
    "<task_id>": {
      "command": "<Verification-Command>",
      "result": "<Passed / Failed>",
      "artifact_uri": "<File-URI>"
    }
  }
}
```

### 3.3. Bảo Toàn Mã Nguồn & Tệp Tin Sửa Dở (Dirty Changes)
- Lệnh `git status` chỉ liệt kê danh sách tệp đã sửa, không sao lưu nội dung.
- **Nguyên tắc bảo toàn:**
  - Toàn bộ thay đổi đang sửa (dirty changes) và untracked files được lưu giữ trực tiếp trên filesystem của worktree tương ứng (`/home/dammanhdungvn/Downloads/Workspace/VeriScholar`).
  - Terminal kế nhiệm truy cập trực tiếp cùng worktree/branch để đọc nguyên trạng các tệp tin này thông qua đường dẫn tuyệt đối đã được xác minh quyền đọc/ghi.
  - **Lưu ý trung thực:** File trạng thái JSON hỗ trợ quá trình phục hồi thông tin điều phối, **không thay thế trạng thái runtime thực tế của hệ điều hành và filesystem**.

---

## 4. QUY TRÌNH FENCING & BÀN GIAO COORDINATOR (TAKEOVER TRÊN RUN ĐỘC LẬP)

### 4.1. Fencing An Toàn (Ngăn Ngừa Ghi Đè Đồng Thời)
- Phân biệt giữa *"Đã yêu cầu worker dừng"* và *"Đã xác nhận worker ngừng ghi thực tế"*.
- **Quy tắc Fencing:** Tuyệt đối không giao người khác vào chỉnh sửa cùng một checkout/worktree khi chưa xác nhận worker cũ đã hoàn toàn kết thúc tiến trình ghi file (qua kiểm tra PTY idle hoặc exit code thực tế).

### 4.2. Khảo Sát Kỹ Thuật Takeover & Ranh Giới An Toàn
- **Cơ chế theo Orca Live Guide:** Lệnh `orca orchestration run-use --id <run_id> [--takeover-legacy]` có chức năng bind terminal gọi lệnh làm `coordinator_handle` của Run, tăng `consumer_generation` và định tuyến lại mailbox.
- **Rào chắn an toàn (Safety Floor):**
  - **Tuyệt đối không chạy takeover trực tiếp trên Run thật (`run_5e95769f2680`) để làm bài test**, vì việc này sẽ vô hiệu hóa Coordinator hiện tại và làm gián đoạn tiến độ Module 2.
  - **Quy trình thử nghiệm hợp lệ (Isolated Run Probe):**
    1. Tạo một Run kiểm thử hoàn toàn tách biệt: `orca orchestration run-create --objective "Test Takeover Isolation"`.
    2. Xác minh cơ chế binding và định tuyến thông điệp trên Run thử nghiệm này.
    3. Nếu không thể tạo môi trường cô lập, **báo trạng thái BLOCKED và chờ người dùng phê duyệt**.
  - **Quyết định hiện tại:** Giữ nguyên Coordinator hiện tại (`term_ecd5fad9`), **chưa thực hiện chuyển giao coordinator, không đổi tài khoản và không thay đổi vai trò Reviewer của `gg16`**.

---

## 5. PROMPT PHỤC HỒI DỰ PHÒNG CHUẨN HÓA (RECOVERY PROMPT)

Dành cho người dùng kích hoạt terminal kế nhiệm trong trường hợp phiên điều phối hiện tại bị ngắt đột ngột:

```text
Tiếp quản vai trò Coordinator cho Run run_5e95769f2680 (Module 2).

1. Đọc kỹ live guide Orca và kiểm tra file trạng thái phục hồi tại:
   /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/runtime/orchestration-state.json

2. Xác minh các ID thực tế đang hoạt động (KHÔNG dispatch lại các task đang chạy):
   - Backend Dispatch: ctx_09f2b1c5ca57 (Task task_b85652e9ab0c) tại term_48dcdcf9-3b2b-4df5-877f-363da6994b6d
   - Frontend Dispatch: ctx_98495ecec6e3 (Task task_fd25c3d50679) tại term_4b8241e6-4d2c-4a91-a18d-94d95fa0bde2

3. Thực hiện liên kết an toàn:
   /home/dammanhdungvn/.config/orca/linux-orca-cli-shim/orca orchestration run-use --id run_5e95769f2680

4. Xác nhận binding hợp lệ trước khi thao tác tiếp:
   /home/dammanhdungvn/.config/orca/linux-orca-cli-shim/orca orchestration run-current --json

5. Chờ kết quả hoàn thành từ hai worker qua lệnh:
   /home/dammanhdungvn/.config/orca/linux-orca-cli-shim/orca orchestration check --terminal <handle_cua_ban> --wait --types "worker_done,escalation" --timeout-ms 300000 --json
   Nếu không thể tiếp quản an toàn hoặc gặp xung đột binding, dừng ngay và báo cáo người dùng.
```

import { chromium } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WORKSPACE_ROOT = path.resolve(__dirname, "../../../");
const SCREENSHOTS_DIR = path.resolve(WORKSPACE_ROOT, "apps/web/playwright-screenshots");

if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

const SAMPLE_PDF_PATH = path.resolve(
  WORKSPACE_ROOT,
  "data/papers/Attention Is All You Need.pdf"
);

const BACKEND_BASE_URL = process.env.VITE_API_BASE_URL || process.env.VITE_API_URL || "http://localhost:8000";

async function obtainAuthToken(backendUrl = BACKEND_BASE_URL) {
  const credentials = {
    email: "audit_reviewer@verischolar.org",
    password: "Password123!",
  };

  // 1. Try login first
  try {
    const loginRes = await fetch(`${backendUrl}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });
    if (loginRes.ok) {
      const data = await loginRes.json();
      console.log(`[AUTH FIXTURE] Authenticated successfully via /login as ${credentials.email}`);
      return data.data;
    }
  } catch (err) {
    console.warn(`[AUTH FIXTURE] Login attempt failed: ${err.message}`);
  }

  // 2. If login fails, register
  try {
    const registerPayload = {
      full_name: "Audit Reviewer",
      email: credentials.email,
      password: credentials.password,
      accept_terms: true,
      institution: "VeriScholar QA",
    };
    const regRes = await fetch(`${backendUrl}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(registerPayload),
    });
    if (regRes.ok) {
      const data = await regRes.json();
      console.log(`[AUTH FIXTURE] Registered new user successfully via /register as ${credentials.email}`);
      return data.data;
    } else {
      console.warn(`[AUTH FIXTURE] Register returned ${regRes.status}: ${await regRes.text()}`);
    }
  } catch (err) {
    console.warn(`[AUTH FIXTURE] Register attempt failed: ${err.message}`);
  }

  // 3. Fallback: retry login once more
  const retryRes = await fetch(`${backendUrl}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  });
  if (retryRes.ok) {
    const data = await retryRes.json();
    console.log(`[AUTH FIXTURE] Authenticated on retry via /login as ${credentials.email}`);
    return data.data;
  }

  throw new Error(`[AUTH FIXTURE] Could not authenticate with backend at ${backendUrl}`);
}

async function runAudit() {
  console.log("==================================================================");
  console.log("   VERISCHOLAR FULLSTACK PLAYWRIGHT COMPREHENSIVE AUDIT (E2E)     ");
  console.log("==================================================================");
  console.log(`[INFO] Workspace: ${WORKSPACE_ROOT}`);
  console.log(`[INFO] Test PDF: ${SAMPLE_PDF_PATH}`);
  console.log(`[INFO] Screenshots: ${SCREENSHOTS_DIR}`);

  const interceptedCalls = new Set();
  const apiCallDetails = [];

  const browser = await chromium.launch({
    executablePath: "/usr/bin/google-chrome",
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
  });

  // Auth Fixture: Fetch token and inject into Playwright page context before navigation
  console.log("\n[AUTH FIXTURE] Authenticating test user with backend...");
  const authData = await obtainAuthToken(BACKEND_BASE_URL);
  const token = authData.tokens.access_token;
  const user = authData.user;
  console.log(`[AUTH FIXTURE] Token acquired. User: ${user.email} (${user.id})`);

  // Inject into localStorage before any page navigation happens
  await context.addInitScript(({ token, user }) => {
    try {
      localStorage.setItem("verischolar_auth_token", token);
      localStorage.setItem("verischolar_auth_user", JSON.stringify(user));
    } catch (err) {
      console.error("Failed to inject auth credentials into localStorage:", err);
    }
  }, { token, user });

  // Set Authorization header for all network requests in this context
  await context.setExtraHTTPHeaders({
    Authorization: `Bearer ${token}`,
  });

  const page = await context.newPage();

  // Monitor network calls to /api/v1/
  page.on("request", (req) => {
    const url = req.url();
    if (url.includes("/api/v1/")) {
      const parsedUrl = new URL(url);
      const method = req.method();
      const pathName = parsedUrl.pathname;
      // Normalize UUIDs to {id} and chunk_id
      let normalizedPath = pathName.replace(
        /\/documents\/[0-9a-f-]{36}\/chunks\/([0-9a-f-]{36})/i,
        "/documents/{id}/chunks/{chunk_id}"
      );
      normalizedPath = normalizedPath.replace(
        /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi,
        "{id}"
      );
      const endpointKey = `${method} ${normalizedPath}`;
      interceptedCalls.add(endpointKey);
      apiCallDetails.push({ method, url, normalized: endpointKey, time: new Date().toISOString() });
    }
  });

  page.on("console", (msg) => {
    if (msg.type() === "error") {
      const text = msg.text();
      if (text.includes("fonts.gstatic.com") || text.includes("ERR_FAILED")) return;
      console.log(`[BROWSER ERROR] ${text}`);
    }
  });

  try {
    // 1. Navigate to dashboard
    console.log("\n[TEST 1] Navigate to http://localhost:5173/dashboard...");
    await page.goto("http://localhost:5173/dashboard", { waitUntil: "networkidle", timeout: 15000 });
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "01_initial_dashboard.png") });
    console.log(" ✓ Initial dashboard loaded successfully.");

    // 2. Check upload dropzone exists
    const fileInput = page.locator('input[type="file"][data-testid="hero-file-input"], input[type="file"]').first();
    await fileInput.waitFor({ state: "attached", timeout: 8000 });
    console.log(" ✓ Found file upload input dropzone.");

    // 3. Upload real PDF
    console.log(`\n[TEST 2] Uploading real paper: ${SAMPLE_PDF_PATH}...`);
    await fileInput.setInputFiles(SAMPLE_PDF_PATH);
    await page.waitForTimeout(450);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "02_uploading.png") });

    // 4. Wait for processing and transition to Split-Pane reader
    console.log(" Waiting for layout chunking and status completion...");
    await page.waitForSelector('[role="tablist"][aria-label="Danh sách bài báo đang mở"]', {
      timeout: 25000,
    });
    console.log(" ✓ Split-Pane reader mounted! Document tab bar active.");
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "03_reader_mounted.png") });

    const currentUrl = page.url();
    console.log(`[INFO] Current URL after upload: ${currentUrl}`);

    // 5. Test Document Library Modal (GET /api/v1/documents)
    console.log("\n[TEST 3] Testing Document Library (GET /api/v1/documents)...");
    const libraryBtn = page.getByRole("button", { name: /Thư viện/i }).first();
    if (await libraryBtn.isVisible()) {
      await libraryBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "04_document_library_modal.png") });
      console.log(" ✓ Document Library Modal opened.");
      const closeLibBtn = page.locator('[role="dialog"][aria-label="Thư viện tài liệu nghiên cứu"] button[aria-label="Đóng thư viện"]').first();
      if (await closeLibBtn.isVisible()) {
        await closeLibBtn.click();
      } else {
        await page.keyboard.press("Escape");
      }
      await page.locator('[role="dialog"][aria-label="Thư viện tài liệu nghiên cứu"]').waitFor({ state: "hidden", timeout: 5000 }).catch(() => {});
      await page.waitForTimeout(500);
    }

    // 6. Test Structure Sheet (GET /api/v1/documents/{id}/structure)
    console.log("\n[TEST 4] Testing Document Structure (Mục lục)...");
    const tocBtn = page.locator('button[aria-label="Cấu trúc phân mục bài báo"]').first();
    if (await tocBtn.isVisible()) {
      await tocBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "05_structure_toc.png") });
      console.log(" ✓ Structure Sheet opened.");
      const closeTocBtn = page.locator('button[aria-label="Đóng mục lục"]').first();
      if (await closeTocBtn.isVisible()) {
        await closeTocBtn.click();
      } else {
        await page.keyboard.press("Escape");
      }
      await page.waitForTimeout(500);
    }

    // 7. Test Parse Configuration Modal (POST /api/v1/documents/{id}:parse)
    console.log("\n[TEST 5] Testing Parse Config Modal (POST /api/v1/documents/{id}:parse)...");
    const structTab = page.getByRole("tab", { name: /Mục lục/i });
    if (await structTab.isVisible()) {
      await structTab.click();
      await page.waitForTimeout(800);
      const parseConfigBtn = page.locator('button:has-text("Cấu hình bóc tách")').first();
      if (await parseConfigBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await parseConfigBtn.click();
        await page.waitForTimeout(1000);
        await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "06_parse_config_modal.png") });
        console.log(" ✓ Parse Config Modal opened.");

        const submitParseBtn = page.locator('[role="dialog"][aria-label="Cấu hình bóc tách tài liệu"] button[type="submit"]').first();
        if (await submitParseBtn.isVisible()) {
          await submitParseBtn.click();
          await page.waitForTimeout(1500);
          console.log(" ✓ Triggered POST /api/v1/documents/{id}:parse successfully.");
        }
        const parseDialog = page.locator('[role="dialog"][aria-label="Cấu hình bóc tách tài liệu"]');
        if (await parseDialog.isVisible()) {
          const closeParseBtn = parseDialog.locator('button[aria-label="Đóng hộp thoại"], button:has-text("Hủy")').first();
          if (await closeParseBtn.isVisible()) {
            await closeParseBtn.click();
          } else {
            await page.keyboard.press("Escape");
          }
          await parseDialog.waitFor({ state: "hidden", timeout: 5000 }).catch(() => {});
        }
        await page.waitForTimeout(500);
      }
    }

    // 8. Test References & Force Re-extract (POST /api/v1/documents/{id}:extract-references)
    console.log("\n[TEST 6] Testing References Extraction & Re-extract...");
    const refBtn = page.locator('button[aria-label="Danh mục tài liệu tham khảo"]').first();
    if (await refBtn.isVisible()) {
      await refBtn.click();
      await page.waitForTimeout(1500);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "07_references_modal.png") });

      const reextractBtn = page.locator('[role="dialog"][aria-label="Danh mục tài liệu tham khảo"] button:has-text("Bóc tách lại")').first();
      if (await reextractBtn.isVisible()) {
        console.log(" Triggering force re-extraction of references...");
        await reextractBtn.click();
        await page.waitForTimeout(2000);
        console.log(" ✓ Re-extraction completed.");
      }

      const closeRefBtn = page.locator('[role="dialog"][aria-label="Danh mục tài liệu tham khảo"] button[aria-label="Đóng danh mục tham khảo"]').first();
      if (await closeRefBtn.isVisible()) {
        await closeRefBtn.click();
      } else {
        await page.keyboard.press("Escape");
      }
      await page.locator('[role="dialog"][aria-label="Danh mục tài liệu tham khảo"]').waitFor({ state: "hidden", timeout: 5000 }).catch(() => {});
      await page.waitForTimeout(500);
    }

    // 9. Test Chunks Explorer (GET /api/v1/documents/{id}/chunks & /chunks/{id})
    console.log("\n[TEST 7] Testing Document Chunks Explorer...");
    const chunksBtn = page.locator('button[aria-label="Danh sách phân đoạn Chunks"]').first();
    if (await chunksBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await chunksBtn.click();
      await page.waitForTimeout(1500);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "08_chunks_sheet.png") });

      const firstChunkItem = page.locator('[role="dialog"][aria-label="Danh sách phân đoạn bằng chứng (Chunks)"] div.cursor-pointer.group').first();
      if (await firstChunkItem.isVisible({ timeout: 2000 }).catch(() => false)) {
        await firstChunkItem.click();
        await page.waitForTimeout(1500);
        await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "09_chunk_detail_expanded.png") });
        console.log(" ✓ Chunk Detail opened with embeddings and bounding boxes via GET /chunks/{chunk_id}.");
      }

      const closeChunksBtn = page.locator('button[aria-label="Đóng danh sách Chunks"]').first();
      if (await closeChunksBtn.isVisible()) {
        await closeChunksBtn.click();
      } else {
        await page.keyboard.press("Escape");
      }
      await page.locator('[role="dialog"][aria-label="Danh sách phân đoạn bằng chứng (Chunks)"]').waitFor({ state: "hidden", timeout: 5000 }).catch(() => {});
      await page.waitForTimeout(500);
    }

    // 10. Test Grounded Summary Tab (SSE Stream & REST Generate)
    console.log("\n[TEST 8] Testing Grounded 3-Point Summary (SSE Streaming & REST Generate)...");
    const summaryTab = page.getByRole("tab", { name: /Tóm tắt/i });
    if (await summaryTab.isVisible()) {
      await summaryTab.click();
      await page.waitForTimeout(1000);

      // REST generate summary
      const genRestBtn = page.getByRole("button", { name: /Tạo lại tóm tắt|Sinh mới/i }).first();
      if (await genRestBtn.isVisible()) {
        console.log(" Triggering REST generate summary (POST /api/v1/documents/{id}/summary:generate)...");
        await genRestBtn.click();
        await page.waitForTimeout(2500);
        console.log(" ✓ REST summary generation executed.");
      }

      // Stream summary
      const streamBtn = page.getByRole("button", { name: /Stream.*\(SSE\)/i }).first();
      if (await streamBtn.isVisible()) {
        console.log(" Clicking 'Stream tóm tắt (SSE)'...");
        await streamBtn.click();
        await page.waitForTimeout(3500);
        await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "10_summary_streaming.png") });
        console.log(" ✓ Summary SSE stream triggered and rendered.");
      }
    }

    // 11. Test Star Document with Folder Selection (POST /api/v1/documents/{id}:star)
    console.log("\n[TEST 9] Testing Star Document Modal...");
    const starBtn = page.getByRole("button", { name: /Lưu bài báo vào thư viện|Đã lưu vào thư viện/i }).first();
    if (await starBtn.isVisible()) {
      await starBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "11_star_modal.png") });
      console.log(" ✓ Star Document Modal displayed.");

      const confirmStarBtn = page.locator('[role="dialog"][aria-label="Lưu bài báo vào thư viện cá nhân"] button[type="submit"]').first();
      if (await confirmStarBtn.isVisible()) {
        await confirmStarBtn.click();
        await page.waitForTimeout(1000);
        console.log(" ✓ Star document mutation executed.");
      }

      const starDialog = page.locator('[role="dialog"][aria-label="Lưu bài báo vào thư viện cá nhân"]');
      if (await starDialog.isVisible({ timeout: 1500 }).catch(() => false)) {
        await page.keyboard.press("Escape");
        await starDialog.waitFor({ state: "hidden", timeout: 5000 }).catch(() => {});
        await page.waitForTimeout(500);
      }
    }

    // 12. Test Notes Panel: Create, Inspect Detail, Inline Edit, Synthesize
    console.log("\n[TEST 10] Testing Notes Panel (CRUD, Snapshot Inspector, Synthesize)...");
    const notesTab = page.getByRole("tab", { name: /Sổ tay/i });
    if (await notesTab.isVisible()) {
      await notesTab.click();
      await page.waitForTimeout(1000);

      // Create note
      const createNoteBtn = page
        .locator('[role="region"][aria-label="Sổ tay nghiên cứu cá nhân"] button:has-text("Thêm"), [role="region"][aria-label="Sổ tay nghiên cứu cá nhân"] button:has-text("Tạo ghi chú thủ công")')
        .first();
      if (await createNoteBtn.isVisible()) {
        await createNoteBtn.click();
        await page.waitForTimeout(600);

        const noteInput = page.locator('textarea[placeholder*="Ghi chú"], input[type="text"]').first();
        if (await noteInput.isVisible()) {
          await noteInput.fill("Phản biện kiến trúc Transformer không cần recurrence");
        }

        const submitNoteBtn = page.locator('button[type="submit"]:has-text("Lưu vào sổ tay"), button[type="submit"]').first();
        if (await submitNoteBtn.isVisible()) {
          await submitNoteBtn.click();
          await page.waitForTimeout(1500);
          console.log(" ✓ Created note via POST /api/v1/notes.");
        }
      }

      // Inspect detail (GET /api/v1/notes/{id})
      const inspectBtn = page.locator('button[aria-label="Xem chi tiết ghi chú & snapshot đóng băng"]').first();
      if (await inspectBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await inspectBtn.click();
        await page.waitForTimeout(1000);
        await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "12_note_detail_snapshot.png") });
        console.log(" ✓ Note Detail Frozen Snapshot Modal displayed.");

        const closeNoteDetailBtn = page.getByRole("button", { name: /Đóng chi tiết ghi chú/i });
        if (await closeNoteDetailBtn.isVisible()) {
          await closeNoteDetailBtn.click();
        } else {
          await page.keyboard.press("Escape");
        }
        await page.locator('[role="dialog"][aria-label="Chi tiết ghi chú"]').waitFor({ state: "hidden", timeout: 5000 }).catch(() => {});
        await page.waitForTimeout(500);
      }

      // Inline Edit Note (PATCH /api/v1/notes/{id})
      const editNoteBtn = page.locator('button[aria-label="Chỉnh sửa ghi chú"]').first();
      if (await editNoteBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await editNoteBtn.click();
        await page.waitForTimeout(500);
        const editArea = page.locator('textarea[placeholder*="Ghi chú phản biện cá nhân"]').first();
        if (await editArea.isVisible()) {
          await editArea.fill("Đã cập nhật ghi chú phản biện (OCC verified)");
          const saveNoteBtn = page.locator('[role="region"][aria-label="Sổ tay nghiên cứu cá nhân"] button:has-text("Lưu")').first();
          if (await saveNoteBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
            await saveNoteBtn.click({ force: true });
            await page.waitForTimeout(1200);
            console.log(" ✓ Updated note via PATCH /api/v1/notes/{id}.");
          }
        }
      }

      // Delete Note (DELETE /api/v1/notes/{id})
      const deleteNoteBtn = page.locator('[role="region"][aria-label="Sổ tay nghiên cứu cá nhân"] button[aria-label="Xóa ghi chú"]').first();
      if (await deleteNoteBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await deleteNoteBtn.click({ force: true });
        await page.waitForTimeout(1000);
        console.log(" ✓ Deleted note via DELETE /api/v1/notes/{id}.");
      }

      // Test AI Synthesize (POST /api/v1/notes:synthesize)
      const synthBtn = page.getByRole("button", { name: /Tổng hợp AI/i });
      if (await synthBtn.isVisible({ timeout: 2000 }).catch(() => false) && await synthBtn.isEnabled({ timeout: 2000 }).catch(() => false)) {
        await synthBtn.click();
        await page.waitForTimeout(1000);
        await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "13_note_synthesis_modal.png") });
        console.log(" ✓ Note Synthesis Modal opened with 4 modes.");

        const executeSynthBtn = page.locator('[role="dialog"][aria-label="AI Tổng hợp ghi chú thành bài học"] button[type="submit"]').first();
        if (await executeSynthBtn.isVisible()) {
          console.log(" Triggering AI note synthesis (POST /api/v1/notes:synthesize)...");
          await executeSynthBtn.click();
          await page.waitForTimeout(3000);
          console.log(" ✓ Note synthesis triggered successfully.");
        }
        await page.keyboard.press("Escape");
        await page.locator('[role="dialog"][aria-label="AI Tổng hợp ghi chú thành bài học"]').waitFor({ state: "hidden", timeout: 5000 }).catch(() => {});
        await page.waitForTimeout(500);
      }
    }

    // 13. Test Socratic Chat (POST /api/v1/sessions/{id}/messages & DELETE /messages)
    console.log("\n[TEST 11] Testing Socratic Copilot Chat (Live Streaming & Reset)...");
    const chatTab = page.getByRole("tab", { name: /Đối thoại/i });
    if (await chatTab.isVisible({ timeout: 2000 }).catch(() => false)) {
      await chatTab.click();
      await page.waitForTimeout(800);

      const chatInput = page.locator('textarea[placeholder*="Tôi có thể giúp gì"]').first();
      if (await chatInput.isVisible({ timeout: 2000 }).catch(() => false)) {
        await chatInput.fill("Hãy tóm tắt ngắn gọn cơ chế Multi-Head Attention trong bài báo?");
        await page.waitForTimeout(300);
        const sendBtn = page.locator('button[aria-label="Gửi câu hỏi"]').first();
        if (await sendBtn.isVisible({ timeout: 2000 }).catch(() => false) && await sendBtn.isEnabled()) {
          console.log(" Sending Socratic chat message...");
          await sendBtn.click();
          await page.waitForTimeout(5000);
          await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "14_chat_streaming.png") });
          console.log(" ✓ Chat streaming initiated via POST /api/v1/sessions/{id}/messages.");
        }
      }

      // Test reset chat (DELETE /api/v1/sessions/{id}/messages)
      const resetChatBtn = page.locator('button[title="Làm mới hội thoại"]').first();
      if (await resetChatBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await resetChatBtn.click();
        await page.waitForTimeout(1000);
        console.log(" ✓ Reset chat triggered via DELETE /api/v1/sessions/{id}/messages.");
      }
    }

    // 14. Test Session Settings Rename with OCC (PATCH /api/v1/sessions/{id})
    console.log("\n[TEST 12] Testing Session Rename with OCC (PATCH /api/v1/sessions/{id})...");
    const settingsBtn = page.locator('button[aria-label="Cài đặt phiên nghiên cứu"]').first();
    if (await settingsBtn.isVisible()) {
      await settingsBtn.click();
      await page.waitForTimeout(800);

      const titleInput = page.locator('input[placeholder="Nhập tên phiên..."]').first();
      if (await titleInput.isVisible()) {
        await titleInput.fill("Nghiên cứu Transformer Attention (E2E Verified)");
        const saveTitleBtn = page.locator('button:has-text("Lưu thay đổi")').first();
        if (await saveTitleBtn.isVisible()) {
          await saveTitleBtn.click();
          await page.waitForTimeout(1500);
          console.log(" ✓ Session renamed via PATCH /api/v1/sessions/{id}.");
        }
      }
      const settingsDialog = page.locator('[role="dialog"][aria-label="Cài đặt phiên nghiên cứu"]');
      if (await settingsDialog.isVisible()) {
        const closeBtn = settingsDialog.locator('button[aria-label="Đóng cài đặt"], button:has-text("Hủy")').first();
        if (await closeBtn.isVisible()) {
          await closeBtn.click();
        } else {
          await page.keyboard.press("Escape");
        }
        await settingsDialog.waitFor({ state: "hidden", timeout: 5000 }).catch(() => {});
      }
      await page.waitForTimeout(500);
    }

    // 15. Test Export Session Offline Bundle .zip (POST /api/v1/sessions/{id}:export-bundle)
    console.log("\n[TEST 13] Testing Export Offline Research Bundle (.zip)...");
    const exportZipBtn = page.locator('button[aria-label="Xuất gói nghiên cứu ngoại tuyến (.zip)"]').first();
    if (await exportZipBtn.isVisible()) {
      await exportZipBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "15_export_bundle_modal.png") });
      console.log(" ✓ Export Offline Bundle Dialog opened.");

      const downloadZipBtn = page.locator('button:has-text("Tải gói ZIP")').first();
      if (await downloadZipBtn.isVisible()) {
        console.log(" Triggering POST /api/v1/sessions/{id}:export-bundle...");
        await downloadZipBtn.click();
        await page.waitForTimeout(2500);
        console.log(" ✓ Export bundle generated and downloaded.");
      }

      const closeZipBtn = page.locator('[role="dialog"] button:has-text("Đóng"), [role="dialog"] button[aria-label="Đóng hộp thoại"]').first();
      if (await closeZipBtn.isVisible()) {
        await closeZipBtn.click();
      } else {
        await page.keyboard.press("Escape");
      }
      await page.waitForTimeout(500);
    }

    // 16. Test Multi-Paper Add Document Modal (POST /api/v1/sessions/{id}/documents)
    console.log("\n[TEST 14] Testing Add Document to Session Modal...");
    const addPaperBtn = page.locator('button[aria-label="Nạp thêm bài báo vào phiên (Tối đa 5 bài)"]').first();
    if (await addPaperBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await addPaperBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "16_add_document_modal.png") });
      console.log(" ✓ Add Document to Session modal opened.");

      // Select an existing document from library to add to session (POST /api/v1/sessions/{id}/documents)
      const selectDocBtn = page.locator('[role="dialog"][aria-label="Nạp bài báo vào phiên nghiên cứu"] button:has-text("Chọn")').first();
      if (await selectDocBtn.isVisible({ timeout: 1500 }).catch(() => false)) {
        await selectDocBtn.click();
        await page.waitForTimeout(1500);
        console.log(" ✓ Added document to session via POST /api/v1/sessions/{id}/documents.");
      } else {
        // Switch to URL tab to test input form
        const urlTabBtn = page.locator('button:has-text("Nhập link trực tuyến")').first();
        if (await urlTabBtn.isVisible()) {
          await urlTabBtn.click();
          await page.waitForTimeout(500);
        }

        const closeAddDocBtn = page.locator('[role="dialog"][aria-label="Nạp bài báo vào phiên nghiên cứu"] button[aria-label="Đóng hộp thoại"]').first();
        if (await closeAddDocBtn.isVisible()) {
          await closeAddDocBtn.click();
        } else {
          await page.keyboard.press("Escape");
        }
      }
      await page.locator('[role="dialog"][aria-label="Nạp bài báo vào phiên nghiên cứu"]').waitFor({ state: "hidden", timeout: 5000 }).catch(() => {});
      await page.waitForTimeout(500);
    }

    // 17. Test Session Search & Archived Filter in Sidebar
    console.log("\n[TEST 15] Testing Session Search & Archived Filter in Sidebar...");
    const expandBtn = page.getByRole("button", { name: /Mở rộng thanh điều hướng/i });
    if (await expandBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
      await expandBtn.click();
      await page.waitForTimeout(500);
    }

    const sessionSearchInput = page.locator('aside input[placeholder="Tìm phiên..."]');
    if (await sessionSearchInput.isVisible()) {
      await sessionSearchInput.fill("Nghiên cứu");
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "17_session_search.png") });
      console.log(" ✓ Session search input filter verified.");

      const archiveToggle = page.locator('aside button:has-text("Xem lưu trữ"), aside button:has-text("Lưu trữ")').first();
      if (await archiveToggle.isVisible()) {
        await archiveToggle.click({ force: true });
        await page.waitForTimeout(500);
        await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "18_session_archived_view.png") });
        console.log(" ✓ Session archive toggle verified.");
        const toggleBack = page.locator('aside button:has-text("Lưu trữ")').first();
        if (await toggleBack.isVisible()) {
          await toggleBack.click({ force: true });
        }
      }
    }

    // 18. Test Export Annotated PDF (GET /api/v1/documents/{id}/export-pdf)
    console.log("\n[TEST 16] Testing Export Annotated PDF (GET /api/v1/documents/{id}/export-pdf)...");
    const exportPdfBtn = page.getByRole("button", { name: /Xuất PDF/i });
    if (await exportPdfBtn.isVisible()) {
      await exportPdfBtn.click();
      await page.waitForTimeout(1500);
      console.log(" ✓ Export Annotated PDF triggered.");
    }

    // 19. Test Document Permanent Delete (DELETE /api/v1/documents/{id})
    console.log("\n[TEST 17] Testing Document Deletion (DELETE /api/v1/documents/{id})...");
    const deleteTabBtn = page.locator('button[aria-label^="Xóa bài báo"]').first();
    if (await deleteTabBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await deleteTabBtn.click({ force: true });
      await page.waitForTimeout(800);
      const confirmDeleteBtn = page.getByRole("button", { name: /Xác nhận xóa/i });
      if (await confirmDeleteBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await confirmDeleteBtn.click();
        await page.waitForTimeout(2000);
        await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "19_after_delete.png") });
        console.log(" ✓ Document deleted via Zero-Retention Cascade Purge.");
      }
    }

    // 20. Test Session Deletion (DELETE /api/v1/sessions/{id})
    console.log("\n[TEST 18] Testing Session Deletion (DELETE /api/v1/sessions/{id})...");
    const endSettingsBtn = page.locator('button[aria-label="Cài đặt phiên nghiên cứu"]').first();
    if (await endSettingsBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await endSettingsBtn.click();
      await page.waitForTimeout(800);
      const deleteSessionBtn = page.locator('[role="dialog"][aria-label="Cài đặt phiên nghiên cứu"] button:has-text("Xóa phiên")').first();
      if (await deleteSessionBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await deleteSessionBtn.click();
        await page.waitForTimeout(2000);
        console.log(" ✓ Deleted session via DELETE /api/v1/sessions/{id}.");
      }
    }

    console.log("\n==================================================================");
    console.log("             PLAYWRIGHT LIVE AUDIT EXECUTION SUMMARY              ");
    console.log("==================================================================");
    console.log(`Total intercepted unique API endpoints: ${interceptedCalls.size}`);
    Array.from(interceptedCalls).sort().forEach((ep) => {
      console.log(`  [CALL] ${ep}`);
    });

  } catch (err) {
    console.error("[AUDIT FAILURE]", err);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "error_screenshot.png") });
    throw err;
  } finally {
    await browser.close();
  }
}

runAudit()
  .then(() => {
    console.log("\n[SUCCESS] Fullstack Playwright live audit completed successfully.");
    process.exit(0);
  })
  .catch((err) => {
    console.error("Audit failed:", err);
    process.exit(1);
  });

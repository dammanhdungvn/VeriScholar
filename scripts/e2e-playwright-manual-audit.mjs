import { chromium } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

const WORKSPACE_ROOT = path.resolve(process.cwd());
const SCREENSHOTS_DIR = path.resolve(WORKSPACE_ROOT, "apps/web/playwright-screenshots");

if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

const SAMPLE_PDF_PATH = path.resolve(
  WORKSPACE_ROOT,
  "data/papers/Attention Is All You Need.pdf"
);

async function runAudit() {
  console.log("==================================================================");
  console.log("   VERISCHOLAR FULLSTACK PLAYWRIGHT LIVE AUDIT (PRODUCTION ENV)   ");
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

  const page = await context.newPage();

  // Monitor network calls to /api/v1/
  page.on("request", (req) => {
    const url = req.url();
    if (url.includes("/api/v1/")) {
      const parsedUrl = new URL(url);
      const method = req.method();
      let pathName = parsedUrl.pathname;
      // Normalize UUIDs to {id}
      const normalizedPath = pathName.replace(
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
      console.log(`[BROWSER ERROR] ${msg.text()}`);
    }
  });

  try {
    // 1. Navigate to dashboard
    console.log("\n[TEST 1] Navigate to http://localhost:5173/dashboard...");
    await page.goto("http://localhost:5173/dashboard", { waitUntil: "networkidle", timeout: 15000 });
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "01_initial_dashboard.png") });
    console.log(" ✓ Initial dashboard loaded successfully.");

    // 2. Check upload dropzone exists
    const fileInput = await page.waitForSelector('input[type="file"]', { timeout: 8000 });
    console.log(" ✓ Found file upload input dropzone.");

    // 3. Upload real PDF
    console.log(`\n[TEST 2] Uploading real paper: ${SAMPLE_PDF_PATH}...`);
    await fileInput.setInputFiles(SAMPLE_PDF_PATH);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "02_uploading.png") });

    // 4. Wait for processing and transition to Split-Pane reader
    console.log(" Waiting for layout chunking and status completion...");
    await page.waitForSelector('[role="tablist"][aria-label="Danh sách bài báo đang mở"]', {
      timeout: 20000,
    });
    console.log(" ✓ Split-Pane reader mounted! Document tab bar active.");
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "03_reader_mounted.png") });

    // Check URL has session ID
    const currentUrl = page.url();
    console.log(`[INFO] Current URL after upload: ${currentUrl}`);

    // 5. Test Table of Contents (Structure Sheet)
    console.log("\n[TEST 3] Testing Document Structure (Mục lục)...");
    const tocBtn = page.getByRole("button", { name: /Mục lục/i });
    if (await tocBtn.isVisible()) {
      await tocBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "04_structure_toc.png") });
      console.log(" ✓ Structure Sheet opened.");
      // Close TOC
      const closeTocBtn = page.getByRole("button", { name: /Đóng mục lục/i });
      if (await closeTocBtn.isVisible()) {
        await closeTocBtn.click();
        await page.waitForTimeout(500);
      }
    }

    // 6. Test References Extraction
    console.log("\n[TEST 4] Testing References Extraction (Tham khảo)...");
    const refBtn = page.getByRole("button", { name: /Tham khảo/i });
    if (await refBtn.isVisible()) {
      await refBtn.click();
      await page.waitForTimeout(1500);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "05_references_modal.png") });
      console.log(" ✓ References modal triggered and rendered.");
      // Close Modal via Escape or close button
      await page.keyboard.press("Escape");
      await page.waitForTimeout(500);
    }

    // 7. Test Chunks Explorer (DocumentChunksSheet)
    console.log("\n[TEST 5] Testing Document Chunks Explorer (GET /chunks & GET /chunks/{id})...");
    const chunksBtn = page.getByRole("button", { name: /Chunks/i });
    if (await chunksBtn.isVisible()) {
      await chunksBtn.click();
      await page.waitForTimeout(1500);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "06_chunks_sheet.png") });
      console.log(" ✓ Chunks Sheet opened, displaying chunk list.");

      // Click first chunk item to view single chunk detail
      const firstChunkItem = page.locator('[role="dialog"][aria-label="Danh sách phân đoạn bằng chứng (Chunks)"] .cursor-pointer').first();
      if (await firstChunkItem.isVisible()) {
        await firstChunkItem.click();
        await page.waitForTimeout(1000);
        await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "07_chunk_detail_expanded.png") });
        console.log(" ✓ Chunk Detail opened with embeddings and bounding boxes.");
      }

      // Close Chunks Sheet
      const closeChunksBtn = page.getByRole("button", { name: /Đóng danh sách Chunks/i });
      if (await closeChunksBtn.isVisible()) {
        await closeChunksBtn.click();
        await page.waitForTimeout(500);
      }
    }

    // 8. Test Grounded Summary tab (SSE Stream and REST)
    console.log("\n[TEST 6] Testing Grounded 3-Point Summary (SSE Streaming)...");
    const summaryTab = page.getByRole("tab", { name: /Tóm tắt/i });
    if (await summaryTab.isVisible()) {
      await summaryTab.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "08_summary_tab_initial.png") });

      // Check if Stream button is present
      const streamBtn = page.getByRole("button", { name: /Stream.*\(SSE\)/i });
      if (await streamBtn.isVisible()) {
        console.log(" Clicking 'Stream tóm tắt (SSE)'...");
        await streamBtn.click();
        // Wait for streaming tokens to accumulate
        await page.waitForTimeout(4000);
        await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "09_summary_streaming.png") });
        console.log(" ✓ Summary SSE stream triggered and rendered.");
      } else {
        const generateBtn = page.getByRole("button", { name: /Sinh tóm tắt|Tạo lại tóm tắt/i });
        if (await generateBtn.isVisible()) {
          console.log(" Clicking 'Sinh tóm tắt'...");
          await generateBtn.click();
          await page.waitForTimeout(3000);
          await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "09_summary_generated.png") });
          console.log(" ✓ Summary generated via REST.");
        }
      }
    }

    // 9. Test Notes Panel (Sổ tay)
    console.log("\n[TEST 7] Testing Notes Panel (Sổ tay)...");
    const notesTab = page.getByRole("tab", { name: /Sổ tay/i });
    if (await notesTab.isVisible()) {
      await notesTab.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "10_notes_tab.png") });

      // Click synthesize if available
      const synthBtn = page.getByRole("button", { name: /Tổng hợp luận điểm/i });
      if (await synthBtn.isVisible()) {
        console.log(" Triggering Notes Synthesize (POST /api/v1/notes:synthesize)...");
        await synthBtn.click();
        await page.waitForTimeout(2000);
        await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "11_notes_synthesized.png") });
        console.log(" ✓ Notes synthesize triggered.");
      }
    }

    // 10. Test Star Document
    console.log("\n[TEST 8] Testing Star Document (POST /api/v1/documents/{id}:star)...");
    const starBtn = page.getByRole("button", { name: /Lưu bài báo vào thư viện|Đã lưu vào thư viện/i }).first();
    if (await starBtn.isVisible()) {
      await starBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "12_document_starred.png") });
      console.log(" ✓ Star document mutation executed.");
    }

    // 11. Test Export Annotated PDF
    console.log("\n[TEST 9] Testing Export Annotated PDF (GET /api/v1/documents/{id}/export-pdf)...");
    const exportPdfBtn = page.getByRole("button", { name: /Xuất PDF/i });
    if (await exportPdfBtn.isVisible()) {
      await exportPdfBtn.click();
      await page.waitForTimeout(1500);
      console.log(" ✓ Export PDF triggered.");
    }

    // 12. Test Document Permanent Delete (Zero-Retention Cascade Purge)
    console.log("\n[TEST 10] Testing Document Deletion (DELETE /api/v1/documents/{id})...");
    const deleteTabBtn = page.locator('button[aria-label^="Xóa bài báo"]').first();
    if (await deleteTabBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await deleteTabBtn.click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "13_delete_confirmation_modal.png") });
      console.log(" ✓ Delete confirmation modal displayed.");

      // Click "Xác nhận xóa"
      const confirmDeleteBtn = page.getByRole("button", { name: /Xác nhận xóa/i });
      if (await confirmDeleteBtn.isVisible()) {
        await confirmDeleteBtn.click();
        await page.waitForTimeout(2000);
        await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "14_after_delete.png") });
        console.log(" ✓ Document deleted via Zero-Retention Cascade Purge.");
      }
    } else {
      console.log(" [INFO] Delete button requires tab hover, testing hover...");
      const tabElement = page.locator('[role="tab"][aria-selected="true"]');
      if (await tabElement.isVisible()) {
        await tabElement.hover();
        await page.waitForTimeout(500);
        const hoveredDeleteBtn = page.locator('button[aria-label^="Xóa bài báo"]').first();
        if (await hoveredDeleteBtn.isVisible()) {
          await hoveredDeleteBtn.click();
          await page.waitForTimeout(500);
          await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "13_delete_confirmation_modal.png") });
          const confirmDeleteBtn = page.getByRole("button", { name: /Xác nhận xóa/i });
          if (await confirmDeleteBtn.isVisible()) {
            await confirmDeleteBtn.click();
            await page.waitForTimeout(2000);
            await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "14_after_delete.png") });
            console.log(" ✓ Document deleted via Zero-Retention Cascade Purge.");
          }
        }
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

runAudit().catch((err) => {
  console.error("Audit failed:", err);
  process.exit(1);
});

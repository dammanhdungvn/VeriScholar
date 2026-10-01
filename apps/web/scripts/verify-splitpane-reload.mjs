import { chromium } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

const ROOT_DIR = process.cwd().endsWith("web") ? path.resolve("../..") : process.cwd();
const SCREENSHOTS_DIR = path.resolve(ROOT_DIR, "apps/web/playwright-screenshots/reload-check");
const SAMPLE_PDF_PATH = path.resolve(ROOT_DIR, "data/papers/Attention Is All You Need.pdf");

if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function verifySplitPaneReload() {
  console.log("==================================================================");
  console.log("   SPLIT-PANE WORKSPACE RELOAD ZERO-MOCK LIVE PLAYWRIGHT AUDIT    ");
  console.log("==================================================================");

  const browser = await chromium.launch({
    headless: true,
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2,
  });

  const page = await context.newPage();

  let mockFoundInHtml = false;
  page.on("response", async () => {
    try {
      const text = await page.content();
      if (
        text.includes("Các mô hình chuỗi tuần tự trước đây chủ yếu dựa vào mạng nơ-ron") ||
        text.includes("Mã hóa vị trí (Positional Encoding)")
      ) {
        mockFoundInHtml = true;
      }
    } catch {
      // ignore
    }
  });

  try {
    console.log("[STEP 1] Opening /dashboard and uploading PDF...");
    await page.goto("http://localhost:5173/dashboard", { waitUntil: "networkidle" });
    const fileInput = page.locator('input[type="file"]').first();
    await fileInput.waitFor({ state: "attached", timeout: 8000 });
    await fileInput.setInputFiles(SAMPLE_PDF_PATH);

    // Wait until workspace mounts
    console.log("[STEP 2] Waiting for split-pane workspace to mount...");
    await page.waitForSelector('[role="tablist"][aria-label="Danh sách bài báo đang mở"]', { timeout: 35000 });
    await page.waitForSelector("canvas", { timeout: 15000 });
    console.log(" Workspace mounted with PDF canvas!");
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "10_workspace_before_reload.png") });

    // Now trigger reload!
    console.log("[STEP 3] Triggering page reload (F5 / Refresh)...");
    await page.reload({ waitUntil: "domcontentloaded" });

    // Take screenshot during the immediate post-reload loading window
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "11_workspace_during_reload.png") });

    const reloadContent = await page.content();
    const hasMockDuringReload =
      reloadContent.includes("Các mô hình chuỗi tuần tự trước đây chủ yếu dựa vào mạng nơ-ron") ||
      reloadContent.includes("Mã hóa vị trí (Positional Encoding)");

    console.log(`[CHECK] Mock text during reload: ${hasMockDuringReload ? "FOUND (FAIL)" : "ABSENT (PASS)"}`);

    // Wait for full settlement
    await page.waitForTimeout(3000);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "12_workspace_after_settled.png") });

    const settledContent = await page.content();
    const hasMockSettled =
      settledContent.includes("Các mô hình chuỗi tuần tự trước đây chủ yếu dựa vào mạng nơ-ron") ||
      settledContent.includes("Mã hóa vị trí (Positional Encoding)");

    console.log(`[CHECK] Mock text settled: ${hasMockSettled ? "FOUND (FAIL)" : "ABSENT (PASS)"}`);
    console.log(`[CHECK] Any mock text detected across events: ${mockFoundInHtml ? "FOUND (FAIL)" : "ABSENT (PASS)"}`);

    if (hasMockDuringReload || hasMockSettled || mockFoundInHtml) {
      throw new Error("Audit failed: Mock text was detected on reload!");
    }

    console.log("==================================================================");
    console.log("   AUDIT PASSED: ZERO MOCK DATA EVER DISPLAYED ON RELOAD!       ");
    console.log("==================================================================");
  } finally {
    await browser.close();
  }
}

verifySplitPaneReload().catch((err) => {
  console.error("Test failed:", err);
  process.exit(1);
});

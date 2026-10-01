import { chromium } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

const ROOT_DIR = process.cwd().endsWith("web") ? path.resolve("../..") : process.cwd();
const SCREENSHOTS_DIR = path.resolve(ROOT_DIR, "apps/web/playwright-screenshots/reload-check");

if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function verifyReloadNoMock() {
  console.log("==================================================================");
  console.log("       VERISCHOLAR RELOAD ZERO-MOCK LIVE PLAYWRIGHT AUDIT        ");
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

  let mockTextDetected = false;
  page.on("domcontentloaded", async () => {
    try {
      const content = await page.content();
      if (
        content.includes("Các mô hình chuỗi tuần tự trước đây chủ yếu dựa vào mạng") ||
        content.includes("Mã hóa vị trí (Positional Encoding)")
      ) {
        mockTextDetected = true;
        console.error(" [FAILURE] Mock paper text detected during page lifecycle!");
      }
    } catch {
      // ignore
    }
  });

  try {
    console.log("[STEP 1] Navigating to http://localhost:5173/dashboard...");
    await page.goto("http://localhost:5173/dashboard", { waitUntil: "networkidle", timeout: 15000 });
    await page.waitForTimeout(1000);

    const initialContent = await page.content();
    const hasMockInitial =
      initialContent.includes("Các mô hình chuỗi tuần tự trước đây chủ yếu dựa vào mạng") ||
      initialContent.includes("Mã hóa vị trí (Positional Encoding)");

    console.log(`[CHECK 1] Initial Load Mock Paper Present: ${hasMockInitial ? "YES (FAIL)" : "NO (PASS)"}`);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "01_initial_dashboard.png") });

    console.log("[STEP 2] Triggering hard page reload (simulate F5 / refresh)...");
    await page.reload({ waitUntil: "load" });

    // Check immediately after load event
    const postReloadContent = await page.content();
    const hasMockPostReload =
      postReloadContent.includes("Các mô hình chuỗi tuần tự trước đây chủ yếu dựa vào mạng") ||
      postReloadContent.includes("Mã hóa vị trí (Positional Encoding)");

    console.log(`[CHECK 2] Immediate Post-Reload Mock Paper Present: ${hasMockPostReload ? "YES (FAIL)" : "NO (PASS)"}`);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "02_immediate_post_reload.png") });

    // Wait for network idle and PDF rendering
    await page.waitForTimeout(2000);
    const settledContent = await page.content();
    const hasMockSettled =
      settledContent.includes("Các mô hình chuỗi tuần tự trước đây chủ yếu dựa vào mạng") ||
      settledContent.includes("Mã hóa vị trí (Positional Encoding)");

    console.log(`[CHECK 3] Settled State Mock Paper Present: ${hasMockSettled ? "YES (FAIL)" : "NO (PASS)"}`);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "03_settled_after_reload.png") });

    // Check if canvas is rendered or empty state is rendered
    const canvasCount = await page.locator("canvas").count();
    console.log(`[INFO] Number of active PDF canvas elements: ${canvasCount}`);

    if (hasMockInitial || hasMockPostReload || hasMockSettled || mockTextDetected) {
      throw new Error("Audit Failed: Mock paper data was rendered at some point!");
    }

    console.log("==================================================================");
    console.log("   AUDIT PASSED: Zero mock paper data detected on reload!       ");
    console.log("==================================================================");
  } finally {
    await browser.close();
  }
}

verifyReloadNoMock().catch((err) => {
  console.error("Test failed:", err);
  process.exit(1);
});

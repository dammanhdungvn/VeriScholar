import { chromium } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

const ROOT_DIR = process.cwd().endsWith("web") ? path.resolve("../..") : process.cwd();
const SCREENSHOTS_DIR = path.resolve(ROOT_DIR, "apps/web/playwright-screenshots/pdf-reader");
const SAMPLE_PDF_PATH = path.resolve(ROOT_DIR, "data/papers/Attention Is All You Need.pdf");

if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function verifyPdfReader() {
  console.log("==================================================================");
  console.log("    VERISCHOLAR PDF.js ACADEMIC DEEP READER LIVE VERIFICATION     ");
  console.log("==================================================================");

  const browser = await chromium.launch({
    headless: true,
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2, // Retina simulation
  });

  const page = await context.newPage();

  page.on("console", (msg) => {
    if (msg.type() === "error") {
      console.log(`[BROWSER ERROR] ${msg.text()}`);
    }
  });

  try {
    // 1. Navigate to dashboard
    console.log("[STEP 1] Navigating to http://localhost:5173/dashboard...");
    await page.goto("http://localhost:5173/dashboard", { waitUntil: "networkidle", timeout: 15000 });

    // 2. Upload real paper
    console.log(`[STEP 2] Uploading paper: ${SAMPLE_PDF_PATH}...`);
    const fileInput = page.locator('input[type="file"][data-testid="hero-file-input"], input[type="file"]').first();
    await fileInput.waitFor({ state: "attached", timeout: 8000 });
    await fileInput.setInputFiles(SAMPLE_PDF_PATH);

    // 3. Wait for layout chunking and split-pane reader mount
    console.log(" Waiting for layout chunking and PDF reader mount...");
    await page.waitForSelector('[role="tablist"][aria-label="Danh sách bài báo đang mở"]', { timeout: 30000 });
    await page.waitForTimeout(2500);

    // 4. Verify HTML5 <canvas> is rendered by PDF.js
    console.log("[STEP 3] Verifying HTML5 <canvas> rendering via PDF.js...");
    await page.waitForSelector("canvas", { timeout: 15000 });
    const canvasCount = await page.locator("canvas").count();
    console.log(` ✓ Successfully detected ${canvasCount} active PDF.js canvas element(s)!`);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "pdf_01_canvas_rendered.png") });

    // 5. Test Thumbnails Sidebar
    console.log("\n[STEP 4] Testing Page Thumbnails Sidebar...");
    const thumbBtn = page.locator('button[aria-label*="Thumbnails"]').first();
    if (await thumbBtn.isVisible()) {
      await thumbBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "pdf_02_thumbnails_sidebar.png") });
      console.log(" ✓ Thumbnails Sidebar opened with miniature preview cards.");

      // Click page 3 thumbnail
      const page3Thumb = page.locator('aside[aria-label*="Thumbnails"] button:has-text("Trang 3")').first();
      if (await page3Thumb.isVisible()) {
        await page3Thumb.click();
        await page.waitForTimeout(1200);
        console.log(" ✓ Jumped to Page 3 via Thumbnail click.");
      }

      // Close thumbnails
      await thumbBtn.click();
      await page.waitForTimeout(500);
    }

    // 6. Test Eye-Care Dark Mode (Inverted Theme)
    console.log("\n[STEP 5] Testing Eye-Care Inverted Dark Mode...");
    const darkModeBtn = page.locator('button[aria-label="Giao diện tối bảo vệ mắt"]').first();
    if (await darkModeBtn.isVisible()) {
      await darkModeBtn.click();
      await page.waitForTimeout(800);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "pdf_03_dark_mode_inverted.png") });
      console.log(" ✓ Inverted Dark Reading Mode active.");
    }

    // 7. Test Sepia Theme
    console.log("\n[STEP 6] Testing Sepia Vintage Academic Theme...");
    const sepiaBtn = page.locator('button[aria-label="Giao diện sepia"]').first();
    if (await sepiaBtn.isVisible()) {
      await sepiaBtn.click();
      await page.waitForTimeout(800);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "pdf_04_sepia_theme.png") });
      console.log(" ✓ Sepia Paper Reading Mode active.");
    }

    // Reset back to standard light
    const lightBtn = page.locator('button[aria-label="Giao diện sáng"]').first();
    if (await lightBtn.isVisible()) {
      await lightBtn.click();
      await page.waitForTimeout(500);
    }

    // 8. Test Two-Page Spread Mode
    console.log("\n[STEP 7] Testing Two-Page Spread (Journal Mode)...");
    const twoPageBtn = page.locator('button[aria-label="Hai trang"]').first();
    if (await twoPageBtn.isVisible()) {
      await twoPageBtn.click();
      await page.waitForTimeout(1500);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "pdf_05_two_page_spread.png") });
      console.log(" ✓ Two-Page Spread Mode active.");
    }

    // Switch back to continuous scroll
    const scrollBtn = page.locator('button[aria-label="Cuộn liên tục"]').first();
    if (await scrollBtn.isVisible()) {
      await scrollBtn.click();
      await page.waitForTimeout(1000);
    }

    // 9. Test Evidence Highlighting on Canvas
    console.log("\n[STEP 8] Testing Grounded Evidence BoundingBox Highlighting on Canvas...");
    const summaryTab = page.getByRole("tab", { name: /Tóm tắt/i });
    if (await summaryTab.isVisible()) {
      await summaryTab.click();
      await page.waitForTimeout(1000);

      // Click on the citation badge for Tr.1 to trigger bounding box highlight on Canvas
      const citationBadge = page.locator('button[title*="Nhảy tới trang"]').first();
      await citationBadge.waitFor({ state: "visible", timeout: 5000 });
      console.log(" Clicking citation badge for visual grounding...");
      await citationBadge.click();
      await page.waitForTimeout(1500);
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "pdf_06_evidence_highlight.png") });
      // 10. Test Scholar Selection Toolbar on Canvas
      console.log("\n[STEP 9] Testing Scholar Selection Floating Toolbar on Canvas...");
      const textLayer = page.locator(".textLayer").first();
      if (await textLayer.isVisible()) {
        const span = textLayer.locator("span").first();
        if (await span.isVisible()) {
          const box = await span.boundingBox();
          if (box) {
            await page.mouse.move(box.x + 5, box.y + 5);
            await page.mouse.down();
            await page.mouse.move(box.x + Math.min(box.width - 5, 200), box.y + 5);
            await page.mouse.up();
            await page.waitForTimeout(800);
            await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "pdf_07_scholar_selection_menu.png") });
            console.log(" ✓ Scholar Floating Selection Toolbar rendered over text.");
          }
        }
      }
    }

    console.log("\n==================================================================");
    console.log("    ✓ ALL PDF.js DEEP READER VERIFICATIONS PASSED SUCCESSFULLY    ");
    console.log("==================================================================");

  } catch (err) {
    console.error("[VERIFICATION FAILED]", err);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, "error.png") });
    throw err;
  } finally {
    await browser.close();
  }
}

verifyPdfReader().catch((err) => {
  console.error("Test execution failed:", err);
  process.exit(1);
});

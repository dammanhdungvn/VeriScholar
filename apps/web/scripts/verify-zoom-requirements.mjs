import { chromium } from "@playwright/test";
import path from "node:path";

const ARTIFACT_DIR = "/home/dammanhdungvn/.gemini/antigravity-cli/brain/4f584b1f-4f2c-4f74-b9c8-e23de2375d2e";

async function verifyZoom() {
  console.log("=== Verifying Zoom 100% Display with 144% Underlying Scale (+/-5% Steps) ===");

  const browser = await chromium.launch({
    executablePath: "/usr/bin/google-chrome",
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
  });

  const page = await context.newPage();

  page.on("console", (msg) => {
    if (msg.type() === "error") {
      console.log(`[BROWSER ERROR] ${msg.text()}`);
    }
  });

  const targetUrl = "http://localhost:5173/dashboard/30faba44-b53b-4aad-a76c-a8911d25aab2";
  console.log(`[STEP 1] Navigating to ${targetUrl}...`);
  await page.goto(targetUrl, { waitUntil: "networkidle", timeout: 30000 });

  // Wait for canvas / pdf page to render
  console.log("[STEP 2] Waiting for PDF page to render...");
  await page.waitForSelector("#pdf-page-1", { timeout: 15000 });
  await page.waitForTimeout(2000);

  // 1. Initial State Check
  const zoomBtn = page.locator('button[aria-label^="Đặt lại kích thước"]');
  await zoomBtn.waitFor({ state: "visible" });
  const initialZoomText = (await zoomBtn.textContent())?.trim();
  console.log(`[CHECK 1] Initial Zoom Button Text: "${initialZoomText}" (Expected: "100%")`);

  const page1Box = await page.locator("#pdf-page-1").boundingBox();
  console.log(`[CHECK 1] #pdf-page-1 rendered width: ${page1Box?.width}px (Expected: ~857px from 595.32 * 1.44)`);

  if (initialZoomText !== "100%") {
    throw new Error(`Expected initial zoom to be 100%, but got: ${initialZoomText}`);
  }
  if (!page1Box || page1Box.width < 800) {
    throw new Error(`Expected rendered width ~857px, but got: ${page1Box?.width}px`);
  }

  const s1Path = path.join(ARTIFACT_DIR, "01_zoom_100_percent_default_view.png");
  await page.screenshot({ path: s1Path, fullPage: false });
  console.log(`[SAVED] ${s1Path}`);

  // 2. Click Zoom In (+) -> Expect 105%
  console.log("[STEP 3] Clicking Zoom In button (+)...");
  const zoomInBtn = page.locator('button[aria-label="Phóng to"]');
  await zoomInBtn.click();
  await page.waitForTimeout(600);

  const zoomTextAfterIn = (await zoomBtn.textContent())?.trim();
  const page1BoxAfterIn = await page.locator("#pdf-page-1").boundingBox();
  console.log(`[CHECK 2] After +5%: "${zoomTextAfterIn}" (Expected: "105%"), width: ${page1BoxAfterIn?.width}px`);

  if (zoomTextAfterIn !== "105%") {
    throw new Error(`Expected zoom after in to be 105%, but got: ${zoomTextAfterIn}`);
  }

  const s2Path = path.join(ARTIFACT_DIR, "02_zoom_105_percent.png");
  await page.screenshot({ path: s2Path, fullPage: false });
  console.log(`[SAVED] ${s2Path}`);

  // 3. Click Zoom Out (-) -> Expect 100%
  console.log("[STEP 4] Clicking Zoom Out button (-)...");
  const zoomOutBtn = page.locator('button[aria-label="Thu nhỏ"]');
  await zoomOutBtn.click();
  await page.waitForTimeout(600);

  const zoomTextAfterOut1 = (await zoomBtn.textContent())?.trim();
  console.log(`[CHECK 3] After -5%: "${zoomTextAfterOut1}" (Expected: "100%")`);

  // 4. Click Zoom Out (-) again -> Expect 95%
  console.log("[STEP 5] Clicking Zoom Out button (-) again...");
  await zoomOutBtn.click();
  await page.waitForTimeout(600);

  const zoomTextAfterOut2 = (await zoomBtn.textContent())?.trim();
  const page1BoxAfterOut2 = await page.locator("#pdf-page-1").boundingBox();
  console.log(`[CHECK 4] After second -5%: "${zoomTextAfterOut2}" (Expected: "95%"), width: ${page1BoxAfterOut2?.width}px`);

  if (zoomTextAfterOut2 !== "95%") {
    throw new Error(`Expected zoom after 2nd out to be 95%, but got: ${zoomTextAfterOut2}`);
  }

  const s3Path = path.join(ARTIFACT_DIR, "03_zoom_95_percent.png");
  await page.screenshot({ path: s3Path, fullPage: false });
  console.log(`[SAVED] ${s3Path}`);

  // 5. Click Reset Zoom button -> Expect 100%
  console.log("[STEP 6] Clicking Reset Zoom button (95%)...");
  await zoomBtn.click();
  await page.waitForTimeout(600);

  const finalZoomText = (await zoomBtn.textContent())?.trim();
  const finalPage1Box = await page.locator("#pdf-page-1").boundingBox();
  console.log(`[CHECK 5] After Reset: "${finalZoomText}" (Expected: "100%"), width: ${finalPage1Box?.width}px`);

  if (finalZoomText !== "100%") {
    throw new Error(`Expected zoom after reset to be 100%, but got: ${finalZoomText}`);
  }

  const s4Path = path.join(ARTIFACT_DIR, "04_zoom_reset_to_100_percent.png");
  await page.screenshot({ path: s4Path, fullPage: false });
  console.log(`[SAVED] ${s4Path}`);

  console.log("\n>>> ALL ZOOM VERIFICATION CHECKS PASSED PERFECTLY! <<<");

  await browser.close();
}

verifyZoom().catch((err) => {
  console.error("Verification failed:", err);
  process.exit(1);
});

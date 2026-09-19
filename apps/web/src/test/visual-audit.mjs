import puppeteer from "puppeteer-core";
import fs from "node:fs";

const ARTIFACT_DIR = "/home/dammanhdungvn/.gemini/antigravity-cli/brain/81caa3be-8da7-478e-9823-7cb8ad107e19";
const URL = "http://localhost:5173/";

async function runVisualAudit() {
  console.log("=== Starting VeriScholar Production Visual & Console Audit ===");

  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/google-chrome",
    headless: true,
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      "--window-size=1440,900",
    ],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });

  const consoleErrors = [];
  const consoleWarnings = [];
  const failedRequests = [];

  page.on("console", (msg) => {
    if (msg.type() === "error") {
      consoleErrors.push(msg.text());
    } else if (msg.type() === "warning") {
      consoleWarnings.push(msg.text());
    }
  });

  page.on("pageerror", (err) => {
    consoleErrors.push(err.toString());
  });

  page.on("requestfailed", (request) => {
    failedRequests.push({
      url: request.url(),
      error: request.failure()?.errorText || "unknown",
    });
  });

  console.log(`Navigating to ${URL}...`);
  const response = await page.goto(URL, { waitUntil: "networkidle0", timeout: 15000 });

  const httpStatus = response?.status();
  console.log(`HTTP Status: ${httpStatus}`);

  // 1. Page Title Check
  const pageTitle = await page.title();
  console.log(`Page Title: "${pageTitle}"`);

  // 2. Headline Check
  const h1Text = await page.$eval("h1", (el) => el.textContent?.trim());
  console.log(`H1 Headline: "${h1Text}"`);

  // 3. Computed Style Verification (DESIGN.md Tokens)
  const bodyBg = await page.$eval("body", (el) => window.getComputedStyle(el).backgroundColor);
  console.log(`Body Background: ${bodyBg} (Expected rgb(250, 249, 245) for #faf9f5)`);

  const primaryBtn = await page.$('[data-testid="hero-quick-upload-btn"]');
  const btnBg = await page.evaluate((el) => el ? window.getComputedStyle(el).backgroundColor : null, primaryBtn);
  console.log(`Primary CTA Background: ${btnBg} (Expected rgb(204, 120, 92) for #cc785c)`);

  // 4. Interactive Demo Test
  console.log("Testing Interactive In-Place Demo...");
  const citationBadge = await page.$('[data-testid="demo-citation-badge"]');
  if (citationBadge) {
    await citationBadge.click();
    await new Promise((r) => setTimeout(r, 400));
    const activeBbox = await page.$('[data-testid="demo-bbox-highlight"][data-active="true"]');
    console.log(`Active Bounding Box detected: ${activeBbox !== null ? "YES (PASSED)" : "NO (FAILED)"}`);
  }

  // 5. Quick Upload Modal Test
  console.log("Testing Quick Upload Dialog Focus Trap & ESC...");
  if (primaryBtn) {
    await primaryBtn.click();
    await new Promise((r) => setTimeout(r, 400));
    const dialogVisible = await page.$eval('[role="dialog"]', (el) => el !== null).catch(() => false);
    console.log(`Dialog open state: ${dialogVisible}`);

    await page.keyboard.press("Escape");
    await new Promise((r) => setTimeout(r, 400));
    const dialogClosed = await page.$eval('[role="dialog"]', (el) => el !== null).catch(() => false);
    console.log(`Dialog closed after Escape: ${!dialogClosed}`);
  }

  // 6. Capture Desktop Screenshot
  if (!fs.existsSync(ARTIFACT_DIR)) {
    fs.mkdirSync(ARTIFACT_DIR, { recursive: true });
  }

  const desktopScreenshotPath = `${ARTIFACT_DIR}/landing_page_desktop.png`;
  await page.screenshot({ path: desktopScreenshotPath, fullPage: true });
  console.log(`Desktop fullpage screenshot saved: ${desktopScreenshotPath}`);

  // 7. Mobile Viewport & Screenshot (Viewport only, realistic mobile view)
  await page.setViewport({ width: 375, height: 812, deviceScaleFactor: 2, isMobile: true });
  await page.evaluate(() => window.scrollTo(0, 0));
  await new Promise((r) => setTimeout(r, 400));
  const mobileScreenshotPath = `${ARTIFACT_DIR}/landing_page_mobile.png`;
  await page.screenshot({ path: mobileScreenshotPath, fullPage: false });
  console.log(`Mobile viewport screenshot saved: ${mobileScreenshotPath}`);

  await browser.close();

  // Summary Report
  console.log("\n=== AUDIT RESULTS ===");
  console.log(`Console Errors: ${consoleErrors.length}`);
  if (consoleErrors.length > 0) {
    consoleErrors.forEach((e, idx) => console.log(`  [Error ${idx + 1}] ${e}`));
  }
  console.log(`Console Warnings: ${consoleWarnings.length}`);
  console.log(`Failed Requests: ${failedRequests.length}`);

  const passed = httpStatus === 200 && consoleErrors.length === 0 && failedRequests.length === 0;
  console.log(`VERIFICATION RESULT: ${passed ? "PASSED (100% CLEAN)" : "FAILED"}`);

  if (!passed) {
    process.exit(1);
  }
}

runVisualAudit().catch((err) => {
  console.error("Audit script failed:", err);
  process.exit(1);
});

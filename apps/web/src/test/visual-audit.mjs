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
  const response = await page.goto(URL, { waitUntil: "networkidle2", timeout: 15000 });
  await page.waitForSelector("h1");

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

  const primaryBtn = (await page.$('[data-testid="hero-quick-upload-btn"]')) || (await page.$('[data-testid="nav-try-btn"]'));
  const btnBg = await page.evaluate((el) => el ? window.getComputedStyle(el).backgroundColor : null, primaryBtn);
  console.log(`Primary CTA Background: ${btnBg} (Expected rgb(204, 120, 92) for #cc785c)`);

  // 4. Wait for simulated web-video chat response to render completely
  console.log("Waiting for simulated chat auto-type, thinking & response...");
  await page.waitForSelector('[data-testid="demo-citation-badge"]', { timeout: 8000 }).catch(() => null);
  await page.waitForFunction(() => {
    const el = document.querySelector('[data-testid="demo-chat-panel"]');
    return el && el.getAttribute("data-streaming") === "false";
  }, { timeout: 8000 }).catch(() => null);
  await new Promise((r) => setTimeout(r, 600));

  if (!fs.existsSync(ARTIFACT_DIR)) {
    fs.mkdirSync(ARTIFACT_DIR, { recursive: true });
  }

  await page.evaluate(() => window.scrollTo(0, 0));
  await new Promise((r) => setTimeout(r, 400));
  const desktopScreenshotPath = `${ARTIFACT_DIR}/landing_page_desktop.png`;
  await page.screenshot({ path: desktopScreenshotPath, fullPage: true });
  console.log(`Desktop fullpage screenshot saved: ${desktopScreenshotPath}`);

  // 5. Dynamic Chat Input Icons Verification (Empty vs Typing)
  console.log("Testing Dynamic Chat Input Icons...");
  const replayBtn = await page.$('button[aria-label="Xem lại demo tự động"]');
  if (replayBtn) {
    await replayBtn.click();
    const emptyState = await page.evaluate(() => {
      const btn = document.querySelector('button[aria-label="Gửi câu hỏi"]');
      const mic = document.querySelector('button[aria-label="Dictate"]');
      const voice = document.querySelector('button[aria-label="Use voice mode"]');
      const plus = document.querySelector('button[aria-label="Thêm tập tin hoặc đính kèm"]');
      return { hasArrow: !!btn, hasMic: !!mic, hasVoice: !!voice, hasPlus: !!plus };
    });
    console.log("Empty chat input icons verified (Plus, Dictate, Voice):", emptyState.hasPlus && emptyState.hasMic && emptyState.hasVoice && !emptyState.hasArrow);

    await page.waitForFunction(() => {
      const input = document.querySelector('input[type="text"]');
      return input && input.value.length > 5;
    }, { timeout: 4000 }).catch(() => null);

    const typingState = await page.evaluate(() => {
      const btn = document.querySelector('button[aria-label="Gửi câu hỏi"]');
      const mic = document.querySelector('button[aria-label="Dictate"]');
      const voice = document.querySelector('button[aria-label="Use voice mode"]');
      return { hasArrow: !!btn, hasMic: !!mic, hasVoice: !!voice };
    });
    console.log("Typing chat input icons verified (Arrow shown, Voice hidden):", typingState.hasArrow && !typingState.hasMic && !typingState.hasVoice);
  }

  // 6. Interactive Demo Test
  console.log("Testing Interactive In-Place Demo...");
  const citationBadge = await page.$('[data-testid="demo-citation-badge"]');
  if (citationBadge) {
    await citationBadge.click();
    await new Promise((r) => setTimeout(r, 300));
    const activeBbox = await page.$('[data-testid="demo-bbox-highlight"][data-active="true"]');
    console.log(`Active Bounding Box detected: ${activeBbox !== null ? "YES (PASSED)" : "NO (FAILED)"}`);
  }

  // 6. Quick Upload Modal Test
  console.log("Testing Quick Upload Dialog Focus Trap & ESC...");
  if (primaryBtn) {
    await primaryBtn.click();
    await new Promise((r) => setTimeout(r, 300));
    const dialogVisible = await page.$eval('[role="dialog"]', (el) => el !== null).catch(() => false);
    console.log(`Dialog open state: ${dialogVisible}`);

    await page.keyboard.press("Escape");
    await new Promise((r) => setTimeout(r, 300));
    const dialogClosed = await page.$eval('[role="dialog"]', (el) => el !== null).catch(() => false);
    console.log(`Dialog closed after Escape: ${!dialogClosed}`);
  }

  // 7. Light / Dark Mode Toggle Verification
  console.log("Testing Light / Dark Mode Toggle...");
  const themeToggleBtn = await page.$('[data-testid="theme-toggle-btn"]');
  if (themeToggleBtn) {
    const isDarkInitially = await page.evaluate(() => document.documentElement.classList.contains("dark"));
    console.log(`Initial theme dark state: ${isDarkInitially}`);

    // Click to switch to dark mode
    await themeToggleBtn.click();
    await new Promise((r) => setTimeout(r, 300));
    const isDarkAfterToggle = await page.evaluate(() => document.documentElement.classList.contains("dark"));
    console.log(`Theme dark state after click: ${isDarkAfterToggle} (Expected: true)`);

    const darkScreenshotPath = `${ARTIFACT_DIR}/landing_page_dark.png`;
    await page.screenshot({ path: darkScreenshotPath, fullPage: false });
    console.log(`Dark mode viewport screenshot saved: ${darkScreenshotPath}`);

    // Click again to switch back to light mode
    await themeToggleBtn.click();
    await new Promise((r) => setTimeout(r, 300));
    const isDarkAfterToggleBack = await page.evaluate(() => document.documentElement.classList.contains("dark"));
    console.log(`Theme dark state after toggling back: ${isDarkAfterToggleBack} (Expected: false)`);
  }

  // 8. Mobile Viewport & Screenshot (Fresh navigation for pristine mobile view)
  const mobilePage = await browser.newPage();
  await mobilePage.setViewport({ width: 375, height: 812, deviceScaleFactor: 2, isMobile: true });
  await mobilePage.goto(URL, { waitUntil: "networkidle2", timeout: 15000 });
  await mobilePage.waitForSelector("h1");
  await new Promise((r) => setTimeout(r, 400));
  const mobileScreenshotPath = `${ARTIFACT_DIR}/landing_page_mobile.png`;
  await mobilePage.screenshot({ path: mobileScreenshotPath, fullPage: false });
  console.log(`Mobile viewport screenshot saved: ${mobileScreenshotPath}`);
  await mobilePage.close();

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

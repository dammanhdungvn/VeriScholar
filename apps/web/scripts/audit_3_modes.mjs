import { chromium } from "@playwright/test";
import path from "node:path";

const ARTIFACT_DIR = "/home/dammanhdungvn/.gemini/antigravity-cli/brain/4f584b1f-4f2c-4f74-b9c8-e23de2375d2e";

async function main() {
  const browser = await chromium.launch({
    executablePath: "/usr/bin/google-chrome",
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
  });

  const page = await context.newPage();

  console.log("Navigating to dashboard...");
  await page.goto("http://localhost:5173/dashboard/30faba44-b53b-4aad-a76c-a8911d25aab2", {
    waitUntil: "networkidle",
    timeout: 15000,
  });

  // Wait for canvas to render
  await page.waitForSelector("canvas", { timeout: 10000 });
  await page.waitForTimeout(2000);

  // 1. Capture Default Continuous Mode (100% Zoom, No Top Header)
  console.log("Capturing 01_default_100_percent_continuous.png...");
  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "01_default_100_percent_continuous.png"),
  });

  // 2. Click Single Page mode
  console.log("Clicking Single Page mode...");
  const singleBtn = page.getByRole("radio", { name: /Trang đơn/i });
  await singleBtn.click();
  await page.waitForTimeout(1200);
  console.log("Capturing 02_single_page_mode.png...");
  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "02_single_page_mode.png"),
  });

  // 3. Click Two-Page Spread mode
  console.log("Clicking Two-Page Spread mode...");
  const twoPageBtn = page.getByRole("radio", { name: /Hai trang/i });
  await twoPageBtn.click();
  await page.waitForTimeout(1200);
  console.log("Capturing 03_two_page_spread_mode.png...");
  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "03_two_page_spread_mode.png"),
  });

  // 4. Toggle Theme to Dark Mode
  console.log("Toggling theme in sidebar...");
  const themeBtn = page.getByRole("button", { name: /Chuyển sang chế độ tối/i }).first();
  if (await themeBtn.isVisible()) {
    await themeBtn.click();
    await page.waitForTimeout(800);
    console.log("Capturing 04_dark_mode_two_page.png...");
    await page.screenshot({
      path: path.join(ARTIFACT_DIR, "04_dark_mode_two_page.png"),
    });
  }

  console.log("Audits complete!");
  await browser.close();
}

main().catch((err) => {
  console.error("Audit error:", err);
  process.exit(1);
});

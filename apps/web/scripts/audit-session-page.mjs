import { chromium } from "@playwright/test";

const SCREENSHOT_PATH = "apps/web/playwright-screenshots/session_audit.png";

async function main() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
  });

  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
  await page.goto("http://localhost:5173/dashboard/30faba44-b53b-4aad-a76c-a8911d25aab2", { waitUntil: "networkidle" });
  await page.waitForTimeout(2000);

  await page.screenshot({ path: SCREENSHOT_PATH });
  console.log("Screenshot saved to:", SCREENSHOT_PATH);

  // List toolbar buttons in paper taskbar
  const paperToolbarButtons = await page.$$eval('[role="toolbar"] button', (btns) =>
    btns.map((b) => ({
      label: b.getAttribute("aria-label") || b.getAttribute("title") || b.innerText.trim(),
      title: b.getAttribute("title"),
    }))
  );
  console.log("Paper Toolbar Buttons:", JSON.stringify(paperToolbarButtons, null, 2));

  // List header buttons
  const headerButtons = await page.$$eval('header button', (btns) =>
    btns.map((b) => ({
      label: b.getAttribute("aria-label") || b.getAttribute("title") || b.innerText.trim(),
      title: b.getAttribute("title"),
    }))
  );
  console.log("Header Buttons:", JSON.stringify(headerButtons, null, 2));

  await browser.close();
}

main().catch(console.error);

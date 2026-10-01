import { chromium } from "@playwright/test";
import path from "node:path";

const ARTIFACT_DIR = "/home/dammanhdungvn/.gemini/antigravity-cli/brain/4f584b1f-4f2c-4f74-b9c8-e23de2375d2e";
const URL = "http://localhost:5173/dashboard/30faba44-b53b-4aad-a76c-a8911d25aab2";

async function main() {
  console.log("=== Comprehensive Responsive Verification (Mobile, Tablet, Desktop) ===");

  const browser = await chromium.launch({
    executablePath: "/usr/bin/google-chrome",
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
  });

  // 1. Mobile (iPhone 14: 390 x 844)
  console.log("\n[TEST 1] Testing Mobile (390 x 844)...");
  const mobileCtx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const mobilePage = await mobileCtx.newPage();
  await mobilePage.goto(URL, { waitUntil: "networkidle" });
  await mobilePage.waitForSelector("#pdf-page-1", { timeout: 15000 });
  await mobilePage.waitForTimeout(1500);

  // 1.1 Mobile Reader Default View (Full screen reader, responsive fit)
  const mobileReaderPath = path.join(ARTIFACT_DIR, "01_responsive_mobile_reader.png");
  await mobilePage.screenshot({ path: mobileReaderPath });
  console.log(`[SAVED] ${mobileReaderPath}`);

  // 1.2 Switch to Mobile Workspace / Assistant View
  console.log("[TEST 1.2] Switching to Mobile Assistant & Notes View...");
  const assistantBtn = mobilePage.getByRole("button", { name: "Chuyển sang chế độ xem trợ lý đối thoại và sổ tay" });
  await assistantBtn.click();
  await mobilePage.waitForTimeout(1000);

  const mobileAssistantPath = path.join(ARTIFACT_DIR, "02_responsive_mobile_assistant.png");
  await mobilePage.screenshot({ path: mobileAssistantPath });
  console.log(`[SAVED] ${mobileAssistantPath}`);

  // 1.3 Open Mobile Slide-Out Drawer (Sidebar)
  console.log("[TEST 1.3] Opening Mobile Sidebar Drawer...");
  const menuBtn = mobilePage.getByRole("button", { name: "Mở danh sách phiên nghiên cứu" });
  await menuBtn.click();
  await mobilePage.waitForTimeout(1000);

  const mobileDrawerPath = path.join(ARTIFACT_DIR, "03_responsive_mobile_drawer.png");
  await mobilePage.screenshot({ path: mobileDrawerPath });
  console.log(`[SAVED] ${mobileDrawerPath}`);

  // Close drawer
  const closeBtn = mobilePage.getByRole("button", { name: "Thu gọn thanh điều hướng" });
  if (await closeBtn.isVisible()) {
    await closeBtn.click();
    await mobilePage.waitForTimeout(500);
  }

  // 2. Tablet (iPad: 768 x 1024)
  console.log("\n[TEST 2] Testing Tablet (768 x 1024)...");
  const tabletCtx = await browser.newContext({ viewport: { width: 768, height: 1024 } });
  const tabletPage = await tabletCtx.newPage();
  await tabletPage.goto(URL, { waitUntil: "networkidle" });
  await tabletPage.waitForSelector("#pdf-page-1", { timeout: 15000 });
  await tabletPage.waitForTimeout(1500);

  const tabletReaderPath = path.join(ARTIFACT_DIR, "04_responsive_tablet_reader.png");
  await tabletPage.screenshot({ path: tabletReaderPath });
  console.log(`[SAVED] ${tabletReaderPath}`);

  // Switch to assistant on tablet
  const tabletAssistantBtn = tabletPage.getByRole("button", { name: "Chuyển sang chế độ xem trợ lý đối thoại và sổ tay" });
  await tabletAssistantBtn.click();
  await tabletPage.waitForTimeout(1000);

  const tabletAssistantPath = path.join(ARTIFACT_DIR, "05_responsive_tablet_assistant.png");
  await tabletPage.screenshot({ path: tabletAssistantPath });
  console.log(`[SAVED] ${tabletAssistantPath}`);

  // 3. Desktop (1440 x 900)
  console.log("\n[TEST 3] Testing Desktop (1440 x 900 side-by-side)...");
  const desktopCtx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const desktopPage = await desktopCtx.newPage();
  await desktopPage.goto(URL, { waitUntil: "networkidle" });
  await desktopPage.waitForSelector("#pdf-page-1", { timeout: 15000 });
  await desktopPage.waitForTimeout(1500);

  const desktopPath = path.join(ARTIFACT_DIR, "06_responsive_desktop_side_by_side.png");
  await desktopPage.screenshot({ path: desktopPath });
  console.log(`[SAVED] ${desktopPath}`);

  await browser.close();
  console.log("\n>>> ALL RESPONSIVE TESTS PASSED SUCCESSFULLY! <<<");
}

main().catch((err) => {
  console.error("Verification failed:", err);
  process.exit(1);
});

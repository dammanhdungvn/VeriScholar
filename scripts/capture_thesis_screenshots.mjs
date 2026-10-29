import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

// 1. Load auth payload generated from PostgreSQL
const authRaw = fs.readFileSync('/tmp/demo_auth.json', 'utf8').trim();
const authJsonStr = authRaw.replace(/^AUTH_JSON=/, '');
const authData = JSON.parse(authJsonStr);

const TARGET_DIRS = [
  '/home/dammanhdungvn/Downloads/Workspace/VeriScholar/report-datn/figures',
  '/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.worktrees/thesis-architecture-update/report-datn/figures',
  '/home/dammanhdungvn/Downloads/Workspace/Profile_Antigravity/dungdamgg17/.gemini/antigravity-cli/brain/5f18161a-b7a6-45c1-8887-b6590666986a'
];

function saveScreenshot(filename, buffer) {
  for (const dir of TARGET_DIRS) {
    fs.mkdirSync(dir, { recursive: true });
    const targetPath = path.join(dir, filename);
    fs.writeFileSync(targetPath, buffer);
    console.log(`Saved: ${targetPath} (${buffer.length} bytes)`);
  }
}

// 2. Launch headless Chrome with remote debugging
const chrome = spawn('google-chrome', [
  '--headless',
  '--no-sandbox',
  '--disable-gpu',
  '--remote-debugging-port=9222',
  '--window-size=1440,900',
  'about:blank'
]);

await new Promise(r => setTimeout(r, 2000));

async function createCdpClient() {
  const tabs = await fetch('http://127.0.0.1:9222/json/list').then(r => r.json());
  let pageTab = tabs.find(t => t.type === 'page');
  if (!pageTab) {
    const newTab = await fetch('http://127.0.0.1:9222/json/new').then(r => r.json());
    pageTab = newTab;
  }
  const ws = new WebSocket(pageTab.webSocketDebuggerUrl);
  let id = 1;
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const msgId = id++;
    const handler = (evt) => {
      const data = JSON.parse(evt.data);
      if (data.id === msgId) {
        ws.removeEventListener('message', handler);
        if (data.error) reject(data.error);
        else resolve(data.result);
      }
    };
    ws.addEventListener('message', handler);
    ws.send(JSON.stringify({ id: msgId, method, params }));
  });

  await new Promise(r => ws.addEventListener('open', r));

  // Enable Retina 2x scale for crisp academic paper graphics
  await send('Emulation.setDeviceMetricsOverride', {
    width: 1440,
    height: 900,
    deviceScaleFactor: 2,
    mobile: false
  });

  return { ws, send };
}

const { ws, send } = await createCdpClient();

async function setAuth() {
  await send('Runtime.evaluate', {
    expression: `
      localStorage.setItem('verischolar_auth_token', ${JSON.stringify(authData.token)});
      localStorage.setItem('verischolar_refresh_token', ${JSON.stringify(authData.refreshToken)});
      localStorage.setItem('verischolar_auth_user', ${JSON.stringify(JSON.stringify(authData.user))});
    `
  });
}

// =============================================================================
// SHOT 1: Discovery Subsystem (fig_ui_discovery.png)
// =============================================================================
console.log('--- Capturing 1. Discovery Subsystem ---');
await send('Page.navigate', { url: 'http://localhost:5173/discovery' });
await new Promise(r => setTimeout(r, 2000));
await setAuth();
await send('Page.reload', {});
await new Promise(r => setTimeout(r, 2000));

// Click search chip for RAG
await send('Runtime.evaluate', {
  expression: `
    const buttons = Array.from(document.querySelectorAll('button'));
    const chip = buttons.find(b => b.textContent.includes('Retrieval Augmented Generation'));
    if (chip) chip.click();
  `
});
await new Promise(r => setTimeout(r, 3500));

const shot1 = await send('Page.captureScreenshot', { format: 'png' });
saveScreenshot('fig_ui_discovery.png', Buffer.from(shot1.data, 'base64'));

// =============================================================================
// SHOT 2: Deep Reading & Bounding Box Subsystem (fig_ui_deep_reading.png)
// =============================================================================
console.log('--- Capturing 2. Deep Reading Subsystem ---');
await send('Page.navigate', { url: 'http://localhost:5173/' });
await new Promise(r => setTimeout(r, 2500));
// Scroll precisely into interactive demo
await send('Runtime.evaluate', {
  expression: `
    const el = document.getElementById('interactive-demo');
    if (el) {
      el.scrollIntoView({ behavior: 'instant', block: 'start' });
      window.scrollBy(0, -60);
    }
  `
});
await new Promise(r => setTimeout(r, 1500));
const shot2 = await send('Page.captureScreenshot', { format: 'png' });
saveScreenshot('fig_ui_deep_reading.png', Buffer.from(shot2.data, 'base64'));

// =============================================================================
// SHOT 3: Scholar Profile & BYOK Vault Subsystem (fig_ui_profile.png)
// =============================================================================
console.log('--- Capturing 3. Scholar Profile & BYOK Subsystem ---');
await send('Page.navigate', { url: 'http://localhost:5173/settings' });
await new Promise(r => setTimeout(r, 2000));
await setAuth();
await send('Page.reload', {});
await new Promise(r => setTimeout(r, 2500));

const shot3 = await send('Page.captureScreenshot', { format: 'png' });
saveScreenshot('fig_ui_profile.png', Buffer.from(shot3.data, 'base64'));

// =============================================================================
// SHOT 4: Authoring & LaTeX Monaco Subsystem (fig_ui_writing.png)
// =============================================================================
console.log('--- Capturing 4. Authoring & LaTeX Subsystem ---');
await send('Page.navigate', { url: 'http://localhost:5173/writing' });
await new Promise(r => setTimeout(r, 2000));
await setAuth();
await send('Page.reload', {});
await new Promise(r => setTimeout(r, 3000));

const shot4 = await send('Page.captureScreenshot', { format: 'png' });
saveScreenshot('fig_ui_writing.png', Buffer.from(shot4.data, 'base64'));

ws.close();
chrome.kill();
console.log('All 4 thesis UI screenshots captured successfully!');

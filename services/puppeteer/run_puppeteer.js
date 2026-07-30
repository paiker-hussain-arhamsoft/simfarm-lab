#!/usr/bin/env node
// Puppeteer wrapper for simfarm-lab browser automation.
// Reads CLI args and writes a JSON result object to --output.

const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const args = {
    target: '',
    action: 'navigate',
    script: '',
    selector: '',
    value: '',
    headless: 'true',
    screenshot: 'false',
    output: '',
    browser: 'chromium',
    proxy: '',
  };
  for (let i = 2; i < argv.length; i++) {
    const key = argv[i];
    if (key.startsWith('--') && i + 1 < argv.length) {
      const name = key.slice(2);
      if (name in args) {
        args[name] = argv[i + 1];
        i++;
      }
    }
  }
  return args;
}

function screenshotPathFor(output) {
  const base = output.replace(/\.json$/i, '');
  return `${base}.png`;
}

(async () => {
  const args = parseArgs(process.argv);
  if (!args.target || !args.output) {
    console.error('Usage: node run_puppeteer.js --target <url> --output <json> [--action navigate|screenshot|evaluate|click|type|get_text|html|stealth] [--proxy <url>] [...]');
    process.exit(1);
  }

  const launchArgs = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--window-size=1280,720',
  ];

  if (args.proxy) {
    const proxyUrl = new URL(args.proxy);
    // Chromium's --proxy-server does not accept credentials. Pass the bare
    // server; unauthenticated proxies work, authenticated ones need an
    // unauth local forwarder or a separate proxy helper.
    launchArgs.push(`--proxy-server=${proxyUrl.protocol}//${proxyUrl.hostname}:${proxyUrl.port || 80}`);
  }

  const puppeteer = require('puppeteer');
  const browser = await puppeteer.launch({
    headless: args.headless !== 'false',
    args: launchArgs,
  });

  const result = {
    target: args.target,
    action: args.action,
    headless: args.headless !== 'false',
  };

  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 720 });
    const response = await page.goto(args.target, { waitUntil: 'networkidle2', timeout: 60000 });
    result.title = await page.title();
    result.url = page.url();
    result.status = response ? response.status() : null;

    const action = (args.action || 'navigate').toLowerCase();
    const wantsScreenshot = args.screenshot === 'true' || action === 'screenshot';
    const shotPath = screenshotPathFor(args.output);

    if (action === 'screenshot') {
      await page.screenshot({ path: shotPath, fullPage: false });
      result.screenshot = shotPath;
    } else if (action === 'evaluate') {
      if (!args.script) throw new Error('evaluate requires --script');
      result.evaluate_result = await page.evaluate((s) => { const fn = new Function(s); return fn(); }, args.script);
    } else if (action === 'click') {
      if (!args.selector) throw new Error('click requires --selector');
      await page.click(args.selector);
      result.clicked = args.selector;
    } else if (action === 'type') {
      if (!args.selector || args.value === undefined) throw new Error('type requires --selector and --value');
      await page.type(args.selector, args.value);
      result.filled = args.selector;
    } else if (action === 'get_text') {
      result.text = await page.evaluate(() => document.body.innerText);
    } else if (action === 'html') {
      result.html = await page.content();
    } else if (action === 'stealth') {
      const signals = await page.evaluate(() => ({
        userAgent: navigator.userAgent,
        webdriver: navigator.webdriver,
        plugins: navigator.plugins ? navigator.plugins.length : null,
        languages: navigator.languages,
        platform: navigator.platform,
        hardwareConcurrency: navigator.hardwareConcurrency,
        deviceMemory: navigator.deviceMemory,
        maxTouchPoints: navigator.maxTouchPoints,
        chrome: typeof window.chrome !== 'undefined',
        chromeRuntime: typeof chrome !== 'undefined' && !!chrome.runtime,
        notificationPermissions: typeof Notification !== 'undefined',
      }));
      result.signals = signals;
      const flags = [];
      if (signals.webdriver) flags.push('navigator.webdriver === true');
      if (signals.plugins === 0) flags.push('zero_plugins');
      if (!signals.chrome) flags.push('window.chrome_missing');
      result.flags = flags;
      result.stealth_grade = flags.length === 0 ? 'A' : (flags.length === 1 ? 'B' : 'C');
    } else if (action !== 'navigate' && action !== 'goto') {
      throw new Error(`Unsupported action: ${action}`);
    }

    if (wantsScreenshot && action !== 'screenshot') {
      await page.screenshot({ path: shotPath, fullPage: false });
      result.screenshot = shotPath;
    }
  } catch (err) {
    result.error = err.message;
  } finally {
    await browser.close();
  }

  fs.mkdirSync(path.dirname(args.output), { recursive: true });
  fs.writeFileSync(args.output, JSON.stringify(result, null, 2));
})();

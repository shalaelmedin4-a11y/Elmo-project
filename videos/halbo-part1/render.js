const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [,, mode, outDir, a, b] = process.argv;
  fs.mkdirSync(outDir, { recursive: true });
  const tl = fs.readFileSync(__dirname + '/timeline.json', 'utf8'), lips = fs.readFileSync(__dirname + '/lips.json', 'utf8');
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2 });
  page.on('pageerror', e => console.log('ERR', e.message));
  page.on('console', m => { if (m.type() === 'error') console.log('console:', m.text()); });
  await page.addInitScript(`window.TIMELINE=${tl};window.LIPS=${lips};`);
  await page.goto('http://127.0.0.1:8765/halbo/scene.html');
  await page.waitForFunction(() => window.renderAt && window.READY, null, { timeout: 120000 });
  await page.evaluate(() => window.READY);
  const total = await page.evaluate(() => window.TOTAL);
  let times = [];
  if (mode === 'stills') times = a.split(',').map(Number);
  else { const s = Number(a || 0), e = Math.min(Number(b || total), total); for (let f = Math.round(s * 30); f < e * 30; f++) times.push(f / 30); }
  const t0 = Date.now();
  for (const t of times) {
    await page.evaluate(t => window.renderAt(t), t);
    const name = mode === 'stills' ? `s_${t.toFixed(2)}.jpg` : `f_${String(Math.round(t * 30)).padStart(5, '0')}.jpg`;
    await page.screenshot({ path: `${outDir}/${name}`, type: 'jpeg', quality: 92 });
  }
  console.log('frames', times.length, 'sec', (Date.now() - t0) / 1000, 'total', total);
  await browser.close();
})();

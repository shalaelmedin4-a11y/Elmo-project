const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [,, mode, outDir, a, b] = process.argv; // mode: stills|video
  fs.mkdirSync(outDir, { recursive: true });
  const dur = fs.readFileSync(__dirname + '/vo/dur.json', 'utf8');
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2 });
  page.on('console', m => console.log('console:', m.text()));
  page.on('pageerror', e => console.log('ERR', e.message));
  await page.addInitScript(`window.VO_DUR=${dur}`);
  await page.goto('http://127.0.0.1:8765/index.html');
  await page.waitForFunction(() => window.renderAt && window.READY);
  await page.evaluate(() => window.READY);
  const total = await page.evaluate(() => window.TOTAL);
  const scenes = await page.evaluate(() => window.SCENES);
  fs.writeFileSync(outDir + '/scenes.json', JSON.stringify({ total, scenes }));
  let times = [];
  if (mode === 'stills') times = a.split(',').map(Number);
  else { const fps = 30, s = Number(a || 0), e = Math.min(Number(b || total), total); for (let f = Math.round(s * fps); f < e * fps; f++) times.push(f / fps); }
  const t0 = Date.now();
  for (const t of times) {
    await page.evaluate(t => window.renderAt(t), t);
    const name = mode === 'stills' ? `s_${t.toFixed(2)}.jpg` : `f_${String(Math.round(t * 30)).padStart(5, '0')}.jpg`;
    await page.screenshot({ path: `${outDir}/${name}`, type: 'jpeg', quality: 92 });
  }
  console.log('frames', times.length, 'sec', (Date.now() - t0) / 1000, 'total', total);
  await browser.close();
})();

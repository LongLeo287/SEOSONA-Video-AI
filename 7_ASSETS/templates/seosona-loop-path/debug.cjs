const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--use-gl=angle', '--use-angle=d3d11']
  });
  const page = await browser.newPage();
  
  page.on('pageerror', error => {
    console.error('PAGE ERROR CAUGHT:');
    console.error(error.message);
    console.error(error.stack);
  });

  page.on('console', msg => {
    console.log('CONSOLE:', msg.text());
  });

  await page.goto('file:///' + __dirname.replace(/\\/g, '/') + '/index.html', {waitUntil: 'networkidle0'}).catch(e => console.error("Goto error:", e));

  await browser.close();
})();

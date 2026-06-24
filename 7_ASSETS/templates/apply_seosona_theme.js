const fs = require('fs');
const path = require('path');

const basePath = 'D:/LongLeo/SEOSONA AI/SEOSONA Video/7_ASSETS/video_templates';

const seosonaRoot = `
:root {
  --bg-core: #090B14;
  --bg-deep: #05060A;
  
  --c-cyan: #40E0D0;
  --c-yellow: #FFDF00;
  --c-magenta: #FF007A;
  --c-purple: #8A2BE2;
  --c-green: #00FF88;
  
  --text-main: #FFFFFF;
  --text-dim: #8C92A6;
  --text-label: #B0B8CC;
  
  --font: 'Be Vietnam Pro', sans-serif;
}
`;

const templates = [
  {
    name: 'github-repo-showcase',
    replacements: [
      [/var\(--bg\)/g, 'var(--bg-deep)'],
      [/var\(--white\)/g, 'var(--text-main)'],
      [/var\(--gray\)/g, 'var(--text-dim)'],
      [/var\(--green\)/g, 'var(--c-green)'],
      [/var\(--yellow\)/g, 'var(--c-yellow)'],
      [/var\(--blue\)/g, 'var(--c-cyan)'],
      [/var\(--purple\)/g, 'var(--c-purple)'],
      [/rgba\(0, 255, 100,/g, 'rgba(0, 255, 136,'], // c-green rgba
    ]
  },
  {
    name: 'tech-comparison',
    replacements: [
      [/var\(--bg-dark\)/g, 'var(--bg-deep)'],
      [/var\(--bg-light\)/g, 'var(--bg-core)'],
      [/var\(--white\)/g, 'var(--text-main)'],
      [/var\(--gray\)/g, 'var(--text-dim)'],
      [/var\(--accent\)/g, 'var(--c-cyan)'],
      [/var\(--magenta\)/g, 'var(--c-magenta)'],
    ]
  },
  {
    name: 'app-review-showcase',
    replacements: [
      [/var\(--bg\)/g, 'var(--bg-deep)'],
      [/var\(--white\)/g, 'var(--text-main)'],
      [/var\(--gray\)/g, 'var(--text-dim)'],
      [/var\(--pink\)/g, 'var(--c-magenta)'],
      [/var\(--purple\)/g, 'var(--c-purple)'],
      [/var\(--green\)/g, 'var(--c-green)'],
    ]
  },
  {
    name: 'code-tutorial-showcase',
    replacements: [
      [/var\(--bg\)/g, 'var(--bg-deep)'],
      [/var\(--white\)/g, 'var(--text-main)'],
      [/var\(--gray\)/g, 'var(--text-dim)'],
      [/var\(--accent\)/g, 'var(--c-magenta)'],
      [/var\(--blue\)/g, 'var(--c-cyan)'],
      [/var\(--yellow\)/g, 'var(--c-yellow)'],
    ]
  },
  {
    name: 'product-walkthrough',
    replacements: [
      [/var\(--bg\)/g, 'var(--bg-deep)'],
      [/var\(--white\)/g, 'var(--text-main)'],
      [/var\(--gray\)/g, 'var(--text-dim)'],
      [/var\(--orange\)/g, 'var(--c-yellow)'],
      [/var\(--green\)/g, 'var(--c-cyan)'],
    ]
  },
  {
    name: 'quote-overlay-system',
    replacements: [
      [/var\(--bg\)/g, 'var(--bg-deep)'],
      [/var\(--white\)/g, 'var(--text-main)'],
      [/var\(--gray\)/g, 'var(--text-dim)'],
      [/var\(--pink\)/g, 'var(--c-magenta)'],
      [/var\(--cyan\)/g, 'var(--c-cyan)'],
    ]
  }
];

templates.forEach(t => {
  const tPath = path.join(basePath, t.name, 'index.html');
  let content = fs.readFileSync(tPath, 'utf8');
  
  // Replace the :root block
  content = content.replace(/:root\s*{[^}]*}/, seosonaRoot.trim());
  
  // Apply variable remappings
  t.replacements.forEach(r => {
    content = content.replace(r[0], r[1]);
  });
  
  fs.writeFileSync(tPath, content);
});

console.log('Successfully applied SEOSONA colors to all 6 templates.');

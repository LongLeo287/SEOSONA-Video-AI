const fs = require('fs');
const path = require('path');

const basePath = require('path').resolve(__dirname);  // portable: this templates dir

// 1. github-repo-showcase
let githubPath = path.join(basePath, 'github-repo-showcase', 'index.html');
let githubHtml = fs.readFileSync(githubPath, 'utf8');
githubHtml = githubHtml
  .replace(/KNS – Kỹ năng số thời đại AI/g, 'Tên Kênh - Slogan Kênh')
  .replace(/Eric Tran AI/g, 'Tên Kênh')
  .replace(/github.com\/wquguru\/harness-books/g, 'github.com/username/project-name')
  .replace(/A two-book series on harness engineering for coding agents/g, 'Mô tả ngắn gọn về dự án mã nguồn mở của bạn tại đây')
  .replace(/Source-guided analysis of Claude Code and Codex/g, 'Mô tả chi tiết hơn về các tính năng chính của dự án')
  .replace(/Harness Engineering: A Design Guide to Claude Code/g, 'Tên dự án hoặc tính năng nổi bật 1')
  .replace(/A close reading of Claude Code's runtime structure, focused on control planes, extension, recovery paths, and realization work split./g, 'Mô tả chi tiết cho tính năng 1. Hãy điền các thông tin quan trọng nhất của tính năng này vào đây.')
  .replace(/The Harness Design Philosophies of Claude Code and Codex/g, 'Tên dự án hoặc tính năng nổi bật 2')
  .replace(/A comparison of Claude Code and Codex through control planes, state, policy, and local governance./g, 'Mô tả chi tiết cho tính năng 2. Hãy điền các thông tin quan trọng nhất của tính năng này vào đây.')
  .replace(/wquguru \/ <a>harness-books<\/a>/g, 'username / <a>project-name</a>')
  .replace(/Bộ sách chuyên sâu/g, 'Dự án chuyên sâu')
  .replace(/về Harness Engineering/g, 'về [Chủ đề của bạn]')
  .replace(/Claude Code vs Codex/g, 'Sản phẩm A vs Sản phẩm B')
  .replace(/Sách chuyên sâu/g, 'Tính năng chính')
  .replace(/Tập 2: So sánh Codex & Claude/g, 'Tính năng: So sánh A & B')
  .replace(/Phân tích triết lý thiết kế hệ thống điều khiển bổ trợ lẫn nhau/g, 'Mô tả chi tiết so sánh giữa hai sản phẩm hoặc công nghệ.')
  .replace(/Claude:/g, 'Product A:')
  .replace(/Codex:/g, 'Product B:')
  .replace(/Harness Engineering Books/g, 'Project Documentation')
  .replace(/Add architectural breakdown of Claude Code .../g, 'Add feature A implementation ...')
  .replace(/Compare Codex sandbox limits with local cont.../g, 'Fix issue with module B ...')
  .replace(/Initial release of Harness Engineering books/g, 'Initial release of the project')
  .replace(/wquguru\/harness-books/g, 'username/project-name')
  .replace(/agent-runtime-monitor/g, 'system-monitor-tool')
  .replace(/Tập 2/g, 'Tag 2')
  .replace(/Kỷ luật hoạt động thay vì chỉ Prompts rời rạc/g, 'Mô tả phụ cho nội dung chính của phần giới thiệu này.');
fs.writeFileSync(githubPath, githubHtml);

// 2. tech-comparison
let techPath = path.join(basePath, 'tech-comparison', 'index.html');
let techHtml = fs.readFileSync(techPath, 'utf8');
techHtml = techHtml
  .replace(/Polars/g, 'Tech A')
  .replace(/pandas/g, 'Tech B')
  .replace(/KNS – Kỹ năng số thời đại AI/g, 'Tên Kênh - Slogan Kênh')
  .replace(/Eric Tran AI/g, 'Tên Kênh')
  .replace(/Senior AI Engineer/g, 'Chuyên gia')
  .replace(/2024 có nên đổi\?/g, 'Có nên chuyển đổi?');
fs.writeFileSync(techPath, techHtml);

// 3. app-review-showcase
let appPath = path.join(basePath, 'app-review-showcase', 'index.html');
let appHtml = fs.readFileSync(appPath, 'utf8');
appHtml = appHtml
  .replace(/AIDAILYONE/g, 'CHANNELNAME')
  .replace(/Kiên Trần/g, 'Tên Kênh')
  .replace(/Folo/g, 'App Name');
fs.writeFileSync(appPath, appHtml);

// 4. code-tutorial-showcase
let codePath = path.join(basePath, 'code-tutorial-showcase', 'index.html');
let codeHtml = fs.readFileSync(codePath, 'utf8');
codeHtml = codeHtml
  .replace(/yupvid.com/g, 'your-website.com')
  .replace(/json-render/g, 'your-library')
  .replace(/JSON sang View Component/g, 'Data sang Giao Diện')
  .replace(/RENDER UI TỪ JSON/g, 'TÊN TUTORIAL CỦA BẠN');
fs.writeFileSync(codePath, codeHtml);

// 5. product-walkthrough
let productPath = path.join(basePath, 'product-walkthrough', 'index.html');
let productHtml = fs.readFileSync(productPath, 'utf8');
productHtml = productHtml
  .replace(/Hoàng Anh AI 5 Phút/g, 'Tên Kênh')
  .replace(/@HoangAnhAI/g, '@tenkenh')
  .replace(/Fish Audio/g, 'Product Name')
  .replace(/Claude/g, 'AI Assistant')
  .replace(/Fish\.Audio/g, 'Product.Name');
fs.writeFileSync(productPath, productHtml);

// 6. quote-overlay-system
let quotePath = path.join(basePath, 'quote-overlay-system', 'index.html');
let quoteHtml = fs.readFileSync(quotePath, 'utf8');
quoteHtml = quoteHtml
  .replace(/NHỰT DƯƠNG/g, 'TÊN KÊNH')
  .replace(/@nhat.duong/g, '@ten.kenh')
  .replace(/Gemini/g, 'Sản phẩm')
  .replace(/GOOGLE I\/O 2025/g, 'SỰ KIỆN / NGUỒN')
  .replace(/DEMIS HASSABIS, DEEPMIND/g, 'CHUYÊN GIA')
  .replace(/SUNDAR PICHAI/g, 'CEO')
  .replace(/Omni:/g, 'Product:');
fs.writeFileSync(quotePath, quoteHtml);

console.log('Successfully cleaned up all 6 templates.');

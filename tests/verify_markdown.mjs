/**
 * P0-3 Markdown 渲染验证脚本（基于 marked 库）
 * 验证项: 代码块、图片、视频嵌入、列表、表格、h1、任务列表
 * 运行: cd frontend && node ../tests/verify_markdown.mjs
 */

import { marked } from "marked";
import { parseVideoEmbeds } from "../frontend/src/utils/videoEmbed.js";

let PASS = 0;
let FAIL = 0;

function check(name, condition, detail = "") {
  if (condition) {
    PASS++;
    console.log(`  [PASS] ${name}`);
  } else {
    FAIL++;
    console.log(`  [FAIL] ${name} — ${detail}`);
  }
}

function section(title) {
  console.log(`\n${"=".repeat(50)}`);
  console.log(`  ${title}`);
  console.log(`${"=".repeat(50)}`);
}

// --- 复制 PostDetail.vue 中的渲染逻辑 ---

const VIDEO_PLACEHOLDER_RE = /\{% *(bilibili|youtube) +\S+ *%\}/gi;

marked.setOptions({ breaks: true, gfm: true });

const renderer = new marked.Renderer();
renderer.image = function ({ href, title, text }) {
  const alt = text ? ` alt="${text}"` : "";
  return `<img src="${href}"${alt} class="post-image">`;
};

function renderMarkdown(text) {
  const videoSlots = [];
  const protectedText = text.replace(VIDEO_PLACEHOLDER_RE, (match) => {
    const idx = videoSlots.length;
    videoSlots.push(match);
    return `%%VIDEO_${idx}%%`;
  });

  let html = marked.parse(protectedText, { renderer });

  html = html.replace(/<p>%%VIDEO_(\d+)%%<\/p>/g, (_, i) => videoSlots[parseInt(i)]);
  html = html.replace(/%%VIDEO_(\d+)%%/g, (_, i) => videoSlots[parseInt(i)]);
  return parseVideoEmbeds(html);
}

// ============================================================
// 4. Markdown 代码块
// ============================================================
section("4. Markdown 代码块");

const codeInput =
  '普通文本\n\n```python\nprint("hello")\nif True:\n    pass\n```\n\n后续文本';
const codeHtml = renderMarkdown(codeInput);

check(
  "代码块被 <pre><code> 包裹",
  codeHtml.includes("<pre>") && codeHtml.includes("<code") && codeHtml.includes("</code></pre>"),
  codeHtml.substring(0, 300)
);
check(
  "代码块内容不被额外解析",
  codeHtml.includes('print(&quot;hello&quot;)') || codeHtml.includes('print("hello")'),
  codeHtml.substring(0, 300)
);
check(
  "代码块前后有段落",
  codeHtml.includes("<p>普通文本</p>") && codeHtml.includes("<p>后续文本</p>"),
  codeHtml.substring(0, 300)
);

// ============================================================
// 5. Markdown 图片
// ============================================================
section("5. Markdown 图片");

const imgInput = "![测试图片](https://example.com/test.png)";
const imgHtml = renderMarkdown(imgInput);

check(
  "图片渲染为 <img>",
  imgHtml.includes('<img src="https://example.com/test.png"'),
  imgHtml
);
check(
  "图片有 alt 属性",
  imgHtml.includes('alt="测试图片"'),
  imgHtml
);
check(
  "图片有 post-image class",
  imgHtml.includes('class="post-image"'),
  imgHtml
);

// ============================================================
// 6. Markdown 视频嵌入
// ============================================================
section("6. Markdown 视频嵌入");

const videoInput = "{% bilibili BV1xx411c7mD %}";
const videoHtml = renderMarkdown(videoInput);

check(
  "Bilibili 视频渲染为 iframe",
  videoHtml.includes("<iframe") && videoHtml.includes("bilibili"),
  videoHtml
);
check(
  "视频有 video-embed class",
  videoHtml.includes('class="video-embed"'),
  videoHtml
);

const ytInput = "{% youtube dQw4w9WgXcQ %}";
const ytHtml = renderMarkdown(ytInput);

check(
  "YouTube 视频渲染为 iframe",
  ytHtml.includes("<iframe") && ytHtml.includes("youtube"),
  ytHtml
);

// ============================================================
// 7. 无序列表 (P0-3 新增验证)
// ============================================================
section("7. 无序列表");

const ulInput = "- 第一项\n- 第二项\n- 第三项";
const ulHtml = renderMarkdown(ulInput);

check(
  "无序列表渲染为 <ul>",
  ulHtml.includes("<ul>"),
  ulHtml
);
check(
  "列表项渲染为 <li>",
  ulHtml.includes("<li>") && ulHtml.includes("第一项"),
  ulHtml
);

// ============================================================
// 8. 有序列表 (P0-3 新增验证)
// ============================================================
section("8. 有序列表");

const olInput = "1. 步骤一\n2. 步骤二\n3. 步骤三";
const olHtml = renderMarkdown(olInput);

check(
  "有序列表渲染为 <ol>",
  olHtml.includes("<ol>"),
  olHtml
);
check(
  "有序列表项渲染为 <li>",
  olHtml.includes("<li>") && olHtml.includes("步骤一"),
  olHtml
);

// ============================================================
// 9. 表格 (P0-3 新增验证)
// ============================================================
section("9. 表格");

const tableInput = "| 列1 | 列2 |\n| --- | --- |\n| A | B |\n| C | D |";
const tableHtml = renderMarkdown(tableInput);

check(
  "表格渲染为 <table>",
  tableHtml.includes("<table>"),
  tableHtml
);
check(
  "表头渲染为 <th>",
  tableHtml.includes("<th>"),
  tableHtml
);
check(
  "表格内容渲染为 <td>",
  tableHtml.includes("<td>") && tableHtml.includes("A"),
  tableHtml
);

// ============================================================
// 10. h1 标题 (P0-3 修复验证)
// ============================================================
section("10. h1 标题");

const h1Input = "# 一级标题";
const h1Html = renderMarkdown(h1Input);

check(
  "FIXED: # 渲染为 <h1>（不再是 <h2>）",
  h1Html.includes("<h1>") && !h1Html.includes("<h2>"),
  h1Html
);

// ============================================================
// 11. 任务列表 (P0-3 新增验证)
// ============================================================
section("11. 任务列表");

const taskInput = "- [x] 已完成\n- [ ] 未完成";
const taskHtml = renderMarkdown(taskInput);

check(
  "任务列表包含 checkbox",
  taskHtml.includes('type="checkbox"'),
  taskHtml
);
check(
  "已完成项 checked",
  taskHtml.includes("checked") && taskHtml.includes("已完成"),
  taskHtml
);

// ============================================================
// 汇总
// ============================================================
console.log(`\n${"=".repeat(50)}`);
console.log(`  结果: ${PASS} PASS / ${FAIL} FAIL`);
console.log(`${"=".repeat(50)}`);
process.exit(FAIL > 0 ? 1 : 0);

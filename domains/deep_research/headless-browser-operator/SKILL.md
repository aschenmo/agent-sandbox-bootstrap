---
name: headless-browser-operator
domain: deep_research
description: 类 Claude Computer Use 无头浏览器视觉与自动化交互引擎：基于 Playwright Chromium Headless，支持现代单页应用 (SPA) 动态渲染、高清全屏截图、DOM 元素智能交互（点击/表单填充/滚动）、控制台日志审计与自动化网页 PDF 导出
dependencies: [playwright]
---

# 类 Claude Computer Use 无头浏览器视觉与自动化交互引擎 (Headless Browser Operator)

## 📌 核心定位与能力矩阵
`headless-browser-operator` 在无头 Linux 沙箱中提供了等同于 Claude Computer Use 的自动化 Web 交互与视觉感知能力：
1. **现代 SPA 深度渲染**：驱动无头 Chromium 内核，无视客户端 React / Vue / Angular / Next.js 动态渲染限制，完整等待网络空闲与 DOM 挂载。
2. **多模态视觉截图捕获**：支持自定义分辨率（Viewport，默认 1920x1080）的高清全页长截图（Full-page Screenshot）或局部元素切片，供多模态模型进行视觉审查。
3. **自动化仿真交互流水线**：支持通过 CSS 选择器或文本语义模拟人类用户进行连续点击（Click）、表单键入（Fill/Type）、按键事件（Press Enter）、滚动（Scroll）以及多步骤 Batch 任务批处理。
4. **出版级网页 PDF 导出**：支持打印机样式的高保真网页转 PDF 导出，保留 CSS 矢量排版。
5. **结构化 DOM 与 Markdown 提取**：自动过滤干扰元素，提取语义清晰的 Markdown 正文与链接拓扑。

---

## 🚀 命令行调用指引

### 1. 激活技能
```bash
load_skill headless-browser-operator
```

### 2. 网页高清截图 (Screenshot)
```bash
# 捕获现代网页的高清全页长截图
python3 headless_operator.py --url "https://arxiv.org/abs/1706.03762" --action screenshot --output /tmp/outputs/screenshot.png --full-page
```

### 3. 动态提取网页结构化 Markdown 内容 (Extract)
```bash
python3 headless_operator.py --url "https://news.ycombinator.com" --action extract --output /tmp/outputs/hn_extracted.md
```

### 4. 网页一键高质量转换为 PDF (PDF Export)
```bash
python3 headless_operator.py --url "https://en.wikipedia.org/wiki/Artificial_intelligence" --action pdf --output /tmp/outputs/ai_wiki.pdf
```

### 5. 模拟交互：搜索或表单提交 (Click / Fill / Submit)
```bash
python3 headless_operator.py --url "https://example.com" --action click --selector "a" --output /tmp/outputs/after_click.png
```

### 6. 多步骤自动化流水线 (Batch Pipeline)
通过 JSON 脚本定义操作流：
```bash
python3 headless_operator.py --url "https://duckduckgo.com" --batch-steps '[
  {"action": "fill", "selector": "input[name=q]", "value": "Quantum Computing Nature"},
  {"action": "press", "selector": "input[name=q]", "value": "Enter"},
  {"action": "wait", "value": 2000},
  {"action": "screenshot", "output": "/tmp/outputs/search_results.png"}
]'
```

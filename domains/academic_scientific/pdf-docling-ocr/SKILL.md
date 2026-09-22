---
name: pdf-docling-ocr
domain: academic_scientific
description: 类 OpenAI / IBM Docling 顶刊学术文献视觉排版解析与 OCR 引擎：基于 PyMuPDF 深度版面分析，支持双栏排版智能顺序恢复、LaTeX 复杂数学公式识别与保护、多层级复杂表格 Markdown 还原与矢量/位图图表自动抽离
dependencies: [pymupdf]
---

# 类 OpenAI / IBM Docling 顶刊学术文献视觉排版解析与 OCR 引擎 (PDF Docling OCR)

## 📌 核心定位与能力矩阵
`pdf-docling-ocr` 专注于解决学术论文与技术报告在无头沙箱中排版解析困难（双栏错乱、公式乱码、表格断裂）的核心痛点：
1. **双栏/多栏阅读流恢复 (Two-Column Reading Flow Recovery)**：
   * 基于空间几何坐标（Bounding Box 拓扑聚类）自动探测分栏中缝（Gutter）。
   * 严格按照“先左栏从上至下、再右栏从上至下”的学者阅读顺序恢复正文流，彻底消除传统文本提取中左右两栏内容交错拼接的问题。
2. **多层级学术表格精准还原 (Markdown Tables Extraction)**：
   * 智能识别表格边界与网格线（Tabular Grid & Borderless Layout）。
   * 自动将单元格数据规整为标准 GitHub 风格 Markdown 表格（`| col1 | col2 |`），保留对齐与表头结构。
3. **LaTeX 数学公式与特殊符号保真 (LaTeX Formula Preservation)**：
   * 识别行内公式（`$...$`）与独立行间公式（`$$...$$`）。
   * 保真希腊字母（$\alpha, \beta, \gamma$）、积分微分号、上下标与矩阵结构。
4. **图表与插图自动抽离 (Figure & Image Extraction)**：
   * 自动抽离嵌入的插图与高分辨率位图，归档至 `images/` 子目录。
   * 自动抓取图表说明（Figure Caption / Table Caption）并完成图文交叉索引。
5. **结构化 AST 与纯净 Markdown 双轨交付**：
   * 同步输出出版级学术 Markdown (`parsed_paper.md`) 与结构化版面树 JSON (`layout_structure.json`)。

---

## 🚀 命令行调用指引

### 1. 激活技能
```bash
load_skill pdf-docling-ocr
```

### 2. 解析任意学术论文 PDF
```bash
python3 parse_docling.py -i /path/to/nature_paper.pdf -o /tmp/outputs/docling_out/ --extract-images
```

### 3. 一键运行内置顶刊双栏论文测试（Demo 模式）
```bash
python3 parse_docling.py --demo -o /tmp/outputs/docling_demo/ --extract-images
```

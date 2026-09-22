---
name: office-cli
domain: academic_scientific
description: 专为 AI Agent 设计的原生 Office 全功能套件：无需安装 Microsoft Office 或 LibreOffice 即可实现 DOCX/XLSX/PPTX 毫秒级创建、DOM 级精准编辑、公式自动求值、批量指令处理与无头 HTML/SVG 渲染预览
dependencies: []
---

# AI 原生 Office 全功能自动化套件 (OfficeCLI)

## 📌 核心定位与架构优势
`office-cli` 解决了在轻量化 Linux 容器与无头云端沙箱中无法低成本、高保真操作 Microsoft Office 文件的核心痛点：
1. **无需安装 Office / LibreOffice**：基于独立自包含 C# 原生二进制引擎，单文件仅 ~33MB，毫秒级冷启动，零外部依赖。
2. **三位一体格式支持**：全面覆盖 Word (`.docx`)、Excel (`.xlsx`)、PowerPoint (`.pptx`) 的全生命周期生命管理（创建、查询、修改、删除、合并、校验）。
3. **AI 闭环视觉自检（“给 Agent 装上眼睛”）**：内置原生渲染引擎，支持一键将文档渲染为精美 HTML 或 SVG（`officecli view <doc> html/svg`），让 Agent 能够预览布局、检测排版溢出与格式缺陷并自主修正。
4. **Excel 内部公式计算引擎**：内置计算引擎（支持 `SUM`, `AVERAGE`, `IF`, `VLOOKUP`, `INDEX`, `MATCH` 等），修改数据后无需外部 Office 进程即可自动算出结果。
5. **常驻内存与高性能批处理**：支持 `resident` 常驻模式（`open` / `save` / `close`）与 JSON 批量指令处理（`batch`），极度适合多步骤连续排版任务。
6. **OpenXML 兜底保底机制**：提供 `raw` 与 `raw-set` 接口，支持对底层 OpenXML AST 进行直接操作，满足任意极端特殊排版需求。

---

## 🚀 核心工作流规范 (Mental Model)

推荐遵循 **L1（查验与视图） → L2（DOM 路径式操作） → L3（批量与 OpenXML 回退）** 的渐进式策略：

### 1. 激活技能
```bash
load_skill office-cli
```

### 2. 常用操作命令集

#### 📄 Word 文档 (`.docx`)
```bash
# 1. 创建空白文档并保持常驻
officecli create report.docx

# 2. 添加段落与标题
officecli add report.docx /body --type paragraph --prop style="Heading 1" --prop text="Nature Machine Intelligence 研究综述"
officecli add report.docx /body --type paragraph --prop text="随着大语言模型与多模态架构的迅速演进..."

# 3. 添加表格
officecli add report.docx /body --type table --prop rows=3 --prop cols=3

# 4. 查看文档结构与统计
officecli view report.docx outline
officecli view report.docx stats

# 5. 渲染为 HTML 进行排版自检
officecli view report.docx html > /tmp/report_preview.html

# 6. 保存并释放句柄
officecli close report.docx
```

#### 📊 Excel 电子表格 (`.xlsx`)
```bash
# 1. 创建表格
officecli create data_analysis.xlsx

# 2. 设置单元格数据与公式
officecli set data_analysis.xlsx "Sheet1!A1" --prop value=100
officecli set data_analysis.xlsx "Sheet1!A2" --prop value=200
officecli set data_analysis.xlsx "Sheet1!A3" --prop formula="SUM(A1:A2)"

# 3. 校验公式自动计算值 (无需 Excel 即可查看 A3=300)
officecli view data_analysis.xlsx text

# 4. 批量导入 CSV/TSV
officecli import data_analysis.xlsx "Sheet1!A5" raw_metrics.csv

# 5. 保存并关闭
officecli close data_analysis.xlsx
```

#### 📽️ PowerPoint 演示文稿 (`.pptx`)
```bash
# 1. 创建演示文稿
officecli create presentation.pptx

# 2. 新增幻灯片与文本框/形状
officecli add presentation.pptx / --type slide
officecli add presentation.pptx /slide[1] --type shape --prop text="项目年度汇报" --prop x="60pt" --prop y="80pt" --prop width="400pt" --prop height="60pt"

# 3. 查看幻灯片文本
officecli view presentation.pptx text

# 4. 保存
officecli close presentation.pptx
```

---

## 🐍 Python 辅助调用模块

本技能附带 `office_helper.py` 工具库，可在 Python 代码中实现无缝调用：

```python
from office_helper import OfficeHelper

helper = OfficeHelper()

# 创建 Word 文档并追加内容
helper.create_docx("output.docx")
helper.add_heading("output.docx", "实验结果分析", level=1)
helper.add_paragraph("output.docx", "本实验在 8 张 H100 GPU 上进行了消融验证。")

# 导出 HTML 预览
html_code = helper.render_html("output.docx")
```

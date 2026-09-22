---
name: code-interpreter-pro
domain: academic_scientific
description: OpenAI 风格高级数据分析器 (Code Interpreter / ADA)：全自动探索性数据分析 (EDA)、统计指标度量、相关性分析与交互式数据大屏 HTML 自动总装
dependencies: [pandas, numpy]
---

# OpenAI 风格高级数据分析器 (Code Interpreter Pro)

## 📌 核心定位与能力矩阵
`code-interpreter-pro` 还原并增强了 OpenAI ChatGPT 官方代码解释器（Advanced Data Analysis）的数据处理全流程能力：
1. **多格式数据无缝吞吐**：原生支持 CSV、TSV、Excel (.xlsx)、Parquet、JSON 格式自动推断与摄入。
2. **深度自动化探索性分析 (EDA)**：
   * 自动探测样本量、特征维度与内存占用。
   * 细粒度缺失值（Missingness Rate）与数据质量画像。
   * 全自动数值变量分布测度：均值、标准差、四分位数（IQR）、偏度（Skewness）。
   * 分类变量基数分布与频数统计。
   * 皮尔逊（Pearson）特征相关性矩阵。
3. **单文件交互式 HTML 数据大屏**：一键生成自包含的数据看板（指标卡片、统计指标表、质量审计列表与原始数据切片浏览器），可直接在任何浏览器离线打开。

---

## 🚀 命令行调用指引

### 1. 激活技能
```bash
load_skill code-interpreter-pro
```

### 2. 分析任意数据集并导出分析报告与网页大屏
```bash
python3 run_interpreter.py -i clinical_data.csv -o /tmp/outputs/eda_report/ --dashboard
```

### 3. 一键运行合成科研演示数据集（Demo 模式）
```bash
python3 run_interpreter.py --demo -o /tmp/outputs/eda_demo/ --dashboard
```

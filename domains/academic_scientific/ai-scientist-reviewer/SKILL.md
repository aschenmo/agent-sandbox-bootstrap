---
name: ai-scientist-reviewer
domain: academic_scientific
description: Sakana AI 风格自动化科研创意与同行评审自检系统：面向学术论文、技术方案与实验代码，从立论逻辑、方法学新颖性、基线对比、消融严谨性等 8 个顶刊维度自动生成量化评审报告、致命漏洞攻击向量与交互式雷达图大屏
dependencies: [numpy]
---

# Sakana AI 风格自动化科研评审自检系统 (AI Scientist Reviewer)

## 📌 核心定位与能力矩阵
`ai-scientist-reviewer` 灵感源自 Sakana AI 的自动化科学研究智能体 (The AI Scientist) 同行评审体系：
1. **8 大顶刊同行评审量化评估 (8-Dimensional Rubric)**：
   * **立论严密性 (Clarity & Framing)**：科学问题界定、动机清晰度与逻辑链完整性。
   * **方法新颖性 (Method Novelty)**：理论推导、架构创新与领域贡献度。
   * **基线充分性 (Baseline Rigor)**：前沿 SOTA 对比的充分性与实验公平性（Fair Benchmarking）。
   * **消融严谨性 (Ablation Depth)**：核心模块有效性验证与超参数敏感性探测。
   * **证据匹配度 (Evidence Alignment)**：实验数据对核心 Claim 的因果支撑力度。
   * **复现健康度 (Reproducibility & Hygiene)**：随机种子多轮次运行、置信区间 ($p$-value) 与开源规范。
   * **局限性自诚 (Limitation Honesty)**：Corner Case 失败案例探讨与边界条件明确度。
   * **社会学术影响 (Ethical & Impact)**：学术伦理合规性与未来科研拓展价值。
2. **致命审查漏洞预警 (Reviewer Attack Vectors)**：
   * 自动探测顶会/顶刊（NeurIPS / ICML / Nature / IEEE）严苛审稿人最可能发起致命反击的 3 大薄弱点。
3. **针对性补全与答辩路线图 (Actionable Roadmap)**：
   * 自动生成实验补齐指南（建议补充的消融组与对比 Baseline）。
4. **单文件交互式 HTML 评审雷达图看板**：
   * 自动绘制出版级 SVG 八维蜘蛛雷达图（Radar Chart），支持多维度下钻与结论评审卡片交互。

---

## 🚀 命令行调用指引

### 1. 激活技能
```bash
load_skill ai-scientist-reviewer
```

### 2. 对论文稿件或实验代码发起全自动同行评审
```bash
python3 review_scientist.py -i /path/to/paper.pdf -o /tmp/outputs/review_dir/ --dashboard
```

### 3. 一键运行内置科研方案演示审查（Demo 模式）
```bash
python3 review_scientist.py --demo -o /tmp/outputs/review_demo/ --dashboard
```

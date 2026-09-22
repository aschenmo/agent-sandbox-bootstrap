---
name: science-skills
domain: academic_scientific
description: Google DeepMind Science-Skills 深度科研与计算生物/化学工具集（整合 AlphaFold DB 3D结构预测、UniProt 蛋白质序列与功能注释、RCSB PDB 实验结构解析与 PubChem 分子药效团物理化学参数）
dependencies: [requests, urllib3]
---

# Google DeepMind 科研与生命科学工具集 (Science-Skills)

## 📌 核心功能与科学数据源矩阵
`science-skills` 面向计算生物学、生物医药研发、结构生物学与计算化学场景，提供与 Google DeepMind 学术基础设施无缝集成的自动化检索与数据流水线：

| 模块名称 | 核心数据源 / 协议 | 能力与提取指标 | 凭据与限制 |
| :--- | :--- | :--- | :---: |
| **AlphaFold 3D结构** | **AlphaFold DB (EBI)** | 蛋白质单体/复合体预测三维坐标、残基级 pLDDT 置信度、PAE 图像与 PDB 结构下载 | 🌟 完全免费免 Key |
| **蛋白质功能序列** | **UniProt Knowledgebase** | 氨基酸序列 (FASTA)、基因名、物种分类 TaxID、推荐命名、活性位点与生物学功能摘要 | 🌟 完全免费免 Key |
| **实验级大分子结构** | **RCSB Protein Data Bank** | X射线衍射 / 冷冻电镜 (Cryo-EM) 分辨率、实验方法、原始发表文献 DOI 与 PDB 文件下载 | 🌟 完全免费免 Key |
| **小分子化学与药效学** | **PubChem PUG-REST** | 分子式、分子量、Canonical SMILES、InChIKey、XLogP、TPSA、Lipinski 药物五规则评估 | 🌟 完全免费免 Key |

---

## 🚀 命令行调用指引

### 1. 激活技能
```bash
load_skill science-skills
```

### 2. 检索并下载 AlphaFold 预测蛋白质结构 (以人类 p53 P04637 为例)
```bash
python3 science_tools.py -m alphafold -q "P04637" -d /tmp/outputs/alphafold/
```

### 3. 查询 UniProt 蛋白质序列与功能注释
```bash
# 通过 Accession 或蛋白名称检索
python3 science_tools.py -m uniprot -q "EGFR"
python3 science_tools.py -m uniprot -q "P00533"
```

### 4. 检索 RCSB PDB 实验三维结构元数据与下载 PDB 文件 (以血红蛋白 1A3N 为例)
```bash
python3 science_tools.py -m pdb -q "1A3N" -d /tmp/outputs/pdb/
```

### 5. 查询化合物分子性质与 Lipinski 五规则药物相似性分析
```bash
# 输入小分子通用名或 CID
python3 science_tools.py -m molecule -q "aspirin" -o /tmp/outputs/aspirin_props.json
python3 science_tools.py -m molecule -q "imatinib"
```

### 6. 智能自动模式 (Auto-Detect)
```bash
# 自动识别 PDB ID、Accession 或化合物名称
python3 science_tools.py -q "curcumin"
```

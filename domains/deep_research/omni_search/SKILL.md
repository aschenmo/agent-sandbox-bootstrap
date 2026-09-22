---
name: omni_search
domain: deep_research
description: OmniSearch 2.0 全源统一学术前沿情报与中英文检索调度引擎（聚合 PubMed, S2, OpenAlex, arXiv, SciVerse, Unpaywall, PubChem, Tavily, Brave, 百度, 知乎, 维基百科）
required_keys: [PUBMED_API_KEY, SEMANTIC_SCHOLAR_API_KEY, OPENALEX_KEY, TAVILY_API_KEY, BRAVE_SEARCH_API_KEY]
optional_keys: [SCIVERSE_API_TOKEN, ZHIHU_API_KEY, FIRECRAWL_API_KEY]
---

# OmniSearch 2.0 全源统一科研检索引擎 (Omni-Search Skill)

## 📌 核心功能与检索矩阵 (12-in-1)
`omni_search` 是专为 AI 科研工作流量身打造的高并发跨学科全域检索中枢：

| 引擎类别 | 检索源 / 协议 | 覆盖学科与核心优势 | 访问凭据 / 门槛 |
| :--- | :--- | :--- | :---: |
| **国际权威文献** | **PubMed (NCBI)** | 生物医药、临床医学、生命科学全球金标准 | ✅ 凭据已就绪 |
| **国际权威文献** | **Semantic Scholar** | 计算机科学、人工智能、高被引文献（Influential Citations） | ✅ 凭据已就绪 |
| **国际权威文献** | **OpenAlex** | 2.5亿+ 全球开放科学元数据、学者图谱与基金资助 | ✅ 凭据已就绪 |
| **最前沿预印本** | **arXiv API** | 计算机、物理、数学、机器学习最前沿预印本（零时延直出 PDF 直链） | 🌟 完全免费免 Key |
| **顶刊全文证据** | **Elsevier SciVerse** | 直通爱思唯尔旗下顶级期刊证据与高置信度 RAG 片段 | ✅ 凭据已就绪 |
| **OA 全文解析** | **Unpaywall API** | 输入任一论文 DOI，秒级解析合法免费开源 PDF 全文直链 | 🌟 免费 (带邮箱认证) |
| **化学分子数据** | **PubChem PUG REST** | 分子式、分子量、Canonical SMILES、IUPAC 命名与 CID 档案 | 🌟 完全免费免 Key |
| **全网 AI 情报** | **Tavily AI Search** | 专为科研优化的高密度事实总结与权威报道过滤 | ✅ 凭据已就绪 |
| **独立全球索引** | **Brave Search** | 独立于谷歌/必应的全球网页索引与开发者技术文档 | ✅ 凭据已就绪 |
| **中文生态搜索** | **百度搜索 (Baidu)** | 中文互联网科技前沿、中文学术期刊与百度百科权威定义 | 🌟 原生支持+代理托底 |
| **专业垂直社区** | **知乎检索 (Zhihu)** | 中文高质量深度讨论、专家见解与专栏分析（零风控直通） | 🌟 原生支持+Brave代理 |
| **权威百科全书** | **维基百科 (Wikipedia)** | 中英双语百科词条定义、背景脉络与术语标准规范 | 🌟 完全免费免 Key |
| **正文高保真穿透** | **Firecrawl / Native** | 穿透任意网页 URL，过滤杂质并清洗为干净结构化 Markdown | ✅ 智能无感回退 |

---

## 🚀 命令行调用指引

### 1. 激活技能
```bash
load_skill omni_search
```

### 2. 全域多源并发综合调研 (默认模式)
```bash
# 自动探测中英文，并发调用学术库 + 全网 + 中文社区
python3 search_omni.py -q "solid state battery LLZO electrolyte" --mode all --limit 4
```

### 3. 权威学术顶刊与预印本专用检索 (PubMed + S2 + OpenAlex + arXiv + SciVerse)
```bash
python3 search_omni.py -q "CRISPR off-target detection methods" --mode academic --limit 5
```

### 4. 中文生态与专业社区专检 (知乎 + 百度 + 中文维基)
```bash
python3 search_omni.py -q "固态电解质 离子电导率 最新突破" --mode chinese --limit 3
```

### 5. 一键解析论文免费正版 PDF 全文直链 (Unpaywall)
```bash
python3 search_omni.py --doi "10.1038/nature12373"
```

### 6. 一键查询化学分子参数与 SMILES 结构式 (PubChem)
```bash
python3 search_omni.py --compound "aspirin"
# 或直接进入化学交叉检索模式
python3 search_omni.py -q "curcumin" --mode chemical
```

### 7. 深度穿透抓取网页正文转 Markdown
```bash
python3 search_omni.py --scrape "https://arxiv.org/abs/2301.00001" -o /tmp/paper_page.md
```

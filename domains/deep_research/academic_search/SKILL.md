---
name: academic_search
domain: deep_research
description: 整合 PubMed、Semantic Scholar 与 OpenAlex 三大权威学术引擎的高并发文献检索工具
required_keys: [PUBMED_API_KEY, SEMANTIC_SCHOLAR_API_KEY, OPENALEX_KEY]
---

# 学术文献检索技能 (Academic Search Skill)

## 📌 功能描述
通过单一接口并发聚合查询全球权威生物医学与综合交叉学科文献库：
- **PubMed**: 生物医学与生命科学权威索引
- **Semantic Scholar**: AI 增强学术图谱与引用分析
- **OpenAlex**: 全球最大开放科学文献与学者网络

## 🚀 命令行调用方法
```bash
# 1. 快速查询文献
python3 search_academic.py --query "zinc-ion battery manganese oxide cathode" --limit 10

# 2. 导出为结构化 Markdown / JSON
python3 search_academic.py --query "CRISPR gene editing therapeutics" --format markdown --output /tmp/inputs/literature.md
```

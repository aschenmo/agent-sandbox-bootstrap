---
name: graph-literature-retrieval
domain: deep_research
description: 异步图谱知识检索与文献拓扑推理系统（文献知识实体抽取、方法-任务-指标关系网络、引用拓扑与交互式图谱生成）
dependencies: [networkx, urllib3]
optional_keys: [SEMANTIC_SCHOLAR_API_KEY]
---

# 异步图谱知识检索与文献拓扑推理系统 (Graph-based Literature Retrieval)

## 📌 核心定位与技术架构
`graph-literature-retrieval` 旨在将海量非结构化文献与论文摘要，转化为富含语义推理能力的**有向知识图谱网络 (Directed Knowledge Graph)**：
1. **多源并发文献采集**：高并发异步请求 arXiv 与 Semantic Scholar 学术检索接口，或直接解析本地论文集合/PDF摘要。
2. **结构化实体与关系三元组抽取**：
   * **实体分类**：`Method`（方法/架构）、`Task`（科研任务/问题）、`Dataset`（基准数据集）、`Metric`（评价指标）、`Concept`（专业术语）。
   * **语义关系**：`proposes`、`addresses`、`applies_to`、`benchmarked_on`、`evaluated_by`、`utilizes`。
3. **图论拓扑与中心度度量**：基于 NetworkX 计算 PageRank、出入度（In/Out-degree），识别领域核心奠基方法与热点问题。
4. **跨概念最短推导路径求解**：求解两个看似不相关的科研概念（如 `Transformer` 与 `Diffusion`）在文献网络中的最短逻辑传导链路。
5. **交互式 HTML 拓扑总装交付**：输出单文件完全自包含的交互式力导向拓扑图（vis-network），支持节点拖拽、高亮聚类与悬停探查。

---

## 🚀 命令行调用指引

### 1. 激活技能
```bash
load_skill graph-literature-retrieval
```

### 2. 自动化前沿文献图谱构建与网页可视化输出
```bash
# 检索特定学术主题，构建知识图谱并导出 JSON 和交互式 HTML
python3 build_graph.py -q "multi agent autonomous reasoning" --limit 6 -o /tmp/outputs/graph.json --html /tmp/outputs/graph.html
```

### 3. 探寻跨概念最短推导路径 (Shortest Reasoning Path)
```bash
python3 build_graph.py -q "diffusion transformer generation" --find-path "Transformer" "Diffusion"
```

### 4. 解析本地已有文献或摘要集
```bash
python3 build_graph.py -i /tmp/inputs/papers.json -o /tmp/outputs/local_graph.json --html /tmp/outputs/local_graph.html
```

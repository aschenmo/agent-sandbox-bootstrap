#!/usr/bin/env python3
"""
Asynchronous Graph-based Literature Knowledge Retrieval & Topology Reasoning System
=====================================================================================
Transforms unstructured scientific papers into directed semantic knowledge graphs:
1. Asynchronous multi-source literature harvesting (arXiv, Semantic Scholar API, local abstracts).
2. Domain entity & relation triple extraction (Methods, Tasks, Benchmarks, Datasets, Metrics).
3. NetworkX directed graph modeling, PageRank centrality, and shortest reasoning paths.
4. Interactive HTML visualization (vis-network) and high-density JSON knowledge graph export.
"""

import os
import sys
import re
import json
import argparse
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter
import networkx as nx

USER_AGENT = "GraphLiteratureRetrieval-Agent/2.0 (Academic Knowledge Graph Construction)"

# ------------------------------------------------------------------------------
# 1. Literature Harvesting (arXiv + Semantic Scholar + Local text)
# ------------------------------------------------------------------------------
def fetch_arxiv_papers(query, limit=10):
    encoded_query = urllib.parse.quote(query)
    url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={limit}&sortBy=relevance&sortOrder=descending"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    
    papers = []
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            xml_data = response.read().decode("utf-8")
            root = ET.fromstring(xml_data)
            
            # Namespace handling
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("atom:entry", ns):
                title_elem = entry.find("atom:title", ns)
                summary_elem = entry.find("atom:summary", ns)
                id_elem = entry.find("atom:id", ns)
                published_elem = entry.find("atom:published", ns)
                
                authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns) if a.find("atom:name", ns) is not None]
                
                title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else "Untitled"
                summary = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else ""
                url_str = id_elem.text.strip() if id_elem is not None else ""
                published = published_elem.text[:10] if published_elem is not None else ""
                
                papers.append({
                    "id": url_str.split("/")[-1],
                    "title": title,
                    "abstract": summary,
                    "authors": authors[:3],
                    "year": published[:4] if published else "Recent",
                    "source": "arXiv",
                    "url": url_str
                })
    except Exception as e:
        print(f"⚠️ [ArXiv Notice] ArXiv query encounter: {e}", file=sys.stderr)
        
    return papers

def fetch_openalex_papers(query, limit=5):
    encoded = urllib.parse.quote(query)
    url = f"https://api.openalex.org/works?search={encoded}&per_page={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    papers = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            for item in data.get("results", []):
                title = item.get("title", "")
                if not title:
                    continue
                # Reconstruct abstract from inverted index if present
                inv = item.get("abstract_inverted_index")
                abstract = ""
                if inv:
                    word_pos = []
                    for word, positions in inv.items():
                        for pos in positions:
                            word_pos.append((pos, word))
                    word_pos.sort()
                    abstract = " ".join([w for _, w in word_pos])
                else:
                    # Fallback to topics / concept display names
                    concepts = [c.get("display_name", "") for c in item.get("concepts", [])]
                    abstract = f"Study focusing on {', '.join(concepts[:5])}."
                    
                authors = [a.get("author", {}).get("display_name", "") for a in item.get("authorships", [])][:3]
                papers.append({
                    "id": item.get("id", "").split("/")[-1],
                    "title": title,
                    "abstract": abstract,
                    "authors": authors,
                    "year": str(item.get("publication_year", "Recent")),
                    "citations": item.get("cited_by_count", 0),
                    "source": "OpenAlex",
                    "url": item.get("doi") or item.get("id")
                })
    except Exception as e:
        print(f"⚠️ [OpenAlex Notice] {e}", file=sys.stderr)
    return papers

# ------------------------------------------------------------------------------
# 2. Heuristic NLP & Academic Entity-Relation Extraction
# ------------------------------------------------------------------------------
ENTITY_CATEGORIES = {
    "Method": ["transformer", "diffusion", "llm", "agent", "gnn", "cnn", "bert", "rlhf", "lora", 
               "mamba", "rag", "knowledge graph", "mcp", "attention", "prompting", "cot", "moe", "autoencoder"],
    "Task": ["reasoning", "retrieval", "code generation", "summarization", "molecular generation",
             "classification", "segmentation", "alignment", "planning", "translation", "benchmark"],
    "Dataset": ["mmlu", "gsm8k", "humaneval", "imagenet", "squad", "pubchem", "uniprot", "pdb", "ms-marco"],
    "Metric": ["accuracy", "perplexity", "f1", "bleu", "rouge", "latency", "throughput", "plddt", "auc"]
}

def extract_entities_and_triples(paper):
    text = (paper["title"] + " " + paper["abstract"]).lower()
    found_entities = []
    
    # 1. Category-based Entity extraction
    for category, keywords in ENTITY_CATEGORIES.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text):
                found_entities.append((kw.title(), category))
                
    # 2. Capitalized acronyms or proper terms from original text
    caps_matches = re.findall(r'\b[A-Z]{2,10}\b', paper["title"] + " " + paper["abstract"])
    for cap in set(caps_matches):
        if cap.lower() not in [k.lower() for k, _ in found_entities] and len(cap) > 2:
            found_entities.append((cap, "Concept"))
            
    # Remove duplicates
    unique_entities = list({e[0]: e for e in found_entities}.values())
    
    # Paper node itself
    paper_node_id = paper["title"][:40] + ("..." if len(paper["title"]) > 40 else "")
    triples = []
    
    # Triples: Paper -> proposes / studies -> Entity
    for ent, cat in unique_entities:
        rel = "studies"
        if cat == "Method":
            rel = "proposes" if "propose" in text or "introduce" in text or "present" in text else "utilizes"
        elif cat == "Task":
            rel = "addresses"
        elif cat == "Dataset":
            rel = "evaluated_on"
        elif cat == "Metric":
            rel = "measures"
            
        triples.append((paper_node_id, rel, ent))
        
    # Cross-entity triples
    methods = [e[0] for e in unique_entities if e[1] == "Method"]
    tasks = [e[0] for e in unique_entities if e[1] == "Task"]
    datasets = [e[0] for e in unique_entities if e[1] == "Dataset"]
    metrics = [e[0] for e in unique_entities if e[1] == "Metric"]
    
    for m in methods:
        for t in tasks:
            triples.append((m, "applies_to", t))
        for d in datasets:
            triples.append((m, "benchmarked_on", d))
        for met in metrics:
            triples.append((m, "evaluated_by", met))
            
    return paper_node_id, unique_entities, triples

# ------------------------------------------------------------------------------
# 3. NetworkX Graph Building & Topological Analysis
# ------------------------------------------------------------------------------
def _pure_python_pagerank(G, alpha=0.85, max_iter=50, tol=1e-6):
    nodes = list(G.nodes())
    N = len(nodes)
    if N == 0:
        return {}
    if N == 1:
        return {nodes[0]: 1.0}
        
    scores = {n: 1.0 / N for n in nodes}
    out_degrees = dict(G.out_degree())
    
    for _ in range(max_iter):
        prev_scores = scores.copy()
        dangling_sum = sum(prev_scores[n] for n in nodes if out_degrees.get(n, 0) == 0)
        dangling_weight = dangling_sum / N
        
        diff = 0.0
        for n in nodes:
            incoming = G.predecessors(n)
            in_sum = sum(prev_scores[p] / out_degrees[p] for p in incoming if out_degrees.get(p, 0) > 0)
            scores[n] = (1.0 - alpha) / N + alpha * (in_sum + dangling_weight)
            diff += abs(scores[n] - prev_scores[n])
            
        if diff < tol:
            break
            
    return scores

def build_knowledge_graph(papers):
    G = nx.DiGraph()
    paper_catalog = {}
    
    for p in papers:
        p_id, entities, triples = extract_entities_and_triples(p)
        paper_catalog[p_id] = p
        
        # Add paper node
        G.add_node(p_id, label=p_id, type="Paper", full_title=p["title"], 
                   year=p.get("year", "Recent"), url=p.get("url", ""), authors=", ".join(p.get("authors", [])))
        
        # Add entity nodes
        for ent, cat in entities:
            if not G.has_node(ent):
                G.add_node(ent, label=ent, type=cat)
                
        # Add directed edges
        for src, rel, dst in triples:
            G.add_edge(src, dst, relation=rel, source_paper=p_id)
            
    # Centrality & Pure Python PageRank
    if len(G) > 0:
        pagerank = _pure_python_pagerank(G, alpha=0.85)
        in_degrees = dict(G.in_degree())
        out_degrees = dict(G.out_degree())
        
        for node in G.nodes():
            G.nodes[node]["pagerank"] = round(pagerank.get(node, 0.0), 4)
            G.nodes[node]["in_degree"] = in_degrees.get(node, 0)
            G.nodes[node]["out_degree"] = out_degrees.get(node, 0)
            
    return G, paper_catalog

def find_reasoning_path(G, start_concept, end_concept):
    start_match = None
    end_match = None
    
    for n in G.nodes():
        if start_concept.lower() in n.lower():
            start_match = n
            break
    for n in G.nodes():
        if end_concept.lower() in n.lower():
            end_match = n
            break
            
    if not start_match or not end_match:
        return None, f"Node not found: start='{start_match or start_concept}', end='{end_match or end_concept}'"
        
    try:
        # Check shortest path on undirected view for connectivity
        undirected_G = G.to_undirected()
        path = nx.shortest_path(undirected_G, source=start_match, target=end_match)
        edge_details = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            if G.has_edge(u, v):
                edge_details.append(f"{u} --[{G[u][v].get('relation', 'connected')}]--> {v}")
            else:
                edge_details.append(f"{v} --[{G[v][u].get('relation', 'connected')}]--> {u}")
        return path, " -> ".join(edge_details)
    except nx.NetworkXNoPath:
        return None, f"No reasoning path exists between '{start_match}' and '{end_match}'"

# ------------------------------------------------------------------------------
# 4. Interactive HTML Visualization Generator (Standalone vis-network)
# ------------------------------------------------------------------------------
def generate_interactive_html(G, title="Literature Knowledge Graph"):
    type_color_map = {
        "Paper": "#4f46e5",    # Indigo
        "Method": "#059669",   # Emerald
        "Task": "#d97706",     # Amber
        "Dataset": "#dc2626",  # Red
        "Metric": "#7c3aed",   # Purple
        "Concept": "#0284c7"   # Sky Blue
    }
    
    nodes_data = []
    for node, attrs in G.nodes(data=True):
        ntype = attrs.get("type", "Concept")
        color = type_color_map.get(ntype, "#64748b")
        size = 20 + min(35, attrs.get("in_degree", 1) * 4)
        if ntype == "Paper":
            size = 18
            
        nodes_data.append({
            "id": node,
            "label": node,
            "group": ntype,
            "color": {"background": color, "border": "#1e293b"},
            "size": size,
            "title": f"<b>{node}</b><br>Type: {ntype}<br>In-Degree: {attrs.get('in_degree', 0)}<br>PageRank: {attrs.get('pagerank', 0)}"
        })
        
    edges_data = []
    for u, v, attrs in G.edges(data=True):
        rel = attrs.get("relation", "relates")
        edges_data.append({
            "from": u,
            "to": v,
            "label": rel,
            "arrows": "to",
            "color": {"color": "#94a3b8", "highlight": "#2563eb"},
            "font": {"size": 11, "align": "middle", "color": "#475569"}
        })
        
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 0;
      background-color: #0f172a;
      color: #f8fafc;
      overflow: hidden;
    }}
    #header {{
      padding: 12px 24px;
      background: #1e293b;
      border-bottom: 1px solid #334155;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    #header h2 {{ margin: 0; font-size: 18px; font-weight: 600; color: #38bdf8; }}
    #stats {{ font-size: 13px; color: #94a3b8; }}
    #legend {{
      display: flex;
      gap: 16px;
      font-size: 12px;
    }}
    .legend-item {{ display: flex; align-items: center; gap: 6px; }}
    .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
    #network {{
      width: 100vw;
      height: calc(100vh - 58px);
      background: #090d16;
    }}
  </style>
</head>
<body>
  <div id="header">
    <h2>🕸️ {title}</h2>
    <div id="legend">
      <div class="legend-item"><span class="legend-dot" style="background:#4f46e5;"></span> Paper</div>
      <div class="legend-item"><span class="legend-dot" style="background:#059669;"></span> Method</div>
      <div class="legend-item"><span class="legend-dot" style="background:#d97706;"></span> Task</div>
      <div class="legend-item"><span class="legend-dot" style="background:#dc2626;"></span> Dataset</div>
      <div class="legend-item"><span class="legend-dot" style="background:#7c3aed;"></span> Metric</div>
      <div class="legend-item"><span class="legend-dot" style="background:#0284c7;"></span> Concept</div>
    </div>
    <div id="stats">Nodes: {len(G.nodes)} | Edges: {len(G.edges)}</div>
  </div>
  <div id="network"></div>
  <script type="text/javascript">
    const nodes = new vis.DataSet({json.dumps(nodes_data, ensure_ascii=False)});
    const edges = new vis.DataSet({json.dumps(edges_data, ensure_ascii=False)});
    const container = document.getElementById('network');
    const data = {{ nodes: nodes, edges: edges }};
    const options = {{
      physics: {{
        solver: 'forceAtlas2Based',
        forceAtlas2Based: {{
          gravitationalConstant: -50,
          centralGravity: 0.01,
          springLength: 100,
          springConstant: 0.08
        }},
        maxVelocity: 50,
        minVelocity: 0.1,
        stabilization: {{ iterations: 150 }}
      }},
      nodes: {{
        font: {{ color: '#e2e8f0', size: 13 }},
        borderWidth: 1.5
      }},
      edges: {{
        smooth: {{ type: 'continuous' }}
      }},
      interaction: {{ hover: true, tooltipDelay: 100, zoomView: true, navigationButtons: true }}
    }};
    const network = new vis.Network(container, data, options);
  </script>
</body>
</html>
"""
    return html_content

# ------------------------------------------------------------------------------
# 5. CLI Execution
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Asynchronous Graph-based Literature Knowledge Retrieval & Topology Reasoning System"
    )
    parser.add_argument("--query", "-q", default=None, help="Research topic or search keywords for papers")
    parser.add_argument("--input", "-i", default=None, help="Local JSON / text file of papers or abstracts")
    parser.add_argument("--limit", "-l", type=int, default=8, help="Number of papers to retrieve from each database")
    parser.add_argument("--output", "-o", default=None, help="Output path to save JSON knowledge graph")
    parser.add_argument("--html", default=None, help="Output path to export interactive HTML visualization")
    parser.add_argument("--find-path", nargs=2, metavar=("START", "END"), help="Find reasoning path between two concepts")
    
    args = parser.parse_args()
    
    if not args.query and not args.input:
        print("❌ Error: Please provide --query <topic> or --input <file>", file=sys.stderr)
        sys.exit(1)
        
    papers = []
    if args.input and os.path.exists(args.input):
        print(f"📂 [Graph-Retrieval] Ingesting local file: {args.input}...")
        with open(args.input, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    papers.extend(data)
                elif isinstance(data, dict):
                    papers.append(data)
            except Exception:
                f.seek(0)
                content = f.read()
                papers.append({"id": "local_doc", "title": os.path.basename(args.input), "abstract": content, "year": "2026"})
                
    if args.query:
        print(f"🔍 [Graph-Retrieval] Asynchronously retrieving literature for: '{args.query}'...")
        arxiv_p = fetch_arxiv_papers(args.query, limit=args.limit)
        openalex_p = fetch_openalex_papers(args.query, limit=args.limit)
        papers.extend(arxiv_p)
        papers.extend(openalex_p)
        print(f"📚 Harvested {len(papers)} papers from arXiv & OpenAlex.")

    if not papers:
        print("❌ No papers retrieved or parsed. Exiting.", file=sys.stderr)
        sys.exit(1)
        
    print(f"⚙️ Building semantic knowledge graph and extracting entity-relation triples...")
    G, paper_catalog = build_knowledge_graph(papers)
    
    # Top hub entities by PageRank
    pagerank_sorted = sorted(G.nodes(data=True), key=lambda x: x[1].get("pagerank", 0), reverse=True)
    top_methods = [n for n, d in pagerank_sorted if d.get("type") == "Method"][:5]
    top_tasks = [n for n, d in pagerank_sorted if d.get("type") == "Task"][:5]
    top_papers = [n for n, d in pagerank_sorted if d.get("type") == "Paper"][:3]
    
    summary = {
        "graph_statistics": {
            "total_nodes": len(G.nodes),
            "total_edges": len(G.edges),
            "total_papers": len(papers),
            "entity_breakdown": dict(Counter([d.get("type", "Other") for _, d in G.nodes(data=True)]))
        },
        "top_hub_methods": top_methods,
        "top_addressed_tasks": top_tasks,
        "influential_papers": top_papers
    }
    
    print("\n" + "=" * 65)
    print("🕸️ Literature Knowledge Graph Summary:")
    print("=" * 65)
    print(f"• Total Nodes: {summary['graph_statistics']['total_nodes']}")
    print(f"• Total Edges (Relations): {summary['graph_statistics']['total_edges']}")
    print(f"• Key Methods: {', '.join(top_methods)}")
    print(f"• Key Tasks/Problems: {', '.join(top_tasks)}")
    print("=" * 65)
    
    if args.find_path:
        start_c, end_c = args.find_path
        print(f"\n🧭 Searching reasoning path between: '{start_c}' -> '{end_c}'...")
        path, explanation = find_reasoning_path(G, start_c, end_c)
        print(f"Path Result: {explanation}")
        summary["reasoning_path"] = {"start": start_c, "end": end_c, "path": path, "explanation": explanation}
        
    # Export JSON
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        nodes_export = [{"id": n, **d} for n, d in G.nodes(data=True)]
        edges_export = [{"source": u, "target": v, **d} for u, v, d in G.edges(data=True)]
        export_payload = {"summary": summary, "nodes": nodes_export, "edges": edges_export}
        with open(args.output, "w", encoding="utf-8") as out_f:
            json.dump(export_payload, out_f, indent=2, ensure_ascii=False)
        print(f"💾 Knowledge Graph JSON exported to: {args.output}")
        
    # Export HTML
    if args.html:
        os.makedirs(os.path.dirname(os.path.abspath(args.html)), exist_ok=True)
        html_code = generate_interactive_html(G, title=f"Knowledge Graph: {args.query or 'Literature Review'}")
        with open(args.html, "w", encoding="utf-8") as html_f:
            html_f.write(html_code)
        print(f"🌐 Interactive Visualization HTML exported to: {args.html}")

if __name__ == "__main__":
    main()

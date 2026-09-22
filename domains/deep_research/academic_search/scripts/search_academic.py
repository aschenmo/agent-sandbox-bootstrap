#!/usr/bin/env python3
import os
import sys
import json
import argparse
import urllib.request
import urllib.parse

def search_pubmed(query, limit=5):
    api_key = os.getenv("PUBMED_API_KEY", "")
    email = os.getenv("PUBMED_EMAIL", "")
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": limit}
    if api_key: params["api_key"] = api_key
    if email: params["email"] = email
    url = f"{base}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AgentScholar/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            id_list = data.get("esearchresult", {}).get("idlist", [])
            return [{"source": "PubMed", "id": pmid, "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"} for pmid in id_list]
    except Exception as e:
        return [{"source": "PubMed", "error": str(e)}]

def search_semantic_scholar(query, limit=5):
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    base = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": query, "limit": limit, "fields": "title,authors,year,abstract,citationCount,url"}
    url = f"{base}?{urllib.parse.urlencode(params)}"
    headers = {"User-Agent": "AgentScholar/1.0"}
    if api_key: headers["x-api-key"] = api_key
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            papers = data.get("data", [])
            return [{"source": "SemanticScholar", "title": p.get("title"), "year": p.get("year"), "citations": p.get("citationCount"), "url": p.get("url"), "abstract": p.get("abstract", "")[:200]} for p in papers]
    except Exception as e:
        return [{"source": "SemanticScholar", "error": str(e)}]

def main():
    parser = argparse.ArgumentParser(description="学术文献统一检索工具")
    parser.add_argument("--query", "-q", required=True, help="搜索关键词或论文题目")
    parser.add_argument("--limit", "-n", type=int, default=5, help="每个平台返回条数")
    parser.add_argument("--output", "-o", help="输出保存路径 (可选)")
    args = parser.parse_args()

    print(f"🔍 正在跨库检索文献: [{args.query}] ...")
    pm_results = search_pubmed(args.query, args.limit)
    ss_results = search_semantic_scholar(args.query, args.limit)

    results = {
        "query": args.query,
        "pubmed": pm_results,
        "semantic_scholar": ss_results,
    }

    out_json = json.dumps(results, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_json)
        print(f"✅ 检索结果已保存至: {args.output}")
    else:
        print(out_json)

if __name__ == "__main__":
    main()

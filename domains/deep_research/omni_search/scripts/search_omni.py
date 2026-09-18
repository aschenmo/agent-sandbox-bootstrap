#!/usr/bin/env python3
"""
OmniSearch 2.0: 全源前沿情报与学术科研统一检索调度引擎
- 学术文献中枢: PubMed, Semantic Scholar, OpenAlex, arXiv, Elsevier SciVerse
- 开放获取全文解析: Unpaywall API (通过 DOI 秒级解析免费合法 PDF 直链)
- 分子与化学结构: PubChem PUG REST (分子式, 分子量, SMILES, IUPAC 命名)
- 中文生态与社区: 百度搜索 (Baidu Web), 知乎检索 (Zhihu QA & 专栏), 中文维基 (Wikipedia)
- 全网 AI 情报与穿透: Tavily AI Search, Brave Search, Firecrawl / 原生正文清洗器
"""

import os
import sys
import json
import re
import argparse
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

def get_env_dict():
    """获取环境变量（优先使用当前进程环境变量，其次回退解析 /tmp/env.sh）"""
    env = dict(os.environ)
    if os.path.exists("/tmp/env.sh"):
        try:
            with open("/tmp/env.sh", "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        k = k.replace("export ", "").strip()
                        v = v.strip().strip("\"'")
                        if k not in env or not env[k]:
                            env[k] = v
        except Exception:
            pass
    return env

ENV = get_env_dict()
DEFAULT_EMAIL = ENV.get("PUBMED_EMAIL") or "luchenmo2020@gmail.com"

# ==============================================================================
# 1. 国际权威学术文献引擎 (Academic Literature Engines)
# ==============================================================================

def search_pubmed(query, limit=5):
    """PubMed 官方 API 检索 (生物医学与生命科学金标准)"""
    api_key = ENV.get("PUBMED_API_KEY", "")
    email = ENV.get("PUBMED_EMAIL", DEFAULT_EMAIL)
    base_esearch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": limit}
    if api_key: params["api_key"] = api_key
    if email: params["email"] = email
    
    url = f"{base_esearch}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": f"OmniSearch/2.0 ({email})"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            id_list = data.get("esearchresult", {}).get("idlist", [])
            
        if not id_list:
            return []

        base_esummary = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        sparams = {"db": "pubmed", "id": ",".join(id_list), "retmode": "json"}
        if api_key: sparams["api_key"] = api_key
        surl = f"{base_esummary}?{urllib.parse.urlencode(sparams)}"
        sreq = urllib.request.Request(surl, headers={"User-Agent": f"OmniSearch/2.0 ({email})"})
        
        results = []
        with urllib.request.urlopen(sreq, timeout=10) as sresp:
            sdata = json.loads(sresp.read().decode()).get("result", {})
            for pmid in id_list:
                item = sdata.get(pmid, {})
                title = item.get("title", f"PMID: {pmid}").strip()
                pubdate = item.get("pubdate", "")
                authors = [a.get("name") for a in item.get("authors", []) if "name" in a]
                doi = ""
                for aid in item.get("articleids", []):
                    if aid.get("idtype") == "doi":
                        doi = aid.get("value", "")
                        break
                results.append({
                    "engine": "PubMed",
                    "title": title,
                    "year": pubdate[:4] if pubdate else "",
                    "authors": authors[:3],
                    "id": pmid,
                    "doi": doi,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "type": "paper"
                })
        return results
    except Exception as e:
        return [{"engine": "PubMed", "error": str(e)}]

def search_semantic_scholar(query, limit=5):
    """Semantic Scholar AI 学术图谱检索 (计算机/交叉科学高被引分析)"""
    api_key = ENV.get("SEMANTIC_SCHOLAR_API_KEY", "")
    base = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": query, "limit": limit, "fields": "title,authors,year,abstract,citationCount,url,isOpenAccess,externalIds"}
    url = f"{base}?{urllib.parse.urlencode(params)}"
    headers = {"User-Agent": "OmniSearch/2.0"}
    if api_key: headers["x-api-key"] = api_key
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            papers = data.get("data", [])
            return [{
                "engine": "SemanticScholar",
                "title": p.get("title", "").strip(),
                "year": p.get("year"),
                "citations": p.get("citationCount", 0),
                "authors": [a.get("name") for a in p.get("authors", [])][:3],
                "doi": p.get("externalIds", {}).get("DOI", ""),
                "url": p.get("url", ""),
                "abstract": (p.get("abstract") or "")[:250],
                "type": "paper"
            } for p in papers]
    except Exception as e:
        return [{"engine": "SemanticScholar", "error": str(e)}]

def search_openalex(query, limit=5):
    """OpenAlex 全球开放科学学术成果大图谱 (2.5亿+学术文献与学者数据)"""
    api_key = ENV.get("OPENALEX_KEY", "")
    url = f"https://api.openalex.org/works?search={urllib.parse.quote(query)}&per-page={limit}"
    if api_key:
        url += f"&api_key={api_key}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": f"OmniSearch/2.0 (mailto:{DEFAULT_EMAIL})"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            works = data.get("results", [])
            return [{
                "engine": "OpenAlex",
                "title": (w.get("title") or "").strip(),
                "year": w.get("publication_year"),
                "citations": w.get("cited_by_count", 0),
                "doi": w.get("doi", "").replace("https://doi.org/", ""),
                "url": w.get("doi") or (w.get("ids", {}).get("openalex", "")),
                "type": "paper"
            } for w in works]
    except Exception as e:
        return [{"engine": "OpenAlex", "error": str(e)}]

def search_arxiv(query, limit=5):
    """arXiv 官方预印本 API 检索 (计算机、物理、数学最前沿预印本，零时延免 Key)"""
    url = f"https://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&start=0&max_results={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            tree = ET.fromstring(resp.read())
            entries = tree.findall("{http://www.w3.org/2005/Atom}entry")
            results = []
            for e in entries:
                t_el = e.find("{http://www.w3.org/2005/Atom}title")
                title = t_el.text.strip().replace("\n", " ") if t_el is not None and t_el.text else ""
                s_el = e.find("{http://www.w3.org/2005/Atom}summary")
                summary = s_el.text.strip().replace("\n", " ") if s_el is not None and s_el.text else ""
                p_el = e.find("{http://www.w3.org/2005/Atom}published")
                year = p_el.text[:4] if p_el is not None and p_el.text else ""
                id_el = e.find("{http://www.w3.org/2005/Atom}id")
                paper_id = id_el.text.strip() if id_el is not None and id_el.text else ""
                authors = [a.find("{http://www.w3.org/2005/Atom}name").text for a in e.findall("{http://www.w3.org/2005/Atom}author") if a.find("{http://www.w3.org/2005/Atom}name") is not None]
                
                pdf_url = ""
                for link in e.findall("{http://www.w3.org/2005/Atom}link"):
                    if link.attrib.get("title") == "pdf":
                        pdf_url = link.attrib.get("href", "")
                        break
                if not pdf_url and "arxiv.org/abs/" in paper_id:
                    pdf_url = paper_id.replace("/abs/", "/pdf/") + ".pdf"

                results.append({
                    "engine": "arXiv",
                    "title": title,
                    "year": year,
                    "authors": authors[:3],
                    "url": paper_id,
                    "pdf_url": pdf_url,
                    "abstract": summary[:250],
                    "type": "paper"
                })
            return results
    except Exception as e:
        return [{"engine": "arXiv", "error": str(e)}]

def search_sciverse(query, limit=5):
    """Elsevier SciVerse / 顶刊证据 RAG 检索接口"""
    token = ENV.get("SCIVERSE_API_TOKEN") or ENV.get("SCIVERSE_TOKEN")
    if not token:
        return []
    try:
        payload = json.dumps({"query": query, "top_k": limit}).encode("utf-8")
        req = urllib.request.Request(
            "https://api.sciverse.space/agentic-search",
            data=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "OmniSearch/2.0"
            }
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode())
            hits = data.get("hits", [])
            return [{
                "engine": "SciVerse",
                "title": h.get("title", "").strip(),
                "year": h.get("publication_published_year", ""),
                "venue": h.get("publication_venue_name_unified", ""),
                "authors": h.get("author", [])[:3],
                "abstract": (h.get("chunk") or h.get("abstract") or "")[:250],
                "doc_id": h.get("doc_id", ""),
                "type": "paper"
            } for h in hits]
    except Exception as e:
        return [{"engine": "SciVerse", "error": str(e)}]

# ==============================================================================
# 2. 全文开放获取与化学结构引擎 (OA Full-Text & Chemical Data)
# ==============================================================================

def resolve_unpaywall(doi, email=None):
    """通过 DOI 秒级解析 Unpaywall 开放获取免费正版 PDF 下载直链"""
    if not doi:
        return None
    clean_doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
    em = email or DEFAULT_EMAIL
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(clean_doi)}?email={urllib.parse.quote(em)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            best_oa = data.get("best_oa_location") or {}
            return {
                "doi": clean_doi,
                "title": data.get("title", ""),
                "is_oa": data.get("is_oa", False),
                "oa_status": data.get("oa_status", "closed"),
                "pdf_url": best_oa.get("url_for_pdf") or "",
                "landing_url": best_oa.get("url_for_landing_page") or "",
                "host_type": best_oa.get("host_type", ""),
                "license": best_oa.get("license", "")
            }
    except Exception as e:
        return {"doi": clean_doi, "error": str(e)}

def search_pubchem(compound_name):
    """PubChem PUG REST API 检索 (化学化合物分子式、分子量、SMILES 与 IUPAC 命名)"""
    if not compound_name:
        return None
    encoded = urllib.parse.quote(compound_name.strip())
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded}/property/MolecularFormula,MolecularWeight,ConnectivitySMILES,CanonicalSMILES,IUPACName/JSON"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            props = data.get("PropertyTable", {}).get("Properties", [{}])[0]
            cid = props.get("CID")
            smiles = props.get("CanonicalSMILES") or props.get("ConnectivitySMILES")
            return {
                "engine": "PubChem",
                "name": compound_name,
                "cid": cid,
                "formula": props.get("MolecularFormula"),
                "molecular_weight": props.get("MolecularWeight"),
                "smiles": smiles,
                "iupac_name": props.get("IUPACName"),
                "url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}" if cid else "",
                "type": "compound"
            }
    except Exception as e:
        return {"engine": "PubChem", "name": compound_name, "error": str(e)}

# ==============================================================================
# 3. 中文生态与垂直社区引擎 (Chinese Search & Vertical Communities)
# ==============================================================================

def search_baidu(query, limit=5):
    """百度搜索引擎 (中文科技与综合资讯深度收录)"""
    url = f"https://www.baidu.com/s?wd={urllib.parse.quote(query)}&rn={limit}&ie=utf-8"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            results = []
            for h3 in soup.select("h3"):
                a = h3.find("a")
                if a and a.text.strip():
                    title = a.text.strip()
                    link = a.get("href", "")
                    parent = h3.find_parent("div")
                    snippet = ""
                    if parent:
                        spans = parent.select("span.content-right_8Zs40, span.c-font-normal, div.c-summary")
                        if spans:
                            snippet = spans[0].text.strip()
                    results.append({
                        "engine": "Baidu",
                        "title": title,
                        "content": snippet[:200] if snippet else title,
                        "url": link,
                        "type": "web"
                    })
                    if len(results) >= limit:
                        break
            if results:
                return results
    except Exception:
        pass
    
    # 若直接抓取遇拦截，无缝回退至 Brave 针对百度域名的精准代理检索
    brave_key = ENV.get("BRAVE_SEARCH_API_KEY") or ENV.get("BRAVE_API_KEY")
    if brave_key:
        try:
            b_url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote('site:baike.baidu.com ' + query)}&count={limit}"
            breq = urllib.request.Request(b_url, headers={"X-Subscription-Token": brave_key, "Accept": "application/json"})
            with urllib.request.urlopen(breq, timeout=8) as bresp:
                bdata = json.loads(bresp.read().decode())
                return [{
                    "engine": "Baidu (Baike)",
                    "title": it.get("title", ""),
                    "content": it.get("description", ""),
                    "url": it.get("url", ""),
                    "type": "web"
                } for it in bdata.get("web", {}).get("results", [])]
        except Exception:
            pass
            
    return [{"engine": "Baidu", "error": "Baidu search unavailable"}]

def search_zhihu(query, limit=5):
    """知乎高质量问答与专栏检索 (具备 Brave Proxy 智能直通，100% 零风控高防)"""
    zhihu_key = ENV.get("ZHIHU_API_KEY")
    if zhihu_key:
        try:
            u = f"https://developer.zhihu.com/api/v1/content/zhihu_search?Query={urllib.parse.quote(query)}&Count={limit}"
            req = urllib.request.Request(u, headers={"Authorization": f"Bearer {zhihu_key}", "User-Agent": "AntigravitySearch/2.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
                items = []
                for it in data.get("Data", {}).get("Items", []):
                    clean_title = re.sub(r"<[^>]+>", "", it.get("Title", ""))
                    clean_content = re.sub(r"<[^>]+>", "", it.get("ContentText") or it.get("Snippet") or "")
                    items.append({
                        "engine": "Zhihu",
                        "title": clean_title,
                        "content": clean_content[:200],
                        "url": it.get("Url") or it.get("url") or "",
                        "author": it.get("AuthorName") or it.get("author") or "",
                        "type": "community"
                    })
                if items:
                    return items
        except Exception:
            pass

    # 默认零门槛回退：通过 Brave 的 site:zhihu.com 定向检索知乎专栏与问答
    brave_key = ENV.get("BRAVE_SEARCH_API_KEY") or ENV.get("BRAVE_API_KEY")
    if brave_key:
        try:
            b_url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote('site:zhihu.com ' + query)}&count={limit}"
            breq = urllib.request.Request(b_url, headers={"X-Subscription-Token": brave_key, "Accept": "application/json"})
            with urllib.request.urlopen(breq, timeout=8) as bresp:
                bdata = json.loads(bresp.read().decode())
                return [{
                    "engine": "Zhihu (Community)",
                    "title": it.get("title", ""),
                    "content": it.get("description", ""),
                    "url": it.get("url", ""),
                    "type": "community"
                } for it in bdata.get("web", {}).get("results", [])]
        except Exception as e:
            return [{"engine": "Zhihu", "error": str(e)}]
            
    return [{"engine": "Zhihu", "error": "ZHIHU_API_KEY or BRAVE_API_KEY required"}]

def search_wikipedia(query, lang="zh", limit=5):
    """维基百科官方开放 API (权威百科词条定义与背景知识，免 Key)"""
    url = f"https://{lang}.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&utf8=1&srlimit={limit}"
    headers = {"User-Agent": f"OmniSearch/2.0 ({DEFAULT_EMAIL})"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
            results = []
            for it in data.get("query", {}).get("search", []):
                snippet = re.sub(r"<[^>]+>", "", it.get("snippet", ""))
                title = it.get("title", "")
                results.append({
                    "engine": "Wikipedia",
                    "title": title,
                    "content": snippet,
                    "url": f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(title)}",
                    "type": "encyclopedia"
                })
            return results
    except Exception as e:
        return [{"engine": "Wikipedia", "error": str(e)}]

# ==============================================================================
# 4. 全网 AI 深度检索与正文穿透 (Web & Deep Scraper)
# ==============================================================================

def search_tavily(query, limit=5):
    """Tavily AI 深度搜索引擎 (提炼要点与高置信度事实)"""
    api_key = ENV.get("TAVILY_API_KEY") or ENV.get("TAVILY_PROD_API_KEY")
    if not api_key:
        return [{"engine": "Tavily", "error": "TAVILY_API_KEY missing"}]
    
    try:
        payload = json.dumps({
            "api_key": api_key,
            "query": query,
            "max_results": limit,
            "include_answer": True
        }).encode("utf-8")
        req = urllib.request.Request("https://api.tavily.com/search", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode())
            results = []
            if data.get("answer"):
                results.append({
                    "engine": "Tavily (AI Answer)",
                    "title": "💡 核心要点与 AI 提炼",
                    "content": data["answer"],
                    "url": "",
                    "type": "summary"
                })
            for item in data.get("results", []):
                results.append({
                    "engine": "Tavily",
                    "title": item.get("title", ""),
                    "content": item.get("content", "")[:250],
                    "url": item.get("url", ""),
                    "score": item.get("score"),
                    "type": "web"
                })
            return results
    except Exception as e:
        return [{"engine": "Tavily", "error": str(e)}]

def search_brave(query, limit=5):
    """Brave Search 搜索引擎 (独立隐私网页索引)"""
    api_key = ENV.get("BRAVE_SEARCH_API_KEY") or ENV.get("BRAVE_API_KEY")
    if not api_key:
        return [{"engine": "Brave", "error": "BRAVE_SEARCH_API_KEY missing"}]
    
    try:
        url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count={limit}"
        req = urllib.request.Request(url, headers={"X-Subscription-Token": api_key, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            results = []
            for item in data.get("web", {}).get("results", []):
                results.append({
                    "engine": "Brave",
                    "title": item.get("title", ""),
                    "content": item.get("description", ""),
                    "url": item.get("url", ""),
                    "type": "web"
                })
            return results
    except Exception as e:
        return [{"engine": "Brave", "error": str(e)}]

def scrape_url(url):
    """深度穿透抓取网页并提取结构化干净 Markdown"""
    fc_key = ENV.get("FIRECRAWL_API_KEY")
    if fc_key:
        try:
            payload = json.dumps({"url": url, "formats": ["markdown"]}).encode("utf-8")
            req = urllib.request.Request(
                "https://api.firecrawl.dev/v1/scrape",
                data=payload,
                headers={"Authorization": f"Bearer {fc_key}", "Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                md = data.get("data", {}).get("markdown")
                if md:
                    return {"url": url, "source": "Firecrawl", "content": md}
        except Exception:
            pass
            
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "aside", "svg"]):
            tag.decompose()
            
        title = soup.title.string.strip() if soup.title and soup.title.string else url
        body_text = soup.get_text(separator="\n\n", strip=True)
        lines = [line.strip() for line in body_text.splitlines() if line.strip()]
        clean_text = "\n\n".join(lines[:250])
        
        return {
            "url": url,
            "title": title,
            "source": "Native Cleaner",
            "content": clean_text
        }
    except Exception as e:
        return {"url": url, "error": f"Scrape failed: {str(e)}"}

# ==============================================================================
# 5. 多源并发统一调度控制器
# ==============================================================================

def execute_omni_search(query, mode="all", limit=4):
    """高并发统一调度各大检索军团"""
    is_chinese = bool(re.search(r"[\u4e00-\u9fa5]", query))
    tasks = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        # 学术文献组
        if mode in ["academic", "all"]:
            tasks.append(("pubmed", executor.submit(search_pubmed, query, limit)))
            tasks.append(("semantic_scholar", executor.submit(search_semantic_scholar, query, limit)))
            tasks.append(("openalex", executor.submit(search_openalex, query, limit)))
            tasks.append(("arxiv", executor.submit(search_arxiv, query, limit)))
            if ENV.get("SCIVERSE_API_TOKEN") or ENV.get("SCIVERSE_TOKEN"):
                tasks.append(("sciverse", executor.submit(search_sciverse, query, limit)))
            
        # 全网与 AI 综述组
        if mode in ["web", "all"]:
            tasks.append(("tavily", executor.submit(search_tavily, query, limit)))
            tasks.append(("brave", executor.submit(search_brave, query, limit)))

        # 中文生态与垂直社区 (若查询含中文或在 chinese/all 模式下自动触发)
        if mode in ["chinese", "all"] or (is_chinese and mode == "all"):
            tasks.append(("baidu", executor.submit(search_baidu, query, limit)))
            tasks.append(("zhihu", executor.submit(search_zhihu, query, limit)))
            tasks.append(("wikipedia", executor.submit(search_wikipedia, query, "zh" if is_chinese else "en", limit)))
            
        # 化学模式
        if mode == "chemical":
            tasks.append(("pubchem", executor.submit(search_pubchem, query)))
            tasks.append(("pubmed", executor.submit(search_pubmed, query, limit)))
            tasks.append(("arxiv", executor.submit(search_arxiv, query, limit)))
            
        results = {}
        for name, future in tasks:
            try:
                results[name] = future.result()
            except Exception as e:
                results[name] = [{"error": str(e)}]
                
    return results

def format_as_markdown(query, results):
    """将全源多维数据渲染为严谨出版级学术调研 Markdown 报告"""
    lines = [
        f"# 🔍 OmniSearch 2.0 全源科研调研报告: {query}",
        "> 引擎矩阵: PubMed | Semantic Scholar | OpenAlex | arXiv | SciVerse | Tavily | Brave | 百度 | 知乎 | 维基百科",
        ""
    ]
    
    # 1. AI 综述提炼
    tavily_results = results.get("tavily", [])
    for item in tavily_results:
        if item.get("type") == "summary":
            lines.extend([
                "## 💡 核心要点与 AI 事实提炼",
                f"{item.get('content')}",
                ""
            ])
            
    # 2. 化学结构与物理参数 (如果有)
    chem = results.get("pubchem")
    if chem and not chem.get("error") and chem.get("formula"):
        lines.extend([
            "## 🧪 分子与化合物化学属性 (PubChem)",
            f"- **化合物名称**: `{chem.get('name')}` (CID: {chem.get('cid')})",
            f"- **化学分子式**: `{chem.get('formula')}`",
            f"- **相对分子质量**: `{chem.get('molecular_weight')}` g/mol",
            f"- **Canonical SMILES**: `{chem.get('smiles')}`",
            f"- **IUPAC 命名**: {chem.get('iupac_name')}",
            f"- **PubChem 详情直达**: [PubChem Compound #{chem.get('cid')}]({chem.get('url')})",
            ""
        ])
            
    # 3. 国际学术顶刊与预印本文献
    academic_items = []
    for eng in ["pubmed", "semantic_scholar", "openalex", "arxiv", "sciverse"]:
        for it in results.get(eng, []):
            if "title" in it and not it.get("error") and it.get("title"):
                academic_items.append(it)
                
    if academic_items:
        lines.append("## 📚 权威学术文献与预印本 (PubMed / S2 / OpenAlex / arXiv / SciVerse)")
        lines.append("| 引擎来源 | 年份 | 被引 | 论文题目 | 全文 / PDF 直链 |")
        lines.append("| :--- | :---: | :---: | :--- | :--- |")
        seen_titles = set()
        for p in academic_items:
            t = p.get("title", "").strip()
            if not t or t.lower() in seen_titles:
                continue
            seen_titles.add(t.lower())
            eng = p.get("engine", "")
            yr = str(p.get("year") or "-")
            cit = str(p.get("citations", "-"))
            url = p.get("url") or p.get("pdf_url") or "#"
            pdf_tag = f"[📄 PDF]({p.get('pdf_url')})" if p.get("pdf_url") else f"[详情]({url})"
            lines.append(f"| **{eng}** | {yr} | {cit} | {t[:75]}... | {pdf_tag} |")
        lines.append("")
        
    # 4. 中文生态与垂直社区讨论 (百度 / 知乎 / 维基)
    cn_items = []
    for eng in ["zhihu", "baidu", "wikipedia"]:
        for it in results.get(eng, []):
            if "title" in it and not it.get("error"):
                cn_items.append(it)
                
    if cn_items:
        lines.append("## 🇨🇳 中文前沿生态与专业社区问答 (知乎 / 百度 / 维基百科)")
        for it in cn_items[:6]:
            t = it.get("title", "").strip()
            u = it.get("url", "")
            eng = it.get("engine", "")
            desc = (it.get("content") or "").strip()
            lines.extend([
                f"- **[{t}]({u})** `[{eng}]`",
                f"  > {desc[:160]}...",
                ""
            ])
            
    # 5. 全球科技与行业深度前沿 (Tavily / Brave)
    web_items = []
    for eng in ["tavily", "brave"]:
        for it in results.get(eng, []):
            if it.get("type") == "web" and "title" in it and not it.get("error"):
                web_items.append(it)
                
    if web_items:
        lines.append("## 🌐 国际行业动态与前沿报道 (Tavily / Brave)")
        for it in web_items[:6]:
            lines.extend([
                f"- **[{it.get('title')}]({it.get('url')})** ({it.get('engine')})",
                f"  > {it.get('content', '')[:160]}...",
                ""
            ])
            
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="OmniSearch 2.0: 全源统一科研检索与学术正文穿透引擎")
    parser.add_argument("--query", "-q", help="搜索关键词、论文名或科学议题")
    parser.add_argument("--mode", "-m", choices=["all", "academic", "web", "chinese", "chemical"], default="all", help="检索模式 (默认: all 全域聚合)")
    parser.add_argument("--limit", "-n", type=int, default=4, help="各引擎返回条数上限 (默认: 4)")
    parser.add_argument("--doi", "-d", help="解析指定 DOI 论文的合法免费 Open-Access PDF 下载直链 (Unpaywall)")
    parser.add_argument("--compound", "-c", help="查询指定化合物分子的分子式、分子量与 SMILES (PubChem)")
    parser.add_argument("--scrape", "-s", help="深度穿透抓取指定网页 URL 并提取干净 Markdown 正文")
    parser.add_argument("--format", "-f", choices=["json", "md"], default="md", help="输出格式 (默认: md)")
    parser.add_argument("--output", "-o", help="导出报告至指定文件路径")
    
    args = parser.parse_args()
    
    # 功能 1: Unpaywall DOI 免费正版 PDF 直链解析
    if args.doi:
        print(f"🔓 [Unpaywall] 正在解析 DOI: {args.doi} 的开放获取 PDF 直链 ...", file=sys.stderr)
        oa_res = resolve_unpaywall(args.doi)
        if args.format == "json":
            out = json.dumps(oa_res, ensure_ascii=False, indent=2)
        else:
            if oa_res and oa_res.get("is_oa") and oa_res.get("pdf_url"):
                out = f"# 📄 Unpaywall 开放获取全文解析成功\n\n- **DOI**: `{oa_res['doi']}`\n- **论文标题**: {oa_res.get('title')}\n- **OA 状态**: `{oa_res.get('oa_status')}` (合法免费公开)\n- **PDF 直链**: [📥 点击直接下载 PDF]({oa_res['pdf_url']})\n- **出版商落地页**: [访问主页]({oa_res.get('landing_url')})"
            else:
                out = f"# ⚠️ 未找到该 DOI 的开放获取 PDF\n\n- **DOI**: `{args.doi}`\n- **提示**: 论文可能处于付费订阅墙内，建议尝试 arXiv 或 Semantic Scholar 检索作者自存档版本。"
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f: f.write(out)
        else:
            print(out)
        return

    # 功能 2: PubChem 化学分子属性查询
    if args.compound:
        print(f"🧪 [PubChem] 正在检索化合物: {args.compound} 的化学参数与分子结构 ...", file=sys.stderr)
        c_res = search_pubchem(args.compound)
        if args.format == "json":
            out = json.dumps(c_res, ensure_ascii=False, indent=2)
        else:
            if c_res and not c_res.get("error"):
                out = f"# 🧪 PubChem 化合物档案: {args.compound}\n\n- **CID**: `{c_res.get('cid')}`\n- **化学分子式**: `{c_res.get('formula')}`\n- **分子量**: `{c_res.get('molecular_weight')}` g/mol\n- **Canonical SMILES**: `{c_res.get('smiles')}`\n- **IUPAC 命名**: {c_res.get('iupac_name')}\n- **PubChem 主页**: {c_res.get('url')}"
            else:
                out = f"# ⚠️ 未匹配到化合物: {args.compound}\n\n错误信息: {c_res.get('error')}"
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f: f.write(out)
        else:
            print(out)
        return

    # 功能 3: 单 URL 深度正文抓取
    if args.scrape:
        print(f"🌐 [DeepScraper] 正在穿透抓取网页正文: {args.scrape} ...", file=sys.stderr)
        scraped = scrape_url(args.scrape)
        if args.format == "json":
            out = json.dumps(scraped, ensure_ascii=False, indent=2)
        else:
            out = f"# 📄 网页深度萃取: {scraped.get('title', args.scrape)}\n\n来源: {scraped.get('source')} | 网址: {args.scrape}\n\n---\n\n{scraped.get('content')}"
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f: f.write(out)
        else:
            print(out)
        return

    # 功能 4: 全源并发检索
    if not args.query:
        parser.print_help()
        sys.exit(1)
        
    print(f"🚀 [OmniSearch 2.0] 正在多源并发检索: [{args.query}] (模式: {args.mode}) ...", file=sys.stderr)
    res = execute_omni_search(args.query, mode=args.mode, limit=args.limit)
    
    if args.format == "json":
        out = json.dumps(res, ensure_ascii=False, indent=2)
    else:
        out = format_as_markdown(args.query, res)
        
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"✅ 调研报告已输出至: {args.output}", file=sys.stderr)
    else:
        print(out)

if __name__ == "__main__":
    main()

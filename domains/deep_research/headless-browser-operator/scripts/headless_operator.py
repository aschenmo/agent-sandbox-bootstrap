#!/usr/bin/env python3
"""
headless_operator.py - Headless Browser Operator (Claude Computer Use Style)
Supports modern dynamic web rendering, screenshot capture, DOM interaction, and PDF generation.
"""

import os
import sys
import json
import argparse
import asyncio
import shutil
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(
        description="Headless Browser Operator: Automated browser interaction and visual capture."
    )
    parser.add_argument("--url", "-u", type=str, required=True, help="Target URL to navigate to")
    parser.add_argument(
        "--action", "-a",
        type=str,
        choices=["screenshot", "extract", "pdf", "click", "fill", "eval", "batch"],
        default="extract",
        help="Action to execute (default: extract)"
    )
    parser.add_argument("--output", "-o", type=str, default="", help="Output file path (e.g. image.png, page.pdf, doc.md)")
    parser.add_argument("--selector", "-s", type=str, default="", help="CSS selector for click/fill action")
    parser.add_argument("--value", "-v", type=str, default="", help="Value to fill or JavaScript code to evaluate")
    parser.add_argument("--full-page", action="store_true", help="Capture full scrollable page in screenshot")
    parser.add_argument("--viewport", type=str, default="1920x1080", help="Browser viewport WxH (default: 1920x1080)")
    parser.add_argument("--wait-until", type=str, choices=["load", "domcontentloaded", "networkidle"], default="networkidle", help="Wait strategy")
    parser.add_argument("--timeout", type=int, default=30000, help="Navigation timeout in milliseconds (default: 30000)")
    parser.add_argument("--batch-steps", type=str, default="", help="JSON string or file path containing an array of step operations")
    return parser.parse_args()


async def run_playwright_workflow(args):
    from playwright.async_api import async_playwright

    width, height = 1920, 1080
    if "x" in args.viewport:
        try:
            parts = args.viewport.split("x")
            width, height = int(parts[0]), int(parts[1])
        except Exception:
            pass

    chrome_path = os.environ.get("CHROME_PATH") or shutil.which("google-chrome") or shutil.which("chromium")
    launch_kwargs = {
        "headless": True,
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu"
        ]
    }
    if chrome_path and os.path.exists(chrome_path):
        launch_kwargs["executable_path"] = chrome_path

    async with async_playwright() as p:
        browser = await p.chromium.launch(**launch_kwargs)
        context = await browser.new_context(
            viewport={"width": width, "height": height},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Antigravity-Agent/2.0"
        )
        page = await context.new_page()

        print(f"🌐 正在导航至: {args.url}")
        try:
            await page.goto(args.url, wait_until=args.wait_until, timeout=args.timeout)
        except Exception as e:
            print(f"⚠️ 网络等待超时或告警 ({e})，尝试继续处理已加载 DOM...")

        # Small grace period for dynamic UI hydration
        await asyncio.sleep(1)

        result_summary = {"status": "success", "url": page.url, "title": await page.title()}

        # 1. Action: Screenshot
        if args.action == "screenshot":
            out_path = args.output or "screenshot.png"
            os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
            await page.screenshot(path=out_path, full_page=args.full_page)
            print(f"📸 网页截图已保存至: {out_path} (Full Page: {args.full_page})")
            result_summary["screenshot_path"] = out_path

        # 2. Action: Extract Markdown / Clean Text
        elif args.action == "extract":
            title = await page.title()
            # Extract main text, headings and links
            extracted = await page.evaluate("""() => {
                const scripts = document.querySelectorAll('script, style, noscript, nav, footer');
                scripts.forEach(s => s.remove());
                
                const title = document.title;
                const h1s = Array.from(document.querySelectorAll('h1, h2, h3')).map(h => h.innerText.trim()).filter(Boolean);
                const links = Array.from(document.querySelectorAll('a[href]'))
                                  .slice(0, 50)
                                  .map(a => ({ text: a.innerText.trim(), href: a.href }))
                                  .filter(l => l.text && l.href.startsWith('http'));
                const bodyText = document.body ? document.body.innerText.trim() : '';
                return { title, headings: h1s, links, text: bodyText };
            }""")
            
            md_lines = [
                f"# {extracted['title']}",
                f"\n**URL**: {page.url}\n",
                "## 📑 页面核心内容",
                extracted['text'],
                "\n## 🔗 核心页面链接",
            ]
            for link in extracted['links'][:30]:
                md_lines.append(f"- [{link['text']}]({link['href']})")

            md_content = "\n\n".join(md_lines)
            out_path = args.output or "extracted_page.md"
            os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"📝 网页内容已结构化导出至: {out_path} (文本长度: {len(extracted['text'])} 字符)")
            result_summary["extracted_file"] = out_path

        # 3. Action: PDF Export
        elif args.action == "pdf":
            out_path = args.output or "page_export.pdf"
            os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
            await page.pdf(
                path=out_path,
                format="A4",
                print_background=True,
                margin={"top": "20px", "bottom": "20px", "left": "20px", "right": "20px"}
            )
            print(f"📄 网页已导出为出版级 PDF: {out_path}")
            result_summary["pdf_path"] = out_path

        # 4. Action: Click
        elif args.action == "click":
            if not args.selector:
                raise ValueError("执行 click 操作必须提供 --selector 参数")
            print(f"🖱️ 模拟点击元素: {args.selector}")
            await page.click(args.selector)
            await asyncio.sleep(1.5)
            if args.output:
                os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
                await page.screenshot(path=args.output, full_page=args.full_page)
                print(f"📸 点击后截图已保存: {args.output}")

        # 5. Action: Fill
        elif args.action == "fill":
            if not args.selector:
                raise ValueError("执行 fill 操作必须提供 --selector 参数")
            print(f"⌨️ 填充输入框 [{args.selector}] 内容: {args.value}")
            await page.fill(args.selector, args.value)
            await asyncio.sleep(1)
            if args.output:
                os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
                await page.screenshot(path=args.output, full_page=args.full_page)
                print(f"📸 输入后截图已保存: {args.output}")

        # 6. Action: Eval JavaScript
        elif args.action == "eval":
            expr = args.value or "document.title"
            print(f"⚡ 执行浏览器端 JavaScript: {expr}")
            eval_res = await page.evaluate(expr)
            print(f"💡 执行结果: {eval_res}")
            result_summary["eval_result"] = eval_res
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(result_summary, f, ensure_ascii=False, indent=2)

        # 7. Action: Batch multi-step operations
        elif args.action == "batch":
            raw_steps = args.batch_steps
            if os.path.isfile(raw_steps):
                with open(raw_steps, "r", encoding="utf-8") as f:
                    steps = json.load(f)
            else:
                steps = json.loads(raw_steps)

            print(f"🚀 执行批处理流水线，步骤总数: {len(steps)}")
            for idx, step in enumerate(steps, 1):
                s_action = step.get("action", "")
                s_selector = step.get("selector", "")
                s_val = step.get("value", "")
                s_out = step.get("output", "")

                print(f"  [{idx}/{len(steps)}] 执行操作: {s_action} | selector: {s_selector}")
                if s_action == "click":
                    await page.click(s_selector)
                elif s_action == "fill":
                    await page.fill(s_selector, str(s_val))
                elif s_action == "press":
                    await page.press(s_selector, str(s_val))
                elif s_action == "wait":
                    await asyncio.sleep(float(s_val) / 1000.0)
                elif s_action == "screenshot":
                    s_out = s_out or f"step_{idx}.png"
                    os.makedirs(os.path.dirname(os.path.abspath(s_out)), exist_ok=True)
                    await page.screenshot(path=s_out)
                    print(f"    📸 步骤截图已保存: {s_out}")
                elif s_action == "scroll":
                    await page.evaluate(f"window.scrollBy(0, {int(s_val)})")
                await asyncio.sleep(0.5)

            if args.output:
                os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
                await page.screenshot(path=args.output, full_page=True)
                print(f"🎉 批处理完成，最终全页截图: {args.output}")

        await browser.close()
        return result_summary


def fallback_extract(url, output_path):
    import urllib.request
    from bs4 import BeautifulSoup
    print("⚠️ 未检测到 Playwright Chromium 驱动，正在启用优雅降级抓取模式 (urllib + BeautifulSoup)...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    for elem in soup(["script", "style", "nav", "footer"]):
        elem.extract()
    title = soup.title.string.strip() if soup.title else url
    text = soup.get_text(separator="\n", strip=True)
    out_file = output_path or "fallback_extracted.md"
    os.makedirs(os.path.dirname(os.path.abspath(out_file)), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n**URL**: {url}\n\n## 内容\n\n{text}\n")
    print(f"✅ 降级解析已导出至: {out_file}")


def main():
    args = parse_args()
    try:
        asyncio.run(run_playwright_workflow(args))
    except ImportError:
        if args.action == "extract":
            fallback_extract(args.url, args.output)
        else:
            print("❌ 执行截图、PDF或仿真交互需安装 Playwright: pip install playwright && playwright install chromium")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 执行失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

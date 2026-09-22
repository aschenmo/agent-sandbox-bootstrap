#!/usr/bin/env python3
"""
OfficeCLI Python Bridge Helper
提供面向 Python 开发者的简洁接口，封装底层 officecli 命令行调用。
"""

import subprocess
import shutil
import json
import os
import sys
from typing import Optional, List, Dict, Any


class OfficeHelper:
    def __init__(self, cli_path: Optional[str] = None):
        self.cli = cli_path or shutil.which("officecli") or "/usr/local/bin/officecli"
        if not os.path.exists(self.cli) and not shutil.which(self.cli):
            raise FileNotFoundError(
                f"officecli binary not found at '{self.cli}'. Please ensure it is installed."
            )

    def _run(self, args: List[str], check: bool = True) -> str:
        cmd = [self.cli] + args
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if check and res.returncode != 0:
            err = res.stderr.strip() or res.stdout.strip()
            raise RuntimeError(f"OfficeCLI command failed: {' '.join(cmd)}\nError: {err}")
        return res.stdout

    # --- 通用生命周期 ---
    def create(self, filename: str, force: bool = True) -> bool:
        """创建空白文档 (.docx, .xlsx, .pptx)"""
        if force:
            self.close(filename)
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except OSError:
                    pass
        out = self._run(["create", filename])
        return "Created:" in out

    def close(self, filename: str) -> None:
        """保存并关闭常驻文档进程"""
        self._run(["close", filename], check=False)

    def save(self, filename: str) -> None:
        """刷新更改至磁盘"""
        self._run(["save", filename], check=False)

    # --- DOCX 专有便捷接口 ---
    def add_heading(self, filename: str, text: str, level: int = 1) -> str:
        """添加标题 (level: 1-6)"""
        style = f"Heading {level}"
        return self._run([
            "add", filename, "/body", "--type", "paragraph",
            "--prop", f"style={style}",
            "--prop", f"text={text}",
        ])

    def add_paragraph(self, filename: str, text: str) -> str:
        """添加普通正文段落"""
        return self._run(["add", filename, "/body", "--type", "paragraph", "--prop", f"text={text}"])

    def render_html(self, filename: str) -> str:
        """将文档渲染为精美 HTML 字符串"""
        return self._run(["view", filename, "html"])

    def get_stats(self, filename: str) -> str:
        """获取文档统计信息"""
        return self._run(["view", filename, "stats"])

    # --- XLSX 专有便捷接口 ---
    def set_cell_value(self, filename: str, target: str, value: Any) -> str:
        """设置单元格数值/文本，例如 target='Sheet1!A1'"""
        return self._run(["set", filename, target, "--prop", f"value={value}"])

    def set_cell_formula(self, filename: str, target: str, formula: str) -> str:
        """设置单元格公式，例如 target='Sheet1!A3', formula='SUM(A1:A2)'"""
        return self._run(["set", filename, target, "--prop", f"formula={formula}"])

    def view_sheet(self, filename: str) -> str:
        """查看表格计算后的文本内容"""
        return self._run(["view", filename, "text"])

    # --- PPTX 专有便捷接口 ---
    def add_slide(self, filename: str) -> str:
        """添加新幻灯片"""
        return self._run(["add", filename, "/", "--type", "slide"])

    def add_slide_shape(
        self,
        filename: str,
        slide_index: int = 1,
        text: str = "",
        x: str = "50pt",
        y: str = "50pt",
        width: str = "400pt",
        height: str = "100pt",
    ) -> str:
        """在幻灯片中添加文本框/形状"""
        parent = f"/slide[{slide_index}]"
        return self._run([
            "add", filename, parent, "--type", "shape",
            "--prop", f"text={text}",
            "--prop", f"x={x}",
            "--prop", f"y={y}",
            "--prop", f"width={width}",
            "--prop", f"height={height}",
        ])


def run_demo(output_dir: str = "/tmp/office_demo") -> None:
    os.makedirs(output_dir, exist_ok=True)
    helper = OfficeHelper()
    print("🚀 [Demo] 正在测试 OfficeCLI Python Bridge...")

    # 1. 测试 DOCX
    docx_file = os.path.join(output_dir, "demo_academic.docx")
    print(f"📄 正在创建 Word 文档: {docx_file}")
    helper.create(docx_file)
    helper.add_heading(docx_file, "Nature Machine Intelligence 研究综述", level=1)
    helper.add_paragraph(
        docx_file,
        "本文探讨了基于原生 OfficeCLI 与 AI Agent 协作开展多学科科学计算与全自动论文排版的新范式。"
    )
    helper.close(docx_file)
    stats = helper.get_stats(docx_file)
    print(f"✅ Word 文档生成完毕，统计信息:\n{stats.strip()}\n")

    # 2. 测试 XLSX
    xlsx_file = os.path.join(output_dir, "demo_calc.xlsx")
    print(f"📊 正在创建 Excel 表格并计算公式: {xlsx_file}")
    helper.create(xlsx_file)
    helper.set_cell_value(xlsx_file, "Sheet1!A1", 1250)
    helper.set_cell_value(xlsx_file, "Sheet1!A2", 3750)
    helper.set_cell_formula(xlsx_file, "Sheet1!A3", "SUM(A1:A2)")
    helper.close(xlsx_file)
    sheet_content = helper.view_sheet(xlsx_file)
    print(f"✅ Excel 表格公式已自动计算，结果:\n{sheet_content.strip()}\n")

    # 3. 测试 PPTX
    pptx_file = os.path.join(output_dir, "demo_slides.pptx")
    print(f"📽️ 正在创建 PowerPoint 幻灯片: {pptx_file}")
    helper.create(pptx_file)
    helper.add_slide(pptx_file)
    helper.add_slide_shape(
        pptx_file, slide_index=1, text="AI Agent 驱动的出版级科研自动化", x="60pt", y="120pt"
    )
    helper.close(pptx_file)
    print(f"✅ PPT 演示文稿生成完毕: {pptx_file}")

    print(f"\n🎉 全部演示产物已生成至目录: {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
    else:
        print("OfficeHelper CLI Bridge. Usage: python3 office_helper.py --demo")

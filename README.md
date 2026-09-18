# Agent Sandbox Armory (无头沙盒一键安装弹药库)
> **AI-Centric Skill Hub & Zero-Plaintext Security Specification**
> 
> 本仓库专为各类大模型（Gemini / Claude / DeepSeek 等）在**无状态云端沙箱环境**下的秒级冷启动与自主作业设计，同时作为 **AI 自动化自维护规范手册**。
> 采用 **OpenSSL 3.0 AES-256-PBKDF2 单密码加盐加密** 体系，实现 **“零明文入库、零交互解密、抗暴力破解”**。

---

## 🚀 1. 新对话一键冷启动指令 (Cold Start)

每次新开会话或沙箱重置后，向 Agent 发送以下标准指令即可完成秒级全自动恢复：

```bash
git clone --depth=1 https://github.com/aschenmo/agent-sandbox-bootstrap.git /tmp/bootstrap && bash /tmp/bootstrap/init.sh "YOUR_MASTER_PASSWORD"
```
*(注：执行后密码在内存中立即 `unset`，密文安全解密至 `/tmp/env.sh` 并赋予 `600` 权限，自动激活所有学术技能)*

---

## 🏗️ 2. 仓库架构体系 (Directory Tree)

```text
agent-sandbox-bootstrap/
├── registry.json                 # 📖 全局技能元数据索引（供大模型秒级语义路由）
├── init.sh                       # 🚀 沙箱 Master 初始化脚本（安全解密凭证、挂载全局 CLI）
├── load_skill.sh                 # ⚡ 技能按需懒加载运行时（自动安装依赖 + 导出 PATH）
├── secrets.enc                   # 🔐 AES-256-PBKDF2 强加密凭证池 (无明文泄露风险)
└── domains/                      # 🌐 业务领域分类（一级分类：Domain；二级：Skill）
    ├── deep_research/            # 📁 【深度调研与学术检索】
    │   ├── academic_search/      #    - PubMed / Semantic Scholar 跨库文献检索
    │   └── ima-skills/           #    - 腾讯 ima 个人与团队知识库、笔记管理与 COS 直传
    └── academic_scientific/      # 📁 【科研论文与图表】
        └── nature-skills/        #    - Nature 顶刊科研流程与出版技能库 (20+ 技能规范)
```

---

## 🤖 3. AI 智能体自维护与扩展规范 (AI Self-Maintenance SOP)

当用户要求你（AI 助手）**“添加新领域”**、**“上传/补充新技能”** 时，必须严格按以下标准化流程执行：

### 📌 规范 1：技能“标准四件套”契约 (The 4-Piece Contract)
在 `domains/<domain_name>/<skill_name>/` 目录下，每一个新增的技能**必须且仅能**包含以下标准化组件：

1. **`SKILL.md` (元数据与使用说明)**：
   - 必须包含顶部 YAML Frontmatter（`name`, `domain`, `description`, `required_keys`, `dependencies`）。
   - 明确说明调用参数、输入输出格式及 CLI 示例。
2. **`requirements.txt` (按需专属依赖)**：
   - 声明当前技能运行所需的最小 Python / Node 依赖包（若无第三方依赖可省略）。
3. **`scripts/` (可执行脚本目录)**：
   - 包含核心 Python 脚本（如 `main.py` 或特定语义命名的脚本），必须支持标准命令行参数（`--input`, `--output`, `--query` 等），并自带 `#!/usr/bin/env python3` 与标准异常捕获。
4. **`registry.json` (全局注册表同步)**：
   - **必须**在仓库根目录的 `registry.json` 中追加该技能的元数据对象，确保其它 Agent 能秒级发现。

---

### 📌 规范 2：`registry.json` 注册元数据标准
每次新增技能，必须在 `registry.json` 数组中追加以下格式的 JSON 对象：

```json
{
  "id": "unique_skill_id",
  "name": "技能中文名称",
  "domain": "一级领域目录名（如 deep_research）",
  "description": "详细的功能描述与触发场景（包含关键词以利于模型语义匹配）",
  "path": "domains/一级领域目录名/技能目录名",
  "entrypoint": "scripts/入口脚本.py",
  "dependencies": ["可选：依赖库列表"],
  "required_keys": ["可选：所需的环境变量名，如 DEEPSEEK_API_KEY"]
}
```

---

### 📌 规范 3：密钥与环境变量管理准则
1. **统一读取方式**：所有脚本中读取 API Key 必须使用 `os.getenv("KEY_NAME", "默认值")`，禁止在代码中硬编码任何明文私钥。
2. **零明文规则**：禁止将任何明文 `.env` 提交至 Git 仓库。如需增减 API Key，请使用 OpenSSL 加密为 `secrets.enc` 后提交。
3. **自动注入机制**：`init.sh` 会在沙箱启动时自动将 `secrets.enc` 解密为 `/tmp/env.sh`，供所有子进程直接读取。

---

## 📝 4. AI 维护示例模板 (Quick Copy-Paste Templates)

### 示例 A：新增一个技能的 `SKILL.md` 模板
```markdown
---
name: my_awesome_skill
domain: data_analysis
description: 对科研时间序列数据进行平稳性检验与自回归预测分析
required_keys: [MY_API_KEY]
dependencies: [pandas, statsmodels, numpy]
---

# 时间序列分析技能

## 📌 功能描述
提供针对学术实验时间序列的平稳性检验 (ADF)、季节性分解及预测。

## 🚀 CLI 调用示例
```bash
python3 analyze_series.py --input /tmp/inputs/data.csv --output /tmp/outputs/forecast.png
```
```

### 示例 B：标准 Python 执行脚本模板 (`scripts/xxx.py`)
```python
#!/usr/bin/env python3
import os
import sys
import argparse
import json

def run_task(input_path, output_path):
    api_key = os.getenv("MY_SERVICE_KEY", "")
    # 执行业务核心逻辑...
    print(f"✅ 处理完成: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="技能描述")
    parser.add_argument("--input", "-i", required=True, help="输入数据路径")
    parser.add_argument("--output", "-o", default="/tmp/outputs/result.json", help="输出路径")
    args = parser.parse_args()
    run_task(args.input, args.output)
```

---

## ✅ 5. AI 提交前自检清单 (Pre-Commit Checklist)

在为用户完成仓库修改并提交 Git 前，AI 必须确认：
- [ ] 目录是否置于正确的 `domains/<domain_name>/<skill_name>/` 下？
- [ ] 是否编写了符合规范的 `SKILL.md` 并包含 YAML 元数据？
- [ ] `scripts/` 下的 Python/Bash 脚本是否已添加执行权限 (`chmod +x`) 且没有硬编码明文密钥？
- [ ] 根目录的 `registry.json` 是否已同步追加，且 JSON 格式合法无语法错误？
- [ ] 执行 `bash init.sh` 能否在 1 秒内无报错打印全部技能清单？

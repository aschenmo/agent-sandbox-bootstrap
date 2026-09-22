#!/usr/bin/env bash
# office-cli 技能环境自检与激活脚本

if ! command -v officecli &>/dev/null; then
  echo "🔍 [office-cli] 检测到未安装 officecli 二进制，正在自动拉取安装..."
  curl -fsSL "https://github.com/iOfficeAI/OfficeCLI/releases/latest/download/officecli-linux-x64" -o /usr/local/bin/officecli 2>/dev/null || true
  chmod +x /usr/local/bin/officecli 2>/dev/null || true
fi

if command -v officecli &>/dev/null; then
  VERSION=$(officecli --version 2>/dev/null || echo "ready")
  echo "📄 [office-cli] 引擎就绪: OfficeCLI v${VERSION}"
else
  echo "⚠️ [office-cli] officecli 安装未完成，请检查网络连接。"
fi

#!/usr/bin/env bash
# ==============================================================================
# Agent Sandbox Master Bootstrap (OpenSSL AES-256-PBKDF2 安全解密与技能引擎)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
mkdir -p "$BIN_DIR" /tmp/inputs /tmp/outputs

# 获取传入的主密码（优先使用第1个参数，其次读取环境变量 BOOTSTRAP_PASS）
MASTER_KEY="${1:-$BOOTSTRAP_PASS}"

echo "================================================================="
echo "🚀 启动 Agent Sandbox 极速初始化流程 (Secure Armory)"
echo "================================================================="

# ------------------------------------------------------------------------------
# 1. 安全解密并加载环境变量
# ------------------------------------------------------------------------------
echo "🔑 [1/3] 正在安全解密 API 凭证池..."

if [ -n "$MASTER_KEY" ] && [ -f "$SCRIPT_DIR/secrets.enc" ]; then
  # 解密到 /tmp/env.sh，静默错误流防止任何明文或调用栈泄露
  if openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 -in "$SCRIPT_DIR/secrets.enc" -out /tmp/env.sh -pass pass:"$MASTER_KEY" 2>/dev/null; then
    chmod 600 /tmp/env.sh
    set -a
    source /tmp/env.sh
    set +a
    echo "✅ [SUCCESS] 凭据解密成功，已安全载入沙箱上下文 (/tmp/env.sh)"
  else
    echo "❌ [ERROR] 凭据解密失败！请检查输入的主密码是否正确。"
    unset MASTER_KEY BOOTSTRAP_PASS
    exit 1
  fi
elif [ -f "/tmp/env.sh" ]; then
  set -a
  source /tmp/env.sh
  set +a
  echo "✅ 已安全复用当前沙箱会话已存在的环境变量 (/tmp/env.sh)"
else
  echo "⚠️ 未提供主密码或未检测到 secrets.enc，跳过私有 Key 解密。"
fi

# 立即销毁内存中的密码变量，防止子进程继承
unset MASTER_KEY BOOTSTRAP_PASS

# ------------------------------------------------------------------------------
# 2. 自动同步 Git 子模块 (顶刊学术技能矩阵)
# ------------------------------------------------------------------------------
if [ -f "$SCRIPT_DIR/.gitmodules" ]; then
  echo "🔄 [2/3] 正在同步学术技能子模块..."
  (cd "$SCRIPT_DIR" && git submodule update --init --recursive 2>/dev/null) || true
fi

# ------------------------------------------------------------------------------
# 3. 挂载全局 CLI 快捷命令 (load_skill)
# ------------------------------------------------------------------------------
echo "⚡ [3/3] 注册 load_skill 全局命令至系统 PATH..."
chmod +x "$SCRIPT_DIR/load_skill.sh"

# 建立用户级软链接
mkdir -p /usr/local/bin 2>/dev/null || true
ln -sf "$SCRIPT_DIR/load_skill.sh" /usr/local/bin/load_skill 2>/dev/null || ln -sf "$SCRIPT_DIR/load_skill.sh" "$BIN_DIR/load_skill" 2>/dev/null || true

export PATH="$SCRIPT_DIR:$BIN_DIR:/usr/local/bin:$PATH"
echo "export PATH=\"$SCRIPT_DIR:$BIN_DIR:/usr/local/bin:\$PATH\"" >> ~/.bashrc
echo "alias load_skill='source $SCRIPT_DIR/load_skill.sh'" >> ~/.bashrc

echo "================================================================="
echo "🎉 沙箱环境已就绪！输入 'load_skill' 即可按需加载业务模块。"
echo "================================================================="
echo "📚 当前可用技能库清单："
if [ -f "$SCRIPT_DIR/registry.json" ]; then
  python3 -c "import json; data=json.load(open('$SCRIPT_DIR/registry.json')); print('\n'.join([f\"  • \033[1;32m{item['id']}\033[0m [\033[1;34m{item['domain']}\033[0m] : {item['description']}\" for item in data]))" 2>/dev/null || cat "$SCRIPT_DIR/registry.json"
fi
echo "================================================================="

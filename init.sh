#!/usr/bin/env bash
# ==============================================================================
# Agent Sandbox Master Bootstrap (动静分离 · 自愈持久化 · OpenSSL 凭据安全引擎)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
mkdir -p "$BIN_DIR" /tmp/inputs /tmp/outputs

# ------------------------------------------------------------------------------
# 0. 自动固化与动静分离保障 (Auto-Persistence)
# 若脚本在 /tmp 内存虚拟文件系统中被克隆，自动迁移至系统持久目录，根除重启丢失
# ------------------------------------------------------------------------------
PERSIST_TARGET="/opt/bootstrap"
if [ "$SCRIPT_DIR" != "$PERSIST_TARGET" ] && [ "$SCRIPT_DIR" != "${HOME}/.agent-bootstrap" ]; then
  if [ -w "/opt" ] || [ "$(id -u)" -eq 0 ]; then
    echo "📦 检测到核心仓库运行于临时路径 ($SCRIPT_DIR)，自动固化至系统持久路径 $PERSIST_TARGET ..."
    mkdir -p "$PERSIST_TARGET"
    cp -rn "$SCRIPT_DIR"/* "$PERSIST_TARGET"/ 2>/dev/null || cp -r "$SCRIPT_DIR"/* "$PERSIST_TARGET"/ 2>/dev/null || true
    SCRIPT_DIR="$PERSIST_TARGET"
  else
    USER_PERSIST="${HOME}/.agent-bootstrap"
    echo "📦 检测到非 root 环境，自动固化至用户主目录持久路径 $USER_PERSIST ..."
    mkdir -p "$USER_PERSIST"
    cp -rn "$SCRIPT_DIR"/* "$USER_PERSIST"/ 2>/dev/null || cp -r "$SCRIPT_DIR"/* "$USER_PERSIST"/ 2>/dev/null || true
    SCRIPT_DIR="$USER_PERSIST"
  fi
fi

# 获取传入的主密码（优先使用第1个参数，其次读取环境变量 BOOTSTRAP_PASS）
MASTER_KEY="${1:-$BOOTSTRAP_PASS}"

echo "================================================================="
echo "🚀 启动 Agent Sandbox 极速初始化流程 (动静分离与自愈安全架构)"
echo "📍 核心技能库常驻路径: $SCRIPT_DIR"
echo "================================================================="

# ------------------------------------------------------------------------------
# 1. 安全解密并加载环境变量（内存级防护，重启物理自毁）
# ------------------------------------------------------------------------------
echo "🔑 [1/3] 正在安全解密 API 凭证池..."

if [ -n "$MASTER_KEY" ] && [ -f "$SCRIPT_DIR/secrets.enc" ]; then
  # 解密到 /tmp/env.sh，静默错误流防止任何明文或调用栈泄露
  if openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 -in "$SCRIPT_DIR/secrets.enc" -out /tmp/env.sh -pass pass:"$MASTER_KEY" 2>/dev/null; then
    chmod 600 /tmp/env.sh
    cp -f /tmp/env.sh "$SCRIPT_DIR/.env" 2>/dev/null || true
    [ -f "$SCRIPT_DIR/.env" ] && chmod 600 "$SCRIPT_DIR/.env"
    set -a
    source /tmp/env.sh
    set +a
    grep -qF "/tmp/env.sh" ~/.bashrc 2>/dev/null || echo "[ -f /tmp/env.sh ] && source /tmp/env.sh" >> ~/.bashrc
    grep -qF "/tmp/env.sh" ~/.profile 2>/dev/null || echo "[ -f /tmp/env.sh ] && source /tmp/env.sh" >> ~/.profile
    echo "✅ [SUCCESS] 凭据解密成功，已载入当前沙箱环境与 /tmp/env.sh"
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
# 3. 安装自愈型 load_skill 全局 Launcher（彻底根除死软链接）
# ------------------------------------------------------------------------------
echo "⚡ [3/3] 安装 load_skill 自愈启动器至系统 PATH..."
chmod +x "$SCRIPT_DIR/load_skill.sh"

# 生成自愈型 Launcher 包装脚本（避免使用脆弱的指向 /tmp 的软链接）
INSTALL_WRAPPER="/tmp/load_skill_launcher.sh"
cat << 'EOF' > "$INSTALL_WRAPPER"
#!/usr/bin/env bash
# ==============================================================================
# Agent Sandbox Skill Launcher (Self-Healing Dispatcher)
# ==============================================================================
CANDIDATE_DIRS=(
  "${BOOTSTRAP_DIR}"
  "/opt/bootstrap"
  "${HOME}/.agent-bootstrap"
  "/tmp/bootstrap"
)

RESOLVED_DIR=""
for dir in "${CANDIDATE_DIRS[@]}"; do
  if [ -n "$dir" ] && [ -f "$dir/load_skill.sh" ]; then
    RESOLVED_DIR="$dir"
    break
  fi
done

if [ -z "$RESOLVED_DIR" ]; then
  echo "❌ [Agent Sandbox Alert] 未在系统中检测到 agent-sandbox-bootstrap 技能库！"
  echo "💡 请执行快速初始化命令："
  echo "   [ -d /opt/bootstrap ] && bash /opt/bootstrap/init.sh \"[密码]\" || (git clone --depth=1 https://github.com/aschenmo/agent-sandbox-bootstrap.git /opt/bootstrap 2>/dev/null || git clone --depth=1 https://github.com/aschenmo/agent-sandbox-bootstrap.git ~/.agent-bootstrap) && ([ -d /opt/bootstrap ] && bash /opt/bootstrap/init.sh \"[密码]\" || bash ~/.agent-bootstrap/init.sh \"[密码]\")"
  return 1 2>/dev/null || exit 1
fi

# 检查内存凭据状态（容器重启感知）
if [ ! -f "/tmp/env.sh" ] && [ ! -f "$RESOLVED_DIR/.env" ]; then
  echo "⚠️ [Agent Sandbox Notice] 沙箱容器可能曾被重启，内存凭据池 (/tmp/env.sh) 处于待激活状态。"
  echo "💡 若当前技能依赖 API Key，请先补充密码极速激活：bash $RESOLVED_DIR/init.sh \"[密码]\""
  echo "------------------------------------------------------------------"
fi

if [ -f "/tmp/env.sh" ] && [ -z "$GEMINI_API_KEY" ] && [ -z "$SILICONFLOW_API_KEY" ]; then
  set -a
  source /tmp/env.sh 2>/dev/null || true
  set +a
fi

if [[ "${BASH_SOURCE[0]}" != "${0}" ]] || [ -n "$ZSH_EVAL_CONTEXT" ]; then
  source "$RESOLVED_DIR/load_skill.sh" "$@"
else
  bash "$RESOLVED_DIR/load_skill.sh" "$@"
  if [ $? -eq 0 ] && [ -n "$1" ]; then
    echo "💡 [提示] 若需要将该技能的 Python/PATH 永久置入当前交互式 Shell，请使用: source load_skill $1"
  fi
fi
EOF

chmod +x "$INSTALL_WRAPPER"

# 优先清理旧的死软链接或残存文件
mkdir -p /usr/local/bin 2>/dev/null || true
rm -f /usr/local/bin/load_skill "$BIN_DIR/load_skill" 2>/dev/null || true
cp -f "$INSTALL_WRAPPER" /usr/local/bin/load_skill 2>/dev/null || true
cp -f "$INSTALL_WRAPPER" "$BIN_DIR/load_skill" 2>/dev/null || true
chmod +x /usr/local/bin/load_skill 2>/dev/null || true
chmod +x "$BIN_DIR/load_skill" 2>/dev/null || true
rm -f "$INSTALL_WRAPPER"

export PATH="$SCRIPT_DIR:$BIN_DIR:/usr/local/bin:$PATH"
grep -qF "export PATH=\"/opt/bootstrap" ~/.bashrc 2>/dev/null || echo "export PATH=\"/opt/bootstrap:\$HOME/.agent-bootstrap:\$HOME/.local/bin:/usr/local/bin:\$PATH\"" >> ~/.bashrc
grep -qF "alias load_skill='source load_skill'" ~/.bashrc 2>/dev/null || echo "alias load_skill='source load_skill'" >> ~/.bashrc

echo "================================================================="
echo "🎉 沙箱环境已就绪！核心库已常驻，load_skill 已进化为自愈启动器。"
echo "💡 提示：容器重启后无需重新 git clone，仅需执行以下命令 0 秒唤醒："
echo "   bash $SCRIPT_DIR/init.sh \"[主密码]\""
echo "================================================================="
echo "📚 当前可用技能库清单："
if [ -f "$SCRIPT_DIR/registry.json" ]; then
  python3 -c "import json; data=json.load(open('$SCRIPT_DIR/registry.json')); print('\n'.join([f\"  • \033[1;32m{item['id']}\033[0m [\033[1;34m{item['domain']}\033[0m] : {item['description']}\" for item in data]))" 2>/dev/null || cat "$SCRIPT_DIR/registry.json"
fi
echo "================================================================="


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

# 获取传入的主密码（优先级：参数1 > 环境变量 BOOTSTRAP_PASS > /root/.bootstrap_token > ~/.agent-bootstrap/.token）
MASTER_KEY="${1:-$BOOTSTRAP_PASS}"
if [ -z "$MASTER_KEY" ]; then
  if [ -f "/root/.bootstrap_token" ]; then
    MASTER_KEY="$(cat /root/.bootstrap_token 2>/dev/null || echo '')"
  elif [ -f "${HOME}/.agent-bootstrap/.token" ]; then
    MASTER_KEY="$(cat "${HOME}/.agent-bootstrap/.token" 2>/dev/null || echo '')"
  fi
fi

echo "================================================================="
echo "🚀 启动 Agent Sandbox 极速初始化流程 (动静分离与自愈安全架构)"
echo "📍 核心技能库常驻路径: $SCRIPT_DIR"
echo "================================================================="

# ------------------------------------------------------------------------------
# 1. 第一优先级：安全解密并加载环境变量凭据池 (0 秒急速就绪)
# ------------------------------------------------------------------------------
echo "🔑 [1/3] 优先安全解密 API 凭证池并注入沙箱环境..."

# 若已存在内存凭据且未传入新密码，直接复用已挂载凭据
if [ -z "$MASTER_KEY" ] && [ -f "/tmp/env.sh" ]; then
  set -a
  set +e
  source /tmp/env.sh 2>/dev/null || true
  set -e
  set +a
  echo "✅ [SUCCESS] 检测到会话内存凭据已激活 (/tmp/env.sh)，已直接复用"
elif [ -f "$SCRIPT_DIR/secrets.enc" ]; then
  CANDIDATE_KEYS=()
  [ -n "$MASTER_KEY" ] && CANDIDATE_KEYS+=("$MASTER_KEY")
  if [ -f "/root/.bootstrap_token" ]; then
    chmod 600 "/root/.bootstrap_token" 2>/dev/null || true
    CANDIDATE_KEYS+=("$(cat /root/.bootstrap_token 2>/dev/null)")
  fi
  if [ -f "${HOME}/.agent-bootstrap/.token" ]; then
    chmod 600 "${HOME}/.agent-bootstrap/.token" 2>/dev/null || true
    CANDIDATE_KEYS+=("$(cat "${HOME}/.agent-bootstrap/.token" 2>/dev/null)")
  fi

  # 仅在未通过参数传入且处于交互终端时允许输入（带 3 秒超时防无头环境挂起）
  if [ ${#CANDIDATE_KEYS[@]} -eq 0 ] && [ "$#" -eq 0 ] && [ -t 0 ] && [ -z "$NON_INTERACTIVE" ] && [ -z "$CI" ]; then
    read -t 3 -s -p "🔐 请输入凭据解密密码 (Master Password，3秒后自动跳过): " input_pass 2>/dev/null || true
    echo ""
    [ -n "$input_pass" ] && CANDIDATE_KEYS+=("$input_pass")
  fi

  # 无密码平滑降级（支持无密一键冷启动，绝不中断退出）
  if [ ${#CANDIDATE_KEYS[@]} -eq 0 ]; then
    echo "⚠️ [NOTICE] 未提供主密码或未挂载凭据 Token，跳过商业 API 凭据池解密。"
    echo "💡 本地算法、开源模型、公共工具链与 load_skill 全套生态仍将完整激活。"
    echo "💡 若后续需接入受保护的商业 API，可随时执行: bash $SCRIPT_DIR/init.sh \"[主密码]\""
  else
    DECRYPTED=0
    for cand in "${CANDIDATE_KEYS[@]}"; do
      [ -z "$cand" ] && continue
      # 采用 env: 传参模式，防止口令暴露于 ps aux / /proc/<PID>/cmdline 进程树 (CWE-214 防护)
      export _BOOTSTRAP_MEM_PASS="$cand"
      if openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 -in "$SCRIPT_DIR/secrets.enc" -out /tmp/env.sh -pass env:_BOOTSTRAP_MEM_PASS 2>/dev/null; then
        DECRYPTED=1
        unset _BOOTSTRAP_MEM_PASS
        break
      fi
      unset _BOOTSTRAP_MEM_PASS
    done

    if [ "$DECRYPTED" -eq 1 ]; then
      # 仅落盘在内存虚拟文件系统 /tmp/env.sh (tmpfs)，绝不在 Git 源码工作区保留明文
      chmod 600 /tmp/env.sh
      rm -f "$SCRIPT_DIR/.env" 2>/dev/null || true

      # 用完即焚：擦除预挂载的临时 token 文件，杜绝多租户/非特权进程横向窥探 (CWE-732 防护)
      [ -f "/root/.bootstrap_token" ] && (shred -u "/root/.bootstrap_token" 2>/dev/null || rm -f "/root/.bootstrap_token")
      [ -f "${HOME}/.agent-bootstrap/.token" ] && (shred -u "${HOME}/.agent-bootstrap/.token" 2>/dev/null || rm -f "${HOME}/.agent-bootstrap/.token")

      set -a
      set +e
      source /tmp/env.sh 2>/dev/null || true
      set -e
      set +a
      grep -qF "/tmp/env.sh" ~/.bashrc 2>/dev/null || echo "[ -f /tmp/env.sh ] && source /tmp/env.sh" >> ~/.bashrc
      grep -qF "/tmp/env.sh" ~/.profile 2>/dev/null || echo "[ -f /tmp/env.sh ] && source /tmp/env.sh" >> ~/.profile
      
      # 自动关联 CLI 工具授权
      if [ -n "$GH_TOKEN" ] && command -v gh &>/dev/null; then
        echo "$GH_TOKEN" | gh auth login --with-token 2>/dev/null || true
        gh auth setup-git 2>/dev/null || true
      elif [ -n "$GITHUB_TOKEN" ] && command -v gh &>/dev/null; then
        echo "$GITHUB_TOKEN" | gh auth login --with-token 2>/dev/null || true
        gh auth setup-git 2>/dev/null || true
      fi

      if [ -n "$KAGGLE_USERNAME" ] && [ -n "$KAGGLE_KEY" ]; then
        mkdir -p ~/.kaggle
        cat << KAGGLE_EOF > ~/.kaggle/kaggle.json
{"username":"$KAGGLE_USERNAME","key":"$KAGGLE_KEY"}
KAGGLE_EOF
        chmod 600 ~/.kaggle/kaggle.json
        echo "$KAGGLE_KEY" > ~/.kaggle/access_token
        chmod 600 ~/.kaggle/access_token
      fi

      [ -n "$CLOUDFLARE_API_TOKEN" ] && export CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN"
      [ -n "$CF_API_TOKEN" ] && export CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-$CF_API_TOKEN}"
      [ -n "$CF_ACCOUNT_ID" ] && export CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-$CF_ACCOUNT_ID}"

      echo "✅ [SUCCESS] 凭据解密成功，已载入当前沙箱环境与 /tmp/env.sh"
    else
      echo "⚠️ [WARNING] 凭据解密失败 (提供的密码不匹配)。跳过私有 Key 解密。"
      echo "💡 本地算法、开源模型、公共工具链与 load_skill 全套生态仍将完整激活。"
      echo "💡 若需重新解密，随时执行: bash $SCRIPT_DIR/init.sh \"[正确密码]\""
    fi
  fi
elif [ -f "/tmp/env.sh" ]; then
  set -a
  source /tmp/env.sh
  set +a
  echo "✅ 已安全复用当前沙箱会话已存在的环境变量 (/tmp/env.sh)"
else
  echo "⚠️ 未提供主密码或未检测到 secrets.enc，跳过私有 Key 解密。"
fi

# 立即销毁内存中的全部密码与候选凭证变量，防止子进程继承
unset MASTER_KEY BOOTSTRAP_PASS CANDIDATE_KEYS input_pass _BOOTSTRAP_MEM_PASS cand

# ------------------------------------------------------------------------------
# 2. 安装自愈型 load_skill 全局 Launcher（彻底根除死软链接）
# ------------------------------------------------------------------------------
echo "⚡ [2/3] 安装 load_skill 自愈启动器至系统 PATH..."
chmod +x "$SCRIPT_DIR/load_skill.sh"

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

# ------------------------------------------------------------------------------
# 3. 核心工具链极速就绪 (轻量同步就绪 + 重型生态后台异步预热，绝不阻塞握手)
# ------------------------------------------------------------------------------
echo "🛠️ [3/3] 就绪核心工具链与运行时生态..."

# 3.1 GitHub CLI (gh - 快速检测并就绪)
if ! command -v gh &>/dev/null; then
  (curl -fsSL "https://github.com/cli/cli/releases/download/v2.101.0/gh_2.101.0_linux_amd64.tar.gz" -o /tmp/gh.tar.gz 2>/dev/null && \
   tar -xzf /tmp/gh.tar.gz -C /tmp && \
   cp /tmp/gh_2.101.0_linux_amd64/bin/gh /usr/local/bin/gh && \
   chmod +x /usr/local/bin/gh && \
   rm -rf /tmp/gh*) 2>/dev/null || true
fi

# 3.2 OfficeCLI (快速检测并就绪)
if ! command -v officecli &>/dev/null; then
  (curl -fsSL "https://github.com/iOfficeAI/OfficeCLI/releases/latest/download/officecli-linux-x64" -o /usr/local/bin/officecli 2>/dev/null && \
   chmod +x /usr/local/bin/officecli) 2>/dev/null || true
fi

# 3.3 Kaggle CLI (pip 轻量安装)
if ! command -v kaggle &>/dev/null; then
  pip3 install --break-system-packages --quiet kaggle 2>/dev/null || true
fi

# 3.4 顶刊学术技能矩阵 (nature-skills) 就绪与增量同步 (多重容错兜底)
NATURE_SKILLS_DIR="$SCRIPT_DIR/domains/academic_scientific/nature-skills"
if [ ! -d "$NATURE_SKILLS_DIR/skills" ]; then
  echo "📥 正在就绪顶刊学术套件 (nature-skills)..."
  mkdir -p "$(dirname "$NATURE_SKILLS_DIR")"
  (cd "$SCRIPT_DIR" && git submodule update --init --recursive 2>/dev/null) || \
  git clone --depth=1 https://github.com/Yuan1z0825/nature-skills.git "$NATURE_SKILLS_DIR" 2>/dev/null || true
elif [ -d "$NATURE_SKILLS_DIR/.git" ]; then
  (cd "$NATURE_SKILLS_DIR" && git pull --ff-only 2>/dev/null) || true
fi

# 3.5 无头 Chrome 与重型 CLI (后台静默预热，绝不阻塞沙箱握手返回)
(
  # Cloudflare Wrangler & Vercel
  command -v wrangler &>/dev/null || npm install -g wrangler --silent 2>/dev/null || true
  command -v vercel &>/dev/null || npm install -g vercel --silent 2>/dev/null || true
  
  # 无头 Google Chrome & 中文字体
  if ! command -v google-chrome &>/dev/null && [ ! -f "/usr/bin/google-chrome" ]; then
    (apt-get update -qq 2>/dev/null && apt-get install -y --no-install-recommends google-chrome-stable fonts-wqy-microhei fonts-wqy-zenhei 2>/dev/null && fc-cache -f 2>/dev/null) || true
  fi
  pip3 install --break-system-packages --quiet playwright 2>/dev/null || true
) &>/dev/null &

export CHROME_PATH="${CHROME_PATH:-/usr/bin/google-chrome}"
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD="1"

echo "================================================================="
if [ -f "/tmp/env.sh" ]; then
  echo "🎉 沙箱环境已秒级就绪！核心凭证池已解密，load_skill 已全面激活。"
else
  echo "🎉 沙箱环境已秒级就绪！公共科研技能矩阵与 load_skill 调度器已全面就绪。"
fi
echo "💡 提示：容器重启后无需重新 git clone，仅需执行以下命令 0 秒唤醒："
echo "   bash $SCRIPT_DIR/init.sh \"[主密码]\""
echo "================================================================="
echo "📚 当前可用技能库清单："
if [ -f "$SCRIPT_DIR/registry.json" ]; then
  python3 -c "import json; data=json.load(open('$SCRIPT_DIR/registry.json')); print('\n'.join([f\"  • \033[1;32m{item['id']}\033[0m [\033[1;34m{item['domain']}\033[0m] : {item['description']}\" for item in data]))" 2>/dev/null || cat "$SCRIPT_DIR/registry.json"
fi
echo "================================================================="

#!/usr/bin/env bash
# Agent Sandbox On-Demand Skill Loader (按需加载运行时)
# 用法: source load_skill.sh <skill_name_or_path>

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$1"

if [ -z "$TARGET" ]; then
  echo "❌ 请指定要加载的技能名称或路径！"
  echo "例如: load_skill academic_search 或 load_skill domains/academic_scientific/nature_figure"
  echo ""
  echo "当前可用技能列表（来自 registry.json）："
  if [ -f "$ROOT_DIR/registry.json" ]; then
    python3 -c "import json; data=json.load(open('$ROOT_DIR/registry.json')); print('\n'.join([f\"  • {item['id']} ({item['domain']}) - {item['description']}\" for item in data]))" 2>/dev/null || cat "$ROOT_DIR/registry.json"
  fi
  return 1 2>/dev/null || exit 1
fi

SKILL_DIR=""
NORMALIZED_TARGET="$(echo "$TARGET" | tr '_' '-')"
NORMALIZED_TARGET_UNDERSCORE="$(echo "$TARGET" | tr '-' '_')"

if [ -d "$ROOT_DIR/$TARGET" ]; then
  SKILL_DIR="$ROOT_DIR/$TARGET"
elif [ -d "$ROOT_DIR/domains/$TARGET" ]; then
  SKILL_DIR="$ROOT_DIR/domains/$TARGET"
else
  # 在 domains 目录下全量递归智能匹配（支持 Submodule 与下划线/短横线互通）
  FOUND="$(find "$ROOT_DIR/domains" -maxdepth 5 -type d \( -name "$TARGET" -o -name "$NORMALIZED_TARGET" -o -name "$NORMALIZED_TARGET_UNDERSCORE" \) 2>/dev/null | head -n 1)"
  if [ -n "$FOUND" ] && [ -d "$FOUND" ]; then
    SKILL_DIR="$FOUND"
  fi
fi

if [ -z "$SKILL_DIR" ] || [ ! -d "$SKILL_DIR" ]; then
  echo "❌ 未找到技能: $TARGET"
  return 1 2>/dev/null || exit 1
fi

echo "🚀 [Skill Loader] 正在按需加载技能: $(basename "$SKILL_DIR") ..."

# 1. 按需安装 Python 依赖（带安装缓存标记）
if [ -f "$SKILL_DIR/requirements.txt" ]; then
  if [ ! -f "$SKILL_DIR/.installed" ]; then
    echo "📦 正在安装专属依赖 ($(basename "$SKILL_DIR"))..."
    pip install -q -r "$SKILL_DIR/requirements.txt" --break-system-packages 2>/dev/null || pip install -q -r "$SKILL_DIR/requirements.txt" 2>/dev/null || true
    touch "$SKILL_DIR/.installed"
  fi
fi

# 2. 导出 PYTHONPATH 与 PATH
if [ -d "$SKILL_DIR/scripts" ]; then
  export PATH="$SKILL_DIR/scripts:$PATH"
  export PYTHONPATH="$SKILL_DIR/scripts:$PYTHONPATH"
fi
export PYTHONPATH="$SKILL_DIR:$PYTHONPATH"

# 3. 检查是否有特定的 setup/activate 脚本
if [ -f "$SKILL_DIR/activate.sh" ]; then
  source "$SKILL_DIR/activate.sh"
fi

echo "✅ 技能 [$(basename "$SKILL_DIR")] 加载就绪！"

# 4. 如果存在 SKILL.md，打印简短操作摘要
if [ -f "$SKILL_DIR/SKILL.md" ]; then
  echo "📖 技能使用摘要:"
  head -n 20 "$SKILL_DIR/SKILL.md"
fi

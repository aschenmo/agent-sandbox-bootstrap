#!/usr/bin/env bash
# ==============================================================================
# pack_secrets.sh - 一键加密打包环境变量工具 (AES-256-PBKDF2 100,000次迭代)
# 专为 Agent Sandbox 弹药库设计：任何人均可使用此工具打包自己的私密凭据
# ==============================================================================
set -e

ENV_FILE="${1:-.env}"
OUTPUT_ENC="${2:-secrets.enc}"

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ 错误: 找不到指定的环境变量文件: $ENV_FILE"
  echo "用法: $0 [源.env路径] [输出.enc路径] [可选直接指定口令]"
  echo "示例: $0 .env secrets.enc"
  exit 1
fi

if [ -z "$3" ]; then
  read -s -p "🔐 请输入加密主口令 (Master Password): " PASS1
  echo ""
  read -s -p "🔐 请再次输入主口令进行确认: " PASS2
  echo ""
  if [ "$PASS1" != "$PASS2" ]; then
    echo "❌ 错误: 两次输入的口令不一致，操作已取消。"
    exit 1
  fi
  PASSWORD="$PASS1"
else
  PASSWORD="$3"
fi

if [ -z "$PASSWORD" ]; then
  echo "❌ 错误: 口令不能为空。"
  exit 1
fi

echo "📦 正在使用 OpenSSL AES-256-PBKDF2 (100,000次加盐迭代) 打包凭据..."
export _PACK_MEM_PASS="$PASSWORD"
openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -salt -in "$ENV_FILE" -out "$OUTPUT_ENC" -pass env:_PACK_MEM_PASS
unset _PACK_MEM_PASS PASSWORD PASS1 PASS2
chmod 644 "$OUTPUT_ENC"

echo "✅ 打包完成: $OUTPUT_ENC"
echo "✨ 特性说明:"
echo "   1. 采用金融级 OpenSSL 3.0 AES-256-PBKDF2 强加密，无任何明文落盘；"
echo "   2. 只有持有此主口令者在沙箱中执行 init.sh 时方可秒级解密；"
echo "   3. 任何人克隆本仓库后，均可运行本脚本生成其专属的 secrets.enc，实现各用各密。"

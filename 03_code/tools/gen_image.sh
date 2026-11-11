#!/usr/bin/env bash
# ============================================
# 脚本名称：gen_image.sh
# 功能描述：经 toapis 网关调用 gpt-image-2 生成课程插图（异步任务：提交→轮询→下载）
# 用法：    bash 03_code/tools/gen_image.sh <prompt文件> <输出.png> [比例] [分辨率]
#           比例默认 3:2（=1536x1024@1K），分辨率默认 1K
# 凭据：    只读环境变量 OPENAI_API_KEY（toapis 的 sk- key），不落盘、不进 git；
#           教师机器上可 export OPENAI_API_KEY=sk-... 后直接运行
# 文档：    https://docs.toapis.com/docs/cn/api-reference/images/gpt-image-2/generation
# ============================================
set -euo pipefail

PROMPT_FILE=${1:?用法: gen_image.sh <prompt文件> <输出.png> [比例] [分辨率]}
OUT=${2:?用法: gen_image.sh <prompt文件> <输出.png> [比例] [分辨率]}
SIZE=${3:-3:2}
RESOLUTION=${4:-1K}

: "${OPENAI_API_KEY:?未设置 OPENAI_API_KEY（toapis 的 sk- key）}"
BASE_URL=${OPENAI_BASE_URL:-https://toapis.com/v1}

# prompt 正文 = markdown 文件里的非标题/引用/列表/代码块行
PROMPT=$(python3 - "$PROMPT_FILE" <<'PY'
import sys, re
lines = open(sys.argv[1], encoding="utf-8").read().splitlines()
keep, in_code = [], False
for ln in lines:
    s = ln.strip()
    if s.startswith("```"):
        in_code = not in_code
        continue
    if in_code or not s or s.startswith(("#", ">", "|", "-")):
        continue
    keep.append(s)
print(re.sub(r"\s+", " ", " ".join(keep)))
PY
)

mkdir -p "$(dirname "$OUT")"
echo ">> 提交生成任务：model=gpt-image-2 size=$SIZE resolution=$RESOLUTION"
TASK=$(curl -sS "${BASE_URL}/images/generations" \
  -H "Authorization: Bearer ${OPENAI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$(python3 -c '
import json, sys
print(json.dumps({"model": "gpt-image-2", "prompt": sys.argv[1],
                  "n": 1, "size": sys.argv[2], "resolution": sys.argv[3],
                  "response_format": "url"}))' "$PROMPT" "$SIZE" "$RESOLUTION")")

TASK_ID=$(printf '%s' "$TASK" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("id",""))')
[ -n "$TASK_ID" ] || { echo "!! 提交失败：$TASK" >&2; exit 1; }
echo ">> 任务 ID：$TASK_ID"

# 轮询：初始等 2s，间隔 3s，最长 180s（官方建议 5–30s 典型）
for i in $(seq 1 60); do
  sleep 3
  STATUS_JSON=$(curl -sS "${BASE_URL}/images/generations/${TASK_ID}" \
    -H "Authorization: Bearer ${OPENAI_API_KEY}")
  STATUS=$(printf '%s' "$STATUS_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("status",""))')
  echo "   [$i] status=$STATUS"
  case "$STATUS" in
    completed)
      URL=$(printf '%s' "$STATUS_JSON" | python3 -c '
import json, sys
d = json.load(sys.stdin)
print(d["result"]["data"][0]["url"])')
      curl -sS -o "$OUT" "$URL"
      echo ">> 完成：$OUT（24h 内 URL 会过期，图已落盘）"
      exit 0
      ;;
    failed)
      echo "!! 生成失败：$STATUS_JSON" >&2
      exit 1
      ;;
  esac
done
echo "!! 轮询超时（180s），任务可能仍在队列：$TASK_ID" >&2
exit 1

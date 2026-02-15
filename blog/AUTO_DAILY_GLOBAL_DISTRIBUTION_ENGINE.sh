#!/usr/bin/env bash
# ============================================================
# AUTO DAILY GLOBAL DISTRIBUTION ENGINE (SAFE, NO SPAM)
# Secrets are read from environment variables (Render)
# ============================================================

set -e

# ------------------------
# CONFIG (FROM ENV)
# ------------------------
BOT_TOKEN="${BOT_TOKEN}"
OWNER_CHAT_ID="${OWNER_CHAT_ID}"
OWNER_EMAIL="${OWNER_EMAIL}"

if [[ -z "$BOT_TOKEN" || -z "$OWNER_CHAT_ID" ]]; then
  echo "ERROR: BOT_TOKEN or OWNER_CHAT_ID not set in environment."
  exit 1
fi

SITE_BASE="https://www.elevateaura.co.in"
TODAY=$(date +"%Y-%m-%d")
DAILY_URL="${SITE_BASE}/blog/daily-free-ssc-questions-${TODAY}.html"

DISTRIBUTION_DIR="./distribution-packs"
PACK_FILE="${DISTRIBUTION_DIR}/distribution-pack-${TODAY}.txt"

mkdir -p "${DISTRIBUTION_DIR}"

echo "=== GLOBAL DISTRIBUTION ENGINE STARTED (${TODAY}) ==="

# ------------------------
# 1) AUTO-POST TO TELEGRAM (OWNED CHANNEL)
# ------------------------
TG_TEXT="📘 Today's Free SSC Questions (${TODAY})\n\nPractice exam-level SSC questions with full solutions (Hindi + English):\n${DAILY_URL}\n\nJoin daily free practice: https://t.me/ElevateAura_Bot"

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d chat_id="@ElevateAura_Bot" \
  -d text="${TG_TEXT}" \
  -d disable_web_page_preview=false || echo "WARN: Failed to post to channel"

# ------------------------
# 2) GENERATE HUMAN-READY SHARE SNIPPETS (NO BOT POSTING TO QUORA/REDDIT)
# ------------------------
cat <<EOF > "${PACK_FILE}"
DAILY DISTRIBUTION PACK – ${TODAY}
Link to share:
${DAILY_URL}

Telegram:
"Free SSC daily questions with full solutions (Hindi + English): ${DAILY_URL}"

Quora:
"I've been using this free SSC daily practice page with full solutions in Hindi + English. Useful for SSC CGL/CHSL beginners: ${DAILY_URL}"

Reddit:
"I built a free daily SSC practice page (Hindi + English). Feedback welcome: ${DAILY_URL}"

X (Twitter):
"Free SSC daily practice with solutions (Hindi + English): ${DAILY_URL} #SSC #SSCCGL #ExamPrep"

Facebook:
"Anyone preparing for SSC? Here’s a free daily practice page with full solutions (Hindi + English): ${DAILY_URL}"

LinkedIn:
"Sharing a free SSC daily practice resource with full solutions (Hindi + English) for aspirants: ${DAILY_URL}"

Medium:
"Free SSC Daily Practice with solutions (Hindi + English): ${DAILY_URL}"

YouTube comments:
"Free SSC daily practice with solutions (Hindi + English): ${DAILY_URL}"

WhatsApp status:
"Free SSC daily questions (Hindi + English): ${DAILY_URL}"

(Use different lines on different days. Do NOT post the same text everywhere.)
EOF

# ------------------------
# 3) OWNER NOTIFICATION (DM YOU)
# ------------------------
OWNER_MSG="📦 Daily Distribution Pack ready (${TODAY}).\n\nLink:\n${DAILY_URL}\n\nPack saved at:\n${PACK_FILE}\n\nPost manually on Quora/Reddit/X/FB to avoid bans."

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d chat_id="${OWNER_CHAT_ID}" \
  -d text="${OWNER_MSG}" || echo "WARN: Failed to DM owner"

echo "=== GLOBAL DISTRIBUTION ENGINE COMPLETED (SAFE MODE) ==="

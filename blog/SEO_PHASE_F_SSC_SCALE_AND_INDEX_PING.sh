#!/usr/bin/env bash
# ============================================================
# SEO PHASE F – SSC SCALE + GOOGLE INDEXING PING ENGINE
# Purpose: Safely scale 500+ SSC SEO doors and trigger crawling
# ============================================================

echo "Starting Phase F – SSC Scale + Index Ping Engine..."

# ============================================================
# 1. Generate 100 New SSC Topic Doors (Batch Mode)
# ============================================================

TOPIC_FILE="/seo/ssc_topics_batch_next.txt"
OUTPUT_DIR="/blog"

while read -r TOPIC
do
  SLUG="free-ssc-${TOPIC}-questions"
  FILE="${OUTPUT_DIR}/${SLUG}.html"

  TITLE="Free SSC ${TOPIC//-/ } Questions with Solutions (Hindi + English) | Elevate Aura"
  H1="Free SSC ${TOPIC//-/ } Questions with Full Solutions"

  echo "Creating: $FILE"

  # Antigravity Instructions:
  # Create SEO page using SSC master template with:
  # - <title>: $TITLE
  # - <h1>: $H1
  # - Topic-specific intro (mention 'free SSC practice')
  # - 10–15 SSC exam-level questions (Hindi + English + full solutions)
  # - Internal links to:
  #   - /blog/free-ssc-questions.html
  #   - /blog/trending-ssc-questions.html
  #   - 3 other SSC topic pages
  # - CTA to Telegram: https://t.me/ElevateAura_Bot

done < "$TOPIC_FILE"

# ============================================================
# 2. Update Sitemap.xml Automatically
# ============================================================

echo "Regenerating sitemap.xml to include all new SSC pages..."

# Antigravity Instructions:
# - Regenerate sitemap.xml
# - Ensure all /blog/free-ssc-*-questions.html URLs are included
# - Ensure lastmod is updated to current date

# ============================================================
# 3. Create Internal Index Pages (Crawl Depth Control)
# ============================================================

echo "Updating internal index pages..."

# Antigravity Instructions:
# Update:
# - /blog/ssc-question-topics.html
# - /blog/free-ssc-questions.html
# - /blog/trending-ssc-questions.html
# To include links to all newly generated SSC topic pages

# ============================================================
# 4. Indexing Ping Instructions (Manual Step Reminder)
# ============================================================

echo "IMPORTANT MANUAL STEP:"
echo "After deployment:"
echo "1. Go to Google Search Console"
echo "2. Submit updated sitemap.xml"
echo "3. Request indexing for:"
echo "   - /blog/free-ssc-questions.html"
echo "   - /blog/trending-ssc-questions.html"
echo "   - 5–10 newly created SSC pages"

# ============================================================
# 5. Throttle Safety (Anti-Spam Control)
# ============================================================

echo "Scaling Rule:"
echo "- Do NOT publish more than 50–100 new pages per week."
echo "- This avoids Google spam classification."
echo "- Let pages age and get crawled."

echo "Phase F completed. SSC SEO scale engine is live."

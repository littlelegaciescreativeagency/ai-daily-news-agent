import feedparser
import requests
import os
from datetime import datetime

# -----------------------------
# 1. LOAD RSS FEEDS
# -----------------------------
def get_feeds():
    return [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.theverge.com/artificial-intelligence/rss/index.xml",
        "https://www.technologyreview.com/topic/artificial-intelligence/feed/"
    ]

# -----------------------------
# 2. FETCH NEWS
# -----------------------------
def get_news():
    feeds = get_feeds()
    articles = []

    for url in feeds:
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            articles.append({
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "link": entry.get("link", "")
            })

    return articles

# -----------------------------
# 3. FORMAT NEWS FOR AI
# -----------------------------
def format_news(articles):
    output = ""

    for a in articles:
        output += f"""
TITLE: {a['title']}
SUMMARY: {a['summary']}
LINK: {a['link']}
---
"""
    return output

# -----------------------------
# 4. CALL GROQ AI
# -----------------------------
def generate_content(news_text):
    api_key = os.getenv("GROQ_API_KEY")

    url = "https://api.groq.com/openai/v1/chat/completions"

    prompt = f"""
You are an AI news analyst and content creator.

Using the news below, create:

1. 5–7 top AI news stories
2. What changed since yesterday
3. A YouTube / Second Life on-camera script
4. Podcast talking points
5. LinkedIn post
6. Threads post
7. Instagram caption
8. 7 tweets

Keep it clear, engaging, and structured.

NEWS DATA:
{news_text}
"""

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
    )

    result = response.json()

    return result["choices"][0]["message"]["content"]

# -----------------------------
# 5. SAVE OUTPUT FILE
# -----------------------------
def save_output(text):
    os.makedirs("output", exist_ok=True)

    filename = f"output/{datetime.now().strftime('%Y-%m-%d')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

# -----------------------------
# 6. RUN EVERYTHING
# -----------------------------
if __name__ == "__main__":
    print("Fetching AI news...")

    news = get_news()
    formatted = format_news(news)

    print("Sending to AI model...")

    content = generate_content(formatted)

    print("Saving output...")

    save_output(content)

    print("DONE - AI News Agent Complete")

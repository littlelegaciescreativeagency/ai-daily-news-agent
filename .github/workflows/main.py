import feedparser
import requests
import os
from datetime import datetime

def get_news():
    feeds = [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.theverge.com/artificial-intelligence/rss/index.xml",
        "https://www.technologyreview.com/topic/artificial-intelligence/feed/"
    ]

    articles = []

    for feed in feeds:
        parsed = feedparser.parse(feed)
        for entry in parsed.entries[:5]:
            articles.append({
                "title": entry.title,
                "summary": getattr(entry, "summary", ""),
                "link": entry.link
            })

    return articles


def format_news(articles):
    text = ""
    for a in articles:
        text += f"""
Title: {a['title']}
Summary: {a['summary']}
Link: {a['link']}

"""
    return text


def generate_ai(news_text):
    api_key = os.getenv("GROQ_API_KEY")

    url = "https://api.groq.com/openai/v1/chat/completions"

    prompt = f"""
You are an AI news analyst.

Create:
1. 5–7 AI news stories
2. What changed since yesterday
3. Video script
4. Talking points
5. LinkedIn post
6. Threads post
7. Instagram caption
8. 7 tweets

NEWS:
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
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    return response.json()["choices"][0]["message"]["content"]


def save_output(content):
    os.makedirs("output", exist_ok=True)

    filename = f"output/{datetime.now().strftime('%Y-%m-%d')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    news = get_news()
    formatted = format_news(news)
    result = generate_ai(formatted)
    save_output(result)

    print("Done")

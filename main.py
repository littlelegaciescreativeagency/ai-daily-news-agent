import feedparser
import requests
import os
from datetime import datetime

# ----------------
# GET NEWS
# ----------------
FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/artificial-intelligence/rss/index.xml",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed/"
]

def get_news():
    articles = []

    for url in FEEDS:
        feed = feedparser.parse(url)

        for item in feed.entries[:5]:
            articles.append({
                "title": item.get("title", ""),
                "summary": item.get("summary", ""),
                "link": item.get("link", "")
            })

    return articles


# ----------------
# FORMAT NEWS
# ----------------
def format_news(data):

    output = ""

    for article in data:
        output += f"""
TITLE: {article['title']}
SUMMARY: {article['summary']}
LINK: {article['link']}

"""

    return output


# ----------------
# CALL GROQ
# ----------------
def generate_content(news):

    key = os.getenv("GROQ_API_KEY")

    if not key:
        raise Exception("Missing GROQ_API_KEY")

    url = "https://api.groq.com/openai/v1/chat/completions"

    prompt = f"""
Create:

1. Top 5–7 AI stories
2. What changed from yesterday
3. Video script
4. Talking points
5. LinkedIn post
6. Threads post
7. Instagram caption
8. Seven tweets

NEWS:
{news}
"""

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    )

    print("Status:", response.status_code)
    print(response.text)

    data = response.json()

    if "choices" not in data:
        raise Exception(
            f"Groq error:\n{data}"
        )

    return data["choices"][0]["message"]["content"]


# ----------------
# SAVE OUTPUT
# ----------------
def save(text):

    os.makedirs(
        "output",
        exist_ok=True
    )

    filename = (
        f"output/"
        f"{datetime.now().strftime('%Y-%m-%d')}.txt"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(text)


# ----------------
# RUN
# ----------------
print("Fetching AI news...")

news = get_news()

formatted = format_news(news)

print("Sending to AI model...")

content = generate_content(
    formatted
)

print("Saving...")

save(content)

print("SUCCESS")

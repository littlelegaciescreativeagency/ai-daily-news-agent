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
You are a senior AI industry analyst and high-level content strategist.

You are NOT summarizing news. You are analyzing trends and explaining impact.

Using the news below, produce:

---

## 1. Top AI News (5–7 stories)
- Only the most important stories
- No filler stories
- Each must include:
  - What happened
  - Why it matters (real-world impact, not generic explanation)

---

## 2. What Changed Since Yesterday
Focus ONLY on:
- New developments today
- What accelerated or slowed down
- What gained vs lost relevance
- Industry direction shifts

Do NOT repeat headlines.

---

## 3. On-Camera Video Script
- Start with a strong hook (NO greetings like "welcome back")
- Assume audience already watches AI news
- Make it sound like a real creator talking, not corporate
- Include emotional + practical relevance
- End with a strong takeaway or question

---

## 4. Talking Points
Bullet format:
- insights
- implications
- creator/business impact
- controversy or tension if present

---

## 5. Social Media Pack

- LinkedIn post (professional insight, not hype)
- Threads post (opinion + engagement question)
- Instagram caption (short, punchy, modern tone)
- 7 X tweets:
  - each must be unique insight
  - NO duplicates of headlines
  - include at least 2 opinion-based tweets

---

RULES:
- No filler intros or greetings
- No repetitive phrasing
- Be analytical, not descriptive
- Keep output tight, useful, and creator-focused

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

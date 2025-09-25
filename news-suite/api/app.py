from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os
import openai
import requests
import feedparser

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

class NewsPost(BaseModel):
    title: str
    content: str

@app.get("/health")
def health():
    return {"ok": True}

NEWS_SOURCES = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",  # BBC World News
    "http://rss.cnn.com/rss/edition_world.rss",    # CNN World News
    "https://www.scmp.com/rss/91/feed"             # South China Morning Post
]

@app.get("/search")
def search_news():
    news_items = []
    for source in NEWS_SOURCES:
        try:
            feed = feedparser.parse(source)
            for entry in feed.entries[:5]:  # Limit to 5 entries per source
                news_items.append({"title": entry.title, "link": entry.link})
        except Exception as e:
            news_items.append({"error": f"Error fetching from {source}: {str(e)}"})

    return {"results": news_items}

AI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = AI_API_KEY

@app.post("/generate")
def generate_summary():
    if not AI_API_KEY:
        return {"error": "AI API key not configured"}

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes news."},
                {"role": "user", "content": "Summarize the latest news from BBC, CNN, and SCMP."}
            ]
        )
        generated_content = response['choices'][0]['message']['content'].strip()
        return {"summary": generated_content}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")
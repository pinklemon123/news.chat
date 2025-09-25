from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os
import openai
import requests
import feedparser
import logging

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = AI_API_KEY

# Check environment variables
if not AI_API_KEY:
    logger.warning("OPENAI_API_KEY is not set. AI features will not work.")

# Helper function to fetch news
def fetch_news(source):
    try:
        feed = feedparser.parse(source)
        return [
            {"title": entry.title, "link": entry.link}
            for entry in feed.entries[:5]  # Limit to 5 entries per source
        ]
    except Exception as e:
        logger.error(f"Error fetching from {source}: {str(e)}")
        return [{"error": f"Error fetching from {source}: {str(e)}"}]

@app.get("/search")
def search_news():
    news_items = []
    for source in NEWS_SOURCES:
        news_items.extend(fetch_news(source))
    return {"results": news_items}

@app.post("/generate")
def generate_summary(user_input: NewsPost):
    if not AI_API_KEY:
        return {"error": "AI API key not configured"}

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes news."},
                {"role": "user", "content": user_input.content}
            ]
        )
        generated_content = response['choices'][0]['message']['content'].strip()
        return {"summary": generated_content}
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return {"error": "Failed to generate summary. Please try again later."}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": "An unexpected error occurred."}

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")
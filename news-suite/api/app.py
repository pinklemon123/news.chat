from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os
import openai
import requests

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
    "https://www.reuters.com/rssFeed/topNews",    # Reuters Top News
    "https://www.scmp.com/rss/91/feed"             # South China Morning Post
]

@app.get("/search")
def search_news(page: int = 1, page_size: int = 5):
    news_items = []
    for source in NEWS_SOURCES:
        try:
            response = requests.get(source)
            response.raise_for_status()
            # Parse RSS feed (simplified for demonstration)
            news_items.append(f"News from {source}")
        except Exception as e:
            news_items.append(f"Error fetching from {source}: {str(e)}")

    # Paginate results
    start = (page - 1) * page_size
    end = start + page_size
    paginated_news = news_items[start:end]

    return {"page": page, "page_size": page_size, "results": paginated_news}

AI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = AI_API_KEY

@app.post("/generate")
def generate_post(news: NewsPost = None):
    if not news:
        # Use default content if no input is provided
        news = NewsPost(title="Default Title", content="Default Content")
    if not AI_API_KEY:
        return {"error": "AI API key not configured"}

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes news."},
                {"role": "user", "content": f"Generate a news summary based on the following content:\n{news.content}"}
            ]
        )
        generated_content = response['choices'][0]['message']['content'].strip()
        return {"title": news.title, "content": generated_content}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")
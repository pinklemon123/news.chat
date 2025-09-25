from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

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

@app.get("/search")
def search_news(query: str):
    # Placeholder for news search logic
    return {"query": query, "results": ["News 1", "News 2"]}

@app.post("/generate")
def generate_post(news: NewsPost):
    # Placeholder for AI-generated post logic
    return {"title": news.title, "content": f"Generated content based on: {news.content}"}

@app.get("/")
def read_root():
    return {"message": "Welcome to the News API"}
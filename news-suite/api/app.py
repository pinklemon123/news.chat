from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shared.supabase_client import supabase
from shared.redis_client import redis_client
from worker.pipeline import enqueue_crawl
from pydantic import BaseModel
from typing import List
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

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

@app.post("/trigger-crawl")
async def trigger_crawl(req: Request):
    body = await req.json()
    enqueue_crawl(body.get("source_id"))
    return {"queued": True}

@app.post("/billing/webhook")
async def billing_webhook(req: Request):
    # TODO: 验签 Stripe Webhook，更新 subscriptions/profiles.plan
    return {"received": True}
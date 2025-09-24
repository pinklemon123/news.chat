from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shared.supabase_client import supabase
from shared.redis_client import redis_client
from worker.pipeline import enqueue_crawl
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

# 修改 list_articles 方法，支持关键词筛选，语言固定为中文
@app.get("/articles")
def list_articles(q: str | None = None, limit: int = 20, cursor: int | None = None):
    """
    查询新闻文章，支持关键词筛选，语言固定为中文。
    """
    # TODO: 从 Supabase 查询文章，按关键词筛选
    return {"items": [], "nextCursor": None}

@app.post("/trigger-crawl")
async def trigger_crawl(req: Request):
    body = await req.json()
    enqueue_crawl(body.get("source_id"))
    return {"queued": True}

@app.post("/billing/webhook")
async def billing_webhook(req: Request):
    # TODO: 验签 Stripe Webhook，更新 subscriptions/profiles.plan
    return {"received": True}
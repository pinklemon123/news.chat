from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os
import openai

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

AI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = AI_API_KEY

@app.post("/generate")
def generate_post(news: NewsPost):
    if not AI_API_KEY:
        return {"error": "AI API key not configured"}

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Generate a news summary based on the following content:\n{news.content}",
            max_tokens=100
        )
        generated_content = response.choices[0].text.strip()
        return {"title": news.title, "content": generated_content}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")
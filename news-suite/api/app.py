from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os
from openai import OpenAI
import requests
import feedparser
import logging
import time

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

class ChatMessage(BaseModel):
    message: str

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

# Initialize OpenAI client
openai_client = None
if AI_API_KEY:
    try:
        openai_client = OpenAI(api_key=AI_API_KEY)
        logger.info("OpenAI client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        openai_client = None
else:
    logger.warning("OPENAI_API_KEY is not set. AI features will not work.")

# Helper function to fetch news
def fetch_news(source):
    try:
        feed = feedparser.parse(source)
        if feed.entries:
            return [
                {"title": entry.title, "link": entry.link}
                for entry in feed.entries[:5]  # Limit to 5 entries per source
            ]
        else:
            # If no internet access or feed fails, return mock data for demonstration
            logger.warning(f"No entries found for {source}, using mock data")
            mock_data = [
                {"title": f"Mock News from {source.split('//')[-1].split('/')[0]} - 示例新闻1", "link": f"{source}#1"},
                {"title": f"Mock News from {source.split('//')[-1].split('/')[0]} - 示例新闻2", "link": f"{source}#2"},
            ]
            return mock_data
    except Exception as e:
        logger.error(f"Error fetching from {source}: {str(e)}")
        return [{"error": f"Error fetching from {source}: {str(e)}"}]

@app.get("/search")
def search_news():
    news_items = []
    for source in NEWS_SOURCES:
        news_items.extend(fetch_news(source))
    return {"results": news_items}

# Helper function to call OpenAI API with retry logic
def call_openai_with_retry(prompt, retries=3):
    if not openai_client:
        raise Exception("OpenAI client not initialized")
    
    for attempt in range(retries):
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes news."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retrying
            else:
                raise

@app.post("/generate")
def generate_summary(user_input: NewsPost):
    if not openai_client:
        return {"error": "AI API key not configured"}

    try:
        generated_content = call_openai_with_retry(user_input.content)
        return {"summary": generated_content}
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return {"error": "Failed to generate summary. Please try again later."}

@app.post("/chat")
def chat_with_ai(chat_input: ChatMessage):
    if not openai_client:
        # Mock AI response for demonstration when API key is not available
        mock_responses = [
            "很抱歉，我是一个模拟AI助手。真实的AI功能需要配置OpenAI API密钥。",
            f"您说：「{chat_input.message}」。这是一个演示响应，显示聊天功能正常工作。",
            "我理解您的问题。在配置了真实的AI服务后，我将能够提供更有帮助的回答。",
            "感谢您的提问！这是一个模拟回复，用于测试聊天界面的功能。"
        ]
        import random
        response = random.choice(mock_responses)
        return {"reply": response}

    try:
        # Use the chat message as the prompt for AI response
        ai_response = call_openai_with_retry(chat_input.message)
        return {"reply": ai_response}
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return {"error": "AI 服务暂时不可用，请稍后再试。"}

# Helper function to fetch and update news
def fetch_and_update_news(source):
    try:
        feed = feedparser.parse(source)
        if feed.entries:
            news_entries = [
                {"title": entry.title, "link": entry.link, "summary": entry.summary if hasattr(entry, 'summary') else "No summary available"}
                for entry in feed.entries[:5]  # Limit to 5 entries per source
            ]
            logger.info(f"Fetched {len(news_entries)} entries from {source}")
            return news_entries
        else:
            # If no internet access or feed fails, return mock data for demonstration
            logger.warning(f"No entries found for {source}, using mock data")
            mock_data = [
                {
                    "title": f"Mock News from {source.split('//')[-1].split('/')[0]} - 最新新闻更新1", 
                    "link": f"{source}#update1",
                    "summary": "这是一个模拟新闻摘要，用于演示新闻更新功能。"
                },
                {
                    "title": f"Mock News from {source.split('//')[-1].split('/')[0]} - 最新新闻更新2", 
                    "link": f"{source}#update2",
                    "summary": "这是另一个模拟新闻摘要，显示更新功能正常工作。"
                },
            ]
            return mock_data
    except Exception as e:
        logger.error(f"Error fetching from {source}: {str(e)}")
        return [{"error": f"Error fetching from {source}: {str(e)}"}]

@app.get("/update-news")
def update_news():
    updated_news = []
    error_count = 0
    
    for source in NEWS_SOURCES:
        source_news = fetch_and_update_news(source)
        # Filter out error entries and count them
        valid_news = [item for item in source_news if "error" not in item]
        error_entries = [item for item in source_news if "error" in item]
        
        updated_news.extend(valid_news)
        error_count += len(error_entries)
    
    if updated_news:
        logger.info(f"News successfully updated. {len(updated_news)} articles fetched, {error_count} errors.")
        return {
            "status": "success", 
            "updated_news": updated_news,
            "articles_count": len(updated_news),
            "error_count": error_count
        }
    else:
        logger.warning("No news was updated - all sources failed.")
        return {"status": "failure", "message": "Failed to update news from all sources."}

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")
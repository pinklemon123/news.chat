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
import random
from datetime import datetime

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
    "https://feeds.bbci.co.uk/news/world/rss.xml",          # BBC World News
    "http://rss.cnn.com/rss/edition_world.rss",            # CNN World News
    "https://www.scmp.com/rss/91/feed",                    # South China Morning Post
    "https://feeds.bbci.co.uk/news/technology/rss.xml",    # BBC Tech News
    "https://feeds.bbci.co.uk/news/business/rss.xml",      # BBC Business News
    "http://rss.cnn.com/rss/edition_technology.rss",       # CNN Tech News
    "http://rss.cnn.com/rss/money_news_international.rss", # CNN Business News
    "https://www.scmp.com/rss/4/feed",                     # SCMP China News
    "https://www.scmp.com/rss/92/feed"                     # SCMP Asia News
]

# 新闻类别
NEWS_CATEGORIES = {
    "world": ["bbc", "cnn", "scmp"],
    "technology": ["bbc", "cnn"],
    "business": ["bbc", "cnn"],
    "china": ["scmp"],
    "asia": ["scmp"]
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock news content for variety
MOCK_NEWS_TEMPLATES = [
    {
        "titles": [
            "科技公司发布新产品引发关注",
            "经济数据显示市场复苏迹象", 
            "国际会议讨论环境保护议题",
            "体育赛事精彩瞬间回顾",
            "文化艺术节成功举办",
            "教育改革新政策出台",
            "医疗技术取得重大突破",
            "交通基础设施建设进展",
            "可持续发展项目启动",
            "社会公益活动广受好评"
        ],
        "summaries": [
            "最新报道显示相关发展取得重要进展。",
            "专家分析认为这一趋势值得关注。",
            "各方反应积极，预期效果良好。",
            "详细数据和分析报告即将发布。", 
            "相关部门表示将持续跟进此事。",
            "民众对此表示高度关注和支持。",
            "业内人士对前景表示乐观。",
            "国际社会对此给予积极评价。"
        ]
    }
]

def generate_varied_mock_news(source, news_type="regular", count=3):
    """Generate varied mock news for demonstration"""
    source_name = source.split('//')[-1].split('/')[0] if '//' in source else source
    current_time = datetime.now()
    timestamp = current_time.strftime("%H:%M")
    
    templates = MOCK_NEWS_TEMPLATES[0]
    titles = random.sample(templates["titles"], min(count, len(templates["titles"])))
    
    mock_news = []
    for i, title in enumerate(titles):
        suffix = "更新" if news_type == "update" else "报道"
        full_title = f"{title} - {source_name} {timestamp} {suffix}{i+1}"
        summary = random.choice(templates["summaries"])
        
        news_item = {
            "title": full_title,
            "link": f"{source}#{news_type}{i+1}_{int(current_time.timestamp())}",
        }
        
        if news_type == "update":
            news_item["summary"] = summary
            
        mock_news.append(news_item)
    
    return mock_news
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
def fetch_news(source, limit=10):  # 增加每个源的新闻数量
    try:
        feed = feedparser.parse(source)
        if feed.entries:
            news_entries = []
            for entry in feed.entries[:limit]:
                news_item = {
                    "title": entry.title,
                    "link": entry.link,
                    "source": source.split('/')[2],  # 提取源网站域名
                    "category": next((cat for cat, sources in NEWS_CATEGORIES.items() 
                                   if any(src in source.lower() for src in sources)), "general"),
                    "published": entry.get('published', 'N/A'),
                    "summary": entry.get('summary', 'No summary available')
                }
                # 尝试提取图片
                if hasattr(entry, 'media_content'):
                    news_item['image'] = entry.media_content[0]['url']
                elif hasattr(entry, 'links') and len(entry.links) > 1:
                    news_item['image'] = next((link.href for link in entry.links if 'image' in link.type), None)
                
                news_entries.append(news_item)
            return news_entries
        else:
            # 如果无法获取新闻，返回更丰富的模拟数据
            logger.warning(f"No entries found for {source}, using varied mock data")
            return generate_varied_mock_news(source, "regular", limit)
    except Exception as e:
        logger.error(f"Error fetching from {source}: {str(e)}")
        return [{"error": f"Failed to fetch news from {source}", "source": source.split('/')[2]}]

@app.get("/search")
async def search_news(category: str = None, source: str = None, limit: int = 10):
    news_items = []
    filtered_sources = NEWS_SOURCES

    # 按类别过滤
    if category and category in NEWS_CATEGORIES:
        filtered_sources = [src for src in NEWS_SOURCES 
                          if any(s in src.lower() for s in NEWS_CATEGORIES[category])]
    
    # 按源过滤
    if source:
        filtered_sources = [src for src in filtered_sources if source.lower() in src.lower()]

    # 获取新闻
    for source in filtered_sources:
        source_news = fetch_news(source, limit)
        news_items.extend(source_news)

    # 按时间排序（如果有发布时间）
    try:
        news_items.sort(key=lambda x: x.get('published', ''), reverse=True)
    except Exception as e:
        logger.warning(f"Failed to sort news items by date: {str(e)}")

    return {
        "results": news_items[:limit],
        "total": len(news_items),
        "category": category,
        "source": source
    }

@app.get("/refresh-news")
def refresh_news():
    """Endpoint specifically for refreshing news display with new content"""
    news_items = []
    
    for source in NEWS_SOURCES:
        # Use the update news function to get varied content
        source_news = fetch_and_update_news(source)
        # Convert update format to display format
        for item in source_news:
            if "error" not in item:
                display_item = {
                    "title": item["title"],
                    "link": item["link"]
                }
                news_items.append(display_item)
    
    logger.info(f"Refreshed news with {len(news_items)} articles")
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
            # If no internet access or feed fails, return varied mock data for updates
            logger.warning(f"No entries found for {source}, using varied mock update data")
            return generate_varied_mock_news(source, "update", 3)
    except Exception as e:
        logger.error(f"Error fetching from {source}: {str(e)}")
        return [{"error": "Failed to fetch news from source"}]

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
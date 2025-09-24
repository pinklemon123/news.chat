from apscheduler.schedulers.asyncio import AsyncIOScheduler
from jobs.crawl import crawl_all_enabled_sources

async def scheduled():
    """
    定时任务：抓取新闻并存储。
    """
    await crawl_all_enabled_sources()

def start_scheduler():
    sched = AsyncIOScheduler()
    sched.add_job(scheduled, "interval", minutes=10, id="main-pipeline")
    sched.start()

if __name__ == "__main__":
    import asyncio
    start_scheduler()
    asyncio.get_event_loop().run_forever()
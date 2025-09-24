from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def store_subscription(user_id, subscription_data):
    """
    存储用户订阅信息。
    """
    response = supabase.table("subscriptions").upsert({
        "user_id": user_id,
        **subscription_data
    }).execute()
    return response
import json
import requests
import os
from datetime import datetime, timedelta
import pytz

# Load secrets
IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
API_BASE = os.getenv("IG_API_BASE", "https://graph.facebook.com/v21.0")

# Load schedule file
with open("schedule.json", "r", encoding="utf-8") as f:
    posts = json.load(f)

# Load timezone
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)
current_time = now.strftime("%H:%M")

# Helper: mark post as done
def mark_posted(post_id):
    for p in posts:
        if p["id"] == post_id:
            p["posted"] = True
    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

def post_to_instagram(post):
    media_url = f"{API_BASE}/{IG_USER_ID}/media"
    payload = {
        "image_url": post["media_url"],
        "caption": post["description"],
        "access_token": ACCESS_TOKEN,
    }
    r = requests.post(media_url, data=payload)
    r.raise_for_status()
    media_id = r.json()["id"]

    publish_url = f"{API_BASE}/{IG_USER_ID}/media_publish"
    pub_res = requests.post(publish_url, data={"creation_id": media_id, "access_token": ACCESS_TOKEN})
    pub_res.raise_for_status()

    print(f"✅ Posted: {post['file_name']} at {current_time}")

for post in posts:
    if post.get("selected") and not post.get("posted"):
        post_time = datetime.strptime(post["time"], "%H:%M").time()
        post_datetime = now.replace(hour=post_time.hour, minute=post_time.minute, second=0, microsecond=0)

        diff = abs((now - post_datetime).total_seconds())
        if diff <= 600:  # within 10 minutes window
            try:
                post_to_instagram(post)
                mark_posted(post["id"])
            except Exception as e:
                print(f"❌ Failed to post {post['file_name']}: {e}")

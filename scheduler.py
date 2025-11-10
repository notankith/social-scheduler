import requests
import datetime
import pytz
import json
import os

ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
PAGE_ID = os.getenv("FB_PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID")
API_BASE = "https://graph.facebook.com/v21.0"

with open("posts.json", "r") as f:
    posts = json.load(f)

ist = pytz.timezone("Asia/Kolkata")

def schedule_facebook_post(image_url, caption, schedule_time):
    print(f"📘 Scheduling FB post for {schedule_time}")
    utc_time = ist.localize(schedule_time).astimezone(pytz.utc)
    ts = int(utc_time.timestamp())

    res = requests.post(
        f"{API_BASE}/{PAGE_ID}/photos",
        params={
            "url": image_url,
            "caption": caption,
            "published": "false",
            "scheduled_publish_time": ts,
            "access_token": PAGE_ACCESS_TOKEN,
        },
    )
    print("FB Response:", res.json())

def create_instagram_container(image_url, caption):
    print("📸 Creating IG container...")
    res = requests.post(
        f"{API_BASE}/{IG_USER_ID}/media",
        params={
            "image_url": image_url,
            "caption": caption,
            "access_token": ACCESS_TOKEN,
        },
    )
    data = res.json()
    if "id" in data:
        print(f"✅ IG container created: {data['id']}")
        return data["id"]
    else:
        print("❌ Failed IG container:", data)
        return None

def main():
    now = datetime.datetime.now(ist)
    for post in posts:
        if not post.get("selected", False):
            continue

        time_str = post["time"]
        schedule_time = now.replace(
            hour=int(time_str.split(":")[0]),
            minute=int(time_str.split(":")[1]),
            second=0,
            microsecond=0,
        )
        if schedule_time < now:
            schedule_time += datetime.timedelta(days=1)

        image = post["media_url"]
        caption = post["description"]

        # Facebook schedules natively
        schedule_facebook_post(image, caption, schedule_time)

        # Create IG container (for cron job)
        ig_container = create_instagram_container(image, caption)
        if ig_container:
            with open("pending_ig.txt", "a") as f:
                f.write(f"{schedule_time.strftime('%H:%M')}|{ig_container}\n")

if __name__ == "__main__":
    main()

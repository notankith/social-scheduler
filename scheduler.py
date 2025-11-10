import requests
import datetime
import pytz
import json
import os

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")
API_BASE = os.getenv("API_BASE", "https://graph.facebook.com/v21.0")

IST = pytz.timezone("Asia/Kolkata")

STATUS_FILE = "scheduler_status.txt"

def log_status(message):
    timestamp = datetime.datetime.now(IST).strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {message}")
    with open(STATUS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")

def create_instagram_container(media_url, caption):
    res = requests.post(
        f"{API_BASE}/{IG_USER_ID}/media",
        params={
            "image_url": media_url,
            "caption": caption,
            "access_token": ACCESS_TOKEN,
        },
    )
    data = res.json()
    if "id" in data:
        cid = data["id"]
        log_status(f"✅ Created container {cid} for caption start: {caption[:40]}...")
        return cid
    else:
        log_status(f"❌ Failed to create container: {data}")
        return None

def publish_container(cid):
    res = requests.post(
        f"{API_BASE}/{IG_USER_ID}/media_publish",
        params={
            "creation_id": cid,
            "access_token": ACCESS_TOKEN,
        },
    )
    data = res.json()
    if "id" in data:
        log_status(f"🚀 Published IG post successfully → Post ID {data['id']}")
        return True
    else:
        log_status(f"⚠️ Failed to publish container {cid}: {data}")
        return False

def main():
    now = datetime.datetime.now(IST)
    log_status("==== SCHEDULER RUN STARTED ====")

    # load existing pending list
    pending_path = "pending_ig.json"
    if os.path.exists(pending_path):
        with open(pending_path, "r") as f:
            pending = json.load(f)
    else:
        pending = []

    # load new posts
    with open("posts.json", "r") as f:
        posts = json.load(f)

    # create new containers for today's posts if not already pending
    for post in posts:
        if not post.get("selected", False):
            continue

        time_str = post["time"]
        hour, minute = map(int, time_str.split(":"))
        scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if scheduled_time < now:
            scheduled_time += datetime.timedelta(days=1)

        # check if already queued
        if any(p["id"] == post["id"] for p in pending):
            continue

        container_id = create_instagram_container(post["media_url"], post["description"])
        if container_id:
            pending.append({
                "id": post["id"],
                "container_id": container_id,
                "time": time_str,
                "status": "queued"
            })

    # check and publish due posts
    current_time = now.strftime("%H:%M")
    for p in pending:
        if p["status"] == "queued" and p["time"] == current_time:
            ok = publish_container(p["container_id"])
            p["status"] = "posted" if ok else "failed"

    # save pending list
    with open(pending_path, "w") as f:
        json.dump(pending, f, indent=2)

    log_status("==== SCHEDULER RUN COMPLETE ====\n")

if __name__ == "__main__":
    main()

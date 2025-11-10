import requests
import datetime
import pytz
import os

ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")
API_BASE = "https://graph.facebook.com/v21.0"

ist = pytz.timezone("Asia/Kolkata")
now = datetime.datetime.now(ist).strftime("%H:%M")

try:
    with open("pending_ig.txt", "r") as f:
        lines = f.readlines()
except FileNotFoundError:
    print("No pending IG posts.")
    exit()

remaining = []
for line in lines:
    time_str, container_id = line.strip().split("|")
    if time_str == now:
        print(f"⏰ Publishing IG post scheduled for {time_str}")
        res = requests.post(
            f"{API_BASE}/{IG_USER_ID}/media_publish",
            params={"creation_id": container_id, "access_token": ACCESS_TOKEN},
        )
        print("Response:", res.json())
    else:
        remaining.append(line)

# keep unposted ones
with open("pending_ig.txt", "w") as f:
    f.writelines(remaining)

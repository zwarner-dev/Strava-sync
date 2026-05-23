import os
import json
import time
import requests
from datetime import datetime

CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["STRAVA_REFRESH_TOKEN"]

# Step 1: Get a fresh access token
print("Refreshing access token...")
token_response = requests.post(
    "https://www.strava.com/oauth/token",
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    },
)
token_response.raise_for_status()
access_token = token_response.json()["access_token"]

# Step 2: Page through ALL activities until empty
print("Fetching all activities (this may take a few minutes)...")
activities = []
page = 1
while True:
    r = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"per_page": 200, "page": page},
    )
    r.raise_for_status()
    batch = r.json()
    if not batch:
        break
    activities.extend(batch)
    print(f"  Page {page}: {len(batch)} activities (total so far: {len(activities)})")
    page += 1
    # Be nice to Strava's API
    time.sleep(0.5)

# Step 3: Write to file
output = {
    "last_updated": datetime.utcnow().isoformat() + "Z",
    "activity_count": len(activities),
    "activities": activities,
}

with open("activities_full.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\nDone. Wrote {len(activities)} total activities to activities_full.json")

"""List OpenAQ locations near Bengaluru. Requires OPENAQ_API_KEY in .env."""
from dotenv import load_dotenv
import os, requests
load_dotenv()
key=os.getenv("OPENAQ_API_KEY")
if not key: raise SystemExit("Set OPENAQ_API_KEY in .env first.")
response=requests.get("https://api.openaq.org/v3/locations",headers={"X-API-Key":key},params={"coordinates":"12.9716,77.5946","radius":25000},timeout=20)
response.raise_for_status()
for location in response.json().get("results",[]):
    print(location["id"], "-", location["name"])
    for sensor in location.get("sensors",[]): print("   ",sensor["parameter"]["name"])

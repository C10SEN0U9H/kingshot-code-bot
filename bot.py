import os
import json
import requests
from bs4 import BeautifulSoup

# Target webpage providing Kingshot gift codes
URL = "https://kingshot.net"
HISTORY_FILE = "codes_history.txt"

def fetch_active_codes():
    print("Fetching active codes from Kingshot.net...")
    try:
        response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        response.raise_for_status()
        
        # Parse the page layout cleanly using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        valid_codes = set()

        # Target the code blocks specifically
        # We look for common card layouts, header elements, or button sibling structures
        # where gift codes are traditionally text-nested on kingshot.net
        for element in soup.find_all(text=True):
            cleaned = element.strip()
            # Filter for the exact text lengths of the active codes shown in your panels
            if 5 <= len(cleaned) <= 12 and cleaned.isalnum():
                # Avoid collecting common non-code interface labels 
                if cleaned not in ["Active", "Expired", "Copy Code", "Redeem Now", "Share Link"]:
                    # Ensure it matches common game code formats (has letters and numbers, or is fully uppercase)
                    if cleaned.isupper() or (any(c.isdigit() for c in cleaned) and any(c.isalpha() for c in cleaned)):
                        valid_codes.add(cleaned)
                        
        return list(valid_codes)
    except Exception as e:
        print(f"Error scraping the website: {e}")
        return []

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return [line.strip() for line in f.readlines()]
    return []

def save_history(all_codes):
    with open(HISTORY_FILE, "w") as f:
        for code in all_codes:
            f.write(f"{code}\n")

def send_to_discord(new_code):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL environment variable is missing.")
        return

    payload = {
        "username": "Kingshot Code Watcher",
        "avatar_url": "https://kingshot.net",
        "content": f"🚨 **New Kingshot Gift Code Spotted!** 🚨\n\nGrab it quickly: `{new_code}`\n\n🔗 Redeem it in-game or via the [Kingshot Gift Code Center](https://kingshot.net).",
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code in:
        print(f"Successfully posted code {new_code} to Discord!")
    else:
        print(f"Failed to post to Discord. Status code: {response.status_code}")

def main():
    active_codes = fetch_active_codes()
    if not active_codes:
        print("No codes retrieved. Exiting execution cycle.")
        return

    history = load_history()
    
    # Clean out any bad data from previous test runs out of our tracking loop
    clean_history = [item for item in history if not (any(x in item.lower() for x in ['019l5', 'version', 'utc']))]
    
    new_discoveries = [code for code in active_codes if code not in clean_history]

    if new_discoveries:
        print(f"Found new codes: {new_discoveries}")
        for code in new_discoveries:
            send_to_discord(code)
            clean_history.append(code)
        save_history(clean_history)
    else:
        print("No new codes discovered since the last check.")

if __name__ == "__main__":
    main()

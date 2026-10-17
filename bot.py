import os
import re
import json
import requests

URL = "https://kingshot.net"
HISTORY_FILE = "codes_history.txt"

def fetch_active_codes():
    print("Connecting to Kingshot.net...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Scrape all unique alphanumeric strings between 5 and 12 characters long
        found = re.findall(r'\b[A-Z0-9]{5,12}\b', response.text, re.IGNORECASE)
        
        valid_codes = []
        # System structural words to ignore so we don't grab garbage layouts
        ignore_list = ["ACTIVE", "EXPIRED", "TOTAL", "VERSION", "REDEEM", "COPY", "CODES", "GIFTS", "SERVER"]
        
        for item in found:
            cleaned = item.strip().upper()
            if cleaned not in ignore_list and cleaned not in valid_codes:
                # Ensure the code string contains at least one letter and one number to avoid raw numbers
                if any(c.isdigit() for c in cleaned) and any(c.isalpha() for c in cleaned):
                    valid_codes.append(cleaned)
                    
        print(f"Extracted valid codes: {valid_codes}")
        return valid_codes
    except Exception as e:
        print(f"Connection failed: {e}")
        return []

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return [line.strip().upper() for line in f.readlines()]
    return []

def save_history(all_codes):
    with open(HISTORY_FILE, "w") as f:
        for code in all_codes:
            f.write(f"{code}\n")

def send_to_discord(new_code):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return

    payload = {
        "username": "Kingshot Code Watcher",
        "content": f"🚨 **New Kingshot Gift Code Spotted!** 🚨\n\nGrab it quickly: `{new_code}`\n\n🔗 Redeem it here: [Kingshot Gift Code Center](https://kingshot.net)."
    }
    requests.post(webhook_url, json=payload)

def main():
    active_codes = fetch_active_codes()
    if not active_codes:
        print("No codes found.")
        return

    history = load_history()
    new_discoveries = [code for code in active_codes if code not in history]

    if new_discoveries:
        print(f"Posting new codes: {new_discoveries}")
        for code in new_discoveries:
            send_to_discord(code)
            history.append(code)
        save_history(history)
    else:
        print("No new codes discovered since the last check.")

if __name__ == "__main__":
    main()

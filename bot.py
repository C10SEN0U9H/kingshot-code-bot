import os
import re
import json
import requests

# Target webpage providing Kingshot gift codes
URL = "https://kingshot.net/gift-codes"
HISTORY_FILE = "codes_history.txt"

def fetch_active_codes():
    print("Fetching active codes from Kingshot.net...")
    try:
        response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        response.raise_for_status()
        
        # Scrape the webpage text using regular expressions to extract alphanumeric codes
        # Target common active codes listed (e.g., VIP1017, KS1017, IG200KS)
        text_content = response.text
        
        # Find matches for potential standard code patterns mentioned on the page
        found_codes = re.findall(r'\b[A-Z0-9]{5,15}\b', text_content)
        
        # Filter for known valid seeds or prefixes if needed, or take the unique list
        # Kingshot codes are usually uppercase mixed with numbers
        valid_codes = set()
        for code in found_codes:
            # Simple verification filter to avoid capturing UI layout strings
            if any(char.isdigit() for char in code) and any(char.isalpha() for char in code):
                if not code.startswith("VERSION") and not code.startswith("UTC"):
                    valid_codes.add(code)
                    
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
        "content": f"🚨 **New Kingshot Gift Code Spotted!** 🚨\n\nGrab it quickly: `{new_code}`\n\n🔗 Redeem it in-game or via the [Kingshot Gift Code Center](https://kingshot.net/gift-codes).",
        "embeds": []
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code in [200, 204]:
        print(f"Successfully posted code {new_code} to Discord!")
    else:
        print(f"Failed to post to Discord. Status code: {response.status_code}")

def main():
    active_codes = fetch_active_codes()
    if not active_codes:
        print("No codes retrieved. Exiting execution cycle.")
        return

    history = load_history()
    new_discoveries = [code for code in active_codes if code not in history]

    if new_discoveries:
        print(f"Found new codes: {new_discoveries}")
        for code in new_discoveries:
            send_to_discord(code)
            history.append(code)
        save_history(history)
    else:
        print("No new codes discovered since the last check.")

if __name__ == "__main__":
    main()

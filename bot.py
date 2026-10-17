import os
import re
import json
import requests

URL = "https://kingshot.net"
HISTORY_FILE = "codes_history.txt"

def fetch_active_codes():
    print("Connecting to Kingshot.net...")
    try:
        # Standard browser profile headers to bypass connection blocks
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Search the page text for specific active code words
        # This regex looks for common code variants like VIP1017, KS1017, IG200KS, Hangul2026, Kingshot888, VIP777
        found = re.findall(r'\b(VIP\d+|KS\d+|IG\d+KS|Hangul\d+|Kingshot\d+)\b', response.text, re.IGNORECASE)
        
        # Clean up the findings and make them unique uppercase codes
        valid_codes = []
        for item in found:
            cleaned = item.strip().upper()
            if cleaned not in valid_codes:
                valid_codes.append(cleaned)
                
        print(f"Extracted codes from page: {valid_codes}")
        return valid_codes
    except Exception as e:
        print(f"Connection failed: {e}")
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
        print("Error: DISCORD_WEBHOOK_URL is missing from GitHub Secrets.")
        return

    payload = {
        "username": "Kingshot Code Watcher",
        "content": f"🚨 **New Kingshot Gift Code Spotted!** 🚨\n\nGrab it quickly: `{new_code}`\n\n🔗 Redeem it here: [Kingshot Gift Code Center](https://kingshot.net)."
    }
    
    # Send the data to Discord safely without a broken if-statement block
    response = requests.post(webhook_url, json=payload)
    if response.status_code >= 200 and response.status_code < 300:
        print(f"Successfully posted code {new_code} to Discord!")
    else:
        print(f"Discord API returned status code: {response.status_code}")

def main():
    active_codes = fetch_active_codes()
    if not active_codes:
        print("No active codes retrieved. Exiting execution loop.")
        return

    history = load_history()
    
    # Filter historical layout anomalies out of tracking history
    clean_history = [item.upper() for item in history if not any(x in item.lower() for x in ['019l5', 'version', 'utc'])]
    
    new_discoveries = [code for code in active_codes if code not in clean_history]

    if new_discoveries:
        print(f"Found new codes to post: {new_discoveries}")
        for code in new_discoveries:
            send_to_discord(code)
            clean_history.append(code)
        save_history(clean_history)
        print("Discord update sequence completed.")
    else:
        print("No new codes discovered since the last execution check.")

if __name__ == "__main__":
    main()

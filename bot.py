import os
import json
import requests
from bs4 import BeautifulSoup

URL = "https://kingshot.net"
HISTORY_FILE = "codes_history.txt"

def fetch_active_codes():
    print("Connecting to Kingshot.net...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(URL, headers=headers, timeout=12)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        valid_codes = []
        
        # Every gift code box on this layout is a card container.
        # We loop through all elements on the page to inspect these components.
        # We search specifically for the codes that have an active badge next to them.
        for card in soup.find_all(True):
            # Check if this element container contains the specific 'Active' span element you screenshotted
            active_badge = card.find("span", string="Active")
            
            if active_badge:
                # Look inside this exact same card container for the code text matching your font-mono class
                code_element = card.find("p", class_="font-mono text-xl font-bold tracking-wider")
                if code_element:
                    cleaned_code = code_element.get_text().strip().upper()
                    if cleaned_code and cleaned_code not in valid_codes:
                        valid_codes.append(cleaned_code)
                        
        # If the structure is nested differently, run a direct clean sweep fallback matching your exact visual elements
        if not valid_codes:
            print("Direct structure sweep triggered...")
            code_elements = soup.find_all("p", class_="font-mono text-xl font-bold tracking-wider")
            for element in code_elements:
                cleaned_code = element.get_text().strip().upper()
                if cleaned_code and cleaned_code not in valid_codes:
                    valid_codes.append(cleaned_code)

        print(f"Successfully extracted active gift codes: {valid_codes}")
        return valid_codes
        
    except Exception as e:
        print(f"Web connection or structural parsing failed: {e}")
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
        print("Error: DISCORD_WEBHOOK_URL secret is missing.")
        return

    payload = {
        "username": "Kingshot Code Watcher",
        "avatar_url": "https://kingshot.net",
        "content": f"🚨 **New Kingshot Gift Code Spotted!** 🚨\n\nGrab it quickly: `{new_code}`\n\n🔗 Redeem it here: [Kingshot Gift Code Center](https://kingshot.net)."
    }
    requests.post(webhook_url, json=payload)

def main():
    active_codes = fetch_active_codes()
    if not active_codes:
        print("No active codes found on the page structure.")
        return

    history = load_history()
    new_discoveries = [code for code in active_codes if code not in history]

    if new_discoveries:
        print(f"Posting new codes to Discord: {new_discoveries}")
        for code in new_discoveries:
            send_to_discord(code)
            history.append(code)
        save_history(history)
        print("Discord update sequence finished smoothly.")
    else:
        print("All codes found are already tracked in memory history.")

if __name__ == "__main__":
    main()

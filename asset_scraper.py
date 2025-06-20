import customtkinter as ctk
import requests
import threading
import os
from datetime import datetime

# --- Globals for UI ---
global bot_token_entry, guild_id_entry, log_box

def open_window():
    global bot_token_entry, guild_id_entry, log_box
    scraper_window = ctk.CTkToplevel()
    scraper_window.title("Asset Scraper")
    scraper_window.geometry("550x500")

    # --- UI Elements ---
    bot_token_label = ctk.CTkLabel(scraper_window, text="Bot Token (must be in the server):")
    bot_token_label.pack(pady=(10, 2))
    bot_token_entry = ctk.CTkEntry(scraper_window, width=500, show="*")
    bot_token_entry.pack(pady=2)

    guild_id_label = ctk.CTkLabel(scraper_window, text="Server ID to Scrape:")
    guild_id_label.pack(pady=(10, 2))
    guild_id_entry = ctk.CTkEntry(scraper_window, width=500)
    guild_id_entry.pack(pady=2)

    scrape_button = ctk.CTkButton(scraper_window, text="Start Scraping", command=start_scraping)
    scrape_button.pack(pady=20)

    # --- Log Box ---
    log_box = ctk.CTkTextbox(scraper_window, width=530, height=280, font=("Courier", 12))
    log_box.pack(pady=10, padx=10, fill="both", expand=True)
    log_box.tag_config("timestamp", foreground="#888888")
    log_box.tag_config("info", foreground="#3399FF")
    log_box.tag_config("success", foreground="#00FF00")
    log_box.tag_config("error", foreground="#FF3333")
    log_box.configure(state="disabled")

    add_log("Enter bot token and server ID to begin.", "info")

def add_log(text, color="white"):
    if log_box is None: return
    log_box.configure(state="normal")
    log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] ", "timestamp")
    log_box.insert("end", f"{text}\n", color)
    log_box.configure(state="disabled")
    log_box.see("end")

def scraper_worker(token, guild_id):
    headers = {"Authorization": f"Bot {token}"}
    
    # --- Get Guild Info for Naming Folder ---
    try:
        res = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}", headers=headers)
        if res.status_code != 200:
            add_log(f"Failed to fetch guild info: {res.status_code}. Check token and ID.", "error")
            return
        guild_name = res.json().get('name', 'Unknown_Server').replace(' ', '_')
        save_path = os.path.join('scraped_assets', guild_name)
        os.makedirs(save_path, exist_ok=True)
        add_log(f"Saving assets to: {os.path.abspath(save_path)}", "info")
    except Exception as e:
        add_log(f"Error creating directory: {e}", "error")
        return

    # --- Scrape Emojis ---
    try:
        res = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/emojis", headers=headers)
        emojis = res.json()
        add_log(f"Found {len(emojis)} emojis. Downloading...", "info")
        for emoji in emojis:
            ext = ".gif" if emoji['animated'] else ".png"
            url = f"https://cdn.discordapp.com/emojis/{emoji['id']}{ext}"
            with open(os.path.join(save_path, f"emoji_{emoji['name']}{ext}"), 'wb') as f:
                f.write(requests.get(url).content)
            add_log(f"Downloaded emoji: {emoji['name']}", "info")
        add_log("Emoji scraping complete.", "success")
    except Exception as e:
        add_log(f"Error scraping emojis: {e}", "error")

    # --- Scrape Stickers ---
    try:
        res = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/stickers", headers=headers)
        stickers = res.json()
        add_log(f"Found {len(stickers)} stickers. Downloading...", "info")
        for sticker in stickers:
            # Sticker format: 1=PNG, 2=APNG, 3=LOTTIE. We'll save all as .png for simplicity.
            ext = ".png"
            url = f"https://media.discordapp.net/stickers/{sticker['id']}.png"
            with open(os.path.join(save_path, f"sticker_{sticker['name']}{ext}"), 'wb') as f:
                f.write(requests.get(url).content)
            add_log(f"Downloaded sticker: {sticker['name']}", "info")
        add_log("Sticker scraping complete.", "success")
    except Exception as e:
        add_log(f"Error scraping stickers: {e}", "error")

def start_scraping():
    token = bot_token_entry.get().replace('Bot ', '').strip()
    guild_id = guild_id_entry.get().strip()
    if not token or not guild_id:
        add_log("Token and Server ID cannot be empty.", "error")
        return

    add_log("Starting asset scrape...", "info")
    threading.Thread(target=scraper_worker, args=(token, guild_id)).start()

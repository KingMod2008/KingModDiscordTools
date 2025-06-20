import customtkinter as ctk
import requests
import threading
import os
import time
from datetime import datetime

# --- Globals for UI ---
global bot_token_entry, guild_id_entry, log_box

def open_window():
    global bot_token_entry, guild_id_entry, log_box
    archiver_window = ctk.CTkToplevel()
    archiver_window.title("Server Archiver")
    archiver_window.geometry("600x550")

    # --- UI Elements ---
    bot_token_label = ctk.CTkLabel(archiver_window, text="Bot Token (Read Message History permission needed):")
    bot_token_label.pack(pady=(10, 2))
    bot_token_entry = ctk.CTkEntry(archiver_window, width=550, show="*")
    bot_token_entry.pack(pady=2)

    guild_id_label = ctk.CTkLabel(archiver_window, text="Server ID to Archive:")
    guild_id_label.pack(pady=(10, 2))
    guild_id_entry = ctk.CTkEntry(archiver_window, width=550)
    guild_id_entry.pack(pady=2)

    archive_button = ctk.CTkButton(archiver_window, text="Start Archiving", command=start_archiving)
    archive_button.pack(pady=20)

    # --- Log Box ---
    log_box = ctk.CTkTextbox(archiver_window, width=580, height=350, font=("Courier", 12))
    log_box.pack(pady=10, padx=10, fill="both", expand=True)
    log_box.tag_config("timestamp", foreground="#888888")
    log_box.tag_config("info", foreground="#3399FF")
    log_box.tag_config("success", foreground="#00FF00")
    log_box.tag_config("error", foreground="#FF3333")
    log_box.tag_config("warning", foreground="#F1C40F")
    log_box.configure(state="disabled")

    add_log("Enter bot token and server ID to begin.", "info")
    add_log("This can take a very long time for large servers.", "warning")

def add_log(text, color="white"):
    if log_box is None: return
    log_box.configure(state="normal")
    log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] ", "timestamp")
    log_box.insert("end", f"{text}\n", color)
    log_box.configure(state="disabled")
    log_box.see("end")

def archive_worker(token, guild_id):
    headers = {"Authorization": f"Bot {token}"}
    
    # --- Get Guild Info & Create Directory ---
    try:
        res = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}", headers=headers)
        if res.status_code != 200:
            add_log(f"Failed to fetch guild info: {res.status_code}. Check token and ID.", "error")
            return
        guild_name = res.json().get('name', 'Unknown_Server').replace(' ', '_')
        save_path = os.path.join('server_archives', guild_name)
        os.makedirs(save_path, exist_ok=True)
        add_log(f"Saving archives to: {os.path.abspath(save_path)}", "success")
    except Exception as e:
        add_log(f"Error creating directory: {e}", "error")
        return

    # --- Get Channels ---
    try:
        res = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers=headers)
        if res.status_code != 200:
            add_log(f"Failed to fetch channels: {res.status_code}", "error")
            return
        channels = [c for c in res.json() if c['type'] == 0] # Text channels only
        add_log(f"Found {len(channels)} text channels to archive.", "info")
    except Exception as e:
        add_log(f"Error fetching channels: {e}", "error")
        return

    # --- Archive Each Channel ---
    for channel in channels:
        channel_name = channel['name']
        channel_id = channel['id']
        add_log(f"Starting archive for channel: #{channel_name}", "info")
        message_count = 0
        last_message_id = None
        
        try:
            with open(os.path.join(save_path, f"{channel_name}.txt"), 'w', encoding='utf-8') as f:
                while True:
                    params = {"limit": 100}
                    if last_message_id:
                        params['before'] = last_message_id
                    
                    res = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages", headers=headers, params=params)
                    if res.status_code != 200:
                        add_log(f"Error fetching messages for #{channel_name}: {res.status_code}", "error")
                        break
                    
                    messages = res.json()
                    if not messages:
                        break # No more messages

                    last_message_id = messages[-1]['id']
                    message_count += len(messages)
                    add_log(f"Fetched {message_count} messages from #{channel_name}...", "info")

                    for msg in reversed(messages): # Write oldest first
                        timestamp = msg['timestamp'][:19] # Format: YYYY-MM-DDTHH:MM:SS
                        author = f"{msg['author']['username']}#{msg['author']['discriminator']}"
                        content = msg['content']
                        f.write(f"[{timestamp}] {author}: {content}\n")
                        if msg.get('attachments'):
                            for attachment in msg['attachments']:
                                f.write(f"  [Attachment: {attachment['url']}]\n")
                    
                    time.sleep(1) # Rate limit
            add_log(f"Finished archiving #{channel_name}. Total messages: {message_count}", "success")
        except Exception as e:
            add_log(f"An error occurred during archive of #{channel_name}: {e}", "error")

    add_log("Server archiving complete!", "success")

def start_archiving():
    token = bot_token_entry.get().replace('Bot ', '').strip()
    guild_id = guild_id_entry.get().strip()
    if not token or not guild_id:
        add_log("Token and Server ID cannot be empty.", "error")
        return

    add_log("Starting archive process...", "info")
    threading.Thread(target=archive_worker, args=(token, guild_id)).start()

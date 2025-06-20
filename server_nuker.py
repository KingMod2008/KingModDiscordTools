import customtkinter as ctk
import requests
import threading
import time
from datetime import datetime

# --- Globals for UI ---
global bot_token_entry, guild_id_entry, log_box

def open_window():
    global bot_token_entry, guild_id_entry, log_box
    nuker_window = ctk.CTkToplevel()
    nuker_window.title("Server Nuker")
    nuker_window.geometry("550x500")

    # --- UI Elements ---
    bot_token_label = ctk.CTkLabel(nuker_window, text="Bot Token (with Admin permissions):")
    bot_token_label.pack(pady=(10, 2))
    bot_token_entry = ctk.CTkEntry(nuker_window, width=500, show="*")
    bot_token_entry.pack(pady=2)

    guild_id_label = ctk.CTkLabel(nuker_window, text="Server ID (Guild ID) to Nuke:")
    guild_id_label.pack(pady=(10, 2))
    guild_id_entry = ctk.CTkEntry(nuker_window, width=500)
    guild_id_entry.pack(pady=2)

    # --- Buttons ---
    button_frame = ctk.CTkFrame(nuker_window)
    button_frame.pack(pady=20)

    delete_channels_button = ctk.CTkButton(button_frame, text="Delete All Channels", command=lambda: start_task('channels'), fg_color="#E67E22", hover_color="#D35400")
    delete_channels_button.pack(side="left", padx=10)

    delete_roles_button = ctk.CTkButton(button_frame, text="Delete All Roles", command=lambda: start_task('roles'), fg_color="#E67E22", hover_color="#D35400")
    delete_roles_button.pack(side="left", padx=10)

    nuke_button = ctk.CTkButton(button_frame, text="NUKE SERVER", command=lambda: start_task('all'), fg_color="#C0392B", hover_color="#A93226")
    nuke_button.pack(side="left", padx=10)

    # --- Log Box ---
    log_box = ctk.CTkTextbox(nuker_window, width=530, height=280, font=("Courier", 12))
    log_box.pack(pady=10, padx=10, fill="both", expand=True)
    log_box.tag_config("timestamp", foreground="#888888")
    log_box.tag_config("info", foreground="#3399FF")
    log_box.tag_config("success", foreground="#00FF00")
    log_box.tag_config("error", foreground="#FF3333")
    log_box.tag_config("warning", foreground="#F1C40F")
    log_box.configure(state="disabled")

    add_log("WARNING: This tool is highly destructive.", "warning")
    add_log("The provided bot token MUST have Administrator permissions.", "warning")

def add_log(text, color="white"):
    if log_box is None: return
    log_box.configure(state="normal")
    log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] ", "timestamp")
    log_box.insert("end", f"{text}\n", color)
    log_box.configure(state="disabled")
    log_box.see("end")

def nuke_worker(token, guild_id, mode):
    headers = {"Authorization": f"Bot {token}"}

    if mode in ['channels', 'all']:
        add_log("Fetching channels to delete...", "info")
        try:
            res = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers=headers)
            if res.status_code == 200:
                channels = res.json()
                add_log(f"Found {len(channels)} channels. Deleting...", "info")
                for channel in channels:
                    requests.delete(f"https://discord.com/api/v9/channels/{channel['id']}", headers=headers)
                    add_log(f"Deleted channel: #{channel['name']}", "info")
                    time.sleep(0.5) # Avoid rate limits
                add_log("All channels deleted.", "success")
            else:
                add_log(f"Failed to fetch channels: {res.status_code}", "error")
        except Exception as e:
            add_log(f"Error deleting channels: {e}", "error")

    if mode in ['roles', 'all']:
        add_log("Fetching roles to delete...", "info")
        try:
            res = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/roles", headers=headers)
            if res.status_code == 200:
                roles = res.json()
                add_log(f"Found {len(roles)} roles. Deleting...", "info")
                for role in roles:
                    if not role['managed'] and role['name'] != '@everyone':
                        requests.delete(f"https://discord.com/api/v9/guilds/{guild_id}/roles/{role['id']}", headers=headers)
                        add_log(f"Deleted role: @{role['name']}", "info")
                        time.sleep(0.5)
                add_log("All roles deleted.", "success")
            else:
                add_log(f"Failed to fetch roles: {res.status_code}", "error")
        except Exception as e:
            add_log(f"Error deleting roles: {e}", "error")

def start_task(mode):
    token = bot_token_entry.get().replace('Bot ', '').strip()
    guild_id = guild_id_entry.get().strip()
    if not token or not guild_id:
        add_log("Token and Server ID cannot be empty.", "error")
        return

    add_log(f"Starting task: Delete {mode}. This is IRREVERSIBLE.", "warning")
    threading.Thread(target=nuke_worker, args=(token, guild_id, mode)).start()

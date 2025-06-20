import customtkinter as ctk
import requests
import threading
import time
from datetime import datetime

# --- Globals for UI ---
global bot_token_entry, source_guild_entry, target_guild_entry, log_box

def open_window():
    global bot_token_entry, source_guild_entry, target_guild_entry, log_box
    cloner_window = ctk.CTkToplevel()
    cloner_window.title("Guild Cloner")
    cloner_window.geometry("550x500")

    # --- UI Elements ---
    bot_token_label = ctk.CTkLabel(cloner_window, text="Bot or User Token (Admin in both servers):")
    bot_token_label.pack(pady=(10, 2))
    bot_token_entry = ctk.CTkEntry(cloner_window, width=500, show="*")
    bot_token_entry.pack(pady=2)

    source_guild_label = ctk.CTkLabel(cloner_window, text="Source Server ID (to copy from):")
    source_guild_label.pack(pady=(10, 2))
    source_guild_entry = ctk.CTkEntry(cloner_window, width=500)
    source_guild_entry.pack(pady=2)

    target_guild_label = ctk.CTkLabel(cloner_window, text="Target Server ID (to copy to):")
    target_guild_label.pack(pady=(10, 2))
    target_guild_entry = ctk.CTkEntry(cloner_window, width=500)
    target_guild_entry.pack(pady=2)

    clone_button = ctk.CTkButton(cloner_window, text="Start Cloning", command=start_cloning)
    clone_button.pack(pady=20)

    # --- Log Box ---
    log_box = ctk.CTkTextbox(cloner_window, width=530, height=250, font=("Courier", 12))
    log_box.pack(pady=10, padx=10, fill="both", expand=True)
    log_box.tag_config("timestamp", foreground="#888888")
    log_box.tag_config("info", foreground="#3399FF")
    log_box.tag_config("success", foreground="#00FF00")
    log_box.tag_config("error", foreground="#FF3333")
    log_box.tag_config("warning", foreground="#F1C40F")
    log_box.configure(state="disabled")

    add_log("Token must have Admin permissions in BOTH servers.", "warning")
    add_log("For Bot tokens, include the 'Bot ' prefix in the token.", "warning")
    add_log("Using user tokens for this is against ToS (self-botting).", "warning")

def add_log(text, color="white"):
    if log_box is None: return
    log_box.configure(state="normal")
    log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] ", "timestamp")
    log_box.insert("end", f"{text}\n", color)
    log_box.configure(state="disabled")
    log_box.see("end")

def clone_worker(token, source_id, target_id):
    headers = {"Authorization": token}
    role_map = {}

    # --- 1. Clone Roles ---
    try:
        res = requests.get(f"https://discord.com/api/v9/guilds/{source_id}/roles", headers=headers)
        if res.status_code != 200:
            add_log(f"Error fetching roles: {res.status_code} - {res.text}", "error")
            return
        
        source_roles = sorted(res.json(), key=lambda r: r['position'], reverse=True)
        add_log(f"Found {len(source_roles)} roles to clone.", "info")
        for role in source_roles:
            if role['name'] == '@everyone': continue
            payload = {'name': role['name'], 'permissions': role['permissions'], 'color': role['color'], 'hoist': role['hoist'], 'mentionable': role['mentionable']}
            create_res = requests.post(f"https://discord.com/api/v9/guilds/{target_id}/roles", headers=headers, json=payload)
            if create_res.status_code == 200:
                new_role = create_res.json()
                role_map[role['id']] = new_role['id']
                add_log(f"Created role: @{role['name']}", "info")
            else:
                add_log(f"Failed to create role @{role['name']}: {create_res.text}", "error")
            time.sleep(0.5)
        add_log("Role cloning complete.", "success")
    except Exception as e:
        add_log(f"Error during role cloning: {e}", "error")
        return

    # --- 2. Clone Channels ---
    try:
        res = requests.get(f"https://discord.com/api/v9/guilds/{source_id}/channels", headers=headers)
        if res.status_code != 200:
            add_log(f"Error fetching channels: {res.status_code} - {res.text}", "error")
            return
        
        source_channels = res.json()
        categories = {c['id']: c for c in source_channels if c['type'] == 4}
        channel_map = {}

        add_log(f"Found {len(source_channels)} channels/categories to clone.", "info")
        # Create categories first
        for cat_id, category in sorted(categories.items(), key=lambda item: item[1]['position']):
            payload = {'name': category['name'], 'type': 4, 'position': category['position']}
            create_res = requests.post(f"https://discord.com/api/v9/guilds/{target_id}/channels", headers=headers, json=payload)
            if create_res.status_code == 201:
                new_cat = create_res.json()
                channel_map[cat_id] = new_cat['id']
                add_log(f"Created category: {category['name']}", "info")
            else:
                add_log(f"Failed to create category {category['name']}: {create_res.text}", "error")
            time.sleep(0.5)
        
        # Create other channels
        for channel in sorted(source_channels, key=lambda c: c['position']):
            if channel['type'] == 4: continue # Skip categories
            payload = {'name': channel['name'], 'type': channel['type'], 'topic': channel.get('topic'), 'nsfw': channel.get('nsfw'), 'position': channel['position']}
            if channel.get('parent_id') in channel_map:
                payload['parent_id'] = channel_map[channel['parent_id']]
            
            create_res = requests.post(f"https://discord.com/api/v9/guilds/{target_id}/channels", headers=headers, json=payload)
            if create_res.status_code == 201:
                add_log(f"Created channel: #{channel['name']}", "info")
            else:
                add_log(f"Failed to create channel #{channel['name']}: {create_res.text}", "error")
            time.sleep(0.5)
        add_log("Channel cloning complete.", "success")
    except Exception as e:
        add_log(f"Error cloning channels: {e}", "error")

def start_cloning():
    token = bot_token_entry.get().strip()
    source_id = source_guild_entry.get().strip()
    target_id = target_guild_entry.get().strip()
    if not all([token, source_id, target_id]):
        add_log("All fields are required.", "error")
        return

    add_log("Starting guild clone...", "info")
    threading.Thread(target=clone_worker, args=(token, source_id, target_id)).start()

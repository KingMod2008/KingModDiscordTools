import customtkinter as ctk
import requests
import threading
from datetime import datetime

# --- Globals for UI ---
global token_entry, invite_entry, log_box

def open_window():
    global token_entry, invite_entry, log_box
    joiner_window = ctk.CTkToplevel()
    joiner_window.title("Server Joiner")
    joiner_window.geometry("550x450")

    # --- UI Elements ---
    token_label = ctk.CTkLabel(joiner_window, text="User Token:")
    token_label.pack(pady=(10, 2))
    token_entry = ctk.CTkEntry(joiner_window, width=500)
    token_entry.pack(pady=2)

    invite_label = ctk.CTkLabel(joiner_window, text="Server Invite Code or URL:")
    invite_label.pack(pady=(10, 2))
    invite_entry = ctk.CTkEntry(joiner_window, width=500)
    invite_entry.pack(pady=2)

    join_button = ctk.CTkButton(joiner_window, text="Join Server", command=start_joining)
    join_button.pack(pady=20)

    # --- Log Box ---
    log_box = ctk.CTkTextbox(joiner_window, width=530, height=250, font=("Courier", 12))
    log_box.pack(pady=10, padx=10, fill="both", expand=True)
    log_box.tag_config("timestamp", foreground="#888888")
    log_box.tag_config("info", foreground="#3399FF")
    log_box.tag_config("success", foreground="#00FF00")
    log_box.tag_config("error", foreground="#FF3333")
    log_box.configure(state="disabled")

    add_log("Enter a token and invite to begin.", "info")

def add_log(text, color="white"):
    if log_box is None: return
    log_box.configure(state="normal")
    log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] ", "timestamp")
    log_box.insert("end", f"{text}\n", color)
    log_box.configure(state="disabled")
    log_box.see("end")

def join_worker(token, invite):
    headers = {"Authorization": token}
    invite_code = invite.split('/')[-1]
    
    add_log(f"Attempting to join with code: {invite_code}", "info")
    try:
        res = requests.post(f"https://discord.com/api/v9/invites/{invite_code}", headers=headers, json={})
        if res.status_code == 200:
            guild_name = res.json().get('guild', {}).get('name', 'Unknown Server')
            add_log(f"Successfully joined '{guild_name}'!", "success")
        elif res.status_code == 401:
            add_log("Token is invalid.", "error")
        elif res.status_code == 404:
            add_log("Invite is invalid or has expired.", "error")
        else:
            add_log(f"Failed to join: {res.status_code} - {res.text}", "error")
    except Exception as e:
        add_log(f"An error occurred: {e}", "error")

def start_joining():
    token = token_entry.get().strip()
    invite = invite_entry.get().strip()
    if not token or not invite:
        add_log("Token and Invite Code cannot be empty.", "error")
        return

    threading.Thread(target=join_worker, args=(token, invite)).start()

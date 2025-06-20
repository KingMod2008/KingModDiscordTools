import customtkinter as ctk
import requests
import threading
from datetime import datetime

# --- Globals for UI ---
global token_entry, bio_entry, status_text_entry, status_emoji_entry, hypesquad_menu, log_box

def open_window():
    global token_entry, bio_entry, status_text_entry, status_emoji_entry, hypesquad_menu, log_box
    changer_window = ctk.CTkToplevel()
    changer_window.title("Profile Changer")
    changer_window.geometry("550x650")

    # --- UI Elements ---
    token_label = ctk.CTkLabel(changer_window, text="User Token:")
    token_label.pack(pady=(10, 2))
    token_entry = ctk.CTkEntry(changer_window, width=500)
    token_entry.pack(pady=2)

    bio_label = ctk.CTkLabel(changer_window, text="New Bio (leave blank to skip):")
    bio_label.pack(pady=(10, 2))
    bio_entry = ctk.CTkTextbox(changer_window, width=500, height=100)
    bio_entry.pack(pady=2)

    status_label = ctk.CTkLabel(changer_window, text="Custom Status (leave blank to skip):")
    status_label.pack(pady=(10, 2))
    status_text_entry = ctk.CTkEntry(changer_window, width=500, placeholder_text="Status Text")
    status_text_entry.pack(pady=2)
    status_emoji_entry = ctk.CTkEntry(changer_window, width=500, placeholder_text="Status Emoji (e.g., '🔥' or 'fire')")
    status_emoji_entry.pack(pady=2)

    hypesquad_label = ctk.CTkLabel(changer_window, text="HypeSquad House (leave default to skip):")
    hypesquad_label.pack(pady=(10, 2))
    hypesquad_menu = ctk.CTkOptionMenu(changer_window, values=["Don't Change", "House of Bravery", "House of Brilliance", "House of Balance"])
    hypesquad_menu.pack(pady=2)

    apply_button = ctk.CTkButton(changer_window, text="Apply Changes", command=start_changing)
    apply_button.pack(pady=20)

    # --- Log Box ---
    log_box = ctk.CTkTextbox(changer_window, width=530, height=200, font=("Courier", 12))
    log_box.pack(pady=10, padx=10, fill="both", expand=True)
    log_box.tag_config("timestamp", foreground="#888888")
    log_box.tag_config("info", foreground="#3399FF")
    log_box.tag_config("success", foreground="#00FF00")
    log_box.tag_config("error", foreground="#FF3333")
    log_box.configure(state="disabled")

    add_log("Fill in the fields you want to change.", "info")

def add_log(text, color="white"):
    if log_box is None: return
    log_box.configure(state="normal")
    log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] ", "timestamp")
    log_box.insert("end", f"{text}\n", color)
    log_box.configure(state="disabled")
    log_box.see("end")

def change_worker(token, bio, status_text, status_emoji, house):
    headers = {"Authorization": token}
    
    # --- Change Bio ---
    if bio:
        add_log("Attempting to change bio...", "info")
        try:
            res = requests.patch("https://discord.com/api/v9/users/@me", headers=headers, json={"bio": bio})
            if res.status_code == 200: add_log("Successfully changed bio.", "success")
            else: add_log(f"Failed to change bio: {res.status_code}", "error")
        except Exception as e: add_log(f"Error changing bio: {e}", "error")

    # --- Change Status ---
    if status_text:
        add_log("Attempting to change status...", "info")
        payload = {"custom_status": {"text": status_text, "emoji_name": status_emoji if status_emoji else None}}
        try:
            res = requests.patch("https://discord.com/api/v9/users/@me/settings", headers=headers, json=payload)
            if res.status_code == 200: add_log("Successfully changed status.", "success")
            else: add_log(f"Failed to change status: {res.status_code} - {res.text}", "error")
        except Exception as e: add_log(f"Error changing status: {e}", "error")

    # --- Change HypeSquad ---
    if house != "Don't Change":
        add_log(f"Attempting to join {house}...", "info")
        house_map = {"House of Bravery": 1, "House of Brilliance": 2, "House of Balance": 3}
        payload = {"house_id": house_map[house]}
        try:
            res = requests.post("https://discord.com/api/v9/hypesquad/online", headers=headers, json=payload)
            if res.status_code == 204: add_log(f"Successfully joined {house}.", "success")
            else: add_log(f"Failed to join HypeSquad: {res.status_code}", "error")
        except Exception as e: add_log(f"Error joining HypeSquad: {e}", "error")

    add_log("All tasks complete.", "info")

def start_changing():
    token = token_entry.get().strip()
    if not token:
        add_log("Token is required.", "error")
        return

    bio = bio_entry.get("1.0", "end-1c").strip()
    status_text = status_text_entry.get().strip()
    status_emoji = status_emoji_entry.get().strip()
    house = hypesquad_menu.get()

    if not any([bio, status_text, house != "Don't Change"]):
        add_log("Nothing to change. Fill at least one field.", "error")
        return

    threading.Thread(target=change_worker, args=(token, bio, status_text, status_emoji, house)).start()

import customtkinter as ctk
import requests
import threading
import time
from datetime import datetime

# --- Globals for UI and control ---
global token_entry, log_box, running
running = False

def open_window():
    global token_entry, log_box
    disabler_window = ctk.CTkToplevel()
    disabler_window.title("Token Disabler")
    disabler_window.geometry("550x450")

    token_label = ctk.CTkLabel(disabler_window, text="User Token to Disable:")
    token_label.pack(pady=(10, 2))
    token_entry = ctk.CTkEntry(disabler_window, width=500)
    token_entry.pack(pady=2)

    start_button = ctk.CTkButton(disabler_window, text="Start Disabler", command=start_disabling)
    start_button.pack(pady=10)
    stop_button = ctk.CTkButton(disabler_window, text="Stop Disabler", command=stop_disabling, fg_color="#D32F2F", hover_color="#B71C1C")
    stop_button.pack(pady=5)

    log_box = ctk.CTkTextbox(disabler_window, width=530, height=250, font=("Courier", 12))
    log_box.pack(pady=10, padx=10, fill="both", expand=True)
    log_box.tag_config("timestamp", foreground="#888888")
    log_box.tag_config("info", foreground="#3399FF")
    log_box.tag_config("success", foreground="#00FF00")
    log_box.tag_config("error", foreground="#FF3333")
    log_box.configure(state="disabled")

    add_log("Enter a user token and press Start.", "info")

def add_log(text, color="white"):
    if log_box is None: return
    log_box.configure(state="normal")
    log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] ", "timestamp")
    log_box.insert("end", f"{text}\n", color)
    log_box.configure(state="disabled")
    log_box.see("end")

def disabler_worker(token):
    global running
    headers = {"Authorization": token}
    modes = ["light", "dark"]
    current_mode = 0

    while running:
        payload = {"theme": modes[current_mode]}
        try:
            res = requests.patch("https://discord.com/api/v9/users/@me/settings", headers=headers, json=payload)
            if res.status_code == 200:
                add_log(f"Successfully changed theme to {modes[current_mode]}.")
            elif res.status_code == 401:
                add_log("Token is invalid or has been disabled!", "success")
                running = False
                break
            else:
                add_log(f"Failed to change theme: {res.status_code}", "error")
            
            current_mode = 1 - current_mode # Switch between 0 and 1
            time.sleep(1) # Don't get rate-limited
        except Exception as e:
            add_log(f"An error occurred: {e}", "error")
            running = False
            break

def start_disabling():
    global running
    token = token_entry.get()
    if not token:
        add_log("Please enter a token first.", "error")
        return
    
    if running:
        add_log("Disabler is already running.", "error")
        return

    running = True
    add_log("Starting token disabler...", "info")
    threading.Thread(target=disabler_worker, args=(token,)).start()

def stop_disabling():
    global running
    if not running:
        add_log("Disabler is not running.", "error")
        return
    
    running = False
    add_log("Stopping disabler process...", "info")

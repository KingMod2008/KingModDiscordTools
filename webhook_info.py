import customtkinter as ctk
import requests
import threading
from datetime import datetime
import time

def open_window():
    info_window = ctk.CTkToplevel()
    info_window.title("Webhook Information")
    info_window.geometry("600x700")

    # Label
    webhook_label = ctk.CTkLabel(info_window, text="Webhook URL:")
    webhook_label.pack(pady=10)

    # Entry
    webhook_entry = ctk.CTkEntry(info_window, width=500)
    webhook_entry.pack(pady=5)

    # Log Box
    log_box = ctk.CTkTextbox(info_window, width=580, height=400, font=("Courier", 12))
    log_box.pack(pady=10)

    # Button
    enter_button = ctk.CTkButton(
        info_window,
        text="Click to Start",
        command=lambda: get_webhook_info(),
        width=200,
        height=40,
        corner_radius=8,
        fg_color="#3399FF",
        hover_color="#0077CC"
    )
    enter_button.pack(pady=10)

    log_box.configure(state="disabled")

    log_lock = threading.Lock()

    # Configure tags (colors)
    log_box.tag_config("info", foreground="#3399FF")     # Blue
    log_box.tag_config("success", foreground="#00FF00")  # Green
    log_box.tag_config("error", foreground="#FF3333")    # Red
    log_box.tag_config("default", foreground="#FFFFFF")  # White for normal text

    def add_log(text, tag="default"):
        with log_lock:
            log_box.configure(state="normal")
            log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] ", "default")
            log_box.insert("end", f"{text}\n", tag)
            log_box.configure(state="disabled")
            log_box.see("end")

    def get_webhook_info():
        webhook_url = webhook_entry.get()

        if not webhook_url:
            add_log("Please enter a valid Webhook URL.", "error")
            return

        add_log(f"Fetching information for Webhook: {webhook_url}", "info")

        try:
            response = requests.get(webhook_url)
            if response.status_code == 200:
                data = response.json()
                add_log("Webhook Information Retrieved Successfully!", "success")
                add_log("=" * 50, "info")
                add_log(f"Name: {data.get('name', 'N/A')}", "default")
                add_log(f"Avatar: {data.get('avatar', 'N/A')}", "default")
                add_log(f"Channel ID: {data.get('channel_id', 'N/A')}", "default")
                add_log(f"Guild ID: {data.get('guild_id', 'N/A')}", "default")
                add_log(f"Token: {data.get('token', 'N/A')}", "info")
                add_log("=" * 50, "info")
            else:
                add_log(f"Failed to fetch Webhook information: {response.status_code}", "error")
        except Exception as e:
            add_log(f"Error fetching Webhook information: {str(e)}", "error")

    # Initial welcome log
    add_log("Enter Webhook URL and click 'Click to Start'.", "info")

# Example to call the window
if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("300x200")
    open_button = ctk.CTkButton(app, text="Open Webhook Checker", command=open_window)
    open_button.pack(pady=50)
    app.mainloop()

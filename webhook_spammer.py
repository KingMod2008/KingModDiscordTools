import customtkinter as ctk
import requests
import threading
from datetime import datetime

def open_window():
    # Create a new window for the webhook spammer
    spammer_window = ctk.CTkToplevel()
    spammer_window.title("Webhook Spammer")
    spammer_window.geometry("500x600")

    # Label and Entry for Webhook URL
    webhook_label = ctk.CTkLabel(spammer_window, text="Webhook URL:")
    webhook_label.pack(pady=10)
    webhook_entry = ctk.CTkEntry(spammer_window, width=400)
    webhook_entry.pack()

    # Label and Entry for Channel ID
    channel_id_label = ctk.CTkLabel(spammer_window, text="Channel ID (Optional):")
    channel_id_label.pack(pady=10)
    channel_id_entry = ctk.CTkEntry(spammer_window, width=400)
    channel_id_entry.pack()

    # Label and Entry for Message
    message_label = ctk.CTkLabel(spammer_window, text="Message to Send:")
    message_label.pack(pady=10)
    message_entry = ctk.CTkEntry(spammer_window, width=400)
    message_entry.pack()

    # Label and Entry for Number of Messages
    count_label = ctk.CTkLabel(spammer_window, text="Number of Messages:")
    count_label.pack(pady=10)
    count_entry = ctk.CTkEntry(spammer_window, width=100)
    count_entry.pack()

    # Function to send logs to the log box
    def add_log(text, color="white"):
        log_box.configure(state="normal")
        log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] ", "timestamp")
        log_box.insert("end", f"{text}\n", color)
        log_box.configure(state="disabled")
        log_box.see("end")

    # Function to display animated text in the log box
    def animated_log(text, color="white"):
        def animate():
            for char in text:
                log_box.configure(state="normal")
                log_box.insert("end", char, color)
                log_box.configure(state="disabled")
                log_box.see("end")
                time.sleep(0.03)
            log_box.insert("end", "\n")
        threading.Thread(target=animate).start()

    # Button to Start Spamming
    def start_spam():
        webhook_url = webhook_entry.get()
        channel_id = channel_id_entry.get()
        message = message_entry.get()
        try:
            count = int(count_entry.get())
        except ValueError:
            animated_log("Invalid number of messages! Please enter a valid integer.", "error")
            return

        if not webhook_url or not message:
            animated_log("Please fill in all required fields (Webhook URL and Message).", "error")
            return

        animated_log(f"Starting to spam {count} messages...", "info")

        for i in range(count):
            try:
                payload = {"content": message}
                if channel_id:  # Add channel ID to the payload if provided
                    payload["channel_id"] = channel_id

                response = requests.post(webhook_url, json=payload)
                if response.status_code == 204:
                    animated_log(f"Sent message {i + 1}/{count}", "success")
                else:
                    animated_log(f"Failed to send message {i + 1}/{count}: {response.status_code}", "error")
            except Exception as e:
                animated_log(f"Error sending message {i + 1}/{count}: {str(e)}", "error")

        animated_log("Spamming completed!", "info")

    spam_button = ctk.CTkButton(spammer_window, text="Start Spamming", command=start_spam)
    spam_button.pack(pady=20)

    # Log Box for displaying messages
    log_box = ctk.CTkTextbox(spammer_window, width=480, height=250, font=("Courier", 12))
    log_box.pack(pady=10)

    # Configure log box tags for different colors
    log_box.tag_config("timestamp", foreground="#888888")  # Gray for timestamps
    log_box.tag_config("info", foreground="#3399FF")       # Blue for info messages
    log_box.tag_config("success", foreground="#00FF00")    # Green for success messages
    log_box.tag_config("error", foreground="#FF3333")      # Red for error messages
    log_box.configure(state="disabled")

    # Initial welcome message
    animated_log("Ready to spam webhooks!", "info")
import customtkinter as ctk
import requests
import threading
from datetime import datetime
import time

def open_window():
    # إنشاء نافذة جديدة
    deleter_window = ctk.CTkToplevel()
    deleter_window.title("Webhook Deleter")
    deleter_window.geometry("500x400")

    # لوجو البداية
    log_box = ctk.CTkTextbox(deleter_window, width=480, height=250, font=("Courier", 12))
    log_box.pack(pady=10)

    # تكوين ألوان النصوص
    log_box.tag_config("timestamp", foreground="#888888")
    log_box.tag_config("info", foreground="#3399FF")
    log_box.tag_config("success", foreground="#00FF00")
    log_box.tag_config("error", foreground="#FF3333")
    log_box.configure(state="disabled")

    # قفل للثريدات
    log_lock = threading.Lock()

    # دالة إضافة لوج ملون
    def add_log(text, color="white"):
        with log_lock:
            log_box.configure(state="normal")
            log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] ", "timestamp")
            log_box.insert("end", f"{text}\n", color)
            log_box.configure(state="disabled")
            log_box.see("end")

    # إدخال رابط الويب هوك
    webhook_label = ctk.CTkLabel(deleter_window, text="Webhook URL to Delete:")
    webhook_label.pack(pady=5)
    webhook_entry = ctk.CTkEntry(deleter_window, width=400)
    webhook_entry.pack(pady=5)

    # دالة حذف الويب هوك
    def delete_webhook():
        webhook_url = webhook_entry.get()

        if not webhook_url:
            add_log("Please enter a valid Webhook URL.", "error")
            return

        add_log(f"Attempting to delete webhook: {webhook_url}", "info")
        try:
            response = requests.delete(webhook_url)
            if response.status_code == 204:
                add_log("Webhook deleted successfully!", "success")
            elif response.status_code == 404:
                add_log("Webhook not found. It might already be deleted.", "error")
            else:
                add_log(f"Failed to delete webhook: {response.status_code}", "error")
        except Exception as e:
            add_log(f"Error deleting webhook: {str(e)}", "error")

    # زر الحذف
    delete_button = ctk.CTkButton(
        deleter_window,
        text="Delete Webhook",
        command=delete_webhook,
        width=200,
        height=40,
        fg_color="#FF3333",
        hover_color="#CC0000"
    )
    delete_button.pack(pady=20)

    # رسالة ترحيب مبدئية
    add_log("Enter a Webhook URL and press Delete!", "info")

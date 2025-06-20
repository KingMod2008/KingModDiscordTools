import tkinter as tk
import customtkinter as ctk
import threading
import time
from datetime import datetime
import importlib

# Set appearance mode and color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Create the main application window
app = ctk.CTk()
app.title("XKing - Advanced Discord Tool")
app.geometry("1000x600")
app.resizable(False, False)

# Title Frame
title_frame = ctk.CTkFrame(app, fg_color="transparent")
title_frame.pack(pady=10)

king_label = ctk.CTkLabel(title_frame, text="King", font=("Arial", 40, "bold"), text_color="white")
king_label.pack(side="left")

mod_label = ctk.CTkLabel(title_frame, text="Mod", font=("Arial", 40, "bold"), text_color="red")
mod_label.pack(side="left")

# Function to add logs to the log box
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

# Function to open a feature from a module
def open_feature(module_name):
    try:
        module = importlib.import_module(module_name)
        module.open_window()
        animated_log(f"Opened {module_name.replace('_', ' ').title()}", "action")
    except Exception as e:
        animated_log(f"Failed to open {module_name}: {str(e)}", "error")

# Frame for the canvas and scrollbar
canvas_frame = ctk.CTkFrame(app)
canvas_frame.pack(pady=20, padx=20, side="left", fill="y")

# Create a canvas widget
canvas = ctk.CTkCanvas(canvas_frame, width=250, height=550)
canvas.pack(side="left", fill="both", expand=True)

# Create a scrollbar for the canvas
scrollbar = ctk.CTkScrollbar(canvas_frame, orientation="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

# Create a frame inside the canvas to hold buttons
button_frame = ctk.CTkFrame(canvas)
canvas.create_window((0, 0), window=button_frame, anchor="nw")

# Update the canvas scroll region after adding buttons
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

# Bind the configure event to the frame
button_frame.bind("<Configure>", on_frame_configure)

# Log box for displaying messages
log_box = ctk.CTkTextbox(app, width=600, height=550, font=("Courier", 14))
log_box.pack(pady=20, padx=20, side="right")

# Configure log box tags for different colors
log_box.tag_config("timestamp", foreground="#888888")
log_box.tag_config("action", foreground="#00FF00")
log_box.tag_config("error", foreground="#FF3333")
log_box.tag_config("info", foreground="#3399FF")
log_box.configure(state="disabled")

# Dictionary mapping feature names to module names
features = {
    "Webhook Spammer": "webhook_spammer",
    "Webhook Information": "webhook_info",
    "Webhook Deleter": "webhook_deleter",
    "Channel Spammer": "channel_spammer",
    "Channel Monitoring": "channel_monitoring",
    "Group Chat Clearer": "group_clearer",
    "Animated Status": "animated_status",
    "IP Address Lookup": "ip_lookup",
    "Token Information": "token_info",
    "Token Payments": "token_payments",
    "Server Nuker": "server_nuker",
    "Guild Cloner": "guild_cloner",
    "Token Disabler": "token_disabler",
    "Token Checker": "token_checker",
    "Server Joiner": "server_joiner",
    "Asset Scraper": "asset_scraper",
    "Profile Changer": "profile_changer",
    "Server Archiver": "server_archiver"
}

# Create buttons for each feature
for feature_name, module_name in features.items():
    btn = ctk.CTkButton(
        button_frame,
        text=feature_name,
        width=230,
        height=40,
        corner_radius=8,
        command=lambda name=module_name: open_feature(name)
    )
    btn.pack(pady=5)

# Welcome message on startup
animated_log("Welcome to XKing Discord Tool GUI Version!", "info")

# Run the application
app.mainloop()

import customtkinter as ctk
import requests
import threading
from datetime import datetime

# --- Globals for UI and state ---
global token_input_box, valid_log_box, invalid_log_box, status_label

def open_window():
    global token_input_box, valid_log_box, invalid_log_box, status_label
    checker_window = ctk.CTkToplevel()
    checker_window.title("Token Checker")
    checker_window.geometry("800x600")

    # --- Main Frame ---
    main_frame = ctk.CTkFrame(checker_window)
    main_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # --- Input Area ---
    input_label = ctk.CTkLabel(main_frame, text="Paste Tokens Below (one per line):")
    input_label.pack(pady=(0, 5))
    token_input_box = ctk.CTkTextbox(main_frame, width=740, height=150)
    token_input_box.pack(pady=5, fill="x", expand=True)

    start_button = ctk.CTkButton(main_frame, text="Start Checking", command=start_checking)
    start_button.pack(pady=10)

    status_label = ctk.CTkLabel(main_frame, text="Status: Idle")
    status_label.pack(pady=5)

    # --- Output Area ---
    output_frame = ctk.CTkFrame(main_frame)
    output_frame.pack(pady=10, fill="both", expand=True)
    output_frame.grid_columnconfigure(0, weight=1)
    output_frame.grid_columnconfigure(1, weight=1)
    output_frame.grid_rowconfigure(1, weight=1)

    valid_label = ctk.CTkLabel(output_frame, text="Valid Tokens", text_color="#00FF00")
    valid_label.grid(row=0, column=0, padx=10, pady=5)
    invalid_label = ctk.CTkLabel(output_frame, text="Invalid Tokens", text_color="#FF3333")
    invalid_label.grid(row=0, column=1, padx=10, pady=5)

    valid_log_box = ctk.CTkTextbox(output_frame, width=350, font=("Courier", 12))
    valid_log_box.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
    valid_log_box.configure(state="disabled")

    invalid_log_box = ctk.CTkTextbox(output_frame, width=350, font=("Courier", 12))
    invalid_log_box.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
    invalid_log_box.configure(state="disabled")

def add_to_log(box, text):
    box.configure(state="normal")
    box.insert("end", f"{text}\n")
    box.configure(state="disabled")
    box.see("end")

def check_token(token):
    headers = {"Authorization": token}
    try:
        res = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=5)
        if res.status_code == 200:
            add_to_log(valid_log_box, token)
        else:
            add_to_log(invalid_log_box, token)
    except requests.exceptions.RequestException:
        add_to_log(invalid_log_box, f"{token} (Error)")

def checker_worker(tokens):
    threads = []
    for token in tokens:
        if token.strip():
            thread = threading.Thread(target=check_token, args=(token.strip(),))
            threads.append(thread)
            thread.start()
    
    for thread in threads:
        thread.join()
    
    status_label.configure(text="Status: Finished Checking")

def start_checking():
    tokens = token_input_box.get("1.0", "end-1c").splitlines()
    if not tokens:
        status_label.configure(text="Status: No tokens provided.")
        return

    # Clear previous results
    valid_log_box.configure(state="normal")
    valid_log_box.delete("1.0", "end")
    valid_log_box.configure(state="disabled")
    invalid_log_box.configure(state="normal")
    invalid_log_box.delete("1.0", "end")
    invalid_log_box.configure(state="disabled")

    status_label.configure(text=f"Status: Checking {len(tokens)} tokens...")
    threading.Thread(target=checker_worker, args=(tokens,)).start()

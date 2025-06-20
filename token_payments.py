import customtkinter as ctk
import requests
import threading
from datetime import datetime
import time
import stripe

def open_window():
    payment_window = ctk.CTkToplevel()
    payment_window.title("Advanced Token Payments")
    payment_window.geometry("600x600")

    tab_view = ctk.CTkTabview(payment_window, width=580)
    tab_view.pack(padx=10, pady=5)

    tab_message = tab_view.add("Send Message")
    tab_payment = tab_view.add("Create Stripe Payment")
    tab_automation = tab_view.add("Discord Automation")

    log_box = ctk.CTkTextbox(payment_window, width=580, height=250, font=("Courier", 12))
    log_box.pack(pady=10, padx=10, fill="both", expand=True)

    log_box.tag_config("timestamp", foreground="#888888")
    log_box.tag_config("info", foreground="#3399FF")
    log_box.tag_config("success", foreground="#00FF00")
    log_box.tag_config("error", foreground="#FF3333")
    log_box.tag_config("human_token", foreground="#FF0000")
    log_box.tag_config("bot_token", foreground="#00FF00")
    log_box.configure(state="disabled")
    log_lock = threading.Lock()

    def add_log(text, color="white"):
        with log_lock:
            log_box.configure(state="normal")
            log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] ", "timestamp")
            log_box.insert("end", f"{text}\n", color)
            log_box.configure(state="disabled")
            log_box.see("end")

    # --- Tab 1: Send Message --- #
    token_label = ctk.CTkLabel(tab_message, text="Discord Token:")
    token_label.pack(pady=(10, 2))
    token_entry = ctk.CTkEntry(tab_message, width=500)
    token_entry.pack(pady=2)

    message_label = ctk.CTkLabel(tab_message, text="Message Content:")
    message_label.pack(pady=(10, 2))
    message_entry = ctk.CTkEntry(tab_message, width=500)
    message_entry.pack(pady=2)

    channel_id_label = ctk.CTkLabel(tab_message, text="Channel ID:")
    channel_id_label.pack(pady=(10, 2))
    channel_id_entry = ctk.CTkEntry(tab_message, width=500)
    channel_id_entry.pack(pady=2)

    def send_message_func():
        token = token_entry.get()
        message = message_entry.get()
        channel_id = channel_id_entry.get()

        if not token or not message or not channel_id:
            add_log("Please fill in all fields (Token, Channel ID, Message).", "error")
            return

        if 'bot' in token.lower():
            headers = {"Authorization": f"Bot {token.replace('Bot ', '')}", "Content-Type": "application/json"}
            token_type = "Bot"
        else:
            headers = {"Authorization": token, "Content-Type": "application/json"}
            token_type = "Human"

        payload = {"content": message}
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"

        def send_request():
            add_log(f"Sending message with {token_type} token...", "info")
            try:
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    add_log("Message sent successfully!", "success")
                else:
                    add_log(f"Error: {response.status_code} - {response.text}", "error")
            except Exception as e:
                add_log(f"An error occurred: {e}", "error")

        threading.Thread(target=send_request).start()

    send_button = ctk.CTkButton(tab_message, text="Send Message", command=send_message_func, width=200, height=40)
    send_button.pack(pady=20)

    # --- Tab 2: Create Stripe Payment --- #
    def create_stripe_payment_link():
        api_key = stripe_api_key_entry.get()
        product_name = product_name_entry.get()
        price_amount = price_entry.get()
        currency = currency_entry.get().lower()

        if not all([api_key, product_name, price_amount, currency]):
            add_log("Please fill all Stripe fields.", "error")
            return

        try:
            price_in_cents = int(float(price_amount) * 100)
        except ValueError:
            add_log("Invalid price format. Please enter a number.", "error")
            return

        def create_link():
            try:
                add_log("Connecting to Stripe...", "info")
                stripe.api_key = api_key
                
                add_log(f"Creating product: {product_name}...", "info")
                product = stripe.Product.create(name=product_name)
                
                add_log(f"Creating price: {price_amount} {currency.upper()}...", "info")
                price = stripe.Price.create(
                    product=product.id,
                    unit_amount=price_in_cents,
                    currency=currency,
                )
                
                add_log("Generating payment link...", "info")
                payment_link = stripe.PaymentLink.create(line_items=[{"price": price.id, "quantity": 1}])
                
                add_log("Successfully created payment link!", "success")
                add_log(f"Link: {payment_link.url}", "info")

            except stripe.error.AuthenticationError:
                add_log("Stripe authentication failed. Check your API key.", "error")
            except Exception as e:
                add_log(f"An error occurred with Stripe: {e}", "error")

        threading.Thread(target=create_link).start()

    # UI Elements for Stripe Tab
    stripe_api_key_label = ctk.CTkLabel(tab_payment, text="Stripe Secret Key (Find yours at dashboard.stripe.com/apikeys)")
    stripe_api_key_label.pack(pady=(10, 2))
    stripe_api_key_entry = ctk.CTkEntry(tab_payment, width=500, show="*")
    stripe_api_key_entry.pack(pady=2)

    product_name_label = ctk.CTkLabel(tab_payment, text="Product Name:")
    product_name_label.pack(pady=(10, 2))
    product_name_entry = ctk.CTkEntry(tab_payment, width=500)
    product_name_entry.pack(pady=2)

    # Frame for price and currency to be side-by-side
    price_currency_frame = ctk.CTkFrame(tab_payment)
    price_currency_frame.pack(pady=(10, 2), padx=10, fill="x")

    price_label = ctk.CTkLabel(price_currency_frame, text="Price (e.g., 9.99):")
    price_label.pack(side='left', padx=(0, 5))
    price_entry = ctk.CTkEntry(price_currency_frame, width=150)
    price_entry.pack(side='left', expand=True, fill='x', padx=5)

    currency_label = ctk.CTkLabel(price_currency_frame, text="Currency (e.g., USD):")
    currency_label.pack(side='left', padx=(10, 5))
    currency_entry = ctk.CTkEntry(price_currency_frame, width=150)
    currency_entry.pack(side='left', expand=True, fill='x', padx=5)
    currency_entry.insert(0, "USD")

    create_payment_button = ctk.CTkButton(tab_payment, text="Create Payment Link", command=create_stripe_payment_link, width=200, height=40)
    create_payment_button.pack(pady=20)

    # --- Tab 3: Discord Automation --- #
    def grant_role_on_discord():
        bot_token = bot_token_entry.get()
        server_id = server_id_entry.get()
        user_id = user_id_entry.get()
        role_id = role_id_entry.get()

        if not all([bot_token, server_id, user_id, role_id]):
            add_log("Please fill all Discord Automation fields.", "error")
            return

        def grant():
            url = f"https://discord.com/api/v9/guilds/{server_id}/members/{user_id}/roles/{role_id}"
            # Sanitize the token to ensure it doesn't have a duplicate "Bot " prefix
            clean_token = bot_token.replace('Bot ', '').strip()
            headers = {"Authorization": f"Bot {clean_token}"}
            
            add_log(f"Attempting to grant role {role_id} to user {user_id}...", "info")
            try:
                response = requests.put(url, headers=headers)
                if response.status_code == 204:
                    add_log("Role granted successfully!", "success")
                elif response.status_code == 401:
                    add_log("Authentication failed. Check your Bot Token.", "error")
                elif response.status_code == 403:
                    add_log("Bot is missing permissions to grant this role.", "error")
                elif response.status_code == 404:
                    add_log("User or Role not found in the specified server.", "error")
                else:
                    add_log(f"An error occurred: {response.status_code} - {response.text}", "error")
            except Exception as e:
                add_log(f"An error occurred during the request: {e}", "error")

        threading.Thread(target=grant).start()

    # UI Elements for Automation Tab
    bot_token_label = ctk.CTkLabel(tab_automation, text="Your Discord Bot Token:")
    bot_token_label.pack(pady=(10, 2))
    bot_token_entry = ctk.CTkEntry(tab_automation, width=500, show="*")
    bot_token_entry.pack(pady=2)

    server_id_label = ctk.CTkLabel(tab_automation, text="Server ID (Guild ID):")
    server_id_label.pack(pady=(10, 2))
    server_id_entry = ctk.CTkEntry(tab_automation, width=500)
    server_id_entry.pack(pady=2)

    user_id_label = ctk.CTkLabel(tab_automation, text="User ID (to grant role to):")
    user_id_label.pack(pady=(10, 2))
    user_id_entry = ctk.CTkEntry(tab_automation, width=500)
    user_id_entry.pack(pady=2)

    role_id_label = ctk.CTkLabel(tab_automation, text="Role ID (to grant):")
    role_id_label.pack(pady=(10, 2))
    role_id_entry = ctk.CTkEntry(tab_automation, width=500)
    role_id_entry.pack(pady=2)

    grant_role_button = ctk.CTkButton(tab_automation, text="Grant Role", command=grant_role_on_discord, width=200, height=40)
    grant_role_button.pack(pady=20)

    add_log("Advanced Payments window opened. Select a tab to begin.", "info")

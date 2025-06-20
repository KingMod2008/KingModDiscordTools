import customtkinter as ctk
import requests
import threading
from datetime import datetime
import discord
import asyncio

# Global variables for UI elements
token_entry = None
log_box = None

def open_window():
    global token_entry, log_box
    info_window = ctk.CTkToplevel()
    info_window.title("Discord Token Information")
    info_window.geometry("550x500")

    token_label = ctk.CTkLabel(info_window, text="Enter Discord Token (Bot or User):")
    token_label.pack(pady=(10, 2))
    token_entry = ctk.CTkEntry(info_window, width=500)
    token_entry.pack(pady=2)

    fetch_button = ctk.CTkButton(info_window, text="Fetch Information", command=lambda: threading.Thread(target=fetch_token_info).start())
    fetch_button.pack(pady=20)

    log_box = ctk.CTkTextbox(info_window, width=530, height=350, font=("Courier", 12))
    log_box.pack(pady=10, padx=10, fill="both", expand=True)
    log_box.tag_config("timestamp", foreground="#888888")
    log_box.tag_config("info", foreground="#3399FF")
    log_box.tag_config("success", foreground="#00FF00")
    log_box.tag_config("error", foreground="#FF3333")
    log_box.configure(state="disabled")

    add_log("Enter a token and click fetch to see its details.", "info")

def add_log(text, color="white"):
    if log_box is None:
        return
    log_box.configure(state="normal")
    log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] ", "timestamp")
    log_box.insert("end", f"{text}\n", color)
    log_box.configure(state="disabled")
    log_box.see("end")

def fetch_token_info():
    token = token_entry.get()
    if not token:
        add_log("Please enter a token.", "error")
        return

    add_log("Fetching token info...", "info")
    # Decide if it's a bot or user token
    if 'bot' in token.lower() or len(token) > 80:
        asyncio.run(get_bot_info(token))
    else:
        get_user_info(token)

def get_user_info(token):
    headers = {"Authorization": token}
    # --- Basic User Info ---
    try:
        res = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
        if res.status_code != 200:
            add_log(f"Invalid user token or API error: {res.status_code}", "error")
            return
        
        data = res.json()
        nitro_types = {0: "No Nitro", 1: "Nitro Classic", 2: "Nitro", 3: "Nitro Basic"}
        
        log_text = "--- (1/4) Basic User Info ---\n"
        log_text += f"ID: {data.get('id')}\n"
        log_text += f"Username: {data.get('username')}#{data.get('discriminator')}\n"
        log_text += f"Global Name: {data.get('global_name')}\n"
        log_text += f"Email: {data.get('email')}\n"
        log_text += f"Phone: {data.get('phone')}\n"
        log_text += f"Verified: {data.get('verified')}\n"
        log_text += f"MFA Enabled: {data.get('mfa_enabled')}\n"
        log_text += f"Locale: {data.get('locale')}\n"
        log_text += f"Nitro: {nitro_types.get(data.get('premium_type'), 'Unknown')}\n"
        log_text += f"Avatar URL: https://cdn.discordapp.com/avatars/{data.get('id')}/{data.get('avatar')}.png\n"
        log_text += f"Banner URL: https://cdn.discordapp.com/banners/{data.get('id')}/{data.get('banner')}.png\n"
        add_log(log_text, "success")

    except Exception as e:
        add_log(f"An error occurred fetching basic info: {e}", "error")
        return # Stop if basic info fails

    # --- (2/4) Billing Info ---
    try:
        res = requests.get("https://discord.com/api/v9/users/@me/billing/payment-sources", headers=headers)
        billing_data = res.json()
        billing_text = "--- (2/4) Billing Information ---\n"
        if not billing_data:
            billing_text += "No payment methods found.\n"
        else:
            for source in billing_data:
                if source['type'] == 1:
                    billing_text += f"- Credit Card: **** **** **** {source['last_4']} (Expires: {source['expires_month']}/{source['expires_year']})\n"
                elif source['type'] == 2:
                    billing_text += f"- PayPal: {source['email']}\n"
        add_log(billing_text, "success")
    except Exception as e:
        add_log(f"Could not fetch billing info: {e}", "error")

    # --- (3/4) Guilds Info ---
    try:
        res = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=headers)
        guilds_data = res.json()
        guilds_text = f"--- (3/4) Server List ({len(guilds_data)} servers) ---\n"
        for guild in guilds_data[:15]: # Limit to 15 to not spam the log
            guilds_text += f"- {guild['name']} (ID: {guild['id']})\n"
        if len(guilds_data) > 15:
            guilds_text += f"...and {len(guilds_data) - 15} more.\n"
        add_log(guilds_text, "success")
    except Exception as e:
        add_log(f"Could not fetch guilds: {e}", "error")

    # --- (4/4) Connections Info ---
    try:
        res = requests.get("https://discord.com/api/v9/users/@me/connections", headers=headers)
        connections_data = res.json()
        connections_text = f"--- (4/4) Connections ({len(connections_data)} connected accounts) ---\n"
        if not connections_data:
            connections_text += "No connected accounts.\n"
        else:
            for conn in connections_data:
                connections_text += f"- {conn['type'].capitalize()}: {conn['name']} (Verified: {conn['verified']})\n"
        add_log(connections_text, "success")
    except Exception as e:
        add_log(f"Could not fetch connections: {e}", "error")

async def get_bot_info(token):
    intents = discord.Intents.default()
    intents.guilds = True
    client = discord.Client(intents=intents)
    try:
        token_to_use = token.replace('Bot ', '')
        await client.login(token_to_use)
        
        app_info = await client.application_info()

        log_text = "--- Bot Token Info ---\n"
        log_text += f"ID: {client.user.id}\n"
        log_text += f"Name: {client.user.name}\n"
        log_text += f"Owner: {app_info.owner.name} ({app_info.owner.id})\n"
        log_text += f"Public: {app_info.bot_public}\n"
        log_text += f"Requires Code Grant: {app_info.bot_require_code_grant}\n"
        log_text += f"Description: {app_info.description or 'None'}\n"
        log_text += f"Tags: {', '.join(app_info.tags) if app_info.tags else 'None'}\n"
        log_text += f"Avatar: {client.user.avatar.url if client.user.avatar else 'None'}\n"
        add_log(log_text, "success")

    except discord.errors.LoginFailure:
        add_log("Invalid bot token. Please check it and try again.", "error")
    except Exception as e:
        add_log(f"An error occurred with the bot: {e}", "error")
    finally:
        if client.is_ready():
            await client.close()

import discord
from discord.ext import commands
import customtkinter as ctk
import threading
import asyncio
from datetime import datetime

def open_window():
    info_window = ctk.CTkToplevel()
    info_window.title("Clear Group Messages")
    info_window.geometry("600x700")

    # Labels and Entry for Token and Channel ID
    token_label = ctk.CTkLabel(info_window, text="Enter your Discord Token:")
    token_label.pack(pady=10)
    token_entry = ctk.CTkEntry(info_window, width=500)
    token_entry.pack(pady=5)

    channel_label = ctk.CTkLabel(info_window, text="Enter Channel ID:")
    channel_label.pack(pady=10)
    channel_entry = ctk.CTkEntry(info_window, width=500)
    channel_entry.pack(pady=5)

    # Log Box
    log_box = ctk.CTkTextbox(info_window, width=580, height=400, font=("Courier", 12))
    log_box.pack(pady=10)

    # Button
    enter_button = ctk.CTkButton(
        info_window,
        text="Fetch Server Info",
        command=lambda: start_clear_messages(token_entry.get(), channel_entry.get(), log_box),
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

    # Function to clear messages
    async def clear_messages(token, channel_id, log_box):
        intents = discord.Intents.default()
        intents.messages = True
        client = None

        # Check if token is bot or user token
        if token.startswith("Bot "):  # Bot token
            client = commands.Bot(command_prefix="!", intents=intents)
            bot_or_user = "Bot Token"
        else:  # User token
            client = discord.Client(intents=intents)
            bot_or_user = "User Token"

        # Log into Discord
        @client.event
        async def on_ready():
            add_log(f"[{datetime.now().strftime('%H:%M:%S')}] Logged in with {bot_or_user}", "info")

            # Get the channel
            channel = client.get_channel(int(channel_id))

            if not channel:
                add_log(f"[{datetime.now().strftime('%H:%M:%S')}] Channel not found.", "error")
                await client.close()
                return

            # Clear messages (limit set to 100 messages, can be adjusted)
            try:
                deleted = await channel.purge(limit=100)  # Change limit as needed
                add_log(f"[{datetime.now().strftime('%H:%M:%S')}] Deleted {len(deleted)} messages.", "success")
            except Exception as e:
                add_log(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {str(e)}", "error")

            await client.close()

        # Log the token attempt
        print(f"Attempting to log in with token: {token}")

        # Run the bot
        await client.start(token)

    # Function to run the async clear_messages function in a new thread
    def start_clear_messages(token, channel_id, log_box):
        asyncio.run(clear_messages(token, channel_id, log_box))

# Example to call the window
if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("300x200")
    open_button = ctk.CTkButton(app, text="Open Group Clearer", command=open_window)
    open_button.pack(pady=50)
    app.mainloop()

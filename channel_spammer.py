import customtkinter as ctk
import discord

class ChannelSpammer:
    def __init__(self, token, channel_id, message, count):
        self.token = token
        self.channel_id = channel_id
        self.message = message
        self.count = count

    async def spam(self):
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            channel = client.get_channel(self.channel_id)
            for _ in range(self.count):
                await channel.send(self.message)
                print("Message sent!")
            await client.close()

        await client.start(self.token)

def open_window():
    # Create a new window for the channel spammer
    spammer_window = ctk.CTkToplevel()
    spammer_window.title("Channel Spammer")
    spammer_window.geometry("400x300")

    # Label and Entry for Discord Token
    token_label = ctk.CTkLabel(spammer_window, text="Discord Token:")
    token_label.pack(pady=10)
    token_entry = ctk.CTkEntry(spammer_window, width=300, show="*")
    token_entry.pack()

    # Label and Entry for Channel ID
    channel_label = ctk.CTkLabel(spammer_window, text="Channel ID:")
    channel_label.pack(pady=10)
    channel_entry = ctk.CTkEntry(spammer_window, width=300)
    channel_entry.pack()

    # Label and Entry for Message
    message_label = ctk.CTkLabel(spammer_window, text="Message to Send:")
    message_label.pack(pady=10)
    message_entry = ctk.CTkEntry(spammer_window, width=300)
    message_entry.pack()

    # Spinbox for Number of Messages
    count_label = ctk.CTkLabel(spammer_window, text="Number of Messages:")
    count_label.pack(pady=10)
    count_spinbox = ctk.CTkSpinBox(spammer_window, from_=1, to=100, width=100)
    count_spinbox.pack()

    # Button to Start Spamming
    def start_spam():
        token = token_entry.get()
        channel_id = int(channel_entry.get())
        message = message_entry.get()
        count = int(count_spinbox.get())

        spammer = ChannelSpammer(token, channel_id, message, count)
        import asyncio
        asyncio.run(spammer.spam())

    spam_button = ctk.CTkButton(spammer_window, text="Start Spamming", command=start_spam)
    spam_button.pack(pady=20)
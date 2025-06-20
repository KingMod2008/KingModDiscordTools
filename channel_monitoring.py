import discord
import customtkinter as ctk
import logging
import threading

# Set up logging to log to a file and display logs in the GUI
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[logging.FileHandler('channel_monitoring.log'), logging.StreamHandler()])

# Function to handle message logging in the GUI
def log_message(log_box, message, tag="default"):
    log_box.configure(state="normal")
    log_box.insert("end", message + "\n", tag)
    log_box.configure(state="disabled")
    log_box.yview("end")

# Create a client instance
class ChannelMonitorClient(discord.Client):
    def __init__(self, log_box, monitored_channel_id):
        super().__init__(intents=discord.Intents.default())
        self.log_box = log_box
        self.monitored_channel_id = monitored_channel_id

    async def on_ready(self):
        logging.info(f'Logged in as {self.user}')
        log_message(self.log_box, f'Logged in as {self.user}', "success")
        # Fetch the channel to confirm the bot can access it
        channel = self.get_channel(self.monitored_channel_id)
        if channel:
            log_message(self.log_box, f"Monitoring channel: {channel.name}", "info")
        else:
            log_message(self.log_box, "Channel not found. Please check the ID.", "error")

    async def on_message(self, message):
        # Skip the bot's own messages
        if message.author == self.user:
            return

        # Check if the message is in the monitored channel
        if message.channel.id == self.monitored_channel_id:
            # Make sure to print the actual message content
            if message.content:
                # Apply different colors based on the author or message content
                if "error" in message.content.lower():
                    log_message(self.log_box, f"Error message from {message.author} in {message.channel.name}: {message.content}", "error")
                elif "success" in message.content.lower():
                    log_message(self.log_box, f"Success message from {message.author} in {message.channel.name}: {message.content}", "success")
                else:
                    log_message(self.log_box, f"Message from {message.author} in {message.channel.name}: {message.content}", "default")
            else:
                # Log empty or non-content messages as default (if necessary)
                log_message(self.log_box, f"Empty message from {message.author} in {message.channel.name}", "default")

# Function to start the bot in a separate thread
def start_bot(token, channel_id, log_box):
    client = ChannelMonitorClient(log_box, int(channel_id))
    client.run(token)

# Function to open the main window for channel monitoring
def open_window():
    window = ctk.CTk()
    window.geometry("500x400")
    window.title("Channel Monitor")

    # Bot Token Label and Entry
    token_label = ctk.CTkLabel(window, text="Enter Bot Token:")
    token_label.pack(pady=10)
    token_entry = ctk.CTkEntry(window, width=300)
    token_entry.pack(pady=5)

    # Channel ID Label and Entry
    channel_label = ctk.CTkLabel(window, text="Enter Channel ID to Monitor:")
    channel_label.pack(pady=10)
    channel_entry = ctk.CTkEntry(window, width=300)
    channel_entry.pack(pady=5)

    # Log Box
    log_box = ctk.CTkTextbox(window, width=480, height=200, font=("Courier", 12))
    log_box.pack(pady=10)
    
    # Configure tags (colors)
    log_box.tag_config("default", foreground="#FFFFFF")  # White for default messages
    log_box.tag_config("error", foreground="#FF0000")    # Red for error messages
    log_box.tag_config("success", foreground="#00FF00")  # Green for success messages
    log_box.tag_config("info", foreground="#ADD8E6")     # Light Blue for info messages (e.g. 'Starting the bot...')

    log_box.configure(state="disabled")

    # Button to start the bot
    def on_start_button_click():
        token = token_entry.get()
        channel_id = channel_entry.get()

        if token and channel_id:
            log_message(log_box, "Starting the bot...", "info")  # Blue for "Starting"
            # Start the bot in a separate thread
            threading.Thread(target=start_bot, args=(token, channel_id, log_box), daemon=True).start()
        else:
            log_message(log_box, "Please provide both Bot Token and Channel ID.", "error")

    start_button = ctk.CTkButton(window, text="Start Monitoring", command=on_start_button_click, width=200, height=40, corner_radius=8, fg_color="#3399FF", hover_color="#0077CC")
    start_button.pack(pady=20)

    window.mainloop()

# Main entry point for the GUI application
if __name__ == "__main__":
    open_window()

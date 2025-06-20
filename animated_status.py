import discord
import customtkinter as ctk
import threading
import time

# Custom Client Class for Discord Bot
class AnimatedStatusClient(discord.Client):
    def __init__(self, log_box, activity_list):
        super().__init__(intents=discord.Intents.default())
        self.log_box = log_box
        self.activity_list = activity_list
        self.current_activity = 0
        self.auto_change_enabled = False
        self.auto_change_interval = 5  # Default to 5 seconds if not set

    async def on_ready(self):
        log_message(self.log_box, f'Logged in as {self.user}')
        await self.update_status()

    async def update_status(self):
        while True:
            activity = self.activity_list[self.current_activity]
            await self.change_presence(activity=activity)
            self.current_activity = (self.current_activity + 1) % len(self.activity_list)
            time.sleep(self.auto_change_interval)  # Update activity based on interval

    def set_auto_change(self, interval):
        self.auto_change_interval = interval
        self.auto_change_enabled = True

# Function to handle message logging in the GUI
def log_message(log_box, message, tag="default"):
    log_box.configure(state="normal")
    log_box.insert("end", message + "\n", tag)
    log_box.configure(state="disabled")
    log_box.yview("end")

# Function to start the bot in a separate thread
def start_bot(token, log_box, activity_list):
    client = AnimatedStatusClient(log_box, activity_list)
    client.run(token)

# Function to open the main window for animated status
def open_window():
    window = ctk.CTk()
    window.geometry("600x700")
    window.title("Animated Status Bot")

    # Bot Token Label and Entry
    token_label = ctk.CTkLabel(window, text="Enter Bot Token:")
    token_label.pack(pady=10)
    token_entry = ctk.CTkEntry(window, width=300)
    token_entry.pack(pady=5)

    # Log Box
    log_box = ctk.CTkTextbox(window, width=480, height=200, font=("Courier", 12))
    log_box.pack(pady=10)
    
    # Configure tags (colors)
    log_box.tag_config("default", foreground="#FFFFFF")  # White for default messages
    log_box.tag_config("error", foreground="#FF0000")    # Red for error messages
    log_box.tag_config("success", foreground="#00FF00")  # Green for success messages
    log_box.tag_config("info", foreground="#ADD8E6")     # Light Blue for info messages (e.g. 'Starting the bot...')

    log_box.configure(state="disabled")

    # List to store the activity messages
    activity_list = []

    # Function to add a new activity message
    def add_activity():
        new_activity_window = ctk.CTkToplevel(window)
        new_activity_window.geometry("400x250")
        new_activity_window.title("Add New Activity")

        # Activity Type Label and Dropdown
        activity_type_label = ctk.CTkLabel(new_activity_window, text="Select Activity Type:")
        activity_type_label.pack(pady=10)
        activity_type = ctk.CTkComboBox(new_activity_window, values=["Playing", "Listening", "Streaming"], width=300)
        activity_type.pack(pady=5)

        # New message entry
        new_message_label = ctk.CTkLabel(new_activity_window, text="Enter New Activity Message:")
        new_message_label.pack(pady=10)
        new_message_entry = ctk.CTkEntry(new_activity_window, width=300)
        new_message_entry.pack(pady=5)

        def on_add_button_click():
            activity_message = new_message_entry.get()
            activity_type_value = activity_type.get()

            if activity_message and activity_type_value:
                activity_type_map = {
                    "Playing": discord.ActivityType.playing,
                    "Listening": discord.ActivityType.listening,
                    "Streaming": discord.ActivityType.streaming
                }

                new_activity = discord.Activity(type=activity_type_map[activity_type_value], name=activity_message)
                activity_list.append(new_activity)
                log_message(log_box, f"Added new activity: {activity_message} ({activity_type_value})", "success")
                new_activity_window.destroy()
            else:
                log_message(log_box, "Please fill both fields.", "error")

        add_button = ctk.CTkButton(new_activity_window, text="Add Activity", command=on_add_button_click, width=200, height=40, corner_radius=8, fg_color="#3399FF", hover_color="#0077CC")
        add_button.pack(pady=20)

    # Function to edit an existing activity message
    def edit_activity(index):
        edit_activity_window = ctk.CTkToplevel(window)
        edit_activity_window.geometry("400x250")
        edit_activity_window.title("Edit Activity")

        # Activity Type Label and Dropdown
        activity_type_label = ctk.CTkLabel(edit_activity_window, text="Select Activity Type:")
        activity_type_label.pack(pady=10)
        activity_type = ctk.CTkComboBox(edit_activity_window, values=["Playing", "Listening", "Streaming"], width=300)
        activity_type.set(activity_list[index].type.name.capitalize())  # Set current activity type
        activity_type.pack(pady=5)

        # New message entry
        new_message_label = ctk.CTkLabel(edit_activity_window, text="Edit Activity Message:")
        new_message_label.pack(pady=10)
        new_message_entry = ctk.CTkEntry(edit_activity_window, width=300)
        new_message_entry.insert(0, activity_list[index].name)  # Set current activity message
        new_message_entry.pack(pady=5)

        def on_edit_button_click():
            activity_message = new_message_entry.get()
            activity_type_value = activity_type.get()

            if activity_message and activity_type_value:
                activity_type_map = {
                    "Playing": discord.ActivityType.playing,
                    "Listening": discord.ActivityType.listening,
                    "Streaming": discord.ActivityType.streaming
                }

                updated_activity = discord.Activity(type=activity_type_map[activity_type_value], name=activity_message)
                activity_list[index] = updated_activity
                log_message(log_box, f"Updated activity: {activity_message} ({activity_type_value})", "success")
                edit_activity_window.destroy()
            else:
                log_message(log_box, "Please fill both fields.", "error")

        edit_button = ctk.CTkButton(edit_activity_window, text="Update Activity", command=on_edit_button_click, width=200, height=40, corner_radius=8, fg_color="#3399FF", hover_color="#0077CC")
        edit_button.pack(pady=20)

    # Function to enable auto-change for activity status
    def enable_auto_change(index):
        auto_change_window = ctk.CTkToplevel(window)
        auto_change_window.geometry("400x250")
        auto_change_window.title("Auto-Change Settings")

        # Text Entry for Current Activity
        activity_label = ctk.CTkLabel(auto_change_window, text=f"Activity: {activity_list[index].name}")
        activity_label.pack(pady=10)

        # Interval Input for Auto-Change
        interval_label = ctk.CTkLabel(auto_change_window, text="Set Auto-Change Interval (1-60 seconds):")
        interval_label.pack(pady=10)
        interval_entry = ctk.CTkEntry(auto_change_window, width=300)
        interval_entry.pack(pady=5)

        def on_enable_button_click():
            try:
                interval = int(interval_entry.get())
                if 1 <= interval <= 60:
                    client.set_auto_change(interval)
                    log_message(log_box, f"Auto-change enabled with {interval} second(s) interval.", "success")
                    auto_change_window.destroy()
                else:
                    log_message(log_box, "Please enter a valid interval (1-60 seconds).", "error")
            except ValueError:
                log_message(log_box, "Please enter a valid number.", "error")

        enable_button = ctk.CTkButton(auto_change_window, text="Enable Auto-Change", command=on_enable_button_click, width=200, height=40, corner_radius=8, fg_color="#3399FF", hover_color="#0077CC")
        enable_button.pack(pady=20)

    # Display activity list and add/edit buttons
    def display_activities():
        for widget in activity_list_frame.winfo_children():
            widget.destroy()

        for i, activity in enumerate(activity_list):
            activity_frame = ctk.CTkFrame(activity_list_frame)
            activity_frame.pack(fill="x", padx=10, pady=5)

            activity_label = ctk.CTkLabel(activity_frame, text=f"{activity.type.name.capitalize()}: {activity.name}")
            activity_label.pack(side="left", padx=10)

            edit_button = ctk.CTkButton(activity_frame, text="Edit", command=lambda index=i: edit_activity(index), width=100)
            edit_button.pack(side="left", padx=5)

            enable_auto_change_button = ctk.CTkButton(activity_frame, text="Enable Auto-Change", command=lambda index=i: enable_auto_change(index), width=150)
            enable_auto_change_button.pack(side="left", padx=5)

            delete_button = ctk.CTkButton(activity_frame, text="Delete", command=lambda index=i: delete_activity(index), width=100)
            delete_button.pack(side="left", padx=5)

    def delete_activity(index):
        del activity_list[index]
        display_activities()

    # Button to add new activity message
    add_message_button = ctk.CTkButton(window, text="Add New Activity", command=add_activity, width=200, height=40, corner_radius=8, fg_color="#3399FF", hover_color="#0077CC")
    add_message_button.pack(pady=10)

    # Frame to hold the activity list
    activity_list_frame = ctk.CTkFrame(window)
    activity_list_frame.pack(fill="x", pady=10)

    # Button to start the bot
    def on_start_button_click():
        token = token_entry.get()

        if token:
            log_message(log_box, "Starting the bot...", "info")  # Blue for "Starting"
            # Start the bot in a separate thread
            threading.Thread(target=start_bot, args=(token, log_box, activity_list), daemon=True).start()
        else:
            log_message(log_box, "Please provide a Bot Token.", "error")

    start_button = ctk.CTkButton(window, text="Start Animated Status", command=on_start_button_click, width=200, height=40, corner_radius=8, fg_color="#3399FF", hover_color="#0077CC")
    start_button.pack(pady=20)

    # Display the activities in the list
    display_activities()

    window.mainloop()

# Main entry point for the GUI application
if __name__ == "__main__":
    open_window()

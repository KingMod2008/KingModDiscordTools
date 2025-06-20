import discord
import customtkinter as ctk
import threading
import asyncio

# Function to clear DMs for the user
async def clear_dms(client, user_id):
    try:
        user = await client.fetch_user(user_id)
        messages = await user.dm_channels[0].history(limit=100).flatten()  # Fetch the last 100 DMs
        for message in messages:
            await message.delete()
        print(f"Cleared DMs for {user.name}")
    except discord.errors.HTTPException as e:
        print(f"Error clearing DMs for user {user_id}: {str(e)}")

# Function to start the DM cleaner process in a separate thread
def start_cleaner(client, user_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(clear_dms(client, user_id))

# Function to open the main window for DM cleaner
def open_window():
    cleaner_window = ctk.CTkToplevel()
    cleaner_window.title("DM Cleaner")
    cleaner_window.geometry("500x400")

    # Label
    user_id_label = ctk.CTkLabel(cleaner_window, text="Enter User ID to clean DMs:")
    user_id_label.pack(pady=10)

    # Entry for User ID
    user_id_entry = ctk.CTkEntry(cleaner_window, width=300)
    user_id_entry.pack(pady=5)

    # Log Box
    log_box = ctk.CTkTextbox(cleaner_window, width=480, height=200, font=("Courier", 12))
    log_box.pack(pady=10)

    # Button to start the cleaner
    def on_clean_button_click():
        user_id = user_id_entry.get()
        if user_id:
            log_box.configure(state="normal")
            log_box.insert("end", f"Starting to clean DMs for user ID: {user_id}\n", "info")
            log_box.configure(state="disabled")
            start_cleaner(client, user_id)
        else:
            log_box.configure(state="normal")
            log_box.insert("end", "Please enter a valid User ID.\n", "error")
            log_box.configure(state="disabled")
    
    clean_button = ctk.CTkButton(
        cleaner_window,
        text="Clean DMs",
        command=on_clean_button_click,
        width=200,
        height=40,
        corner_radius=8,
        fg_color="#3399FF",
        hover_color="#0077CC"
    )
    clean_button.pack(pady=10)

    log_box.configure(state="disabled")

    # Configure tags (colors)
    log_box.tag_config("info", foreground="#FF3333")     # Light Sky Blue
    log_box.tag_config("error", foreground="#FF0000")    # Red
    log_box.tag_config("default", foreground="#FFFFFF")  # White for normal text

# Main GUI setup
if __name__ == "__main__":
    # Create a Discord client to interact with the API
    client = discord.Client()

    # Open main window for DM Cleaner
    app = ctk.CTk()
    app.geometry("300x200")

    # Open button to start the cleaner window
    open_button = ctk.CTkButton(app, text="Open DM Cleaner", command=open_window)
    open_button.pack(pady=50)

    app.mainloop()

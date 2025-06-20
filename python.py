import os
import subprocess

# Path to your folder with Python files
folder_path = r"C:\Users\M\Desktop\my tools py\XkingTool"

# Change the current directory to the folder where Python files are located
os.chdir(folder_path)

# Loop through all .py files in the folder and convert them to .exe
for filename in os.listdir(folder_path):
    if filename.endswith(".py"):
        script_path = os.path.join(folder_path, filename)
        
        # Run PyInstaller for each .py file
        subprocess.run(["python", "-m", "PyInstaller", "--onefile", "--noconsole", script_path])

print("Conversion complete!")

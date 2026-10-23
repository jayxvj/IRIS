import tkinter as tk
from tkinter import filedialog
import json
import base64
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "protected_files.dat")
BAT_FILE = os.path.join(BASE_DIR, "sentinel.bat")

# If already configured → exit silently
if os.path.exists(CONFIG_FILE):
    sys.exit(0)

# ---------- ONE-TIME SETUP UI ----------
root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

files = filedialog.askopenfilenames(
    title="Select files to protect",
    filetypes=[("Text & Code Files", "*.*")]
)

root.destroy()

# If user cancels → exit silently
if not files:
    sys.exit(0)

# Encode file list
encoded = base64.b64encode(
    json.dumps(list(files)).encode("utf-8")
).decode("utf-8")

# Save configuration safely
with open(CONFIG_FILE, "w", encoding="utf-8") as f:
    f.write(encoded)
    f.flush()
    os.fsync(f.fileno())

# Small delay to avoid race condition
time.sleep(0.3)

# Relaunch controller (BAT decides ghost/setup)
if os.path.exists(BAT_FILE):
    os.startfile(BAT_FILE)

sys.exit(0)

# S E N T I N E L
# Python 3.9+ | Windows only

from cryptography.fernet import Fernet
import hashlib, requests, time, pythoncom
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from datetime import datetime
import os, base64, zipfile, tempfile, shutil, sys, subprocess
import tkinter as tk
from tkinter import filedialog
import random
from PIL import Image, ImageTk

# ================= CONTEXT SENSORS =================
def get_master_volume():
    try:
        pythoncom.CoInitialize()
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return round(volume.GetMasterVolumeLevelScalar() * 100)
    except:
        return 50


def get_sp500_change():
    try:
        url = (
            "https://www.alphavantage.co/query"
            "?function=GLOBAL_QUOTE&symbol=^GSPC"
            "&apikey=4YWSI2R28AJFUGJA"
        )
        data = requests.get(url, timeout=3).json()
        return float(
            data["Global Quote"]["10. change percent"].replace("%", "")
        )
    except:
        return 0.001


def generate_context_key():
    ctx = f"{get_sp500_change()}|{get_master_volume()}|{datetime.now():%Y-%m-%d}"
    return base64.urlsafe_b64encode(hashlib.sha256(ctx.encode()).digest())


# ================= SENTINEL DIALOG =================
def sentinel_dialog(parent, title, message, mode="info"):
    colors = {
        "info": "#00d2ff",
        "success": "#00ff9c",
        "error": "#ff4b2b"
    }

    if parent is not None and parent.winfo_exists():
        root = parent
        cleanup = False
    else:
        root = tk.Tk()
        root.withdraw()
        cleanup = True

    dlg = tk.Toplevel(root)
    dlg.overrideredirect(True)
    dlg.configure(bg="#0d111a")
    dlg.attributes("-topmost", True)
    
    lines = message.count("\n") + 1
    w = 360
    h = 100 + (lines * 18)
    
    x = dlg.winfo_screenwidth() // 2 - w // 2
    y = dlg.winfo_screenheight() // 2 - h // 2
    dlg.geometry(f"{w}x{h}+{x}+{y}")

    accent = colors.get(mode, "#00d2ff")

    frame = tk.Frame(
        dlg,
        bg="#0d111a",
        highlightbackground=accent,
        highlightthickness=1
    )
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame,
        text=title,
        bg=accent,
        fg="black",
        font=("OCR A Extended", 11, "bold"),
        pady=6
    ).pack(fill="x")

    tk.Label(
        frame,
        text=message,
        bg="#0d111a",
        fg="white",
        font=("Consolas", 10),
        pady=12,
        wraplength=330,
        justify="center"
    ).pack()

    tk.Button(
        frame,
        text=" ACKNOWLEDGE ",
        command=dlg.destroy,
        bg="#0d111a",
        fg=accent,
        activebackground=accent,
        activeforeground="black",
        relief="flat",
        bd=1,
        highlightthickness=1,
        highlightbackground=accent,
        font=("Segoe UI", 9, "bold")
    ).pack(pady=10)

    dlg.grab_set()
    root.wait_window(dlg)

    if cleanup:
        root.destroy()


# ================= SUCCESS DIALOG HELPERS =================
def encrypt_success_dialog(vault_path):
    sentinel_dialog(
        None,
        "ENCRYPTION SUCCESS",
        f"VAULT CREATED SUCCESSFULLY\n\n{vault_path}",
        "success"
    )


def decrypt_success_dialog(output_dir):
    sentinel_dialog(
        None,
        "DECRYPTION SUCCESS",
        f"VAULT UNLOCKED\n\nFILES RESTORED TO:\n{output_dir}",
        "success"
    )

# ================= UI =================
class SentinelUI:
    def __init__(self):
        self.selected = []
        self.logs = []
        
        self.dx = 0
        self.dy = 0

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.title("SENTINEL VAULT")

        self.colors = {
            "bg": "#05080f",
            "panel": "#0d111a",
            "accent": "#00d2ff",
            "accent_dim": "#003d4d",
            "text": "#8ea1b4"
        }

        self.width, self.height = 850, 520
        self.center()
        self.root.configure(bg=self.colors["bg"])

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=self.colors["bg"],
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.draw_background_grid()
        self.draw_ui()
        self.enable_drag()

        self.root.bind("<Escape>", lambda e: self.close())

        try:
            self.load_entity_image()
        except:
            pass

        self.log("ENVIRONMENT INITIALIZED")

    def center(self):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(
            f"{self.width}x{self.height}+{(sw-self.width)//2}+{(sh-self.height)//2}"
        )

    def safe_destroy(self):
        try:
            self.canvas.delete("all")
            self.entity_imgtk = None
        except:
            pass
        self.root.destroy()

    def load_entity_image(self):
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        img = Image.open(img_path).convert("RGBA")
        img = img.resize((269, 335), Image.LANCZOS)
        self.entity_imgtk = ImageTk.PhotoImage(img)
        self.canvas.create_image(165, 250, image=self.entity_imgtk)

    def draw_background_grid(self):
        for i in range(0, self.width, 40):
            self.canvas.create_line(i, 0, i, self.height, fill="#0a0e17")
        for i in range(0, self.height, 40):
            self.canvas.create_line(0, i, self.width, i, fill="#0a0e17")

    def draw_ui(self):
        c, col = self.canvas, self.colors

        # Top Header & Navigation
        c.create_rectangle(0, 0, self.width, 50, fill=col["panel"], width=0)
        c.create_line(0, 50, self.width, 50, fill=col["accent"])
        c.create_text(
            25, 25, anchor="w",
            text="S  E  N  T  I  N  E  L",
            fill="white",
            font=("OCR A Extended", 14, "bold")
        )

        # Security Module Launchers in Header
        self.make_btn(470, 9, "LIVE SECURITY", self.run_liv_s, w=150, h=32, accent="#ff4b2b")
        self.make_btn(635, 9, "CONCEAL SECURITY", self.run_con_s, w=150, h=32, accent="#00ff9c")
        self.make_btn(800, 9, "✕", self.close, w=32, h=32, accent="#ff4b2b")

        c.create_rectangle(30, 80, 300, 420, outline=col["accent_dim"])

        self.list_frame = tk.Frame(
            self.root,
            bg=col["panel"],
            highlightbackground=col["accent_dim"],
            highlightthickness=1
        )
        self.list_frame.place(x=330, y=80, width=490, height=340)

        self.listbox = tk.Listbox(
            self.list_frame,
            bg=col["panel"],
            fg="white",
            font=("Consolas", 10),
            bd=0
        )
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)

        self.log_text = c.create_text(
            30, 440, text="",
            fill=col["text"],
            anchor="nw",
            font=("Consolas", 8)
        )

        self.make_btn(330, 450, "+ FILES", self.add_files)
        self.make_btn(505, 450, "+ FOLDER", self.add_folder)
        self.make_btn(680, 450, "INITIALIZE", self.finish, primary=True)

    def make_btn(self, x, y, text, cmd, primary=False, w=140, h=35, accent=None):
        col = self.colors
        outline = accent if accent else (col["accent"] if primary else col["accent_dim"])
        tag = f"btn{random.randint(1000,9999)}"

        rect = self.canvas.create_rectangle(
            x, y, x + w, y + h,
            outline=outline,
            fill=col["panel"],
            tags=tag
        )
        self.canvas.create_text(
            x + w / 2, y + h / 2,
            text=text,
            fill="white",
            font=("Segoe UI", 8, "bold"),
            tags=tag
        )
        self.canvas.tag_bind(tag, "<Button-1>", lambda e: cmd())
        self.canvas.tag_bind(tag, "<Enter>", lambda e: (
            self.canvas.config(cursor="hand2"),
            self.canvas.itemconfig(rect, outline=accent or col["accent"])
        ))
        self.canvas.tag_bind(tag, "<Leave>", lambda e: (
            self.canvas.config(cursor=""),
            self.canvas.itemconfig(rect, outline=outline)
        ))

    def run_liv_s(self):
        self.log("STARTING LIV_S SECURITY...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        bat_path = os.path.join(root_dir, "LIV_S", "sentinel.bat")
        if os.path.exists(bat_path):
            try:
                subprocess.Popen(["cmd.exe", "/c", bat_path], cwd=os.path.dirname(bat_path))
                self.log("LIV_S EXECUTED (sentinel.bat)")
            except Exception as e:
                self.log(f"LIV_S LAUNCH ERROR: {e}")
                sentinel_dialog(self.root, "LAUNCH ERROR", f"COULD NOT EXECUTE LIV_S:\n{e}", "error")
        else:
            self.log("ERROR: LIV_S sentinel.bat NOT FOUND")
            sentinel_dialog(self.root, "FILE NOT FOUND", f"LIV_S BAT NOT FOUND:\n{bat_path}", "error")

    def run_con_s(self):
        self.log("STARTING CON_S SECURITY...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        bat_path = os.path.join(root_dir, "CON_S", "sentinel.bat")
        if os.path.exists(bat_path):
            try:
                subprocess.Popen(["cmd.exe", "/c", bat_path], cwd=os.path.dirname(bat_path))
                self.log("CON_S EXECUTED (sentinel.bat)")
            except Exception as e:
                self.log(f"CON_S LAUNCH ERROR: {e}")
                sentinel_dialog(self.root, "LAUNCH ERROR", f"COULD NOT EXECUTE CON_S:\n{e}", "error")
        else:
            self.log("ERROR: CON_S sentinel.bat NOT FOUND")
            sentinel_dialog(self.root, "FILE NOT FOUND", f"CON_S BAT NOT FOUND:\n{bat_path}", "error")

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f">> {ts} : {msg}")
        self.logs = self.logs[-4:]
        self.canvas.itemconfig(self.log_text, text="\n".join(self.logs))

    def enable_drag(self):
        self.canvas.bind("<ButtonPress-1>", self.drag_start)
        self.canvas.bind("<B1-Motion>", self.drag)

    def drag_start(self, e):
        self.dx, self.dy = e.x, e.y

    def drag(self, e):
        self.root.geometry(
            f"+{self.root.winfo_x()+e.x-self.dx}"
            f"+{self.root.winfo_y()+e.y-self.dy}"
        )

    # ✅ UPDATED
    def add_files(self):
        for f in filedialog.askopenfilenames():

            if f.lower().endswith(".geofenced"):
                sentinel_dialog(
                    self.root,
                    "INVALID SELECTION",
                    "THIS FILE IS ALREADY ENCRYPTED\n\n"
                    "ENCRYPTING A VAULT AGAIN IS NOT ALLOWED",
                    "error"
                )
                self.log("BLOCKED RE-ENCRYPTION ATTEMPT")
                continue

            if f not in self.selected:
                self.selected.append(f)
                self.listbox.insert(tk.END, f"FILE  {os.path.basename(f)}")
                self.log(f"ADDED {os.path.basename(f)}")

    # ✅ UPDATED
    def add_folder(self):
        f = filedialog.askdirectory()
        if not f:
            return

        for root, _, files in os.walk(f):
            for file in files:
                if file.lower().endswith(".geofenced"):
                    sentinel_dialog(
                        self.root,
                        "INVALID FOLDER",
                        "THIS FOLDER CONTAINS AN ENCRYPTED VAULT\n\n"
                        "REMOVE IT BEFORE ENCRYPTION",
                        "error"
                    )
                    self.log("BLOCKED FOLDER WITH VAULT")
                    return

        if f not in self.selected:
            self.selected.append(f)
            self.listbox.insert(tk.END, f"DIR   {os.path.basename(f)}")
            self.log(f"ADDED {os.path.basename(f)}")

    def finish(self):
        if not self.selected:
            sentinel_dialog(
                self.root,
                "CRITICAL ERROR",
                "NO TARGETS SELECTED",
                "error"
            )
            return
        self.safe_destroy()

    def close(self):
        self.selected = []
        self.safe_destroy()

    def run(self):
        self.root.mainloop()
        return self.selected


# ================= ZIP =================
def zip_targets(targets, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for t in targets:
            if os.path.isfile(t):
                zipf.write(t, arcname=os.path.basename(t))
            else:
                for root, _, files in os.walk(t):
                    for f in files:
                        full = os.path.join(root, f)
                        arc = os.path.relpath(full, start=os.path.dirname(t))
                        zipf.write(full, arc)


# ================= ENCRYPT =================
def encrypt_in_place():
    ui = SentinelUI()
    targets = ui.run()
    if not targets:
        return

    # ✅ FINAL SAFETY NET
    for t in targets:
        if t.lower().endswith(".geofenced"):
            sentinel_dialog(
                None,
                "CRITICAL SAFETY BLOCK",
                "ENCRYPTED VAULT DETECTED IN TARGETS\n\n"
                "OPERATION ABORTED",
                "error"
            )
            return

    base_dir = os.path.dirname(targets[0])
    vault_path = os.path.join(base_dir, "vault.geofenced")

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "payload.zip")

    zip_targets(targets, zip_path)

    encrypted = Fernet(generate_context_key()).encrypt(
        open(zip_path, "rb").read()
    )

    with open(vault_path, "wb") as f:
        f.write(b"GEOFENCEv1\n")
        f.write(encrypted)

    for t in targets:
        if os.path.isfile(t):
            os.remove(t)
        else:
            shutil.rmtree(t)

    shutil.rmtree(temp_dir)
    encrypt_success_dialog(vault_path)


# ================= DECRYPT =================
def decrypt_vault(path):
    if not os.path.exists(path):
        sentinel_dialog(None, "ERROR", "VAULT FILE NOT FOUND", "error")
        return

    try:
        with open(path, "rb") as f:
            header = f.readline().strip()
            if header != b"GEOFENCEv1":
                sentinel_dialog(None, "ERROR", "INVALID OR CORRUPTED VAULT FILE", "error")
                return
            encrypted = f.read()
            if not encrypted:
                sentinel_dialog(None, "ERROR", "VAULT CONTAINS NO DATA", "error")
                return
    except Exception as e:
        sentinel_dialog(None, "ERROR", f"FAILED TO READ VAULT\n{e}", "error")
        return

    out_dir = os.path.dirname(path)
    for _ in range(50):
        try:
            data = Fernet(generate_context_key()).decrypt(encrypted)
            zip_path = os.path.join(out_dir, "payload_temp.zip")
            open(zip_path, "wb").write(data)
            with zipfile.ZipFile(zip_path) as z:
                z.extractall(out_dir)
            os.remove(zip_path)
            os.remove(path)
            decrypt_success_dialog(out_dir)
            return
        except:
            time.sleep(10)

    sentinel_dialog(None, "FAILED", "CONTEXT NEVER MATCHED\nTRY AGAIN LATER", "error")


def decrypt_with_ui():
    root = tk.Tk()
    root.withdraw()
    for v in filedialog.askopenfilenames(
        title="Select vault.geofenced file(s)",
        filetypes=[("Geofenced Vault", "*.geofenced")]
    ):
        decrypt_vault(v)


# ================= MAIN =================
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "decrypt":
        decrypt_with_ui()
    else:
        encrypt_in_place()

# S E N T I N E L  //  C O N _ S
# Concealment Security (Steganographic Obfuscation)

import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCK_SCRIPT = os.path.join(BASE_DIR, "lock.py")
UNLOCK_SCRIPT = os.path.join(BASE_DIR, "unlock.py")

def sentinel_msg(parent, title, message, mode="info"):
    colors = {
        "info": "#00d2ff",
        "success": "#00ff9c",
        "error": "#ff4b2b"
    }
    accent = colors.get(mode, "#00d2ff")

    dlg = tk.Toplevel(parent)
    dlg.overrideredirect(True)
    dlg.configure(bg="#0d111a")
    dlg.attributes("-topmost", True)

    lines = message.count("\n") + 1
    w = 380
    h = 100 + (lines * 18)
    sw = dlg.winfo_screenwidth()
    sh = dlg.winfo_screenheight()
    dlg.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    frame = tk.Frame(dlg, bg="#0d111a", highlightbackground=accent, highlightthickness=1)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame, text=title, bg=accent, fg="black",
        font=("OCR A Extended", 10, "bold"), pady=6
    ).pack(fill="x")

    tk.Label(
        frame, text=message, bg="#0d111a", fg="white",
        font=("Consolas", 9), pady=12, wraplength=350, justify="center"
    ).pack()

    tk.Button(
        frame, text=" ACKNOWLEDGE ", command=dlg.destroy,
        bg="#0d111a", fg=accent, activebackground=accent, activeforeground="black",
        relief="flat", bd=1, highlightthickness=1, highlightbackground=accent,
        font=("Segoe UI", 9, "bold")
    ).pack(pady=10)

    dlg.grab_set()
    parent.wait_window(dlg)

class ConcealmentUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.title("CON_S CONCEALMENT SECURITY")
        self.root.configure(bg="#05080f")

        self.w, self.h = 460, 290
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{self.w}x{self.h}+{(sw-self.w)//2}+{(sh-self.h)//2}")

        self.dx = 0
        self.dy = 0

        self.setup_ui()
        self.enable_drag()
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def enable_drag(self):
        self.root.bind("<ButtonPress-1>", self.drag_start)
        self.root.bind("<B1-Motion>", self.drag)

    def drag_start(self, e):
        self.dx, self.dy = e.x, e.y

    def drag(self, e):
        self.root.geometry(f"+{self.root.winfo_x()+e.x-self.dx}+{self.root.winfo_y()+e.y-self.dy}")

    def setup_ui(self):
        main = tk.Frame(self.root, bg="#0d111a", highlightbackground="#00d2ff", highlightthickness=1)
        main.pack(fill="both", expand=True)

        # Header
        hdr = tk.Frame(main, bg="#00d2ff", height=38)
        hdr.pack(fill="x")
        tk.Label(
            hdr, text="SENTINEL // CON_S STEALTH ENGINE",
            bg="#00d2ff", fg="black", font=("OCR A Extended", 11, "bold"), pady=6
        ).pack(side="left", padx=12)

        close_btn = tk.Button(
            hdr, text="✕", command=self.root.destroy,
            bg="#00d2ff", fg="black", activebackground="#ff4b2b", activeforeground="white",
            relief="flat", font=("Segoe UI", 10, "bold"), bd=0, padx=8
        )
        close_btn.pack(side="right")

        # Body info
        body = tk.Frame(main, bg="#0d111a", padx=20, pady=15)
        body.pack(fill="both", expand=True)

        tk.Label(
            body,
            text="STEGANOGRAPHIC CODE OBFUSCATION\nZero-Width Character Concealment & Maze Decoy Engine",
            bg="#0d111a", fg="#8ea1b4", font=("Consolas", 8), justify="center"
        ).pack(pady=5)

        # Action Buttons
        btn_frame = tk.Frame(body, bg="#0d111a")
        btn_frame.pack(pady=12, fill="x")

        lock_btn = tk.Button(
            btn_frame,
            text="🔒 LOCK / CONCEAL FILE",
            command=self.lock_files,
            bg="#0d111a", fg="#00d2ff", activebackground="#00d2ff", activeforeground="black",
            relief="flat", bd=1, highlightthickness=1, highlightbackground="#00d2ff",
            font=("Segoe UI", 9, "bold"), pady=8
        )
        lock_btn.pack(fill="x", pady=4)

        unlock_btn = tk.Button(
            btn_frame,
            text="🔓 UNLOCK / RESTORE FILE",
            command=self.unlock_files,
            bg="#0d111a", fg="#00ff9c", activebackground="#00ff9c", activeforeground="black",
            relief="flat", bd=1, highlightthickness=1, highlightbackground="#00ff9c",
            font=("Segoe UI", 9, "bold"), pady=8
        )
        unlock_btn.pack(fill="x", pady=4)

        tk.Label(
            body,
            text="Press ESC to close",
            bg="#0d111a", fg="#4a5568", font=("Consolas", 8)
        ).pack(side="bottom", pady=2)

    def lock_files(self):
        paths = filedialog.askopenfilenames(
            title="Select file(s) to conceal",
            filetypes=[("Text & Code Files", "*.*")]
        )
        if not paths:
            return

        locked_count = 0
        errors = []
        for p in paths:
            try:
                res = subprocess.run(
                    [sys.executable, LOCK_SCRIPT, p],
                    capture_output=True, text=True
                )
                if res.returncode == 0:
                    locked_count += 1
                else:
                    errors.append(f"{os.path.basename(p)}: {res.stderr.strip() or res.stdout.strip()}")
            except Exception as e:
                errors.append(f"{os.path.basename(p)}: {e}")

        if locked_count > 0:
            msg = f"{locked_count} FILE(S) CONCEALED SUCCESSFULLY\nDecoy maze game injected with invisible payload."
            if errors:
                msg += f"\n\nErrors encountered:\n" + "\n".join(errors[:3])
            sentinel_msg(self.root, "CONCEALMENT ACTIVE", msg, "success")
        elif errors:
            sentinel_msg(self.root, "ERROR", "\n".join(errors[:4]), "error")

    def unlock_files(self):
        paths = filedialog.askopenfilenames(
            title="Select concealed file(s) to unlock",
            filetypes=[("Text & Code Files", "*.*")]
        )
        if not paths:
            return

        unlocked_count = 0
        errors = []
        for p in paths:
            try:
                res = subprocess.run(
                    [sys.executable, UNLOCK_SCRIPT, p],
                    capture_output=True, text=True
                )
                if res.returncode == 0:
                    unlocked_count += 1
                else:
                    err = res.stderr.strip() or res.stdout.strip()
                    errors.append(f"{os.path.basename(p)}: {err}")
            except Exception as e:
                errors.append(f"{os.path.basename(p)}: {e}")

        if unlocked_count > 0:
            msg = f"{unlocked_count} FILE(S) RESTORED SUCCESSFULLY\nOriginal source code recovered."
            if errors:
                msg += f"\n\nErrors encountered:\n" + "\n".join(errors[:3])
            sentinel_msg(self.root, "FILE RESTORED", msg, "success")
        elif errors:
            sentinel_msg(self.root, "ERROR", "\n".join(errors[:4]), "error")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        # Direct CLI invocation for single file
        target = sys.argv[1]
        action = sys.argv[2] if len(sys.argv) > 2 else "lock"
        script = LOCK_SCRIPT if action.lower() == "lock" else UNLOCK_SCRIPT
        subprocess.run([sys.executable, script, target])
    else:
        app = ConcealmentUI()
        app.run()

import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API")

# ---------------- GHOST HARDENING ----------------
import ctypes, sys, os, json, base64
ctypes.windll.kernel32.FreeConsole()
sys.stdout = open(os.devnull, "w")
sys.stderr = open(os.devnull, "w")

# ---------------- CONFIG LOAD ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "protected_files.dat")

if not os.path.exists(CONFIG_FILE):
    os._exit(0)

try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        FILE_PATHS = json.loads(base64.b64decode(f.read()).decode("utf-8"))
except:
    os._exit(0)

FILE_PATHS = [p for p in FILE_PATHS if os.path.exists(p)]
if not FILE_PATHS:
    os._exit(0)

# -------- SESSION-ONLY PROTECTION --------
# Config is deleted AFTER loading so next run forces setup again
try:
    os.remove(CONFIG_FILE)
except:
    pass

# ---------------- ORIGINAL IMPORTS ----------------
import cv2
import face_recognition
import time
import hashlib
import difflib
import stat
import winsound
import threading
import datetime
import pygetwindow as gw
import msvcrt
import win32api
import win32gui
import win32con

# ---------------- CONFIG ----------------
ADMIN_PHOTO = os.path.join(BASE_DIR, "admin.jpg")
INTRUDER_FOLDER = os.path.join(BASE_DIR, "intruder_evidence")
INITIAL_GRACE_PERIOD = 5

ALLOWED_EXTENSIONS = {
    '.txt','.md','.json','.xml','.csv','.log','.ini','.cfg','.conf',
    '.py','.java','.c','.cpp','.h','.hpp','.cs','.js','.jsx','.ts',
    '.tsx','.html','.css','.scss','.php','.rb','.go','.rs','.swift',
    '.kt','.lua','.pl','.sh','.bat','.ps1','.sql','.yaml','.yml'
}

os.makedirs(INTRUDER_FOLDER, exist_ok=True)

# =====================================================
# ================= FINAL GUARDIAN ====================
# =====================================================

class FinalGuardian:

    def __init__(self, file_paths, admin_image_path):
        self.raw_paths = file_paths
        self.file_paths = []
        self.admin_image_path = admin_image_path
        self.script_path = os.path.abspath(__file__)

        self.cap = None
        self.camera_lock = threading.Lock()

        self.is_authenticated = False
        self.alarm_triggered = False
        self.warning_shown = False
        self.detection_start_time = None
        self.missing_admin_counter = 0

        self.file_database = {}

        win32api.SetConsoleCtrlHandler(self.on_exit_attempt, True)

        # SELF LOCK
        try:
            h = open(self.script_path, "r")
            msvcrt.locking(h.fileno(), msvcrt.LK_NBLCK, os.path.getsize(self.script_path))
        except:
            pass

        if self.script_path not in self.raw_paths:
            self.raw_paths.append(self.script_path)

        for p in self.raw_paths:
            if os.path.splitext(p)[1].lower() in ALLOWED_EXTENSIONS:
                self.file_paths.append(p)

        if not self.file_paths:
            os._exit(0)

        # LOAD ADMIN FACE
        admin_img = face_recognition.load_image_file(self.admin_image_path)
        enc = face_recognition.face_encodings(admin_img)
        if not enc:
            os._exit(0)
        self.admin_encoding = enc[0]

        # INIT FILE DATABASE
        for p in self.file_paths:
            try:
                s = os.stat(p)
                self.file_database[p] = {
                    "mtime": s.st_mtime,
                    "hash": self.calculate_hash(p),
                    "content": self.read_file_content(p)
                }
            except:
                pass

    # ---------------- UTILS ----------------
    def open_with_shell(self, path):
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "open", path, None, None, 1)
        except:
            pass

    # ---------------- CAMERA ----------------
    def get_camera_frame(self):
        with self.camera_lock:
            if self.cap is None or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
                for _ in range(5):
                    self.cap.read()
            return self.cap.read()

    def release_camera(self):
        with self.camera_lock:
            if self.cap:
                self.cap.release()
            self.cap = None

    # ---------------- FACE ----------------
    def get_face_match(self, frame):
        try:
            small = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            encs = face_recognition.face_encodings(rgb)
            if not encs:
                encs = face_recognition.face_encodings(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            return any(
                face_recognition.compare_faces([self.admin_encoding], e, 0.50)[0]
                for e in encs
            )
        except:
            return False

    def is_admin_active(self, timeout=2.0):
        start = time.time()
        while time.time() - start < timeout:
            r, f = self.get_camera_frame()
            if r and self.get_face_match(f):
                return True
            time.sleep(0.1)
        return False

    # ---------------- FILE ----------------
    def calculate_hash(self, path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for c in iter(lambda: f.read(4096), b""):
                h.update(c)
        return h.hexdigest()

    def read_file_content(self, path):
        try:
            return open(path, "r", encoding="utf-8", errors="ignore").readlines()
        except:
            return []

    def update_file_database(self, path):
        s = os.stat(path)
        self.file_database[path] = {
            "mtime": s.st_mtime,
            "hash": self.calculate_hash(path),
            "content": self.read_file_content(path)
        }

    # ---------------- EXIT BLOCK ----------------
    def on_exit_attempt(self, event):
        if self.alarm_triggered:
            return True

        start = time.time()
        while time.time() - start < 6:
            r,f = self.get_camera_frame()
            if r and self.get_face_match(f):
                self.release_camera()
                os._exit(0)
        return True

    # ---------------- ALARM ----------------
    def trigger_alarm(self, path):
        self.alarm_triggered = True
        self.get_camera_frame()

        intrusion_start = datetime.datetime.now()
        evidence_photos = []

        def siren():
            while self.alarm_triggered:
                winsound.Beep(2500,500)
                time.sleep(0.1)

        threading.Thread(target=siren, daemon=True).start()

        # Capture evidence ONLY of unauthorized users / intruders (never admin)
        start_time = time.time()
        while self.alarm_triggered and (time.time() - start_time < 5.0):
            r, f = self.get_camera_frame()
            if r:
                if self.get_face_match(f):
                    # Admin verified, disarm immediately without capturing as intruder
                    self.alarm_triggered = False
                    break
                else:
                    if len(evidence_photos) < 3:
                        p = os.path.join(INTRUDER_FOLDER, f"intruder_{int(time.time())}_{len(evidence_photos)}.jpg")
                        cv2.imwrite(p, f)
                        evidence_photos.append(p)
            time.sleep(0.3)

        # 🔒 BLOCK HERE UNTIL ADMIN FACE
        while self.alarm_triggered:
            r,f = self.get_camera_frame()
            if r and self.get_face_match(f):
                self.alarm_triggered = False
            time.sleep(0.1)

        self.release_camera()

        for p in self.file_paths:
            try:
                os.chmod(p, stat.S_IWRITE)
                self.update_file_database(p)
            except:
                pass

        # ONLY generate report and display evidence if ACTUAL INTRUDER photos were captured
        if evidence_photos:
            log_file = os.path.join(INTRUDER_FOLDER, f"incident_{int(time.time())}.txt")
            try:
                old = self.file_database[path]["content"]
                new = self.read_file_content(path)
                diff = difflib.ndiff(old, new)

                with open(log_file, "w", encoding="utf-8") as f:
                    f.write("🚨 SECURITY INCIDENT REPORT\n")
                    f.write(f"🕒 Incident Start : {intrusion_start}\n")
                    f.write(f"📂 File          : {path}\n")
                    f.write("-"*60 + "\n")
                    f.write("📡 LIVE FILE MODIFICATION TRACE\n\n")

                    for line in diff:
                        if line.startswith(("+ ","- ")):
                            ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                            f.write(f"[{ts}] {line}")
            except:
                pass

            if os.path.exists(log_file):
                self.open_with_shell(log_file)
            for p in evidence_photos:
                if os.path.exists(p):
                    self.open_with_shell(p)

    # ---------------- MAIN LOOP ----------------
    def start(self):
        while True:
            try:
                # 🚨 HARD BLOCK DURING ALARM
                if self.alarm_triggered:
                    time.sleep(0.2)
                    continue

                if self.are_any_files_open():

                    # PRE-EDIT AUTH
                    if not self.is_authenticated:
                        if self.detection_start_time is None:
                            self.detection_start_time = time.time()

                        r,f = self.get_camera_frame()
                        if r:
                            if self.get_face_match(f):
                                self.is_authenticated = True
                                self.missing_admin_counter = 0
                                self.warning_shown = False
                                self.release_camera()
                            else:
                                self.missing_admin_counter += 1
                                elapsed = time.time() - self.detection_start_time
                                if self.missing_admin_counter > 2 and elapsed > INITIAL_GRACE_PERIOD:
                                    if not self.warning_shown:
                                        self.warning_shown = True
                                        ctypes.windll.user32.MessageBoxW(
                                            0,
                                            "UNAUTHORIZED USER DETECTED.\nDO NOT EDIT.",
                                            "WARNING",
                                            0x10 | 0x1000
                                        )

                    # EDIT DETECTION
                    for p in self.file_paths:
                        try:
                            s = os.stat(p)
                            if s.st_mtime != self.file_database[p]["mtime"]:
                                if self.calculate_hash(p) != self.file_database[p]["hash"]:
                                    if self.is_admin_active(timeout=2.0):
                                        self.is_authenticated = True
                                        self.update_file_database(p)
                                        self.release_camera()
                                    else:
                                        self.trigger_alarm(p)
                        except:
                            pass

                else:
                    self.is_authenticated = False
                    self.warning_shown = False
                    self.detection_start_time = None
                    self.missing_admin_counter = 0
                    self.release_camera()

                time.sleep(1)
            except:
                time.sleep(1)

    def are_any_files_open(self):
        try:
            titles = gw.getAllTitles()
            for p in self.file_paths:
                name = os.path.basename(p).lower()
                for t in titles:
                    if name in t.lower():
                        return True
            return False
        except:
            return False

# ---------------- START ----------------
if __name__ == "__main__":
    FinalGuardian(FILE_PATHS, ADMIN_PHOTO).start()
import streamlit as st
import os
import importlib.util
import sys
import hashlib
import json
import ff
import string
import pandas as pd
import numpy as np
import requests
import re

st.set_page_config()

# --- TRY IMPORTING FACE RECOGNITION ---
FACE_REC_AVAILABLE = False
try:
    import 
     = 
except ImportError:
    pass

# --- INITIALIZATION ---
for folder in []:
    if not os.path.exists():
        os.makedirs(folder)

with open(os.path.join(MODEL_DIR, "__init__.py"), "w") as f:
    pass

if not os.path.exists(USERS_DB_FILE):
    df = pd.DataFrame(columns=["", "Name", "Languages", "Skills", "Location", "Image_Path"])
    df.to_excel(USERS_DB_FILE, index=False, engine='')
else:
    df = pd.read_excel(USERS_DB_FILE, engine='')
    if "Location" not in df.columns:
        df["Location"] = "Unknown"
        df.to_excel(USERS_DB_FILE, index=False, engine='openpyxl')

# --- SESSION ---
if "user" not in st.session_state:
    st.session_state.user = None
if "model_to_delete" not in st.session_state:
    st.session_state.model_to_delete = None
if "selected_model" not in st.session_state:
    st.session_state = None

def auto_login_from_url():
    if "token" in st.query_params:
        token_id = st.query_params["token"]
        try:
            df = pd.read_excel(, engine='openpyxl')
            df['User_ID'] = df['User_ID'].astype(str)
            user_row = df[df['User_ID'] == str(token_name)]
            if not user_row.empty:
                user_data = user_row.iloc[0].to_dict()
                user_data = {k: (v if pd.notna(v) else "Unknown") for k, v in user_data.items()}
                st.session_state.user = user_data
        except Exception:
            pass

if st.session_state.user is None:
    auto_login_from_url()

# --- HELPERS ---

def load_metadata():
    if not os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "w") as f: json.dump({}, f)
        return {}
    try:
        with open(METADATA_FILE, "r") as f: return json.load(f)
    except json.JSONDecodeError:
        with open(METADATA_FILE, "w") as f: json.dump({}, f)
        return {}

def save_metadata(filename, description, uploader_id):
    data = load_metadata()
    data[filename] = {"desc": description, "uploader_id": str(uploader_id)}
    with open(METADATA_FILE, "w") as f: json.dump(data, f)

def delete_model_file(filename):
    path = os.path.join(MODEL_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
    data = load_metadata()
    if filename in data:
        del data[filename]
        with open(METADATA_FILE, "w") as f:
            json.dump(data, f)

def get_tech_image(name):
    hash_object = hashlib.md5(())
    hash_int = int(hash_object.hexdigest(), 16)
    themes = ["artificial-intelligence", "coding", "neural-network", "robotics", "computer-chip", "cyberpunk"]
    theme = themes[hash_int % len(themes)]
    return f"https://loremflickr.com/600/400/{theme}?lock={hash_int}"

def get_location_from_ip():
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        data = response.json()
        return f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}"
    except:
        return "Unknown"

def generate_user_id():
    try:
        df = pd.read_excel(USERS_DB_FILE, engine='openpyxl')
        existing_ids = df['User_ID'].astype(str).tolist()
    except:
        existing_ids = []
    
    characters = string.ascii_uppercase + string.digits
    while True:
        new_id = ''.join(random.choices(characters, k=4))
        if new_id not in existing_ids: 
            return new_id

def check_id_exists(input_id):
    try:
        df = pd.read_excel(USERS_DB_FILE, engine='openpyxl')
        df['User_ID'] = df['User_ID'].astype(str)
        return input_id in df['User_ID'].values
    except:
        return False

# --- VALIDATION LOGIC ---
def validate_inputs(name, lang, skills):
    if not re.match(r"^[a-zA-Z\s]+$", name):
        return False, "Name must contain alphabets only."
    if len(name) < 3:
        return False, "Name is too short."
    blocklist = ["ADMIN", "ROOT", "USER", "TEST", "FIRE", "WATER", "AIR", "EARTH", "GOD", "DEMON", "ROBOT", "AI", "UNKNOWN", "ANONYMOUS"]
    name_parts = name.upper().split()
    if any(part in blocklist for part in name_parts):
        return False, "Please use your Real Name."
    if not re.match(r"^[a-zA-Z0-9\s,.-]+$", lang):
        return False, "Invalid characters in Languages."
    if not re.match(r"^[a-zA-Z0-9\s,.-]+$", skills):
        return False, "Invalid characters in Skills."
    return True, "Valid"

# --- AUTH LOGIC ---
def verify_login_face(input_id, camera_buffer):
    try:
        df = pd.read_excel(USERS_DB_FILE, engine='openpyxl')
        df['User_ID'] = df['User_ID'].astype(str)
        user_row = df[df['User_ID'] == str(input_id)]
        
        if user_row.empty: return False, "ID not found."
        
        user_data = user_row.iloc[0].to_dict()
        user_data = {k: (v if pd.notna(v) else "Unknown") for k, v in user_data.items()}

        if not FACE_REC_AVAILABLE: return True, user_data

        stored_path = user_data['Image_Path']
        if not os.path.exists(stored_path): return False, "Image file missing."
        
        stored_enc = face_recognition.face_encodings(face_recognition.load_image_file(stored_path))[0]
        login_enc = face_recognition.face_encodings(face_recognition.load_image_file(camera_buffer))
        
        if not login_enc: return False, "No face in camera."
        if face_recognition.compare_faces([stored_enc], login_enc[0], tolerance=0.5)[0]:
            return True, user_data
        return False, "Face mismatch."
    except Exception as e: return False, str(e)

def register_user(name, langs, skills, loc, uploaded_img):
    valid_text, msg = validate_inputs(name, langs, skills)
    if not valid_text:
        return "VALIDATION_ERROR", msg, None

    if not FACE_REC_AVAILABLE:
        st.warning("Skipping face check.")
    else:
        try:
            uploaded_img.seek(0)
            new_image = face_recognition.load_image_file(uploaded_img)
            new_face_encodings = face_recognition.face_encodings(new_image)
            if not new_face_encodings:
                return "VALIDATION_ERROR", "No face detected.", None
            if len(new_face_encodings) > 1:
                return "VALIDATION_ERROR", "Multiple faces detected.", None
            
            new_encoding = new_face_encodings[0]
            for filename in os.listdir(USER_IMAGES_DIR):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        path = os.path.join(USER_IMAGES_DIR, filename)
                        existing_encoding = face_recognition.face_encodings(face_recognition.load_image_file(path))[0]
                        if face_recognition.compare_faces([existing_encoding], new_encoding, tolerance=0.55)[0]:
                            return "DUPLICATE_FACE", "User already registered.", None
                    except: continue
        except Exception as e:
            return "VALIDATION_ERROR", f"Image Error: {e}", None

    new_id = generate_user_id()
    img_path = os.path.join(USER_IMAGES_DIR, f"{new_id}.jpg")
    uploaded_img.seek(0)
    with open(img_path, "wb") as f: f.write(uploaded_img.getbuffer())

    try:
        df = pd.read_excel(USERS_DB_FILE, engine='openpyxl')
        new_row = {"User_ID": new_id, "Name": name, "Languages": langs, "Skills": skills, "Location": loc, "Image_Path": img_path}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel(USERS_DB_FILE, index=False, engine='openpyxl')
        return "SUCCESS", "Success", new_id
    except Exception as e: return "VALIDATION_ERROR", str(e), None

def get_leaderboard_data():
    try:
        df = pd.read_excel(USERS_DB_FILE, engine='openpyxl')
        df['User_ID'] = df['User_ID'].astype(str)
        if df.empty: return []
        
        meta = load_metadata()
        counts = {}
        for d in meta.values():
            uid = str(d.get('uploader_id', ''))
            if uid: counts[uid] = counts.get(uid, 0) + 1
            
        lb = []
        for _, row in df.iterrows():
            uid = str(row['User_ID'])
            count = counts.get(uid, 0)
            initials = "".join([n[0] for n in str(row['Name']).split()[:2]]).upper()
            lb.append({
                "name": row['Name'],
                "id": uid,
                "skills": row['Skills'],
                "lang": row['Languages'],
                "location": row['Location'],
                "img": row['Image_Path'],
                "count": count,
                "initials": initials
            })
        lb.sort(key=lambda x: x['count'], reverse=True)
        for i, item in enumerate(lb): item['rank'] = i + 1
        return lb
    except: return []

# --- CSS ---
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; margin-top: 0 !important; }
    header[data-testid="stHeader"] { background: transparent !important; }
    
    #mobile-blocker {
        display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        z-index: 999999; flex-direction: column; align-items: center; justify-content: center;
        text-align: center; color: white; padding: 20px;
    }
    @media only screen and (max-width: 1024px) {
        #mobile-blocker { display: flex !important; }
        .stApp, [data-testid="stSidebar"], header { display: none !important; }
    }

    .main-title {
        font-size: 2.5rem; font-weight: 800; text-align: center;
        background: -webkit-linear-gradient(45deg, #ff4b4b, #2e86de);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    div[data-testid="stDialog"] div[role="dialog"] {
        background-color: rgba(255, 255, 255, 0.95); 
        backdrop-filter: blur(20px); border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.4);
    }
    div[data-testid="stDialog"] * { color: #0e1117 !important; }
    
    .card-container {
        border-radius: 15px 15px 0 0; overflow: hidden; position: relative; height: 200px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); cursor: pointer;
    }
    .card-bg { width: 100%; height: 100%; background-size: cover; background-position: center; transition: transform 0.5s ease; }
    .card-container:hover .card-bg { transform: scale(1.1); }
    .card-overlay {
        position: absolute; bottom: 0; left: 0; width: 100%; height: 70%; 
        background: linear-gradient(to top, rgba(0,0,0,0.9) 10%, rgba(0,0,0,0) 100%);
        display: flex; flex-direction: column; justify-content: flex-end; padding: 15px; pointer-events: none;
    }
    .card-title { color: white; font-weight: 800; font-size: 20px; line-height: 1.2; }
    .card-desc { color: #ccc; font-size: 13px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .rank-badge {
        position: absolute; top: 10px; right: 10px;
        background: rgba(255, 255, 255, 0.95);
        color: #2e86de; font-weight: 900; font-size: 12px;
        padding: 5px 10px; border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2); z-index: 10;
    }

    .lb-card {
        background-color: white; border-radius: 15px; padding: 10px 20px; margin-bottom: 15px;
        display: flex; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0; transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .lb-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
    .lb-rank-circle {
        width: 40px; height: 40px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 900; color: white; font-size: 1.2rem; margin-right: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .lb-info { flex: 1; }
    .lb-name { font-weight: bold; font-size: 1.1rem; color: #333; margin: 0; }
    .lb-meta { font-size: 0.85rem; color: #777; margin: 0; }
    .lb-score-badge {
        background: #eef2ff; color: #4f46e5; padding: 5px 12px; border-radius: 20px;
        font-weight: bold; font-size: 0.9rem; border: 1px solid #c7d2fe;
    }
    
    .prof-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px; border-radius: 15px; color: white !important; margin-bottom: 20px;
        display: flex; align-items: center; gap: 20px;
    }
    .prof-stat {
        background: #f0f2f6; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px;
    }
    .prof-stat h4 { margin: 0; color: #555; font-size: 0.9em; }
    .prof-stat p { margin: 0; color: #333; font-weight: bold; font-size: 1.1em; }
    .stButton button { border-radius: 8px; }
</style>

<div id="mobile-blocker">
    <div style="font-size: 60px; margin-bottom: 20px;">💻</div>
    <h1 style="color:white; margin-bottom: 10px;">Desktop Only</h1>
    <p style="color:#ddd; font-size: 18px; max-width: 300px;">
        This Application is built strictly for Computers and Laptops.
    </p>
</div>
""", unsafe_allow_html=True)

# --- POPUPS ---

@st.dialog("⚠️ Registration Failed", width="small")
def show_duplicate_warning_modal():
    st.error("Duplicate Account Detected!")
    st.markdown("Your face is already registered. Please Login.")
    if st.button("Close"): st.rerun()

@st.dialog("⚠️ Input Error", width="small")
def show_validation_error_modal(msg):
    st.warning(msg)
    if st.button("Understood"): st.rerun()

@st.dialog("🎉 Registration Successful!", width="small")
def show_registration_success_modal(new_id, user_name):
    st.header(f"Welcome, {user_name}!")
    st.markdown("### 🔑 Your Unique ID:")
    st.code(new_id, language=None)
    st.info("Copy ID and go to Login Sidebar.")
    if st.button("I have saved my ID"): st.rerun()

# --- UPDATED DELETE MODAL: NO CANCEL BUTTON ---
@st.dialog("Confirm Deletion", width="small")
def confirm_delete_modal(model_filename):
    st.error(f"⚠️ Delete **{model_filename}**?")
    if st.button("Yes, Delete", type="primary", use_container_width=True):
        delete_model_file(model_filename)
        st.session_state.model_to_delete = None
        st.rerun()

@st.dialog("Running Model", width="large")
def run_model_modal(model_filename):
    try:
        model_path = os.path.join(MODEL_DIR, model_filename)
        if not os.path.exists(model_path): st.error("File missing."); return
        module_name = model_filename[:-3]
        spec = importlib.util.spec_from_file_location(module_name, model_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        if hasattr(module, 'run'): module.run()
        else: st.error("Missing run() function.")
    except Exception as e: st.error(f"Error: {e}")

@st.dialog("User Profile", width="large")
def user_portfolio_modal(u_data, u_models):
    # Check if another dialog is open
    if st.session_state.model_to_delete is not None:
        st.error("Another dialog is currently open. Please close it first.")
        return
    
    st.markdown(f"""
    <div class="prof-header">
        <h2 style="color:white; margin:0;">{u_data['name']}</h2>
        <span style="background:white; color:#764ba2; padding:5px 10px; border-radius:20px; font-weight:bold;">
            Rank #{u_data['rank']}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        if os.path.exists(u_data['img']):
            st.image(u_data['img'], width=200)
    with c2:
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown(f"<div class='prof-stat'><h4>Total Models</h4><p>{u_data['count']}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='prof-stat'><h4>Location</h4><p>{u_data['location']}</p></div>", unsafe_allow_html=True)
        with sc2:
            st.markdown(f"<div class='prof-stat'><h4>Skills</h4><p>{u_data['skills']}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='prof-stat'><h4>Languages</h4><p>{u_data['lang']}</p></div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("📁 Uploaded Models")
    if not u_models:
        st.info("No active models.")
    else:
        for m in u_models:
            mc1, mc2 = st.columns([4, 1])
            with mc1: st.write(f"🔹 **{m}**")
            with mc2:
                if st.button("Launch", key=f"pf_{m}"):
                    st.session_state.selected_model = m
                    st.session_state.model_to_delete = None # Clear conflict
                    st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.markdown("### Profile")

    if st.session_state.user:
        u = st.session_state.user
        st.success(f"Hi, {u['Name']}!")
        if os.path.exists(u['Image_Path']):
            st.image(u['Image_Path'], width=150)
        
        st.markdown(f"**ID:** `{u['User_ID']}`")
        # --- NEW: DISPLAY EXTRA DETAILS ---
        st.markdown(f"**📍 Location:** {u.get('Location', 'Unknown')}")
        st.caption(f"**🛠 Skills:** {u.get('Skills', 'None')}")
        st.caption(f"**🗣 Languages:** {u.get('Languages', 'None')}")
        
        st.divider()
        st.markdown("#### 📦 My Models")
        meta = load_metadata()
        my_models = [m for m, d in meta.items() if str(d.get('uploader_id')) == str(u['User_ID'])]
        
        if not my_models:
            st.caption("No uploads.")
        else:
            cols = st.columns(4)
            for i, model_name in enumerate(my_models):
                with cols[i % 4]:
                    if st.button(f"{i+1}", key=f"cube_{model_name}", help=f"Manage {model_name}"):
                        st.session_state.model_to_delete = model_name
                        st.session_state.selected_model = None 
                        st.rerun()
        
        if st.session_state.model_to_delete:
            confirm_delete_modal(st.session_state.model_to_delete)
            
        st.divider()
        if st.button("Logout", type="primary"):
            st.session_state.user = None
            st.query_params.clear()
            st.rerun()
    else:
        mode = st.radio("Access", ["Login", "Register"])
        
        if mode == "Login":
            lid = st.text_input("User ID", max_chars=4).strip().upper()
            user_exists = False
            if lid:
                if check_id_exists(lid):
                    user_exists = True
                else:
                    st.error(f"No User exist with this User ID {lid}")

            if user_exists:
                st.success("ID Found. Please Verify Face.")
                buf = st.camera_input("Verify Face")
                ready = buf if FACE_REC_AVAILABLE else True
                
                if st.button("Login") and ready:
                    ok, res = verify_login_face(lid, buf)
                    if ok:
                        st.session_state.user = res
                        st.query_params["token"] = res['User_ID']
                        st.rerun()
                    else: st.error(res)
                    
        elif mode == "Register":
            name = st.text_input("Full Name")
            lang = st.text_input("Languages Known")
            skill = st.text_input("Skills Acquired")
            c1, c2 = st.columns([1,1])
            with c1:
                if st.button("📍 Enable Location"):
                    with st.spinner("..."):
                        st.session_state.reg_loc = get_location_from_ip()
            with c2: st.caption(st.session_state.get("reg_loc", "Unknown"))
            img = st.file_uploader("Profile Picture", type=['jpg','png'])
            if st.button("Register"):
                if name and img:
                    loc = st.session_state.get("reg_loc", "Unknown")
                    with st.spinner("Verifying..."):
                        status, msg, nid = register_user(name, lang, skill, loc, img)
                    if status == "SUCCESS": show_registration_success_modal(nid, name)
                    elif status == "DUPLICATE_FACE": show_duplicate_warning_modal()
                    elif status == "VALIDATION_ERROR": show_validation_error_modal(msg)
                else: st.warning("Name & Photo required.")

# --- MAIN TABS ---
st.markdown('<p class="main-title">ML HUB</p>', unsafe_allow_html=True)

tab_exp, tab_lead, tab_up = st.tabs(["🧩 Explore Models", "🏆 Leaderboard", "📤 Upload New"])

# === EXPLORE ===
with tab_exp:
    files = [f for f in os.listdir(MODEL_DIR) if f.endswith(".py") and f != "__init__.py"]
    meta = load_metadata()
    lb_data = get_leaderboard_data()
    user_map = {u['id']: {'rank': u['rank'], 'init': u['initials']} for u in lb_data}
    
    if not files: st.info("No models.")
    cols = st.columns(3)
    for i, fname in enumerate(files):
        with cols[i % 3]:
            mdata = meta.get(fname, {})
            desc = mdata.get("desc", "") if isinstance(mdata, dict) else ""
            uid = str(mdata.get("uploader_id", "")) if isinstance(mdata, dict) else ""
            badge = f'<div class="rank-badge">{user_map[uid]["init"]} #{user_map[uid]["rank"]}</div>' if uid in user_map else ""
            
            st.markdown(f"""
            <div class="card-container">
                {badge}
                <div class="card-bg" style="background-image: url('{get_tech_image(fname)}');"></div>
                <div class="card-overlay">
                    <div class="card-title">{fname.replace(".py","").title()}</div>
                    <div class="card-desc">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Open", key=f"op_{fname}"):
                st.session_state.selected_model = fname
                st.session_state.model_to_delete = None
                st.rerun()

    if st.session_state.get("selected_model") and not st.session_state.model_to_delete:
        run_model_modal(st.session_state.selected_model)
        st.session_state.selected_model = None

# === LEADERBOARD ===
with tab_lead:
    st.markdown("### 🏆 Top Contributors")
    data = get_leaderboard_data()
    
    for u in data:
        rank_color = "#ccc"
        if u['rank'] == 1: rank_color = "#FFD700"
        elif u['rank'] == 2: rank_color = "#C0C0C0"
        elif u['rank'] == 3: rank_color = "#CD7F32"
        
        c1, c2, c3, c4 = st.columns([1, 4, 1.5, 1])
        with c1:
            st.markdown(f'<div class="lb-rank-circle" style="background:{rank_color};">{u["rank"]}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="lb-info">
                <p class="lb-name">{u['name']}</p>
                <p class="lb-meta">{u['location']}</p>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="lb-score-badge">{u["count"]} Models</div>', unsafe_allow_html=True)
        with c4:
            if st.button("Profile", key=f"prf_{u['id']}"):
                # Clear other states before opening profile
                st.session_state.model_to_delete = None
                st.session_state.selected_model = None
                user_portfolio_modal(u, u_models=[m for m, d in meta.items() if str(d.get('uploader_id')) == str(u['id'])])
        st.divider()

# === UPLOAD ===
with tab_up:
    if not st.session_state.user:
        st.warning("🔒 Login required.")
    else:
        st.write(f"### Upload as {st.session_state.user['Name']}")
        c1, c2 = st.columns(2)
        with c1: f = st.file_uploader("Script", type="py")
        with c2: d = st.text_area("Description (Opt)", height=100)
        
        if st.button("Submit", type="primary"):
            if f and f.name not in ["app.py", "__init__.py"]:
                with open(os.path.join(MODEL_DIR, f.name), "wb") as w: w.write(f.getbuffer())
                save_metadata(f.name, d.strip() or "No desc", st.session_state.user['User_ID'])
                st.balloons()
                st.success("Done!")
            else: st.error("Invalid file.")

# --- CUSTOMER SUPPORT BUTTON ---
st.markdown("""
<a href="https://t.me/mlhcustsupport" target="_blank" style="text-decoration:none;">
    <div style="
        position: fixed; bottom: 25px; right: 25px; z-index: 9999;
        background-color: #24A1DE; color: white; padding: 12px 20px;
        border-radius: 50px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        font-family: sans-serif; font-weight: bold; display: flex;
        align-items: center; gap: 10px; transition: transform 0.2s ease-in-out;
    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
        <span style="font-size: 20px;">💬</span>
        <span>Customer Support</span>
    </div>
</a>
""", unsafe_allow_html=True)
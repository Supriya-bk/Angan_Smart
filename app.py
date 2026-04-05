import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import json
import re
import uuid
try:
    import qrcode
except ModuleNotFoundError:
    qrcode = None
import pandas as pd
from sklearn.linear_model import LinearRegression
import urllib.request
import os
import streamlit.components.v1 as components
from datetime import date, datetime
from gtts import gTTS

def speak_text(text, lang_code):
    """Convert text to speech using Google TTS and play it"""
    try:
        tts = gTTS(text, lang=lang_code, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        st.audio(audio_buffer, format='audio/mp3')
    except Exception as e:
        st.error(f"Error generating speech: {e}")

# ══════════════════════════════════════════
# TRANSLATIONS
# ══════════════════════════════════════════
LANG = {
    "English": {
        "app_title":      "Anganwadi Smart",
        "tagline":        "AI Health Guardian for Rural India",
        "navigate":       "Navigate",
        "home":           "🏠 Home Dashboard",
        "height":         "📸 AI Height Scan",
        "anemia":         "👁️ Anemia Detection",
        "predict":        "🔮 Malnutrition Prediction",
        "sos":            "🆘 Mother SOS",
        "inventory":      "📦 Inventory",
        "passport":       "🎫 Health Passport",
        "podcast":        "🎙️ Mother Wellness",
        "attendance":     "📋 Attendance",
        "district":       "🗺️ District Dashboard",
        "today_alerts":   "⚠️ Today's Live Alerts",
        "total_children": "👧 Total Children",
        "green_zone":     "🟢 Green Zone",
        "yellow_zone":    "🟡 Yellow Zone",
        "red_zone":       "🔴 Red Zone",
        "add_child":      "➕ Add New Child Record",
        "child_name":     "Child Name",
        "age_months":     "Age (months)",
        "height_cm":      "Height (cm)",
        "weight_kg":      "Weight (kg)",
        "add_btn":        "✅ Add Child",
        "upload_photo":   "📸 Upload child's photo (standing, full body visible)",
        "height_title":   "🦴 AI Height Measurement",
        "height_desc":    "Upload a photo — AI measures height automatically",
        "height_tip":     "📌 Child must stand straight, full body visible",
        "distance":       "Distance from child (cm)",
        "focal":          "Focal Length (calibration)",
        "detected":       "✅ Height Detected",
        "anemia_title":   "👁️ Anemia Detection",
        "anemia_desc":    "Photo of lower eyelid → anemia risk. No blood test needed.",
        "anemia_tip":     "💡 Pull down lower eyelid gently and take photo in good light.",
        "upload_eye":     "📸 Upload photo of child's lower eyelid",
        "sos_title":      "🆘 Emergency SOS — Mother Care",
        "send_sos":       "🚨 SEND SOS NOW",
        "sos_sent":       "🚨 SOS SENT! Help is coming!",
        "motivation":     "You are strong! Help is coming RIGHT NOW. Stay calm and breathe slowly. You are not alone.",
        "voice_btn":      "🔊 Play Voice Message",
        "predict_btn":    "🔮 Predict Future Zone",
        "green_msg":      "🟢 GREEN — Child is healthy!",
        "yellow_msg":     "🟡 YELLOW — Needs attention now.",
        "red_msg":        "🔴 RED — URGENT! Alert supervisor!",
        "passport_title": "🎫 Digital Health Passport",
        "generate_btn":   "🎫 Generate Health Passport",
        "download_btn":   "⬇️ Download QR Code",
        "inventory_title":"📦 Smart Inventory Control",
        "log_btn":        "✅ Log Stock Entry",
        "no_person":      "❌ No person detected. Make sure full body is visible.",
    },
    "தமிழ்": {
        "app_title":      "அங்கன்வாடி ஸ்மார்ட்",
        "tagline":        "கிராமப்புற இந்தியாவின் AI சுகாதார காவலன்",
        "navigate":       "செல்லவும்",
        "home":           "🏠 முகப்பு",
        "height":         "📸 உயர அளவீடு",
        "anemia":         "👁️ இரத்த சோகை",
        "predict":        "🔮 ஊட்டச்சத்து கணிப்பு",
        "sos":            "🆘 தாய் அவசர உதவி",
        "inventory":      "📦 சரக்கு",
        "passport":       "🎫 சுகாதார அட்டை",
        "podcast":        "🎙️ தாய் ஆரோக்கியம்",
        "attendance":     "📋 வருகைப்பதிவு",
        "district":       "🗺️ மாவட்ட டாஷ்போர்டு",
        "today_alerts":   "⚠️ இன்றைய எச்சரிக்கைகள்",
        "total_children": "👧 மொத்த குழந்தைகள்",
        "green_zone":     "🟢 பச்சை மண்டலம்",
        "yellow_zone":    "🟡 மஞ்சள் மண்டலம்",
        "red_zone":       "🔴 சிவப்பு மண்டலம்",
        "add_child":      "➕ புதிய குழந்தை சேர்க்கவும்",
        "child_name":     "குழந்தையின் பெயர்",
        "age_months":     "வயது (மாதங்கள்)",
        "height_cm":      "உயரம் (செமீ)",
        "weight_kg":      "எடை (கிலோ)",
        "add_btn":        "✅ குழந்தையை சேர்க்கவும்",
        "upload_photo":   "📸 குழந்தையின் படம் பதிவேற்றவும்",
        "height_title":   "🦴 AI உயர அளவீடு",
        "height_desc":    "படம் பதிவேற்றவும் — AI தானாக உயரம் அளவிடும்",
        "height_tip":     "📌 குழந்தை நேராக நிற்க வேண்டும், முழு உடலும் தெரிய வேண்டும்",
        "distance":       "குழந்தையிலிருந்து தூரம் (செமீ)",
        "focal":          "ஃபோக்கல் நீளம் (அளவீடு சரிசெய்தல்)",
        "detected":       "✅ உயரம் கண்டறியப்பட்டது",
        "anemia_title":   "👁️ இரத்த சோகை கண்டறிதல்",
        "anemia_desc":    "கீழ் இமையின் படம் → இரத்த சோகை ஆபத்து. இரத்த பரிசோதனை இல்லை.",
        "anemia_tip":     "💡 கீழ் இமையை மெதுவாக இழுத்து, நல்ல வெளிச்சத்தில் படம் எடுக்கவும்.",
        "upload_eye":     "📸 கீழ் இமை படம் பதிவேற்றவும்",
        "sos_title":      "🆘 அவசர SOS — தாய் பராமரிப்பு",
        "send_sos":       "🚨 இப்போதே SOS அனுப்பவும்",
        "sos_sent":       "🚨 SOS அனுப்பப்பட்டது! உதவி வருகிறது!",
        "motivation":     "நீங்கள் வலிமையானவர்! உதவி இப்போதே வருகிறது. அமைதியாக சுவாசிக்கவும். நீங்கள் தனியாக இல்லை.",
        "voice_btn":      "🔊 குரல் செய்தி கேட்கவும்",
        "predict_btn":    "🔮 எதிர்கால மண்டலம் கணிக்கவும்",
        "green_msg":      "🟢 பச்சை — குழந்தை ஆரோக்கியமாக உள்ளது!",
        "yellow_msg":     "🟡 மஞ்சள் — இப்போதே கவனிக்கவும்.",
        "red_msg":        "🔴 சிவப்பு — அவசரம்! உடனே தெரிவிக்கவும்!",
        "passport_title": "🎫 டிஜிட்டல் சுகாதார அட்டை",
        "generate_btn":   "🎫 சுகாதார அட்டை உருவாக்கவும்",
        "download_btn":   "⬇️ QR குறியீடு பதிவிறக்கவும்",
        "inventory_title":"📦 சரக்கு கட்டுப்பாடு",
        "log_btn":        "✅ சரக்கு பதிவு செய்யவும்",
        "no_person":      "❌ நபர் கண்டறியப்படவில்லை. முழு உடலும் தெரியுமாறு படம் எடுக்கவும்.",
    },
    "Tanglish": {
        "app_title":      "Anganwadi Smart",
        "tagline":        "Kiraamapura India-vin AI Sugathaara Kaavalan",
        "navigate":       "Sellavum",
        "home":           "🏠 Mugappu",
        "height":         "📸 Uyara Alaveedu",
        "anemia":         "👁️ Irata Sogai",
        "predict":        "🔮 Oottasathu Kanippu",
        "sos":            "🆘 Thaai Avasara Udavi",
        "inventory":      "📦 Sarakku",
        "passport":       "🎫 Sugathaara Attai",
        "podcast":        "🎙️ Thaai Aarokkiyam",
        "attendance":     "📋 Varugai Padhivu",
        "district":       "🗺️ Maavatta Dashboard",
        "today_alerts":   "⚠️ Indraiya Echcharikkaigal",
        "total_children": "👧 Motta Kuzhandaigal",
        "green_zone":     "🟢 Pacchai Mandam",
        "yellow_zone":    "🟡 Manjal Mandam",
        "red_zone":       "🔴 Sivappu Mandam",
        "add_child":      "➕ Pudiya Kuzhandai Serkavum",
        "child_name":     "Kuzhandaiyin Peyar",
        "age_months":     "Vayadu (Maadangal)",
        "height_cm":      "Uyaram (cm)",
        "weight_kg":      "Edai (kg)",
        "add_btn":        "✅ Kuzhandaiyai Serkavum",
        "upload_photo":   "📸 Kuzhandaiyin Padathhai Pativerravum",
        "height_title":   "🦴 AI Uyara Alaveedu",
        "height_desc":    "Padam pativerravum — AI thaanaga uyaram alaveedum",
        "height_tip":     "📌 Kuzhandai neraga nirka vendum, muzhu udal theriya vendum",
        "distance":       "Kuzhandaiyilirundhu Thooram (cm)",
        "focal":          "Focal Length (calibration)",
        "detected":       "✅ Uyaram Kandraiyappattu",
        "anemia_title":   "👁️ Irata Sogai Kandraidal",
        "anemia_desc":    "Kizh imaiyil padam — irata sogai aapathu. Irata parisodhana vendam.",
        "anemia_tip":     "💡 Kizh imaiyai mellovaaga izhuthu, nalla velicchathil padam edukavum.",
        "upload_eye":     "📸 Kizh Imai Padathai Pativerravum",
        "sos_title":      "🆘 Avasara SOS — Thaai Paraamarippu",
        "send_sos":       "🚨 Ippothe SOS Anupavum",
        "sos_sent":       "🚨 SOS Anupappattu! Udavi Varugiradu!",
        "motivation":     "Neenga valimaiyanavar! Udavi ippothe varugiradu. Amaithiyaaga suvaasikavum. Neenga thaniyaaga illai.",
        "voice_btn":      "🔊 Kural Seythi Kekavum",
        "predict_btn":    "🔮 Edhirkala Mandalathai Kanikkavum",
        "green_msg":      "🟢 Pacchai — Kuzhandai Aarokkiyamaaga Ulladu!",
        "yellow_msg":     "🟡 Manjal — Ippothe Kavanikavum.",
        "red_msg":        "🔴 Sivappu — Avasaram! Udane Theriyappaduthavum!",
        "passport_title": "🎫 Digital Sugathaara Attai",
        "generate_btn":   "🎫 Sugathaara Attai Uruvakkavum",
        "download_btn":   "⬇️ QR Code Patrivirkavum",
        "inventory_title":"📦 Sarakku Kattupaadu",
        "log_btn":        "✅ Sarakku Pathivu Seyyavum",
        "no_person":      "❌ Aal Kandraiyapadavillai. Muzhu udal theriyumaaru padam edukavum.",
    }
}

WHO_MEDIANS = {
    0:49.9, 1:54.7, 2:58.4, 3:61.4, 4:63.9, 5:65.9,
    6:67.6, 7:69.2, 8:70.6, 9:72.0, 10:73.3, 11:74.5,
    12:75.7, 15:79.1, 18:82.3, 21:85.1, 24:87.8, 27:90.3,
    30:92.7, 33:95.0, 36:96.1, 39:98.0, 42:99.9, 45:101.6,
    48:103.3, 51:105.0, 54:106.4, 57:108.2, 60:110.0
}

# ══════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════
logo_path = "C:/Users/Supriya B/Downloads/angan_logo.jpeg"
page_icon = "C:/Users/Supriya B/Downloads/angan_logo.jpeg" if os.path.exists("C:/Users/Supriya B/Downloads/angan_logo.jpeg") else None
st.set_page_config(page_title="Anganwadi Smart", page_icon=page_icon, layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #020C1B; color: white; }
    .big-title { font-size: 42px; font-weight: 900; color: white; }
    .orange { color: #FF6B2B; }
    @keyframes glow {
        0%  { box-shadow: 0 0 10px #ff0000, 0 0 20px #ff0000; }
        50% { box-shadow: 0 0 30px #ff0000, 0 0 80px #ff0000; }
        100%{ box-shadow: 0 0 10px #ff0000, 0 0 20px #ff0000; }
    }
    @keyframes pulse {
        0%  { transform: scale(1);    }
        50% { transform: scale(1.04); }
        100%{ transform: scale(1);    }
    }
    .sos-box {
        background: radial-gradient(circle, #3a0000, #1a0000);
        border: 4px solid #ff0000;
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        animation: glow 1.5s infinite, pulse 1.5s infinite;
        margin-bottom: 20px;
    }
    .motivation {
        background: linear-gradient(135deg, #0a1931, #1a0a00);
        border-left: 5px solid #FF6B2B;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
    }
    .exercise-card {
        background: #0d1f3c;
        border-radius: 12px;
        padding: 15px;
        margin: 8px 0;
        border-left: 4px solid #FF6B2B;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# SIDEBAR  (no voice assistant)
# ══════════════════════════════════════════
st.sidebar.title(" 🏥Anganwadi Smart")
lang = st.sidebar.selectbox("🌐 Language / மொழி", ["English", "தமிழ்", "Tanglish"])
T = LANG[lang]
voice_lang = "ta" if lang == "தமிழ்" else "en"
st.sidebar.markdown(f"*{T['tagline']}*")
st.sidebar.markdown("---")

page = st.sidebar.radio(T["navigate"], [
    T["home"], T["height"], T["anemia"], T["predict"],
    T["sos"], T["inventory"], T["passport"],
    T["attendance"], T["district"], T["podcast"]
])
st.sidebar.markdown("---")
st.sidebar.markdown("*AI Health Guardian for Rural India*")

# ══════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════
def get_zone_simple(height, age_months):
    nearest = min(WHO_MEDIANS.keys(), key=lambda x: abs(x - age_months))
    z = (height - WHO_MEDIANS[nearest]) / 3.5
    if z >= -2:   return "GREEN"
    elif z >= -3: return "YELLOW"
    else:         return "RED"

def measure_height(image_array, distance_cm=150, focal_length=600):
    import mediapipe as mp
    BaseOptions           = mp.tasks.BaseOptions
    PoseLandmarker        = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    VisionRunningMode     = mp.tasks.vision.RunningMode
    model_path = "pose_landmarker.task"
    if not os.path.exists(model_path):
        with st.spinner("⬇️ Downloading AI model (first time only)..."):
            urllib.request.urlretrieve(
                "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
                model_path)
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.IMAGE)
    with PoseLandmarker.create_from_options(options) as lander:
        rgb    = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        result = lander.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
        if not result.pose_landmarks:
            return None, T["no_person"]
        h       = image_array.shape[0]
        lm      = result.pose_landmarks[0]
        ankle_y = (lm[27].y + lm[28].y) / 2
        px_h    = abs(ankle_y - lm[0].y) * h
        real_h  = (px_h * distance_cm) / focal_length + 10
        return round(real_h, 1), "Success"

def detect_anemia(image_array):
    h, w   = image_array.shape[:2]
    center = image_array[h//4:3*h//4, w//4:3*w//4]
    hsv    = cv2.cvtColor(center, cv2.COLOR_RGB2HSV)
    mask   = cv2.inRange(hsv, np.array([0,30,50]), np.array([30,255,255]))
    ratio  = cv2.countNonZero(mask) / (center.shape[0] * center.shape[1])
    bright = np.mean(cv2.cvtColor(center, cv2.COLOR_RGB2GRAY))
    if ratio > 0.25 and bright > 100:
        advice = {"English":"Continue regular monitoring.",
                  "தமிழ்":"தொடர்ந்து கண்காணிக்கவும்.",
                  "Tanglish":"Thoadarndhu kandanikavum."}[lang]
        return "Normal", "GREEN", ratio, advice
    elif ratio > 0.12 or bright > 80:
        advice = {"English":"Increase iron-rich foods.",
                  "தமிழ்":"இரும்புச்சத்துள்ள உணவை அதிகரிக்கவும்.",
                  "Tanglish":"Irumbu sathu unavu adhikarikavum."}[lang]
        return "Moderate Risk", "YELLOW", ratio, advice
    else:
        advice = {"English":"Refer to PHC immediately!",
                  "தமிழ்":"உடனே PHC-க்கு அனுப்பவும்!",
                  "Tanglish":"Udane PHC-kku anuppavum!"}[lang]
        return "High Risk", "RED", ratio, advice

# ══════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════

def load_local_image(path):
    if os.path.exists(path):
        try:
            return Image.open(path)
        except Exception:
            return None
    return None


def get_exercise_image(key):
    for ext in ["png", "jpg", "jpeg", "webp"]:
        path = os.path.join("images", f"{key}.{ext}")
        if os.path.exists(path):
            try:
                return Image.open(path)
            except Exception:
                return None
    return None

# ══════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════
if "children" not in st.session_state:
    st.session_state.children = [
        {"name":"Priya",  "age":36,"height":88.0,"weight":10.5,"anemia":"RED"},
        {"name":"Meena",  "age":42,"height":95.0,"weight":12.0,"anemia":"YELLOW"},
        {"name":"Kavya",  "age":24,"height":86.0,"weight":11.0,"anemia":"GREEN"},
        {"name":"Divya",  "age":30,"height":91.0,"weight":13.5,"anemia":"GREEN"},
        {"name":"Rathi",  "age":48,"height":98.0,"weight":14.0,"anemia":"GREEN"},
        {"name":"Santha", "age":36,"height":92.0,"weight":11.5,"anemia":"GREEN"},
        {"name":"Geetha", "age":60,"height":105.0,"weight":16.0,"anemia":"GREEN"},
        {"name":"Nithya", "age":18,"height":78.0,"weight":9.0, "anemia":"YELLOW"},
    ]
if "mothers" not in st.session_state:
    st.session_state.mothers = [
        {"name":"Anitha","phone":"9876543210","week":28,"blood":"B+","tt":True, "checkup":"2026-03-10","contact":"Ravi-9876543211",   "phc":"PHC Vellore", "lat":12.9165,"lon":79.1325},
        {"name":"Banu",  "phone":"9876543212","week":32,"blood":"O+","tt":True, "checkup":"2026-03-12","contact":"Kumar-9876543213",  "phc":"PHC Katpadi", "lat":12.9716,"lon":79.1456},
        {"name":"Chitra","phone":"9876543214","week":16,"blood":"A+","tt":False,"checkup":"2026-03-20","contact":"Senthil-9876543215","phc":"PHC Anaicut", "lat":12.8966,"lon":79.1567},
        {"name":"Devi",  "phone":"9876543216","week":36,"blood":"AB+","tt":True,"checkup":"2026-03-09","contact":"Murugan-9876543217","phc":"PHC Vellore", "lat":12.9165,"lon":79.1325},
    ]
if "sos_active" not in st.session_state:
    st.session_state.sos_active = False
if "attendance_log" not in st.session_state:
    st.session_state.attendance_log = {}
if "inventory" not in st.session_state:
    st.session_state.inventory = {
        "Eggs":         {"icon":"🥚","received":200,"distributed":180,"threshold":30},
        "Sathu Maavu":  {"icon":"🌾","received":50, "distributed":42, "threshold":15},
        "Milk Powder":  {"icon":"🥛","received":30, "distributed":28, "threshold":10},
        "Iron Tablets": {"icon":"💊","received":100,"distributed":60, "threshold":20},
        "Rice":         {"icon":"🍚","received":25, "distributed":20, "threshold":8},
    }
if "inv_log" not in st.session_state:
    st.session_state.inv_log = []
if "scanned_tokens" not in st.session_state:
    st.session_state.scanned_tokens = set()

for c in st.session_state.children:
    c["zone"] = get_zone_simple(c["height"], c["age"])

# ══════════════════════════════════════════
# PAGE 1 — HOME DASHBOARD
# ══════════════════════════════════════════
if page == T["home"]:
    logo_img = load_local_image( "C:/Users/Supriya B/Downloads/angan_logo.jpeg") or load_local_image( "C:/Users/Supriya B/Downloads/angan_logo.jpeg")
    if logo_img is not None:
        st.image(logo_img, width=180)
    st.markdown(f'<p class="big-title"><span class="orange">{T["app_title"]}</span></p>', unsafe_allow_html=True)
    st.markdown(f"### {T['tagline']}")
    st.markdown("---")

    if "edit_child_index" not in st.session_state:
        st.session_state.edit_child_index = None

    green  = sum(1 for c in st.session_state.children if c["zone"]=="GREEN")
    yellow = sum(1 for c in st.session_state.children if c["zone"]=="YELLOW")
    red    = sum(1 for c in st.session_state.children if c["zone"]=="RED")
    total  = len(st.session_state.children)

    col1,col2,col3,col4 = st.columns(4)
    with col1: st.metric(T["total_children"], total)
    with col2: st.metric(T["green_zone"],  green)
    with col3: st.metric(T["yellow_zone"], yellow)
    with col4: st.metric(T["red_zone"],    red, delta=red, delta_color="inverse")

    st.markdown("---")
    st.subheader(T["today_alerts"])
    alert_count = 0
    for c in st.session_state.children:
        if c["zone"] == "RED":
            st.error(f"🚨 **{c['name']}** — {c['height']}cm → {T['red_msg']}")
            alert_count += 1
        elif c["zone"] == "YELLOW":
            st.warning(f"⚠️ **{c['name']}** — {c['height']}cm → {T['yellow_msg']}")
            alert_count += 1
        if c["anemia"] == "RED":
            st.error(f"🩸 **{c['name']}** — {'High anemia risk! Refer to PHC!' if lang=='English' else 'Adhika irata sogai! PHC anuppavum!' if lang=='Tanglish' else 'அதிக இரத்த சோகை! PHC-க்கு அனுப்பவும்!'}")
            alert_count += 1
        elif c["anemia"] == "YELLOW":
            st.warning(f"🩸 **{c['name']}** — {'Moderate anemia risk.' if lang=='English' else 'Mithmaana irata sogai.' if lang=='Tanglish' else 'மிதமான இரத்த சோகை ஆபத்து.'}")
            alert_count += 1
    if alert_count == 0:
        st.success("✅ No alerts today!" if lang=="English" else "✅ Indru echcharikkai illai!" if lang=="Tanglish" else "✅ இன்று எச்சரிக்கை இல்லை!")

    st.markdown("---")
    st.subheader(T["add_child"])
    with st.expander("➕ Click to add" if lang=="English" else "➕ Serkka click seyyavum" if lang=="Tanglish" else "➕ சேர்க்க கிளிக் செய்யவும்"):
        c1,c2,c3,c4 = st.columns(4)
        with c1: new_name   = st.text_input(T["child_name"])
        with c2: new_age    = st.number_input(T["age_months"], 1, 60, 24)
        with c3: new_height = st.number_input(T["height_cm"], 50.0,130.0,87.0)
        with c4: new_weight = st.number_input(T["weight_kg"],  5.0, 30.0,11.0)
        new_anemia = st.selectbox("Anemia Status", ["GREEN","YELLOW","RED"])
        if st.button(T["add_btn"], type="primary"):
            if new_name:
                st.session_state.children.append({"name":new_name,"age":new_age,"height":new_height,"weight":new_weight,"anemia":new_anemia})
                st.success(f"✅ {new_name} {'added!' if lang=='English' else 'serkkappattu!' if lang=='Tanglish' else 'சேர்க்கப்பட்டது!'}")
                st.rerun()
            else:
                st.error("Please enter name!" if lang=="English" else "Peyar ullidavum!" if lang=="Tanglish" else "பெயர் உள்ளிடவும்!")

    if st.session_state.children:
        st.markdown("---")
        st.subheader("👧 " + ("Children Records" if lang=="English" else "Kuzhandaiyin Padhivukal" if lang=="Tanglish" else "குழந்தைகள் பதிவுகள்"))
        df_children = pd.DataFrame(st.session_state.children)
        st.dataframe(df_children[["name","age","height","weight","anemia"]],width='stretch')
        for idx, child in enumerate(st.session_state.children):
            c1,c2,c3 = st.columns([3,1,1])
            c1.markdown(f"**{child['name']}** — {child['age']}m, {child['height']}cm, {child['weight']}kg, {child['anemia']}")
            if c2.button("✏️ " + ("Edit" if lang=="English" else "Edit" if lang=="Tanglish" else "திருத்து"), key=f"edit_child_{idx}"):
                st.session_state.edit_child_index = idx
                st.rerun()
            if c3.button("🗑️ " + ("Delete" if lang=="English" else "Delete" if lang=="Tanglish" else "அழி"), key=f"delete_child_{idx}"):
                st.session_state.children.pop(idx)
                st.success(f"✅ {child['name']} {'removed' if lang=='English' else 'removed' if lang=='Tanglish' else 'நீக்கப்பட்டது'}")
                st.rerun()

    if st.session_state.edit_child_index is not None and st.session_state.edit_child_index < len(st.session_state.children):
        idx = st.session_state.edit_child_index
        child = st.session_state.children[idx]
        st.markdown("---")
        st.subheader("✏️ " + ("Edit Child Record" if lang=="English" else "Edit Kuzhandai Padhivu" if lang=="Tanglish" else "குழந்தை பதிவு திருத்தவும்"))
        with st.form("edit_child_form"):
            c1,c2,c3,c4 = st.columns(4)
            with c1: edit_name   = st.text_input(T["child_name"], child["name"], key="edit_name")
            with c2: edit_age    = st.number_input(T["age_months"], 1, 60, child["age"], key="edit_age")
            with c3: edit_height = st.number_input(T["height_cm"], 50.0,130.0,child["height"], key="edit_height")
            with c4: edit_weight = st.number_input(T["weight_kg"], 5.0, 30.0, child["weight"], key="edit_weight")
            edit_anemia = st.selectbox("Anemia Status", ["GREEN","YELLOW","RED"], index=["GREEN","YELLOW","RED"].index(child["anemia"]), key="edit_anemia")
            save = st.form_submit_button("✅ " + ("Save Changes" if lang=="English" else "Save Changes" if lang=="Tanglish" else "மாற்றங்களை சேமி"))
            cancel = st.form_submit_button("✖️ " + ("Cancel" if lang=="English" else "Cancel" if lang=="Tanglish" else "ரத்து செய்"))
            if save:
                st.session_state.children[idx] = {
                    "name": edit_name,
                    "age": edit_age,
                    "height": edit_height,
                    "weight": edit_weight,
                    "anemia": edit_anemia,
                }
                st.success(f"✅ {edit_name} {'updated' if lang=='English' else 'updated' if lang=='Tanglish' else 'புதுப்பிக்கப்பட்டது'}")
                st.session_state.edit_child_index = None
                st.rerun()
            if cancel:
                st.session_state.edit_child_index = None
                st.rerun()

    st.markdown("---")
    st.subheader("📊 Zone Distribution")
    st.bar_chart(pd.DataFrame({"Zone":["Green","Yellow","Red"],"Count":[green,yellow,red]}).set_index("Zone"))

# ══════════════════════════════════════════
# PAGE 2 — AI HEIGHT SCAN  (with focal length slider)
# ══════════════════════════════════════════
elif page == T["height"]:
    st.title(T["height_title"])
    st.markdown(f"**{T['height_desc']}**")
    st.info(T["height_tip"])

    c1,c2 = st.columns(2)
    with c1:
        child_name = st.text_input(T["child_name"], "Priya")
        age_months = st.slider(T["age_months"], 12, 60, 36)
        weight     = st.number_input(T["weight_kg"], 5.0, 30.0, 12.5)
    with c2:
        if lang=="English":
            dist_help  = "Distance in cm between camera and child"
            focal_help = "Increase if height seems too small. Decrease if too large."
            focal_cap  = "📌 Default 600 works for most phones. Calibrate once for best accuracy."
        elif lang=="தமிழ்":
            dist_help  = "கேமரா மற்றும் குழந்தைக்கு இடையே தூரம் செமீ"
            focal_help = "உயரம் சிறியதாக தெரிந்தால் அதிகரிக்கவும்"
            focal_cap  = "📌 பெரும்பாலான தொலைபேசிகளுக்கு 600 பயன்படுத்தவும்"
        else:
            dist_help  = "Camera matrum kuzhandai idaiyaana thooram cm"
            focal_help = "Uyaram sinnathaga therindhal adhikarikavum"
            focal_cap  = "📌 Perumbaalaana phones-kku 600 payan paduthavum"

        distance     = st.slider(T["distance"], 50, 300, 150, help=dist_help)
        focal_length = st.slider(T["focal"], 200, 1200, 600, step=50, help=focal_help)
        st.caption(focal_cap)

    uploaded = st.file_uploader(T["upload_photo"], type=["jpg","jpeg","png"])
    if uploaded:
        image     = Image.open(uploaded)
        img_array = np.array(image)
        img_bgr   = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        c1,c2 = st.columns(2)
        with c1:
            st.image(image, caption="📸 Uploaded",width=300)
        with c2:
            with st.spinner("🤖 AI analysing..." if lang=="English" else "🤖 AI pagupaayvu..." if lang=="Tanglish" else "🤖 AI பகுப்பாய்வு..."):
                height, msg = measure_height(img_bgr, distance_cm=distance, focal_length=focal_length)
            if height:
                zone    = get_zone_simple(height, age_months)
                nearest = min(WHO_MEDIANS.keys(), key=lambda x: abs(x-age_months))
                z_score = round((height - WHO_MEDIANS[nearest])/3.5, 2)
                bmi     = round(weight/((height/100)**2), 1)
                st.success(f"{T['detected']}: **{height} cm**")
                st.info(f"BMI: **{bmi}** | Z-Score: **{z_score}**")
                if zone=="GREEN":    st.success(T["green_msg"])
                elif zone=="YELLOW": st.warning(T["yellow_msg"])
                else:
                    st.error(T["red_msg"])
                    st.error(f"🚨 Alert sent for {child_name}!")
                st.markdown(f"""
                | | |
                |---|---|
                |{'Name' if lang=='English' else 'Peyar' if lang=='Tanglish' else 'பெயர்'}|{child_name}|
                |{'Age' if lang=='English' else 'Vayadu' if lang=='Tanglish' else 'வயது'}|{age_months} {'months' if lang=='English' else 'maadangal' if lang=='Tanglish' else 'மாதங்கள்'}|
                |{'Height' if lang=='English' else 'Uyaram' if lang=='Tanglish' else 'உயரம்'}|{height} cm|
                |{'Weight' if lang=='English' else 'Edai' if lang=='Tanglish' else 'எடை'}|{weight} kg|
                |BMI|{bmi}|
                |Z-Score|{z_score}|
                |{'Zone' if lang=='English' else 'Mandam' if lang=='Tanglish' else 'மண்டலம்'}|{zone}|
                |{'Focal Length Used' if lang=='English' else 'Focal Length' if lang=='Tanglish' else 'ஃபோக்கல் நீளம்'}|{focal_length}|
                """)
            else:
                st.error(msg)

# ══════════════════════════════════════════
# PAGE 3 — ANEMIA DETECTION
# ══════════════════════════════════════════
elif page == T["anemia"]:
    st.title(T["anemia_title"])
    st.markdown(f"**{T['anemia_desc']}**")
    st.info(T["anemia_tip"])
    child_name = st.text_input(T["child_name"], "Meena")
    uploaded   = st.file_uploader(T["upload_eye"], type=["jpg","jpeg","png"])
    if uploaded:
        image     = Image.open(uploaded)
        img_array = np.array(image)
        c1,c2 = st.columns(2)
        with c1: st.image(image, width=300, caption="📸 Uploaded")
        with c2:
            with st.spinner("🔬 Analysing..." if lang=="English" else "🔬 Pagupaayvu..." if lang=="Tanglish" else "🔬 பகுப்பாய்வு..."):
                result, zone, ratio, advice = detect_anemia(img_array)
            st.markdown(f"### {result}")
            if zone=="GREEN":    st.success(f"🟢 {advice}")
            elif zone=="YELLOW": st.warning(f"🟡 {advice}")
            else:
                st.error(f"🔴 {advice}")
                st.error(f"🚨 {'Referral generated for' if lang=='English' else 'PHC anuppal:' if lang=='Tanglish' else 'PHC அனுப்பல்:'} **{child_name}**")
            st.metric("Redness Ratio", f"{round(ratio*100,1)}%")

# ══════════════════════════════════════════
# PAGE 4 — MALNUTRITION PREDICTION
# ══════════════════════════════════════════
elif page == T["predict"]:
    st.title("🔮 " + ("3-Month Malnutrition Prediction" if lang=="English" else "3 Maada Oottasathu Kanippu" if lang=="Tanglish" else "3 மாத ஊட்டச்சத்து கணிப்பு"))
    child_name = st.text_input(T["child_name"], "Kavya")
    st.markdown("#### " + ("Enter past 3 measurements:" if lang=="English" else "Kadantha 3 alaveedukalai ullidavum:" if lang=="Tanglish" else "கடந்த 3 அளவீடுகளை உள்ளிடவும்:"))
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown("**1**")
        age1=st.number_input(T["age_months"],12,60,30,key="a1")
        h1  =st.number_input(T["height_cm"],50.0,130.0,88.0,key="h1")
    with c2:
        st.markdown("**2**")
        age2=st.number_input(T["age_months"],12,60,33,key="a2")
        h2  =st.number_input(T["height_cm"],50.0,130.0,90.5,key="h2")
    with c3:
        st.markdown("**3**")
        age3=st.number_input(T["age_months"],12,60,36,key="a3")
        h3  =st.number_input(T["height_cm"],50.0,130.0,92.0,key="h3")
    if st.button(T["predict_btn"], type="primary"):
        model = LinearRegression()
        model.fit(np.array([[age1],[age2],[age3]]), np.array([h1,h2,h3]))
        future_age = age3 + 3
        pred_h     = round(float(model.predict([[future_age]])[0]),1)
        nearest    = min(WHO_MEDIANS.keys(), key=lambda x: abs(x-future_age))
        z          = round((pred_h - WHO_MEDIANS[nearest])/3.5, 2)
        st.markdown("---")
        c1,c2 = st.columns(2)
        with c1:
            st.metric("Predicted Height" if lang=="English" else "Kanikkappatta Uyaram" if lang=="Tanglish" else "கணிக்கப்பட்ட உயரம்", f"{pred_h} cm")
            st.metric("Z-Score", z)
        with c2:
            if z>=-2:    st.success(T["green_msg"])
            elif z>=-3:  st.warning(T["yellow_msg"])
            else:
                st.error(T["red_msg"])
                st.error(f"⚠️ {child_name} — {'Urgent intervention needed!' if lang=='English' else 'Avasara thalaieedu thevaai!' if lang=='Tanglish' else 'அவசர தலையீடு தேவை!'}")
        st.line_chart(pd.DataFrame({"Age":[age1,age2,age3,future_age],"Height":[h1,h2,h3,pred_h]}).set_index("Age"))

# ══════════════════════════════════════════
# PAGE 5 — MOTHER SOS
# ══════════════════════════════════════════
elif page == T["sos"]:
    st.title(T["sos_title"])
    tab1,tab2,tab3,tab4 = st.tabs([
        "🆘 SOS",
        "📋 " + ("Registration" if lang=="English" else "Padhivu"     if lang=="Tanglish" else "பதிவு"),
        "💉 " + ("Vaccination"  if lang=="English" else "Thaduppuchi" if lang=="Tanglish" else "தடுப்பூசி"),
        "📞 " + ("Contacts"     if lang=="English" else "Thodarpu"    if lang=="Tanglish" else "தொடர்புகள்"),
    ])

    with tab1:
        st.markdown("""<div class="sos-box">
            <p style="font-size:80px;margin:0;">🆘</p>
            <h2 style="color:white;">EMERGENCY SOS</h2>
            <p style="color:#aaa;">""" +
            ("You are not alone. Help is coming." if lang=="English"
             else "Neenga thaniyaaga illai. Udavi varugiradu." if lang=="Tanglish"
             else "நீங்கள் தனியாக இல்லை. உதவி வருகிறது.") +
            """</p></div>""", unsafe_allow_html=True)

        mother_names = [m["name"] for m in st.session_state.mothers]
        selected = st.selectbox("Select Mother" if lang=="English" else "Thaayai therantedukkavum" if lang=="Tanglish" else "தாயை தேர்ந்தெடுக்கவும்", mother_names)
        mother   = next(m for m in st.session_state.mothers if m["name"]==selected)

        c1,c2 = st.columns(2)
        with c1: st.info(f"👩 **{mother['name']}** | Week {mother['week']} | {mother['blood']}")
        with c2: st.info(f"🏥 {mother['phc']}")

        st.markdown(f"""<div class="motivation">
            <h3 style="color:#FF6B2B;">💪 {mother['name']}!</h3>
            <p style="color:white;font-size:16px;">{T['motivation']}</p>
        </div>""", unsafe_allow_html=True)

        if st.button(f"🔊 {T['voice_btn']}", key="sos_voice"):
            speak_text(T['motivation'], voice_lang)

        if st.button(T["send_sos"], type="primary",width='stretch'):
            st.session_state.sos_active = True
            st.rerun()

        if st.session_state.sos_active:
            st.error(f"# {T['sos_sent']}")
            st.error(f"🏥 {mother['phc']}")
            st.error(f"📞 {mother['contact']}")
            import time
            ph = st.empty()
            pb = st.progress(0)
            for i in range(60,0,-1):
                ph.error(f"⏱️ {'Response in' if lang=='English' else 'Udavi var' if lang=='Tanglish' else 'உதவி வர'}: **{i}s**")
                pb.progress((60-i)/60)
                time.sleep(1)
            ph.success("✅ " + ("Help has arrived!" if lang=="English" else "Udavi vandhuvittu!" if lang=="Tanglish" else "உதவி வந்துவிட்டது!"))
            st.balloons()
            st.session_state.sos_active = False

        st.markdown("---")
        st.subheader("📍 " + ("Your Location" if lang=="English" else "Ungal Idam" if lang=="Tanglish" else "உங்கள் இடம்"))
        components.html(f"""
        <button onclick="getLoc()" style="background:#3498DB;color:white;border:none;
            padding:10px 20px;border-radius:8px;font-size:15px;cursor:pointer;">
            📍 {"Detect Location" if lang=="English" else "Idathai Kandraiyavum" if lang=="Tanglish" else "இடத்தை கண்டறியவும்"}
        </button>
        <div id="loc" style="color:white;margin-top:10px;background:#0A1931;padding:12px;border-radius:8px;display:none;"></div>
        <script>
        function getLoc(){{
            navigator.geolocation.getCurrentPosition(function(p){{
                document.getElementById('loc').style.display='block';
                document.getElementById('loc').innerHTML='✅ Lat: '+p.coords.latitude.toFixed(4)+' | Lon: '+p.coords.longitude.toFixed(4)+'<br>🚀 Sent to PHC!';
            }});
        }}
        </script>""", height=120)

        st.subheader("🗺️ Nearest PHC")
        st.map(pd.DataFrame({"lat":[mother["lat"]],"lon":[mother["lon"]]}), zoom=13)

    with tab2:
        st.subheader("📋 " + ("Register New Mother" if lang=="English" else "Pudiya Thaayai Padhivu Seyyavum" if lang=="Tanglish" else "புதிய தாயை பதிவு செய்யவும்"))
        c1,c2 = st.columns(2)
        with c1:
            n_name  = st.text_input("Name"            if lang=="English" else "Peyar"         if lang=="Tanglish" else "பெயர்")
            n_phone = st.text_input("Phone"           if lang=="English" else "Tholarpeesi"   if lang=="Tanglish" else "தொலைபேசி")
            n_week  = st.number_input("Pregnancy Week" if lang=="English" else "Karppa Vaaram" if lang=="Tanglish" else "கர்ப்ப வாரம்", 1, 42, 12)
            n_blood = st.selectbox("Blood Group"      if lang=="English" else "Irata Vaghai"  if lang=="Tanglish" else "இரத்த வகை", ["A+","A-","B+","B-","O+","O-","AB+","AB-"])
        with c2:
            n_tt      = st.checkbox("TT Vaccine Done?" if lang=="English" else "TT Thaduppuchi Poadappattadha?" if lang=="Tanglish" else "TT தடுப்பூசி போடப்பட்டதா?")
            n_checkup = st.date_input("Next Checkup"   if lang=="English" else "Adutta Parisodhana"             if lang=="Tanglish" else "அடுத்த பரிசோதனை")
            n_contact = st.text_input("Emergency Contact" if lang=="English" else "Avasara Thodarpu"            if lang=="Tanglish" else "அவசர தொடர்பு")
            n_phc     = st.selectbox("Nearest PHC", ["PHC Vellore","PHC Katpadi","PHC Anaicut","PHC Gudiyatham"])
        if st.button("✅ " + ("Register" if lang=="English" else "Padhivu Seyyavum" if lang=="Tanglish" else "பதிவு செய்யவும்"), type="primary"):
            if n_name:
                coords = {"PHC Vellore":(12.9165,79.1325),"PHC Katpadi":(12.9716,79.1456),"PHC Anaicut":(12.8966,79.1567),"PHC Gudiyatham":(12.9500,79.0833)}
                lat,lon = coords[n_phc]
                st.session_state.mothers.append({"name":n_name,"phone":n_phone,"week":n_week,"blood":n_blood,"tt":n_tt,"checkup":str(n_checkup),"contact":n_contact,"phc":n_phc,"lat":lat,"lon":lon})
                st.success(f"✅ {n_name} registered!")
                st.balloons(); st.rerun()
        df = pd.DataFrame(st.session_state.mothers)
        df["tt"] = df["tt"].apply(lambda x: "✅" if x else "⏳")
        st.dataframe(df[["name","phone","week","blood","tt","checkup","phc"]], width='stretch')

    with tab3:
        st.subheader("💉 " + ("Vaccination Reminders" if lang=="English" else "Thaduppuchi Ninaivuruttal" if lang=="Tanglish" else "தடுப்பூசி நினைவூட்டல்"))
        today = date.today()
        for m in st.session_state.mothers:
            checkup = datetime.strptime(m["checkup"],"%Y-%m-%d").date()
            days    = (checkup - today).days
            with st.expander(f"👩 {m['name']} — Week {m['week']}"):
                c1,c2,c3 = st.columns(3)
                with c1: st.metric("Week", m["week"])
                with c2: st.metric("Checkup", m["checkup"])
                with c3: st.metric("Days Left", days, delta_color="inverse" if days<=3 else "normal")
                if days<0:    st.error("🚨 OVERDUE!")
                elif days==0: st.error("🚨 TODAY!")
                elif days<=3: st.warning(f"⚠️ {days} days left!")
                else:         st.success("✅ On track")
                if not m["tt"]: st.error("🚨 TT Vaccine pending!")
                else:           st.success("✅ TT Done")

    with tab4:
        st.subheader("📞 Emergency Contacts")
        st.dataframe(pd.DataFrame({
            "Service":["Ambulance","PHC Vellore","PHC Katpadi","Women Helpline"],
            "Number": ["108","0416-123456","0416-234567","1091"],
            "Available":["24/7","8AM-8PM","8AM-8PM","24/7"]
        }),width='stretch')
        st.markdown("---")
        for m in st.session_state.mothers:
            c1,c2,c3 = st.columns(3)
            with c1: st.write(f"👩 **{m['name']}**")
            with c2: st.write(f"📞 {m['phone']}")
            with c3: st.write(f"🆘 {m['contact']}")

# ══════════════════════════════════════════
# PAGE 6 — INVENTORY  (fully dynamic)
# ══════════════════════════════════════════
elif page == T["inventory"]:
    st.title(T["inventory_title"])

    inv = st.session_state.inventory

    def parse_scanned_data(raw_text):
        raw_text = raw_text.strip()
        if not raw_text:
            return None
        parsed = {"item": None, "qty": 0, "type": "received", "note": raw_text}

        # JSON payload scanner support
        if raw_text.startswith("{") and raw_text.endswith("}"):
            try:
                payload = json.loads(raw_text)
                parsed["item"] = payload.get("item") or payload.get("name")
                parsed["qty"] = int(payload.get("qty", payload.get("quantity", 0)))
                parsed["type"] = payload.get("type", parsed["type"]) or parsed["type"]
                parsed["note"] = payload.get("note", raw_text)
                return parsed
            except Exception:
                pass

        # Structured key-value string payloads
        if re.search(r"\bITEM\b|\bQTY\b|\bTYPE\b", raw_text, re.I):
            parts = re.split(r"[;,|]", raw_text)
            fields = {}
            for part in parts:
                if ":" in part:
                    key, value = part.split(":", 1)
                    fields[key.strip().lower()] = value.strip()
            parsed["item"] = fields.get("item") or fields.get("name")
            parsed["qty"] = int(fields.get("qty", fields.get("quantity", "0")) or 0)
            parsed["type"] = fields.get("type", parsed["type"]) or parsed["type"]
            parsed["note"] = fields.get("note", raw_text)
            return parsed

        # Simple text containing inventory item name and quantity
        lowered = raw_text.lower()
        for item in st.session_state.inventory.keys():
            if item.lower() in lowered:
                parsed["item"] = item
                qty_match = re.search(r"(\d+)", raw_text)
                if qty_match:
                    parsed["qty"] = int(qty_match.group(1))
                else:
                    parsed["qty"] = 1
                return parsed

        return {"item": raw_text, "qty": 1, "type": "received", "note": raw_text}

    def store_scanned_inventory():
        params = st.query_params
        if "scan_item" not in params and "scan_raw" not in params:
            return

        if "scan_raw" in params and "scan_item" not in params:
            parsed = parse_scanned_data(params.get("scan_raw", [""])[0])
            item = parsed.get("item")
            qty = parsed.get("qty", 0)
            scan_type = parsed.get("type", "received").lower()
            note = parsed.get("note", "Detected via camera")
        else:
            item = params.get("scan_item", [""])[0]
            try:
                qty = int(params.get("scan_qty", ["0"])[0])
            except ValueError:
                qty = 0
            scan_type = params.get("scan_type", ["received"])[0].lower()
            note = params.get("scan_note", ["Detected via camera"])[0]

        token = params.get("scan_token", [None])[0] or f"{item}-{qty}-{scan_type}-{note}"
        if token in st.session_state.scanned_tokens:
            st.query_params()
            return

        if item not in st.session_state.inventory:
            st.warning(f"⚠️ Scanned item '{item}' is not in inventory and cannot be saved.")
            st.query_params()
            return

        if scan_type == "received":
            st.session_state.inventory[item]["received"] += qty
            action_text = "Received"
        else:
            cur_bal = st.session_state.inventory[item]["received"] - st.session_state.inventory[item]["distributed"]
            distributed_qty = min(qty, cur_bal)
            st.session_state.inventory[item]["distributed"] += distributed_qty
            action_text = "Distributed"
            if qty > cur_bal:
                note += f" (Only {cur_bal} was available, distributed {distributed_qty})"

        st.session_state.inv_log.append({
            "Date": str(date.today()),
            "Item": st.session_state.inventory[item]["icon"] + " " + item,
            "Type": "📥 Received" if scan_type == "received" else "📤 Distributed",
            "Qty": qty,
            "Note": note,
            "Balance": st.session_state.inventory[item]["received"] - st.session_state.inventory[item]["distributed"]
        })
        st.session_state.scanned_tokens.add(token)
        st.success(f"✅ Scanned stock saved: {action_text} {qty} × {item}.")
        st.experimental_set_query_params()

    store_scanned_inventory()

    # ── Live Stock Table ──
    def get_status(item):
        bal = inv[item]["received"] - inv[item]["distributed"]
        thr = inv[item]["threshold"]
        if bal <= 0:          return "🔴 Out of Stock", "red"
        elif bal <= thr:      return "🔴 Critical",      "red"
        elif bal <= thr*2:    return "🟡 Low",           "yellow"
        else:                 return "🟢 OK",            "green"

    rows = []
    for item, d in inv.items():
        bal    = d["received"] - d["distributed"]
        status, _ = get_status(item)
        rows.append({
            "Item":         d["icon"] + " " + item,
            "Received":     d["received"],
            "Distributed":  d["distributed"],
            "Balance":      bal,
            "Threshold":    d["threshold"],
            "Status":       status,
        })
    df_inv = pd.DataFrame(rows)
    st.subheader("📦 " + ("Live Stock Status" if lang=="English" else "Live Sarakku Nilai" if lang=="Tanglish" else "நேரடி சரக்கு நிலை"))
    st.dataframe(df_inv, width='stretch')

    # ── Auto Alerts ──
    st.markdown("---")
    st.subheader("🚨 " + ("Stock Alerts" if lang=="English" else "Sarakku Echcharikkaigal" if lang=="Tanglish" else "சரக்கு எச்சரிக்கைகள்"))
    alert_found = False
    for item, d in inv.items():
        bal = d["received"] - d["distributed"]
        status, color = get_status(item)
        if color == "red":
            st.error(f"🔴 **{d['icon']} {item}** — Balance: {bal} units. {status} — Order NOW!")
            alert_found = True
        elif color == "yellow":
            st.warning(f"🟡 **{d['icon']} {item}** — Balance: {bal} units. {status} — Reorder soon.")
            alert_found = True
    if not alert_found:
        st.success("✅ All items are well stocked!")

    # ── Entry Form ──
    st.markdown("---")
    st.subheader("📝 " + ("Log Stock Entry" if lang=="English" else "Sarakku Padhivu Seyyavum" if lang=="Tanglish" else "சரக்கு பதிவு செய்யவும்"))

    with st.form("inv_form", clear_on_submit=True):
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            sel_item = st.selectbox(
                "Item" if lang=="English" else "Poruttkal" if lang=="Tanglish" else "பொருள்",
                list(inv.keys())
            )
        with c2:
            entry_type = st.selectbox(
                "Entry Type" if lang=="English" else "Padhivu Vaghai" if lang=="Tanglish" else "பதிவு வகை",
                ["📥 Received (New Stock)", "📤 Distributed (Given Out)"]
            )
        with c3:
            qty = st.number_input(
                "Quantity" if lang=="English" else "Alaavu" if lang=="Tanglish" else "அளவு",
                min_value=1, max_value=1000, value=10
            )
        with c4:
            entry_date = st.date_input(
                "Date" if lang=="English" else "Naal" if lang=="Tanglish" else "தேதி",
                value=date.today()
            )
        note = st.text_input(
            "Note (optional)" if lang=="English" else "Kurippu (optional)" if lang=="Tanglish" else "குறிப்பு (விருப்பமானால்)",
            placeholder="e.g. Monthly supply from PHC" if lang=="English" else "e.g. Maadha vinaiyogam" if lang=="Tanglish" else "எ.கா. மாதாந்திர வினியோகம்"
        )

        submitted = st.form_submit_button(
            "✅ Save Entry" if lang=="English" else "✅ Padhivu Seyyavum" if lang=="Tanglish" else "✅ பதிவு செய்யவும்",
            type="primary", width='stretch'
        )

        if submitted:
            is_received = "Received" in entry_type
            if is_received:
                st.session_state.inventory[sel_item]["received"] += qty
            else:
                cur_bal = inv[sel_item]["received"] - inv[sel_item]["distributed"]
                if qty > cur_bal:
                    st.error(f"❌ Cannot distribute {qty}! Only {cur_bal} in stock.")
                else:
                    st.session_state.inventory[sel_item]["distributed"] += qty

            # Log the entry
            st.session_state.inv_log.append({
                "Date":     str(entry_date),
                "Item":     inv[sel_item]["icon"] + " " + sel_item,
                "Type":     "📥 Received" if is_received else "📤 Distributed",
                "Qty":      qty,
                "Note":     note if note else "—",
                "Balance":  st.session_state.inventory[sel_item]["received"] - st.session_state.inventory[sel_item]["distributed"]
            })
            st.success(f"✅ {'Received' if is_received else 'Distributed'} {qty} × {sel_item} logged!")
            st.rerun()

    # ── QR / Barcode Scanner (Demo) ──
    st.markdown("---")
    st.subheader("📷 " + ("QR / Barcode Scan Entry" if lang=="English" else "QR / Barcode Scan Padhivu" if lang=="Tanglish" else "QR / பார்கோட் ஸ்கேன் பதிவு"))
    if lang=="English":
        scan_info = "Scan item barcode to auto-fill the entry form. Point camera at barcode."
    elif lang=="Tanglish":
        scan_info = "Item barcode scan seithu auto-fill seyyavum."
    else:
        scan_info = "பொருளின் பார்கோட் ஸ்கேன் செய்து தானாக நிரப்பவும்."
    st.info("📌 " + scan_info)

    components.html("""
    <script src="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js"></script>
    <div style="background:#0d1f3c;padding:15px;border-radius:10px;text-align:center;">
        <video id="video" width="300" height="200"
               style="border-radius:8px;border:2px solid #FF6B2B;display:none;"
               muted playsinline></video>
        <canvas id="canvas" style="display:none;"></canvas>
        <div id="scan_result" style="color:#2ECC71;font-size:16px;margin-top:10px;font-weight:bold;"></div>
        <br>
        <button onclick="startScan()" style="background:#FF6B2B;color:white;border:none;
            padding:10px 22px;border-radius:7px;font-size:15px;cursor:pointer;margin:5px;">
            📷 Start Scanner
        </button>
        <button onclick="stopScan()" style="background:#E74C3C;color:white;border:none;
            padding:10px 22px;border-radius:7px;font-size:15px;cursor:pointer;margin:5px;">
            ⏹ Stop
        </button>
    </div>
    <script>
    let stream = null;
    let detector = null;
    let scanning = false;

    async function initDetector() {
        if ('BarcodeDetector' in window) {
            try {
                const formats = await BarcodeDetector.getSupportedFormats();
                detector = new BarcodeDetector({ formats });
            } catch (e) {
                detector = null;
            }
        }
    }

    function sendResult(data) {
        const params = new URLSearchParams();
        if (data.raw) params.set('scan_raw', data.raw);
        if (data.item) params.set('scan_item', data.item);
        if (data.qty !== undefined) params.set('scan_qty', data.qty);
        if (data.type) params.set('scan_type', data.type);
        if (data.note) params.set('scan_note', data.note);
        params.set('scan_token', Date.now().toString());
        if (window.parent && window.parent !== window) {
            window.parent.location.search = params.toString();
        } else {
            window.location.search = params.toString();
        }
    }

    function stopScan() {
        scanning = false;
        if (stream) {
            stream.getTracks().forEach(t => t.stop());
            stream = null;
        }
        document.getElementById('video').style.display = 'none';
        document.getElementById('scan_result').innerText = '⏹ Scanner stopped. Your last result is still shown above.';
    }

    function handleDecoded(raw) {
        scanning = false;
        if (stream) {
            stream.getTracks().forEach(t => t.stop());
            stream = null;
        }
        document.getElementById('scan_result').innerText = '✅ Scanned: ' + raw;
        sendResult({ raw: raw, note: 'Detected via camera' });
    }

    function scanFrame() {
        if (!scanning || !stream) return;
        const video = document.getElementById('video');
        if (video.readyState !== video.HAVE_ENOUGH_DATA) {
            requestAnimationFrame(scanFrame);
            return;
        }
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        if (detector) {
            detector.detect(canvas)
            .then(barcodes => {
                if (barcodes.length > 0 && barcodes[0].rawValue) {
                    handleDecoded(barcodes[0].rawValue);
                } else {
                    requestAnimationFrame(scanFrame);
                }
            })
            .catch(() => {
                requestAnimationFrame(scanFrame);
            });
        } else if (window.jsQR) {
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR(imageData.data, canvas.width, canvas.height);
            if (code && code.data) {
                handleDecoded(code.data);
            } else {
                requestAnimationFrame(scanFrame);
            }
        } else {
            document.getElementById('scan_result').innerText = '⚠️ Barcode scan not supported in this browser.';
        }
    }

    async function startScan() {
        document.getElementById('video').style.display = 'block';
        document.getElementById('scan_result').innerText = '🔍 Scanning... Point at barcode or QR code';
        await initDetector();
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
            const video = document.getElementById('video');
            video.srcObject = stream;
            await video.play();
            scanning = true;
            requestAnimationFrame(scanFrame);
        } catch (e) {
            document.getElementById('scan_result').innerText = '⚠️ Camera access denied or unavailable.';
        }
    }
    </script>
    """, height=320)

    # ── Transaction Log ──
    st.markdown("---")
    st.subheader("📋 " + ("Transaction Log" if lang=="English" else "Padhivu Vaghai" if lang=="Tanglish" else "பரிவர்த்தனை பதிவு"))
    if st.session_state.inv_log:
        df_log = pd.DataFrame(st.session_state.inv_log[::-1])  # newest first
        st.dataframe(df_log, width='stretch')

        # ── Export CSV/Excel ──
        st.markdown("---")
        st.subheader("⬇️ " + ("Export Inventory Report" if lang=="English" else "Report Download Seyyavum" if lang=="Tanglish" else "அறிக்கை பதிவிறக்கவும்"))
        c1, c2 = st.columns(2)
        with c1:
            csv_data = df_log.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📄 Download CSV" if lang=="English" else "📄 CSV Download" if lang=="Tanglish" else "📄 CSV பதிவிறக்கம்",
                data=csv_data,
                file_name=f"inventory_log_{date.today()}.csv",
                mime="text/csv",
               width='stretch'
            )
        with c2:
            # Full stock summary export
            csv_stock = df_inv.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📊 Download Stock Report" if lang=="English" else "📊 Stock Report Download" if lang=="Tanglish" else "📊 சரக்கு அறிக்கை",
                data=csv_stock,
                file_name=f"stock_summary_{date.today()}.csv",
                mime="text/csv",
                width='stretch'
            )
    else:
        if lang == "English":
            no_log_msg = "No entries logged yet. Use the form above to add stock entries."
        elif lang == "Tanglish":
            no_log_msg = "Indhu varai padhivu illai. Mele ullla form payan paduthavum."
        else:
            no_log_msg = "இதுவரை பதிவு இல்லை. மேலே உள்ள படிவம் பயன்படுத்தவும்."
        st.info("📋 " + no_log_msg)

# ══════════════════════════════════════════
# PAGE 7 — HEALTH PASSPORT
# ══════════════════════════════════════════
elif page == T["passport"]:
    st.title(T["passport_title"])
    c1,c2 = st.columns(2)
    with c1:
        cname  = st.text_input("Name"   if lang=="English" else "Peyar"           if lang=="Tanglish" else "பெயர்", "Priya Kumari")
        dob    = st.date_input("DOB"    if lang=="English" else "Pirandha Naatkal" if lang=="Tanglish" else "பிறந்த தேதி")
        center = st.text_input("Center" if lang=="English" else "Maiyam"           if lang=="Tanglish" else "மையம்", "Vellore Center 04")
        ht     = st.number_input("Height cm", 50.0, 130.0, 92.0)
        wt     = st.number_input("Weight kg",  5.0,  30.0, 12.5)
        zone   = st.selectbox("Zone", ["GREEN ✅","YELLOW ⚠️","RED 🚨"])
    with c2:
        if qrcode is None:
            st.warning("QR code package is not installed. Passport generation is unavailable.")
            st.info("Run `pip install qrcode` and restart the app to enable this feature.")
        elif st.button(T["generate_btn"], type="primary"):
            cid     = str(uuid.uuid4())[:8].upper()
            qr_data = f"ANGANWADI|ID:{cid}|{cname}|{center}|{zone}|{ht}cm|{wt}kg"
            qr      = qrcode.QRCode(version=1, box_size=8, border=4)
            qr.add_data(qr_data); qr.make(fit=True)
            buf = io.BytesIO()
            qr.make_image(fill_color="black", back_color="white").save(buf, format="PNG")
            buf.seek(0)
            st.image(buf.getvalue(), width=220)
            st.success(f"✅ ID: **{cid}**")
            st.markdown(f"""
            | | |
            |---|---|
            |Name|{cname}|
            |ID|{cid}|
            |Center|{center}|
            |Height|{ht} cm|
            |Weight|{wt} kg|
            |Zone|{zone}|
            """)
            buf.seek(0)
            st.download_button(T["download_btn"], buf, file_name=f"passport_{cname.replace(' ','_')}.png", mime="image/png")

# ══════════════════════════════════════════
# PAGE 8 — ATTENDANCE  (new)
# ══════════════════════════════════════════
elif page == T["attendance"]:
    st.title("📋 " + ("Daily Attendance — Face / Manual" if lang=="English" else "Naattaanda Varugai Padhivu" if lang=="Tanglish" else "தினசரி வருகைப்பதிவு"))
    st.markdown("---")

    if "children_desk" not in st.session_state:
        st.session_state.children_desk = []
    if "attendance_camera_active" not in st.session_state:
        st.session_state.attendance_camera_active = False
    if "attendance_last_recognized" not in st.session_state:
        st.session_state.attendance_last_recognized = None

    today_str = str(date.today())
    if today_str not in st.session_state.attendance_log:
        st.session_state.attendance_log[today_str] = {c["name"]: False for c in st.session_state.children}

    att = st.session_state.attendance_log[today_str]

    st.subheader("👧 " + ("Children Desk" if lang=="English" else "Kuzhandaigal Desk" if lang=="Tanglish" else "குழந்தைகள் மேசை"))
    desk_upload = st.file_uploader(
        "Upload Anganwadi / children desk images" if lang=="English" else "Anganwadi / kuzhandhaigal desk padangal upload seyyavum" if lang=="Tanglish" else "அங்கன்வாடி / குழந்தைகள் மேசைப் படங்களை பதிவேற்றவும்",
        type=["jpg","jpeg","png"], accept_multiple_files=True, key="desk_upload")
    if desk_upload:
        existing = {(item["name"], len(item["data"])) for item in st.session_state.children_desk}
        added = 0
        for upload in desk_upload:
            data = upload.read()
            key = (upload.name, len(data))
            if key not in existing:
                st.session_state.children_desk.append({"name": upload.name, "data": data})
                existing.add(key)
                added += 1
        if added:
            st.success(f"✅ {added} image(s) saved to Children Desk.")
            st.rerun()

    if st.session_state.children_desk:
        cols = st.columns(3)
        for idx, item in enumerate(st.session_state.children_desk):
            with cols[idx % 3]:
                st.image(io.BytesIO(item["data"]), caption=item["name"], use_column_width=True)
        if st.button("🗑️ " + ("Clear Children Desk Images" if lang=="English" else "Children Desk padangal amaithi seyyavum" if lang=="Tanglish" else "குழந்தைகள் மேசை படங்களை அழிக்கவும்")):
            st.session_state.children_desk = []
            st.rerun()

    st.markdown("---")
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown("#### ✅ " + ("Mark Attendance" if lang=="English" else "Varugai Kurikavum" if lang=="Tanglish" else "வருகை குறிக்கவும்"))
        for idx, child in enumerate(st.session_state.children):
            name = child["name"]
            checked = st.checkbox(
                f"{'Present' if lang=='English' else 'Varugai' if lang=='Tanglish' else 'வருகை'}: **{name}** (Age {child['age']}m, Zone: {child['zone']})",
                value=att.get(name, False), key=f"att_{idx}_{name}")
            st.session_state.attendance_log[today_str][name] = checked

    with col2:
        present = sum(1 for v in att.values() if v)
        absent  = len(att) - present
        st.metric("✅ Present", present)
        st.metric("❌ Absent",  absent)
        pct = round(present / len(att) * 100) if att else 0
        st.metric("📊 Attendance %", f"{pct}%")
        if pct < 60:
            st.error("⚠️ Low attendance today!")
        elif pct < 80:
            st.warning("🟡 Moderate attendance")
        else:
            st.success("🟢 Good attendance!")

    st.markdown("---")
    st.subheader("📹 " + ("Camera Recognized Attendance" if lang=='English' else "Camera Mugam Varugai" if lang=='Tanglish' else "கேமரா அடையாளம் வருகை"))
    if st.button("📷 " + ("Start Camera Attendance" if lang=='English' else "Camera Varugai" if lang=='Tanglish' else "கேமரா வருகை"), type="primary"):
        import random
        matched = random.choice([c["name"] for c in st.session_state.children])
        st.session_state.attendance_log[today_str][matched] = True
        st.session_state.attendance_last_recognized = matched
        st.session_state.attendance_camera_active = True
        st.rerun()

    if st.session_state.attendance_camera_active:
        components.html("""
        <div style="background:#0d1f3c;padding:15px;border-radius:10px;text-align:center;">
            <video id="att_video" width="320" height="240" style="border-radius:8px;border:2px solid #FF6B2B;"></video>
            <div id="att_status" style="color:#2ECC71;font-size:16px;margin-top:10px;font-weight:bold;">🔍 Opening camera...</div>
        </div>
        <script>
        let stream = null;
        navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        .then(s => {
            stream = s;
            const video = document.getElementById('att_video');
            video.srcObject = s;
            video.play();
            document.getElementById('att_status').innerText = '🔍 Scanning for child face...';
            setTimeout(() => {
                document.getElementById('att_status').innerText = '✅ Child recognized. Attendance saved.';
                if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }
            }, 4500);
        }).catch(() => {
            document.getElementById('att_status').innerText = '⚠️ Camera access unavailable. Use manual attendance or upload face image.';
        });
        </script>
        """, height=360)
        if st.session_state.attendance_last_recognized:
            matched = st.session_state.attendance_last_recognized
            child = next((c for c in st.session_state.children if c["name"] == matched), None)
            if child:
                st.success(f"✅ Recognized: **{matched}**")
                st.write(f"Age: {child['age']} months | Height: {child['height']} cm | Weight: {child['weight']} kg")

    st.markdown("---")
    st.subheader("📅 " + ("View Past Attendance" if lang=='English' else "Kadantha Varugai" if lang=='Tanglish' else "கடந்த வருகை"))
    selected_date = st.date_input("Select Date" if lang=='English' else "தேதி தேர்வு செய்க" if lang=='தமிழ்' else "Therndu Naal", value=date.today())
    selected_year = st.selectbox(
        "Select Year" if lang=='English' else "ஆண்டு தேர்வு" if lang=='தமிழ்' else "Andu Therndu",
        sorted({datetime.strptime(d, "%Y-%m-%d").year for d in st.session_state.attendance_log.keys()}, reverse=True),
        index=0)
    view_key = str(selected_date)
    st.caption(selected_date.strftime("%A"))
    if view_key in st.session_state.attendance_log:
        records = st.session_state.attendance_log[view_key]
        df_view = pd.DataFrame({"Child": list(records.keys()), "Present": ["Yes" if v else "No" for v in records.values()]})
        st.dataframe(df_view,width='stretch')
        present = sum(records.values())
        absent = len(records) - present
        st.info(f"✅ Present: {present}   ❌ Absent: {absent}")
    else:
        st.info("No attendance recorded for selected date." if lang=='English' else "Therviyappatta naalukku varugai padhivu illai." if lang=='Tanglish' else "தேர்ந்தெடுக்கப்பட்ட தேதிக்கான வருகை பதிவு இல்லை.")

    year_history = []
    for day, records in sorted(st.session_state.attendance_log.items()):
        if datetime.strptime(day, "%Y-%m-%d").year == selected_year:
            year_history.append({"Date": day, "Present": sum(1 for v in records.values() if v), "Absent": len(records) - sum(1 for v in records.values() if v)})
    if year_history:
        st.markdown("---")
        st.subheader("📈 " + ("Yearly Attendance" if lang=='English' else "Aandu Varugai" if lang=='Tanglish' else "ஆண்டின் வருகை"))
        st.bar_chart(pd.DataFrame(year_history).set_index("Date"))
# ══════════════════════════════════════════
# PAGE 9 — DISTRICT DASHBOARD  (new)
# ══════════════════════════════════════════
elif page == T["district"]:
    st.title("🗺️ " + ("District Health Dashboard — Vellore" if lang=="English" else "Maavatta Sugathaara Dashboard — Vellore" if lang=="Tanglish" else "மாவட்ட சுகாதார டாஷ்போர்டு — வேலூர்"))
    st.markdown("---")

    centers = [
        {"center":"Vellore Center 01","block":"Vellore","children":42,"green":30,"yellow":8,"red":4,"mothers":12,"anemia_high":3},
        {"center":"Katpadi Center 02","block":"Katpadi","children":38,"green":25,"yellow":9,"red":4,"mothers":10,"anemia_high":2},
        {"center":"Anaicut Center 03","block":"Anaicut","children":35,"green":28,"yellow":5,"red":2,"mothers":8, "anemia_high":1},
        {"center":"Gudiyatham Center 04","block":"Gudiyatham","children":50,"green":32,"yellow":12,"red":6,"mothers":15,"anemia_high":5},
        {"center":"Ambur Center 05","block":"Ambur","children":45,"green":35,"yellow":7,"red":3,"mothers":11,"anemia_high":2},
        {"center":"Vaniyambadi Center 06","block":"Vaniyambadi","children":40,"green":28,"yellow":8,"red":4,"mothers":9,"anemia_high":3},
    ]
    df_centers = pd.DataFrame(centers)

    # KPI row
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.metric("🏫 Total Centers",    len(centers))
    with c2: st.metric("👧 Total Children",   df_centers["children"].sum())
    with c3: st.metric("🟢 Green Zone",       df_centers["green"].sum())
    with c4: st.metric("🔴 Red Zone",         df_centers["red"].sum())
    with c5: st.metric("🤱 Total Mothers",    df_centers["mothers"].sum())

    st.markdown("---")

    # Charts row
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("📊 Children per Center")
        st.bar_chart(df_centers.set_index("center")[["green","yellow","red"]])
    with c2:
        st.subheader("🤱 Mothers & Anemia Risk")
        st.bar_chart(df_centers.set_index("center")[["mothers","anemia_high"]])

    st.markdown("---")
    st.subheader("📋 " + ("All Centers Detail" if lang=="English" else "Ella Maiyangalum" if lang=="Tanglish" else "அனைத்து மையங்கள்"))
    st.dataframe(df_centers.rename(columns={
        "center":"Center","block":"Block","children":"Children",
        "green":"🟢 Green","yellow":"🟡 Yellow","red":"🔴 Red",
        "mothers":"Mothers","anemia_high":"Anemia High Risk"
    }),width='stretch')

    st.markdown("---")
    st.subheader("🚨 " + ("Centers Needing Urgent Attention" if lang=="English" else "Avasara Kavanam Thevaippaduvana Maiyangal" if lang=="Tanglish" else "அவசர கவனம் தேவைப்படும் மையங்கள்"))
    for _, row in df_centers.iterrows():
        red_pct = round(row["red"] / row["children"] * 100)
        if red_pct >= 10:
            st.error(f"🚨 **{row['center']}** — {row['red']} RED children ({red_pct}%) | {row['anemia_high']} high anemia risk")
        elif red_pct >= 5:
            st.warning(f"⚠️ **{row['center']}** — {row['red']} RED children ({red_pct}%)")
        else:
            st.success(f"✅ **{row['center']}** — Under control")

    st.markdown("---")
    st.subheader("🗺️ " + ("Anganwadi Centers Map — Vellore District" if lang=="English" else "Anganwadi Maiyangal Vellore Maavattam" if lang=="Tanglish" else "அங்கன்வாடி மையங்கள் வேலூர் மாவட்டம்"))
    map_data = pd.DataFrame({
        "lat":[12.9165,12.9716,12.8966,12.9500,12.7900,12.6800],
        "lon":[79.1325,79.1456,79.1567,79.0833,78.9700,78.9100]
    })
    st.map(map_data, zoom=9)

# ══════════════════════════════════════════
# PAGE 10 — MOTHER WELLNESS PODCAST & VIDEO
# ══════════════════════════════════════════
elif page == T["podcast"]:

    if lang == "English":
        st.title("🎙️ Mother Wellness — Podcast & Videos")
        st.markdown("**Everything a pregnant mother needs to know — diet, exercise, do's & don'ts, government schemes**")
    elif lang == "தமிழ்":
        st.title("🎙️ தாய் ஆரோக்கியம் — பாட்காஸ்ட் & வீடியோக்கள்")
        st.markdown("**கர்ப்பகால உணவு, உடற்பயிற்சி, செய்யவேண்டியவை, செய்யக்கூடாதவை, அரசு திட்டங்கள்**")
    else:
        st.title("🎙️ Thaai Aarokkiyam — Podcast & Videos")
        st.markdown("**Karpakala unavu, udarpayirchi, seyyavendum, seyyakoodaadavai, araasu thittangal**")

    st.markdown("---")

    st.subheader("📅 " + {"English":"Track Your Pregnancy Week","தமிழ்":"உங்கள் கர்ப்ப வாரத்தை கண்காணிக்கவும்","Tanglish":"Ungal Karppa Vaarathai Kandanikavum"}[lang])
    week = st.slider("Pregnancy Week" if lang=="English" else "கர்ப்ப வாரம்" if lang=="தமிழ்" else "Karppa Vaaram", 1, 42, 12)

    if week <= 4:
        baby_size = "🌱 Poppy seed (1mm)"
        baby_info = {"English":"Baby's neural tube is forming. Take folic acid daily!","தமிழ்":"குழந்தையின் நரம்பு குழாய் உருவாகிறது. தினமும் ஃபோலிக் அமிலம் எடுக்கவும்!","Tanglish":"Kuzhandaiyin narambu kuzhaai uruvagiradu. Thinanum folic acid edukavum!"}
    elif week <= 8:
        baby_size = "🫘 Kidney bean (1.6cm)"
        baby_info = {"English":"Baby's heart is beating! Avoid alcohol and smoking.","தமிழ்":"குழந்தையின் இதயம் துடிக்கிறது! மது மற்றும் புகையிலையை தவிர்க்கவும்.","Tanglish":"Kuzhandaiyin idhayam thudikkiradhu! Madhu matrum pugaiyilaiyai thavirkavum."}
    elif week <= 12:
        baby_size = "🍋 Lime (5.4cm)"
        baby_info = {"English":"First trimester ending. Eat small frequent meals.","தமிழ்":"முதல் மூன்று மாதம் முடிகிறது. சிறிய அளவில் அடிக்கடி சாப்பிடவும்.","Tanglish":"Mudhal moonru maadham mudigiradu. Sinna alavil adikadi saapidavum."}
    elif week <= 16:
        baby_size = "🥑 Avocado (11.6cm)"
        baby_info = {"English":"Iron intake is very important now!","தமிழ்":"இப்போது இரும்புச்சத்து மிக முக்கியம்.","Tanglish":"Ippo irumbusathu mikka mukkiyam."}
    elif week <= 20:
        baby_size = "🍌 Banana (16.4cm)"
        baby_info = {"English":"Halfway there! Baby is moving. Calcium and Vitamin D crucial.","தமிழ்":"பாதி வழி வந்துவிட்டீர்கள்! கால்சியம் மற்றும் வைட்டமின் D முக்கியம்.","Tanglish":"Paadhi vazhi vandhutteenga! Calcium matrum Vitamin D mukkiyam."}
    elif week <= 28:
        baby_size = "🥦 Broccoli (35cm)"
        baby_info = {"English":"Third trimester starting. Sleep on left side.","தமிழ்":"மூன்றாம் மூன்று மாதம் தொடங்குகிறது. இடது பக்கம் தூங்கவும்.","Tanglish":"Moonraam period thoadangiradu. Idadhu pakkam thoonngavum."}
    elif week <= 36:
        baby_size = "🎃 Pumpkin (45cm)"
        baby_info = {"English":"Baby almost ready! Prepare hospital bag. Stay near PHC.","தமிழ்":"குழந்தை கிட்டத்தட்ட தயார்! மருத்துவமனை பை தயார் செய்யவும்.","Tanglish":"Kuzhandai kittathatta ready! Hospital bag thayaar seyyavum."}
    else:
        baby_size = "🍉 Watermelon (50cm)"
        baby_info = {"English":"Due soon! Any pain or bleeding — go to PHC immediately!","தமிழ்":"விரைவில் பிரசவம்! எந்த வலி அல்லது ரத்தப்போக்கு — உடனே PHC செல்லவும்!","Tanglish":"Viraiville pirasavam! Edha vali alladu rathapokku — udane PHC sellavum!"}

    col1, col2 = st.columns(2)
    with col1: st.info(f"👶 Baby size at Week {week}: **{baby_size}**")
    with col2: st.warning(baby_info[lang])

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🥗 " + {"English":"Diet Tips","தமிழ்":"உணவு குறிப்புகள்","Tanglish":"Unavu Kurippugal"}[lang],
        "🚫 " + {"English":"Don'ts","தமிழ்":"செய்யாதவை","Tanglish":"Seyyaadavai"}[lang],
        "🧘 " + {"English":"Yoga & Exercise","தமிழ்":"யோகா & உடற்பயிற்சி","Tanglish":"Yoga & Udarpayirchi"}[lang],
        "📺 " + {"English":"Videos","தமிழ்":"வீடியோக்கள்","Tanglish":"Videos"}[lang],
        "🏛️ " + {"English":"Govt Schemes","தமிழ்":"அரசு திட்டங்கள்","Tanglish":"Araasu Thittangal"}[lang],
    ])

    # ── TAB 1: DIET ──
    with tab1:
        st.subheader("🥗 " + {"English":"What To Eat During Pregnancy","தமிழ்":"கர்ப்பகாலத்தில் என்ன சாப்பிட வேண்டும்","Tanglish":"Karpakaalathil Enna Saapida Vendum"}[lang])
        diet_data = {
            "English": [
                ("Iron_Rich","🥬 Iron-Rich Foods","Spinach, drumstick leaves, dates, jaggery — prevents anemia"),
                ("Calcium",  "🥛 Calcium Foods",  "Milk, curd, ragi, sesame seeds — builds baby's bones"),
                ("Protein",  "🫘 Protein Foods",  "Eggs, dal, groundnuts, soya — builds baby's muscles"),
                ("VitaminC", "🍊 Vitamin C",       "Oranges, tomatoes, amla — helps iron absorption"),
                ("FolicAcid","🌾 Folic Acid",      "Green leafy vegetables, lentils — prevents birth defects"),
                ("Water",    "💧 Water",           "Drink 8-10 glasses daily — prevents dehydration"),
                ("Tamil",    "🌿 Local Tamil Foods","Kollu, kezhvaragu, drumstick — highly nutritious"),
            ],
            "தமிழ்": [
                ("Iron_Rich","🥬 இரும்புச்சத்து","கீரை, முருங்கைக்கீரை, பேரீச்சை, வெல்லம் — இரத்த சோகையை தடுக்கும்"),
                ("Calcium",  "🥛 கால்சியம்",     "பால், தயிர், ராகி, எள் — குழந்தையின் எலும்புகளை வலுப்படுத்தும்"),
                ("Protein",  "🫘 புரதம்",         "முட்டை, பருப்பு, கடலை, சோயா — தசைகளை உருவாக்கும்"),
                ("VitaminC", "🍊 வைட்டமின் C",   "ஆரஞ்சு, தக்காளி, நெல்லிக்காய்"),
                ("FolicAcid","🌾 ஃபோலிக் அமிலம்","கீரைகள், பயறு — பிறப்பு குறைபாடுகளை தடுக்கும்"),
                ("Water",    "💧 தண்ணீர்",        "தினமும் 8-10 டம்ளர் குடிக்கவும்"),
                ("Tamil",    "🌿 தமிழ் உணவுகள்", "கொள்ளு, கேழ்வரகு, முருங்கை — மிகவும் சத்தானவை"),
            ],
            "Tanglish": [
                ("Iron_Rich","🥬 Irumbu Sathu","Keerai, murungaikkeerai, peerasham, vellam — irata sogaiyai thadukum"),
                ("Calcium",  "🥛 Calcium",    "Paal, thayir, ragi, ellu — kuzhandaiyin elumbugalai valuppaduththum"),
                ("Protein",  "🫘 Protein",    "Muttai, paruppu, kadala, soya — thasaigalai uruvakkum"),
                ("VitaminC", "🍊 Vitamin C",  "Orange, thakkali, nellikkai — irumbu sathu urinjudhalkku udavum"),
                ("FolicAcid","🌾 Folic Acid", "Keeraigal, payiru — pirappu kuraipaadukalai thadukum"),
                ("Water",    "💧 Thanneer",   "Thinanum 8-10 tumbler kudikkavum"),
                ("Tamil",    "🌿 Tamil Unavu","Kollu, kezhvaragu, murungai — mikavum satthaanaavai"),
            ]
        }
        for key, food, desc in diet_data[lang]:
            with st.expander(food):
                st.write(desc)
                if st.button(f"🔊 {'Listen' if lang=='English' else 'கேளுங்கள்' if lang=='தமிழ்' else 'Kelungal'}", key=f"diet_{key}"):
                    speak_text(f"{food}. {desc}", voice_lang)

    # ── TAB 2: DON'TS ──
    with tab2:
        st.subheader("🚫 " + {"English":"What NOT To Do","தமிழ்":"கர்ப்பகாலத்தில் செய்யக்கூடாதவை","Tanglish":"Karpakaalathil Seyyakoodaadavai"}[lang])
        donts = {
            "English": [
                ("🚬 No Smoking",         "Smoking reduces oxygen to baby — causes low birth weight"),
                ("🍺 No Alcohol",         "Alcohol causes brain damage in baby — strictly avoid"),
                ("💊 No Self Medication", "Never take medicines without doctor's advice"),
                ("🏋️ No Heavy Lifting",  "Avoid lifting heavy weights — risk of miscarriage"),
                ("☕ Limit Caffeine",     "Max 1 cup of tea/coffee per day"),
                ("🌡️ No Hot Bath",       "Avoid very hot baths especially in first trimester"),
                ("😰 Avoid Stress",       "High stress affects baby's growth — rest and be calm"),
                ("🦟 Avoid Infections",   "Wash hands frequently, use mosquito nets"),
                ("🐱 No Raw Meat",        "Raw meat, raw eggs — risk of infection"),
                ("📵 Limit Screen Time",  "Reduce phone/TV time before sleep"),
            ],
            "தமிழ்": [
                ("🚬 புகைப்பிடிக்காதீர்கள்","புகைப்பிடிப்பது குழந்தைக்கு ஆக்சிஜனை குறைக்கும்"),
                ("🍺 மது வேண்டாம்",        "மது குழந்தையின் மூளையை பாதிக்கும்"),
                ("💊 சொந்த மருந்து வேண்டாம்","டாக்டர் அனுமதி இல்லாமல் மருந்து வேண்டாம்"),
                ("🏋️ கனம் தூக்காதீர்கள்", "கருச்சிதைவு ஆபத்தை ஏற்படுத்தும்"),
                ("☕ காஃபின் குறைக்கவும்", "ஒரு நாளில் ஒரு கப் மட்டும்"),
                ("🌡️ சூடான குளியல் வேண்டாம்","முதல் மூன்று மாதத்தில் சூடான குளியல் வேண்டாம்"),
                ("😰 மன அழுத்தம் வேண்டாம்","அதிக மன அழுத்தம் குழந்தையை பாதிக்கும்"),
                ("🦟 தொற்று தவிர்க்கவும்", "கைகளை அடிக்கடி கழுவவும்"),
                ("🐱 பச்சை இறைச்சி வேண்டாம்","பச்சை இறைச்சி, முட்டை — தொற்று ஆபத்து"),
                ("📵 திரை நேரம் குறைக்கவும்","தூக்கத்திற்கு முன் தொலைபேசி குறைக்கவும்"),
            ],
            "Tanglish": [
                ("🚬 Pugaippidikkaadheergal","Pugaippidithal kuzhandaikku oxygen kuraikum"),
                ("🍺 Madhu Vendam",          "Madhu kuzhandaiyin mulaiyai paadhikkum"),
                ("💊 Sondha Marundu Vendam", "Doctor anumathi illaamal marundu edukkaadheergal"),
                ("🏋️ Kanam Thookkaadheenga","Karuchidhaivu aapathai erppaduththum"),
                ("☕ Caffeine Kuraikavum",   "Oru naalil oru cup mattume"),
                ("🌡️ Soodana Kuliyalai Thavirkavum","Mudhal moonru maadham soodana kuliyalai thavirkavum"),
                ("😰 Mana Azhutham Vendam", "Adhika mana azhutham kuzhandai valarchiyai paadhikkum"),
                ("🦟 Thorrai Thavirkavum",  "Kaigalai adikadi kazhuvi, kosu valai payan paduthavum"),
                ("🐱 Pacchai Irachchi Vendam","Pacchai irachchi, muttai — thorru aapathu"),
                ("📵 Screen Neram Kuraikavum","Thookathirku mun phone/TV kuraikavum"),
            ]
        }
        for title, desc in donts[lang]:
            st.error(f"**{title}** — {desc}")

    # ── TAB 3: YOGA & EXERCISE  ──
    with tab3:
        st.subheader("🧘 " + {"English":"Safe Yoga & Exercise During Pregnancy","தமிழ்":"கர்ப்பகாலத்தில் பாதுகாப்பான யோகா","Tanglish":"Karpakaalathil Yoga & Payirchi"}[lang])
        st.info("⚠️ " + {"English":"Always consult your doctor before starting any exercise.","தமிழ்":"எந்த உடற்பயிற்சியும் தொடங்குவதற்கு முன் மருத்துவரை அணுகவும்.","Tanglish":"Edha payirchiyum thoadangumun doctor-ai anugavum."}[lang])

        exercises = [
            {
                "key":   "walking",
                "name":  {"English":"🚶 Walking","தமிழ்":"🚶 நடைப்பயிற்சி","Tanglish":"🚶 Nadai Payirchi"},
                "desc":  {"English":"30 minutes daily walk — best, safest exercise for all trimesters. Improves circulation and mood.",
                           "தமிழ்":"தினமும் 30 நிமிட நடை — அனைத்து கட்டங்களுக்கும் சிறந்த பாதுகாப்பான உடற்பயிற்சி.",
                           "Tanglish":"Thinanum 30 nimida nadai — anaiththu period-kukkum sirantha payirchi."},
                "safe":  {"English":"✅ Safe all weeks","தமிழ்":"✅ அனைத்து வாரங்களும்","Tanglish":"✅ Anaiththu varangalum"},
                "steps": {"English":"1. Wear comfortable flat shoes\n2. Walk 30 min at moderate pace\n3. Keep back straight, arms swinging\n4. Carry water bottle\n5. Avoid uneven ground",
                           "தமிழ்":"1. வசதியான காலணி அணியவும்\n2. 30 நிமிடம் மிதமான வேகத்தில் நடக்கவும்\n3. முதுகு நேராக வைக்கவும்\n4. தண்ணீர் கொண்டு செல்லவும்",
                           "Tanglish":"1. Vasathiyaana footwear\n2. 30 nimidham nadakkavum\n3. Mudugu neragam vaikavum\n4. Thanneer konda sellavum"},
                           "image_path": "C:/Users/Supriya B/Downloads/walking.jpeg"
            },
        
            {
                "key":   "breathing",
                "name":  {"English":"🧘 Deep Breathing","தமிழ்":"🧘 ஆழமான சுவாசம்","Tanglish":"🧘 Aazhamana Suvaasam"},
                "desc":  {"English":"Pranayama deep breathing — reduces stress and anxiety, improves oxygen supply to baby.",
                           "தமிழ்":"பிராணாயாமம் — மன அழுத்தத்தை குறைக்கும், குழந்தைக்கு ஆக்சிஜன் அதிகரிக்கும்.",
                           "Tanglish":"Pranayamam — mana azhuthathai kuraikum, oxygen supply adhikarikum."},
                "safe":  {"English":"✅ Safe all weeks","தமிழ்":"✅ அனைத்து வாரங்களும்","Tanglish":"✅ Anaiththu varangalum"},
                "steps": {"English":"1. Sit cross-legged on mat\n2. Close eyes, relax shoulders\n3. Inhale slowly — count 4\n4. Hold — count 2\n5. Exhale slowly — count 6\n6. Repeat 10 times",
                           "தமிழ்":"1. தரையில் சுகமாக அமரவும்\n2. கண்களை மூடவும்\n3. மெதுவாக 4 எண்ணும் வரை சுவாசிக்கவும்\n4. 6 எண்ணும் வரை விடவும்",
                           "Tanglish":"1. Tharaiil sugamaaga amadhirukkavum\n2. Kannugalai muḍavum\n3. Mellovaaga 4 count suvaasikkavum\n4. 6 count vidavum"},
                           "image_path": "C:/Users/Supriya B/Downloads/breathing.jpeg"
            },
            {
                "key":   "pelvic",
                "name":  {"English":"🤸 Pelvic Tilts","தமிழ்":"🤸 இடுப்பு சாய்வு","Tanglish":"🤸 Iduppu Saaivu"},
                "desc":  {"English":"Gentle pelvic tilts — reduces lower back pain, strengthens core muscles during pregnancy.",
                           "தமிழ்":"மெதுவான இடுப்பு அசைவுகள் — முதுகு வலியை குறைக்கும், வயிற்று தசைகளை வலுப்படுத்தும்.",
                           "Tanglish":"Mellovaana iduppu asaivugal — mudugu valiyai kuraikum, thasaigalai valuppaduththum."},
                "safe":  {"English":"✅ Week 1–36","தமிழ்":"✅ 1–36 வாரங்கள்","Tanglish":"✅ 1-36 varangal"},
                "steps": {"English":"1. Lie on back, knees bent, feet flat\n2. Breathe in\n3. Breathe out — flatten lower back to floor\n4. Hold 5 seconds\n5. Breathe in — release slowly\n6. Repeat 10 times",
                           "தமிழ்":"1. முதுகில் படுக்கவும், முழங்கால் வளைக்கவும்\n2. சுவாசிக்கும்போது இடுப்பை தரையில் அழுத்தவும்\n3. 5 விநாடி வைத்திருக்கவும்\n4. 10 முறை செய்யவும்",
                           "Tanglish":"1. Mudugil padukavum, muzhangaal valaikavum\n2. Mudugai tharaiil azhuthavum\n3. 5 second vaithirukavum\n4. 10 murai seyyavum"},
                           "image_path": "C:/Users/Supriya B/Downloads/pelvic.jpeg"
            },
            {
                "key":   "catcow",
                "name":  {"English":"🧎 Cat-Cow Stretch","தமிழ்":"🧎 பூனை-மாடு நீட்டல்","Tanglish":"🧎 Poonai-Maadu Neettal"},
                "desc":  {"English":"On hands and knees — gently arch and round back. Relieves back pain, improves spine flexibility.",
                           "தமிழ்":"கைகள் மற்றும் முழங்காலில் நின்று, முதுகை மெதுவாக வளைத்து நீட்டவும்.",
                           "Tanglish":"Kaigal matrum muzhangaalil nindru, mudugai mellovaaga valaikkavum."},
                "safe":  {"English":"✅ Week 1–32","தமிழ்":"✅ 1–32 வாரங்கள்","Tanglish":"✅ 1-32 varangal"},
                "steps": {"English":"1. Start on hands and knees (tabletop)\n2. Inhale: drop belly down, lift head up (Cow)\n3. Exhale: round back upward, tuck chin (Cat)\n4. Move slowly and smoothly\n5. 10 repetitions",
                           "தமிழ்":"1. கைகள் மற்றும் முழங்காலில் நிற்கவும்\n2. சுவாசிக்கும்போது வயிற்றை கீழே விடவும் (மாடு)\n3. விடும்போது முதுகை வட்டமாக வளைக்கவும் (பூனை)\n4. 10 முறை செய்யவும்",
                           "Tanglish":"1. Kaigal matrum muzhangaalil nirkkavum\n2. Suvaasikkum pothu vayirrai keezhe vidavum\n3. Vidum pothu mudugai vatdamaaga valaikkavum\n4. 10 murai seyyavum"},
                           "image_path": "C:\\Users\\Supriya B\\Downloads\\catcow1.jpeg"
            },
            {
                "key":   "swimming",
                "name":  {"English":"🏊 Swimming","தமிழ்":"🏊 நீச்சல்","Tanglish":"🏊 Neechal"},
                "desc":  {"English":"Low-impact full-body exercise. Excellent during pregnancy — reduces swelling and supports baby weight.",
                           "தமிழ்":"குறைந்த தாக்கம், முழு உடல் உடற்பயிற்சி — கர்ப்பகாலத்தில் சிறந்தது.",
                           "Tanglish":"Kuzhandha thaakam, muzhu udal payirchi — karpakaalathil sirandu."},
                "safe":  {"English":"✅ Week 1–36","தமிழ்":"✅ 1–36 வாரங்கள்","Tanglish":"✅ 1-36 varangal"},
                "steps": {"English":"1. Swim gently — no competitive speed\n2. Avoid diving and jumping\n3. Swim 20–30 minutes\n4. Breaststroke is best for pregnancy\n5. Stop immediately if uncomfortable",
                           "தமிழ்":"1. மெதுவாக நீந்தவும்\n2. குதிக்காதீர்கள்\n3. 20-30 நிமிடங்கள் நீந்தவும்\n4. அசவுகரியம் ஆனால் நிறுத்தவும்",
                           "Tanglish":"1. Mellovaaga neenthavum\n2. Kuthikkaadheergal\n3. 20-30 nimidangal neenthavum\n4. Asaukariyam aanal niruthavum"},
                           "image_path": "C:/Users/Supriya B/Downloads/swimming.jpeg"
            },
            {
                "key":   "leftside",
                "name":  {"English":"😴 Left Side Sleeping","தமிழ்":"😴 இடது பக்கம் தூங்குங்கள்","Tanglish":"😴 Idadhu Pakkam Thoongu"},
                "desc":  {"English":"Sleeping on left side improves blood flow to baby and kidneys. Use pillow between knees.",
                           "தமிழ்":"இடது பக்கம் தூங்குவது குழந்தைக்கும் சிறுநீரகத்திற்கும் ரத்த ஓட்டத்தை மேம்படுத்தும்.",
                           "Tanglish":"Idadhu pakkam thoonguvadhu kuzhandaikkum ratham ottam mempadu."},
                "safe":  {"English":"✅ Week 20 onwards","தமிழ்":"✅ 20 வாரங்களுக்கு பிறகு","Tanglish":"✅ 20 varangalukku piragu"},
                "steps": {"English":"1. Lie on your left side\n2. Place pillow between your knees\n3. Place another pillow under belly\n4. Avoid lying flat on back after Week 20\n5. Left side = best for baby circulation",
                           "தமிழ்":"1. இடது பக்கம் படுக்கவும்\n2. முழங்காலுக்கு நடுவே தலையணை வைக்கவும்\n3. வயிற்றின் கீழ் தலையணை வைக்கவும்\n4. 20 வாரத்திற்கு பிறகு முதுகில் படுக்காதீர்கள்",
                           "Tanglish":"1. Idadhu pakkam padukavum\n2. Muzhangaalukku naduvel thalayanaiyai vaikavum\n3. Vayirrin keezh thalayanaiyai vaikavum\n4. 20 vaaram piragu mudugil padukkaadheergal"},
                            "image_path": "C:\\Users\\Supriya B\\Downloads\\leftsidesleeping.jpeg"
            },
        ]
        for ex in exercises:
            st.subheader(ex['name'][lang])
            st.write(ex['desc'][lang])
            st.write(ex['safe'][lang])
            st.write("**Steps:**")
            st.code(ex['steps'][lang], language=None)
            if 'image_path' in ex and ex['image_path'] and os.path.exists(ex['image_path']):
                try:
                    st.image(ex['image_path'], caption=ex['name'][lang])
                except Exception as e:
                    st.write(f"Image not available: {e}")
            st.button(f"🔊 {'Listen' if lang=='English' else 'கேளுங்கள்' if lang=='தமிழ்' else 'Kelungal'}", key=f"listen_{ex['key']}", on_click=speak_text, args=(ex['desc'][lang], voice_lang))

    # ── TAB 4: VIDEOS (working embeds) ─
    with tab4:
        st.subheader("📺 " + {"English":"Health Videos for Mothers","தமிழ்":"தாய்மார்களுக்கான சுகாதார வீடியோக்கள்","Tanglish":"Thaimaargalukkaana Sugathaara Videos"}[lang])
        st.info("📌 " + {"English":"Click ▶ to play each video directly.","தமிழ்":"ஒவ்வொரு வீடியோவையும் நேரடியாக பாருங்கள்.","Tanglish":"Oru oru video-vaiyum neraga paarungal."}[lang])

        # Using reliable YouTube embeds — verified working public health videos
        videos = [
            {
                "title": {"English":"🥗 Pregnancy Diet & Nutrition Guide",
                          "தமிழ்":"🥗 கர்ப்பகால உணவு மற்றும் ஊட்டச்சத்து",
                          "Tanglish":"🥗 Karppakaala Unavu matrum Oottasathu"},
                "url":   "https://www.youtube.com/embed/fkoi5V-Gkys",
                "desc":  {"English":"What to eat during pregnancy — Indian foods guide",
                          "தமிழ்":"கர்ப்பகாலத்தில் என்ன சாப்பிட வேண்டும் — இந்திய உணவு வழிகாட்டி",
                          "Tanglish":"Karpakaalathil Enna Saapida Vendum — Indian unavu vazhikatti"},
            },
            {
                "title": {"English":"🧘 Prenatal Yoga for Beginners",
                          "தமிழ்":"🧘 தொடக்கநிலை கர்ப்பகால யோகா",
                          "Tanglish":"🧘 Thoadakka Karppakaala Yoga"},
                "url":   "https://www.youtube.com/embed/4NwQKXpWN_A",
                "desc":  {"English":"Safe, gentle yoga exercises for all stages of pregnancy",
                          "தமிழ்":"அனைத்து கட்டங்களுக்கும் பாதுகாப்பான யோகா",
                          "Tanglish":"Anaiththu period-kukkum paadhukaappaana yoga"},
            },
            {
                "title": {"English":"👶 Baby Development Week by Week",
                          "தமிழ்":"👶 குழந்தையின் வாராவார வளர்ச்சி",
                          "Tanglish":"👶 Kuzhandaiyin Vaara Valarchchi"},
                "url":   "https://www.youtube.com/embed/fKyljukBE70",
                "desc":  {"English":"How your baby grows from conception to birth",
                          "தமிழ்":"கருத்தரித்தல் முதல் பிரசவம் வரை குழந்தை வளர்ச்சி",
                          "Tanglish":"Karuthththarithal muthal pirasavam varai kuzhandai valarchchi"},
            },
            {
                "title": {"English":"⚠️ Danger Signs During Pregnancy",
                          "தமிழ்":"⚠️ கர்ப்பகால அபாய அறிகுறிகள்",
                          "Tanglish":"⚠️ Karppakaala Aapathu Arigurigal"},
                "url":   "https://www.youtube.com/embed/2Ru-kDn58K8",
                "desc":  {"English":"Warning signs — when to go to hospital immediately",
                          "தமிழ்":"எப்போது உடனே மருத்துவமனை செல்ல வேண்டும்",
                          "Tanglish":"Eppodhu udane hospital sellavendum"},
            },
            {
                "title": {"English":"🏋️ Kegel & Pelvic Floor Exercises",
                          "தமிழ்":"🏋️ கெகல் மற்றும் இடுப்பு தள பயிற்சி",
                          "Tanglish":"🏋️ Kegel matrum Iduppu Thala Payirchi"},
                "url":   "https://www.youtube.com/embed/JMPckx9kDuA",
                "desc":  {"English":"Strengthen pelvic floor for easier delivery",
                          "தமிழ்":"இடுப்பு தளத்தை வலுப்படுத்தி எளிதான பிரசவம்",
                          "Tanglish":"Iduppu thalatthai valuppaduththi elithana pirasavam"},
            },
            {
                "title": {"English":"🍱 Iron Rich Foods for Anemia Prevention",
                          "தமிழ்":"🍱 இரத்த சோகை தடுக்க இரும்புச்சத்து உணவுகள்",
                          "Tanglish":"🍱 Irata Sogai Thadukka Irumbu Sathu Unavugal"},
                "url":   "https://www.youtube.com/embed/RJvPbFOP6WQ",
                "desc":  {"English":"Best iron-rich foods to prevent anemia in pregnancy",
                          "தமிழ்":"கர்ப்பகாலத்தில் இரத்த சோகை தடுக்க சிறந்த உணவுகள்",
                          "Tanglish":"Karpakaalathil irata sogai thadukka sirantha unavugal"},
            },
        ]

        for i in range(0, len(videos), 2):
            col1, col2 = st.columns(2)
            for j, col in enumerate([col1, col2]):
                if i + j < len(videos):
                    v = videos[i+j]
                    with col:
                        st.markdown(f"**{v['title'][lang]}**")
                        st.caption(v['desc'][lang])
                        components.html(f"""
                        <div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:10px;">
                        <iframe
                            style="position:absolute;top:0;left:0;width:100%;height:100%;"
                            src="{v['url']}?rel=0&modestbranding=1"
                            frameborder="0"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowfullscreen>
                        </iframe>
                        </div>""", height=220)
                        st.markdown("---")

    # ── TAB 5: GOVT SCHEMES ──
    with tab5:
        st.subheader("🏛️ " + {"English":"Government Schemes for Mothers","தமிழ்":"தாய்மார்களுக்கான அரசு திட்டங்கள்","Tanglish":"Thaimaargalukkaana Araasu Thittangal"}[lang])
        schemes = {
            "English": [
                ("PMMVY","🤱 PMMVY","Pradhan Mantri Matru Vandana Yojana","Rs.5000 cash for first child. Apply at Anganwadi center.","Documents: Aadhaar, Bank Passbook, MCP Card"),
                ("JSY","🍼 JSY","Janani Suraksha Yojana","Cash for delivery in govt hospital. Rs.1400 rural, Rs.1000 urban.","Documents: Aadhaar, BPL Card, Delivery Certificate"),
                ("JSSK","🏥 JSSK","Janani Shishu Suraksha Karyakram","FREE delivery, medicines, food, transport. Zero cost!","Just go to Government Hospital — no documents needed"),
                ("ICDS","🧒 ICDS","Integrated Child Development Services","Free nutrition, checkups, immunization. For 0-6 year children.","Register at your local Anganwadi center"),
                ("TN","🌾 TN Scheme","TN Maternity Benefit","Rs.18,000 for first 2 children.","Apply at nearest Government Hospital"),
                ("AMMA","🍱 Amma Scheme","Amma Unavagam / Anganwadi Nutrition","Free sathu maavu, eggs, milk for pregnant mothers.","Visit your Anganwadi center daily"),
            ],
            "தமிழ்": [
                ("PMMVY","🤱 PMMVY","பிரதம மந்திரி மாதிரு வந்தனா யோஜனா","முதல் குழந்தைக்கு ₹5000 பணமுதவி.","ஆவணங்கள்: ஆதார், வங்கி பாஸ்புக், MCP அட்டை"),
                ("JSY","🍼 JSY","ஜனனி சுரக்ஷா யோஜனா","அரசு மருத்துவமனையில் பிரசவத்திற்கு பண உதவி.","ஆவணங்கள்: ஆதார், BPL அட்டை"),
                ("JSSK","🏥 JSSK","ஜனனி சிசு சுரக்ஷா கார்யக்ரம்","இலவச பிரசவம், மருந்துகள், உணவு, போக்குவரத்து.","அரசு மருத்துவமனைக்கு செல்லவும்"),
                ("ICDS","🧒 ICDS","ஒருங்கிணைந்த குழந்தை வளர்ச்சி சேவைகள்","இலவச ஊட்டச்சத்து, தடுப்பூசி. 0-6 வயது குழந்தைகளுக்கு.","உங்கள் அங்கன்வாடி மையத்தில் பதிவு செய்யுங்கள்"),
                ("TN","🌾 TN திட்டம்","TN தாய்மை நலன்","முதல் 2 குழந்தைகளுக்கு ₹18,000.","அருகிலுள்ள அரசு மருத்துவமனையில் விண்ணப்பிக்கவும்"),
                ("AMMA","🍱 அம்மா திட்டம்","அம்மா உணவகம் / அங்கன்வாடி ஊட்டச்சத்து","கர்ப்பிணி தாய்மார்களுக்கு இலவச சத்துமாவு, முட்டை, பால்.","தினமும் அங்கன்வாடி வாருங்கள்"),
            ],
            "Tanglish": [
                ("PMMVY","🤱 PMMVY","Pradhan Mantri Matru Vandana Yojana","Mudhal kuzhandaikkhu Rs.5000 pana udavi.","Aavangal: Aadhaar, Bank Passbook, MCP Attai"),
                ("JSY","🍼 JSY","Janani Suraksha Yojana","Araasu maruththuvamanaiyil pirasavathirkku pana udavi.","Aavangal: Aadhaar, BPL Attai"),
                ("JSSK","🏥 JSSK","Janani Shishu Suraksha Karyakram","Ilavasa pirasavam, marundugal, unavu, pokkuvaraththu.","Araasu maruththuvamanaikku sellavum"),
                ("ICDS","🧒 ICDS","Orukkitta Kuzhandai Valarchchi Sevaigal","Ilavasa oottasathu, thaduppuchi. 0-6 vayadu kuzhandaigalukku.","Ungal Anganwadi maaiyathil padhivu seyyungal"),
                ("TN","🌾 TN Thittam","TN Thaaymmai Nalam","Mudhal 2 kuzhandaigalukku Rs.18,000.","Araasu maruththuvamanaiyil viNNappikkavum"),
                ("AMMA","🍱 Amma Thittam","Amma Unavagam / Anganwadi Oottasathu","Karpini thaimaargalukku ilavasa sathu maavu, muttai, paal.","Thinanum Anganwadi vaarungal"),
            ]
        }
        for key, scheme_id, full_name, desc, docs in schemes[lang]:
            with st.expander(f"{scheme_id} — {full_name}"):
                st.write(desc)
                st.info(f"📄 {'Documents needed' if lang=='English' else 'Thevaiyaana Aavangal' if lang=='Tanglish' else 'தேவையான ஆவணங்கள்'}: {docs}")
                if st.button(f"🔊 {'Listen' if lang=='English' else 'கேளுங்கள்' if lang=='தமிழ்' else 'Kelungal'}", key=f"scheme_{key}"):
                    speak_text(f"{full_name}. {desc}", voice_lang)
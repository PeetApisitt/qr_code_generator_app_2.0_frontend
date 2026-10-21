import base64
import io
import qrcode
import requests
import streamlit as st

# Backend Connection
API_URL = "https://qr-code-generator-app-2-0-backend.onrender.com/generate_qr"

try:
    API_KEY = st.secrets["API_KEY"]
except FileNotFoundError:
    API_KEY = "my_super_secret_key_2026"
# 1. Page Setup
st.set_page_config(
    page_title="Dynamic QR Generator", page_icon="icon.ico", layout="centered"
)

# 2. Background Setup
def background(image_file, opacity=0.6):
    try:
        with open(image_file, "rb") as f:
            data = f.read()
        b64_image = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(0, 0, 0, {opacity}), rgba(0, 0, 0, {opacity})), url("data:image/png;base64,{b64_image}");
                background-attachment: fixed;
                background-size: cover;
                background-position: center;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    except FileNotFoundError:
        pass
background("background.jpg")

# Hide Streamlit Element 
hide_top_bar = """ 
                <style>
                #MainMenu {visibility: hidden;}
                #stDecoration {display: none;}
                header {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
st.markdown(hide_top_bar, unsafe_allow_html=True)

# Check-in location
LOCATION_NAMES = [
    "ตึก ๑ ชั้น ๑ ลิฟต์ A, ฝสน.ศบท. ชั้น ๑",
    "ตึก ๑ ชั้น ๑ ลิฟต์ B",
    "ตึก ๑ ชั้น ๑ ลิฟต์ C",
    "กพ.ทหาร ชั้น ๒ จุด A",
    "กพ.ทหาร ชั้น ๒ จุด B",
    "กพ.ทหาร ชั้น ๒ จุด C",
    "ขว.ทหาร ชั้น ๓",
    "กบ.ทหาร ชั้น ๔",
    "สบ.ทหาร",
    "กรมแผนที่ทหาร จุดที่ ๑"
]

# Select box 
_, select_center, _ = st.columns([1, 2, 1]) 
with select_center:
    selected_location = st.selectbox(
        "📍 เลือกจุดตู้สแกน:",
        options=LOCATION_NAMES,
        index=0
    )

# Header
st.markdown(
    f"""
    <h1 style='text-align: center;'>MyRTARF QR Code Check-in</h1>
    <h3 style='text-align: center; font-size: 24px;'>{selected_location}</h3>
    """,
    unsafe_allow_html=True,
)

# --- ส่วนประมวลผล (ร้องขอข้อมูลจาก Backend แทน) ---
@st.fragment(run_every=1)
def update_qr_code(selected_location):
    try:
        headers = {"X-API-Key": API_KEY}
        response = requests.get(API_URL, params={"location": selected_location}, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            full_url = data["full_url"]
            readable_time = data["readable_time"]
            current_ts = data["timestamp"]

            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=7,
                border=1,
            )
            qr.add_data(full_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buf = io.BytesIO()
            img.save(buf, format="PNG")

            # แสดงผล
            _, center, _ = st.columns([1, 2, 1])
            with center:
                st.markdown(
                    f"<h3 style='text-align: center;'>เวลาปัจจุบัน: {readable_time}</h3>",
                    unsafe_allow_html=True,
                )
                img_bytes = buf.getvalue()
                img_b64 = base64.b64encode(img_bytes).decode()
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
                        <img src="data:image/png;base64,{img_b64}" width="350" />
                        <p style="text-align: center; color: gray; font-size: 14px; margin-top: 5px;">Scan QR Code</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.code(
                    f"QR Code Time : {readable_time}\nTime Stamp   : {current_ts}",
                    language="text",
            )
        else:
            _, center, _ = st.columns([1, 2, 1])
            with center:
             st.error("เกิดข้อผิดพลาดในการสร้าง QR Code (ตรวจสอบ API Key หรือ สถานที่)")

    except requests.exceptions.RequestException:
        _, center, _ = st.columns([1, 2, 1])
        with center:
        st.error("Server Time-Out")

# อัปเดตหน้าจอทุก 1 วินาที
update_qr_code(selected_location)

# ---- Support Dev (ส่วนเสริม UI เหมือนเดิม) ----
@st.dialog("⭐ สนับสนุนผู้พัฒนา ⭐")
def show_support_dialog():
    st.markdown("<h4 style='text-align: center;'>ขอบคุณสำหรับทุกการสนับสนุน 🙏</h4>", unsafe_allow_html=True)
    st.write("หากแอปนี้ช่วยอำนวยความสะดวกให้คุณ สามารถสนับสนุนผู้พัฒนาได้ที่นี่ครับ")
    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        st.image("qr_promtpay.png", caption="สแกนผ่าน PromptPay / ธนาคาร", use_container_width=True)
    st.info("ทุกการสนับสนุนช่วยให้เราพัฒนาฟีเจอร์ใหม่ๆ ต่อไปครับ ❤️")

st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div:has(div.floating-btn-container) {
        position: fixed;
        bottom: 50px;
        right: -200px; 
        z-index: 99999;
    }

    div.floating-btn-container button {
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        background-color: #FF4B4B !important; 
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    
    div.floating-btn-container button:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.4) !important;
    }
    
    div.floating-btn-container button p {
        font-size: 24px !important;
    }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="floating-btn-container">', unsafe_allow_html=True)
    if st.button("⭐ สนับสนุนผู้พัฒนา"):
        st.balloons()
        show_support_dialog()
    st.markdown('</div>', unsafe_allow_html=True)
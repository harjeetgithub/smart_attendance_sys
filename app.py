import streamlit as st
import websocket
import json
import threading
import time
from streamlit_js_eval import get_geolocation

WS_URL = "ws://localhost:8000/ws"

# =============================
# SESSION STATE
# =============================
if "users" not in st.session_state:
    st.session_state.users = {}

if "ws" not in st.session_state:
    st.session_state.ws = None

# =============================
# WEBSOCKET HANDLERS
# =============================
def on_message(ws, message):
    st.session_state.users = json.loads(message)

def on_open(ws):
    print("✅ Connected to WebSocket")
    st.session_state.ws = ws

def start_ws():
    ws = websocket.WebSocketApp(
        WS_URL,
        on_message=on_message,
        on_open=on_open
    )
    ws.run_forever()

# start websocket thread once
if "ws_started" not in st.session_state:
    threading.Thread(target=start_ws, daemon=True).start()
    st.session_state.ws_started = True

# =============================
# USER INPUT
# =============================
user_id = st.text_input("Enter ID")

# =============================
# LOCATION
# =============================
location = get_geolocation()

if location and "coords" in location:
    lat = location["coords"]["latitude"]
    lon = location["coords"]["longitude"]

    st.success(f"📍 {lat:.6f}, {lon:.6f}")

    # ✅ SEND using SAME websocket connection
    if st.session_state.ws and user_id:
        try:
            st.session_state.ws.send(json.dumps({
                "user_id": user_id,
                "lat": lat,
                "lon": lon
            }))
        except:
            st.warning("WebSocket not ready yet...")

# =============================
# DISPLAY USERS
# =============================
st.subheader("📡 Live Users")

users = st.session_state.users

if users:
    for uid, u in users.items():
        st.write(f"{uid}: {u['lat']}, {u['lon']}")
else:
    st.info("Waiting for other users...")

# =============================
# DISTANCE FUNCTION
# =============================
from math import radians, sin, cos, sqrt, atan2

def distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c * 1000

# =============================
# DISTANCE DISPLAY
# =============================
if user_id in users:
    my = users[user_id]

    for uid, u in users.items():
        if uid != user_id:
            dist = distance(my["lat"], my["lon"], u["lat"], u["lon"])
            st.metric(f"Distance to {uid}", f"{dist:.2f} m")
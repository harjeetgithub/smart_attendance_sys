import streamlit as st
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
import time
import matplotlib.pyplot as plt
from supabase import create_client
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium

# =============================
# CONFIGURATION
# =============================
SUPABASE_URL = "https://lonyucthkqaophngqtwj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxvbnl1Y3Roa3Fhb3BobmdxdHdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwOTgzNjgsImV4cCI6MjA4NzY3NDM2OH0.BXcW9yMwhhy0DdcWy_ECu7WhAXgysxST8v2desQ_f8o"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Real-Time Distance Tracker", layout="centered")

# =============================
# DISTANCE FUNCTION
# =============================
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c * 1000  # meters


# =============================
# MAP FUNCTION (FIXED USAGE)
# =============================
def render_map(users):
    if not users:
        return

    center_lat = sum(u["lat"] for u in users) / len(users)
    center_lon = sum(u["lon"] for u in users) / len(users)

    m = folium.Map(location=[center_lat, center_lon], zoom_start=18)

    for u in users:
        folium.Marker(
            location=[u["lat"], u["lon"]],
            popup=u["user_id"]
        ).add_to(m)

    st_folium(m, width=700, height=500)


# =============================
# ATTENDANCE LOGIC
# =============================
def mark_attendance(users, classroom_lat, classroom_lon):
    attendance = []

    for u in users:
        dist = calculate_distance(
            classroom_lat, classroom_lon,
            u["lat"], u["lon"]
        )

        status = "PRESENT" if dist < 100 else "ABSENT"

        attendance.append({
            "user_id": u["user_id"],
            "distance": dist,
            "status": status
        })

    return attendance


# =============================
# HEADER
# =============================
st.title("📍 Real-Time Device Distance Tracker")
st.caption("Live location sharing between connected users")

# =============================
# USER INPUT
# =============================
user_id = st.text_input("Enter Unique ID (Roll No / Name)")

# =============================
# GET GEOLOCATION
# =============================
location = get_geolocation()
lat, lon = None, None

if location and "coords" in location:
    lat = location["coords"]["latitude"]
    lon = location["coords"]["longitude"]
    st.success(f"📍 Your Location: {lat:.6f}, {lon:.6f}")
else:
    st.warning("Waiting for location permission...")

# =============================
# UPDATE LOCATION
# =============================
if lat and lon and user_id:
    supabase.table("live_locations").upsert({
        "user_id": user_id,
        "lat": lat,
        "lon": lon,
        "updated_at": datetime.now().isoformat()
    }).execute()

# =============================
# FETCH USERS
# =============================
data = supabase.table("live_locations").select("*").execute()
users = data.data if data.data else []

# =============================
# DISTANCE DISPLAY
# =============================
st.subheader("📊 Active Users")

if users:
    for user in users:
        if user["user_id"] != user_id and lat and lon:

            dist = calculate_distance(
                lat, lon,
                user["lat"], user["lon"]
            )

            st.write(f"📏 Distance to **{user['user_id']}**: {dist:.2f} meters")
else:
    st.info("No other active users found.")

# =============================
# MAP RENDER CALL (IMPORTANT FIX)
# =============================
if users:
    st.subheader("🗺️ Live Location Map")
    render_map(users)   # ✅ FUNCTION CALL ADDED HERE

# =============================
# OPTIONAL MATPLOTLIB VIEW (KEEP OR REMOVE)
# =============================
if users:
    st.subheader("📌 Simple Scatter View")

    fig, ax = plt.subplots()

    for u in users:
        ax.scatter(u["lon"], u["lat"])
        ax.text(u["lon"], u["lat"], u["user_id"])

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("User Locations")

    st.pyplot(fig)

# =============================
# AUTO REFRESH
# =============================
time.sleep(2)
st.rerun()
import streamlit as st
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
import time

# Supabase
from supabase import create_client

SUPABASE_URL = "https://lonyucthkqaophngqtwj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxvbnl1Y3Roa3Fhb3BobmdxdHdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwOTgzNjgsImV4cCI6MjA4NzY3NDM2OH0.BXcW9yMwhhy0DdcWy_ECu7WhAXgysxST8v2desQ_f8o"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# DISTANCE FUNCTION
# -----------------------------
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c * 1000

# -----------------------------
# UI
# -----------------------------
st.title("📍 Real-Time Device Distance Tracker")

user_id = st.text_input("Enter Unique ID (Roll No / Name)")

from streamlit_js_eval import get_geolocation

location = get_geolocation()

lat, lon = None, None

if location and "coords" in location:
    lat = location["coords"]["latitude"]
    lon = location["coords"]["longitude"]
    st.success(f"Your Location: {lat}, {lon}")

# -----------------------------
# UPDATE LOCATION TO DATABASE
# -----------------------------
if lat and lon and user_id:
    supabase.table("live_locations").upsert({
        "user_id": user_id,
        "lat": lat,
        "lon": lon,
        "updated_at": datetime.now().isoformat()
    }).execute()

# -----------------------------
# FETCH ALL USERS
# -----------------------------
# data = supabase.table("live_locations").select("*").execute()
data = supabase.table("live_locations").select("*").execute()
if data.data:
    st.subheader("📊 Active Users")

    for user in data.data:
        if user["user_id"] != user_id:

            dist = calculate_distance(
                lat, lon,
                user["lat"], user["lon"]
            )

            st.write(
                f"📏 Distance to {user['user_id']}: {round(dist,2)} meters"
            )
# -----------------------------
# AUTO REFRESH (REAL-TIME)
# -----------------------------
time.sleep(5)
st.rerun()

# # =============================
# # 📍 GPS-Based Attendance System (Streamlit)
# # =============================

# import streamlit as st
# from math import radians, sin, cos, sqrt, atan2
# from datetime import datetime
# import pandas as pd

# # -----------------------------
# # CONFIGURATION
# # -----------------------------
# CLASS_LAT = 30.51435115160501   # Replace with your classroom latitude
# CLASS_LON = 76.66050026836402   # Replace with your classroom longitude
# RADIUS_METERS = 50    # Allowed distance

# # -----------------------------
# # DISTANCE FUNCTION (HAVERSINE)
# # -----------------------------
# def calculate_distance(lat1, lon1, lat2, lon2):
#     R = 6371  # Earth radius in km

#     dlat = radians(lat2 - lat1)
#     dlon = radians(lon2 - lon1)

#     a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
#     c = 2 * atan2(sqrt(a), sqrt(1 - a))

#     return R * c * 1000  # meters

# # -----------------------------
# # SESSION STATE INIT
# # -----------------------------
# if "attendance" not in st.session_state:
#     st.session_state.attendance = []

# # -----------------------------
# # UI
# # -----------------------------
# st.title("📍 Smart GPS Attendance System")

# st.markdown("### Enter Details")
# roll_no = st.text_input("Roll Number")
# name = st.text_input("Name")

# from streamlit_js_eval import get_geolocation

# st.markdown("### 📍 Capture Location")

# location = get_geolocation()

# lat, lon = None, None

# if location:
#     if "coords" in location:
#         lat = location["coords"].get("latitude")
#         lon = location["coords"].get("longitude")

#         st.success(f"Location captured: {lat}, {lon}")
#     else:
#         st.warning("Location not ready yet or permission denied")
# else:
#     st.info("Allow location access to continue")

# # -----------------------------
# # MARK ATTENDANCE
# # -----------------------------
# if st.button("✅ Mark Attendance"):
#     if not roll_no or not name:
#         st.error("Please enter Roll Number and Name")

#     elif lat is None or lon is None:
#         st.error("Location not captured")

#     else:
#         dist = calculate_distance(CLASS_LAT, CLASS_LON, lat, lon)
#         print(dist,CLASS_LAT, CLASS_LON,lat, lon)
#         status = "Present" if dist <= RADIUS_METERS else "Absent"

#         record = {
#             "Roll No": roll_no,
#             "Name": name,
#             "Latitude": lat,
#             "Longitude": lon,
#             "Distance (m)": round(dist, 2),
#             "Status": status,
#             "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         }

#         st.session_state.attendance.append(record)

#         if status == "Present":
#             st.success(f"✅ Marked PRESENT (Distance: {round(dist,2)} m)")
#         else:
#             st.error(f"❌ Outside classroom (Distance: {round(dist,2)} m)")

# # -----------------------------
# # DISPLAY ATTENDANCE
# # -----------------------------
# st.markdown("---")
# st.markdown("### 📊 Attendance Records")

# if st.session_state.attendance:
#     df = pd.DataFrame(st.session_state.attendance)
#     st.dataframe(df)

#     csv = df.to_csv(index=False).encode("utf-8")
#     st.download_button("⬇ Download CSV", csv, "attendance.csv", "text/csv")
# else:
#     st.info("No attendance marked yet")

# # -----------------------------
# # FOOTER
# # -----------------------------
# st.markdown("---")
# st.caption("Developed for Smart Classroom Attendance 🚀")

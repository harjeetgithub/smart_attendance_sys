# =============================
# 📍 GPS-Based Attendance System (Streamlit)
# =============================

import streamlit as st
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
import pandas as pd

# -----------------------------
# CONFIGURATION
# -----------------------------
CLASS_LAT = 30.514422956759578   # Replace with your classroom latitude
CLASS_LON = 76.66044734358132   # Replace with your classroom longitude
RADIUS_METERS = 50    # Allowed distance

# -----------------------------
# DISTANCE FUNCTION (HAVERSINE)
# -----------------------------
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c * 1000  # meters

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "attendance" not in st.session_state:
    st.session_state.attendance = []

# -----------------------------
# UI
# -----------------------------
st.title("📍 Smart GPS Attendance System")

st.markdown("### Enter Details")
roll_no = st.text_input("Roll Number")
name = st.text_input("Name")

from streamlit_js_eval import get_geolocation

st.markdown("### 📍 Capture Location")

location = get_geolocation()

lat, lon = None, None

if location:
    if "coords" in location:
        lat = location["coords"].get("latitude")
        lon = location["coords"].get("longitude")

        st.success(f"Location captured: {lat}, {lon}")
    else:
        st.warning("Location not ready yet or permission denied")
else:
    st.info("Allow location access to continue")

# -----------------------------
# MARK ATTENDANCE
# -----------------------------
if st.button("✅ Mark Attendance"):
    if not roll_no or not name:
        st.error("Please enter Roll Number and Name")

    elif lat is None or lon is None:
        st.error("Location not captured")

    else:
        dist = calculate_distance(CLASS_LAT, CLASS_LON, lat, lon)
        print(dist,CLASS_LAT, CLASS_LON,lat, lon)
        status = "Present" if dist <= RADIUS_METERS else "Absent"

        record = {
            "Roll No": roll_no,
            "Name": name,
            "Latitude": lat,
            "Longitude": lon,
            "Distance (m)": round(dist, 2),
            "Status": status,
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        st.session_state.attendance.append(record)

        if status == "Present":
            st.success(f"✅ Marked PRESENT (Distance: {round(dist,2)} m)")
        else:
            st.error(f"❌ Outside classroom (Distance: {round(dist,2)} m)")

# -----------------------------
# DISPLAY ATTENDANCE
# -----------------------------
st.markdown("---")
st.markdown("### 📊 Attendance Records")

if st.session_state.attendance:
    df = pd.DataFrame(st.session_state.attendance)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download CSV", csv, "attendance.csv", "text/csv")
else:
    st.info("No attendance marked yet")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption("Developed for Smart Classroom Attendance 🚀")

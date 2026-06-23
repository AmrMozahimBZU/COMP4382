import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import get

st.title("🗺️ Live Parcel Map")

try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

if not FOLIUM_AVAILABLE:
    st.warning("Install folium and streamlit-folium for the interactive map: `pip install folium streamlit-folium`")
    st.info("Showing coordinates table instead.")
    data, err = get("/applications/")
    if data:
        apps = data.get("results", [])
        with_loc = [a for a in apps if a.get("parcel_location")]
        st.write(f"**{len(with_loc)} application(s) with GPS location**")
        for app in with_loc:
            coords = app["parcel_location"]["coordinates"]
            st.write(f"• {app.get('applicant_name','N/A')} — Parcel {app.get('parcel_number','N/A')} — Lon: {coords[0]}, Lat: {coords[1]}")
    st.stop()

# Folium map centered on West Bank
m = folium.Map(location=[31.9522, 35.2033], zoom_start=10)

# Filters
with st.sidebar:
    st.subheader("Map Filters")
    show_pending = st.checkbox("Show Pending Applications", True)
    show_survey = st.checkbox("Show Survey Required", True)
    show_approved = st.checkbox("Show Approved", True)

# Fetch applications
data, err = get("/applications/", params={"limit": 100})
if data:
    apps = data.get("results", [])
    color_map = {
        "submitted": "blue", "pre_checked": "cadetblue", "survey_required": "orange",
        "surveyed": "purple", "legal_review": "darkpurple", "approved": "green",
        "certificate_issued": "darkgreen", "rejected": "red", "on_hold": "gray",
        "under_objection": "darkred", "missing_documents": "beige"
    }

    for app in apps:
        loc = app.get("parcel_location")
        if not loc:
            continue
        coords = loc.get("coordinates", [35.2033, 31.9522])
        lng, lat = coords[0], coords[1]
        status = app.get("status", "")

        # Apply filters
        if status in ["submitted", "pre_checked", "missing_documents"] and not show_pending:
            continue
        if status == "survey_required" and not show_survey:
            continue
        if status == "approved" and not show_approved:
            continue

        color = color_map.get(status, "gray")
        popup_html = f"""
        <b>{app.get('application_type','').replace('_',' ').title()}</b><br>
        Applicant: {app.get('applicant_name','N/A')}<br>
        Parcel: {app.get('parcel_number','N/A')}<br>
        Status: <b>{status.upper().replace('_',' ')}</b><br>
        Zone: {app.get('zone','N/A')}
        """
        folium.Marker(
            [lat, lng],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{app.get('parcel_number','?')} — {status}",
            icon=folium.Icon(color=color, icon="home")
        ).add_to(m)

st_folium(m, width=900, height=550)

st.caption("🟢 Approved | 🔵 Submitted | 🟠 Survey Required | 🔴 Rejected | 🟣 Legal Review")

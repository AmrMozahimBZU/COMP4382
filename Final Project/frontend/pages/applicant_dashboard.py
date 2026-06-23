import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import get

st.title("🏠 Applicant Dashboard")

# Quick stats
data, err = get("/applications/analytics/summary")
if err:
    st.warning(f"Backend: {err}")
    data = {"total_applications": "—", "by_status": {}, "by_type": {}}

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Applications", data.get("total_applications", 0))
col2.metric("Submitted", data.get("by_status", {}).get("submitted", 0))
col3.metric("Approved", data.get("by_status", {}).get("approved", 0))
col4.metric("Certificates Issued", data.get("by_status", {}).get("certificate_issued", 0))

st.divider()
st.subheader("📋 Recent Applications")

applicant_id = st.text_input("Enter your Applicant ID to see your applications", placeholder="e.g. 66abc123...")

if applicant_id:
    apps_data, err = get(f"/applicants/{applicant_id}/applications")
    if err:
        st.error(err)
    elif apps_data:
        apps = apps_data.get("applications", [])
        if not apps:
            st.info("No applications found for this applicant.")
        for app in apps:
            status = app.get("status", "unknown")
            color = {"approved": "🟢", "rejected": "🔴", "submitted": "🔵", "on_hold": "🟡"}.get(status, "⚪")
            with st.expander(f"{color} {app.get('application_type','').replace('_',' ').title()} — {status.upper()}"):
                st.write(f"**Application ID:** `{app.get('_id','')}`")
                st.write(f"**Parcel Number:** {app.get('parcel_number','N/A')}")
                st.write(f"**Zone:** {app.get('zone','N/A')}")
                st.write(f"**Submitted:** {app.get('submitted_at','N/A')}")
                if app.get("rejection_reason"):
                    st.error(f"Rejection Reason: {app['rejection_reason']}")

st.divider()
st.info("💡 Use the sidebar to submit a new application, track status, upload documents, or submit an objection.")

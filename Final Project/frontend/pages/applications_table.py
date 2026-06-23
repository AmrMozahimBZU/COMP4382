import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import get

st.title("📋 Applications Management")

# Filters
with st.expander("🔎 Filters", expanded=True):
    col1, col2, col3 = st.columns(3)
    status_filter = col1.selectbox("Status", ["", "submitted", "pre_checked", "survey_required",
        "surveyed", "legal_review", "approved", "certificate_issued", "closed",
        "rejected", "on_hold", "missing_documents", "under_objection"])
    type_filter = col2.selectbox("Type", ["", "first_registration", "ownership_transfer",
        "parcel_subdivision", "parcel_merge", "boundary_correction", "certificate_request"])
    zone_filter = col3.text_input("Zone")
    applicant_filter = st.text_input("Applicant ID")

params = {}
if status_filter: params["status"] = status_filter
if type_filter: params["application_type"] = type_filter
if zone_filter: params["zone"] = zone_filter
if applicant_filter: params["applicant_id"] = applicant_filter

data, err = get("/applications/", params=params)
if err:
    st.error(err)
elif data:
    apps = data.get("results", [])
    st.write(f"**{len(apps)} application(s) found**")

    if apps:
        rows = []
        for app in apps:
            rows.append({
                "ID": app.get("_id","")[:12] + "...",
                "Type": app.get("application_type","").replace("_"," ").title(),
                "Status": app.get("status","").upper().replace("_"," "),
                "Applicant": app.get("applicant_name","N/A"),
                "Parcel": app.get("parcel_number","N/A"),
                "Zone": app.get("zone","N/A"),
                "Submitted": app.get("submitted_at","")[:10],
                "Full ID": app.get("_id","")
            })
        df = pd.DataFrame(rows)
        st.dataframe(df.drop(columns=["Full ID"]), use_container_width=True)

        st.divider()
        st.subheader("Open Application")
        selected_id = st.selectbox("Select by ID", [r["Full ID"] for r in rows])
        if st.button("Open Details →"):
            st.session_state["selected_app_id"] = selected_id
            st.info(f"Go to 'Application Details' in the sidebar. ID copied: `{selected_id}`")

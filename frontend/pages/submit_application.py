import streamlit as st
import sys, os, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import post

st.title("📝 Submit Land Registration Application")

with st.form("submit_app_form"):
    st.subheader("Applicant Information")
    col1, col2 = st.columns(2)
    applicant_name = col1.text_input("Full Name *", placeholder="Mohammad Ahmed")
    applicant_national_id = col2.text_input("National ID *", placeholder="123456789")
    applicant_id = st.text_input("Applicant Profile ID (if registered)", placeholder="Leave blank if not registered")

    st.subheader("Application Type")
    app_type = st.selectbox("Application Type *", [
        "first_registration", "ownership_transfer", "parcel_subdivision",
        "parcel_merge", "boundary_correction", "certificate_request"
    ], format_func=lambda x: x.replace("_", " ").title())

    st.subheader("Parcel Information")
    col1, col2, col3 = st.columns(3)
    parcel_number = col1.text_input("Parcel Number", placeholder="1234/5")
    block_number = col2.text_input("Block Number", placeholder="Block 7")
    basin_number = col3.text_input("Basin Number", placeholder="Basin 12")
    zone = st.text_input("Zone / Area", placeholder="e.g. North Ramallah")

    st.subheader("Parcel Location (Optional)")
    col1, col2 = st.columns(2)
    longitude = col1.number_input("Longitude", value=35.2033, format="%.6f")
    latitude = col2.number_input("Latitude", value=31.9522, format="%.6f")
    include_location = st.checkbox("Include GPS location")

    submitted = st.form_submit_button("🚀 Submit Application", use_container_width=True)

if submitted:
    if not applicant_name or not applicant_national_id:
        st.error("Please fill in all required fields (*).")
    else:
        payload = {
            "application_type": app_type,
            "applicant_name": applicant_name,
            "applicant_national_id": applicant_national_id,
            "parcel_number": parcel_number or None,
            "block_number": block_number or None,
            "basin_number": basin_number or None,
            "zone": zone or None,
            "idempotency_key": str(uuid.uuid4()),
        }
        if applicant_id:
            payload["applicant_id"] = applicant_id
        if include_location:
            payload["parcel_location"] = {"type": "Point", "coordinates": [longitude, latitude]}

        result, err = post("/applications/", payload)
        if err:
            st.error(f"Error: {err}")
        else:
            st.success("✅ Application submitted successfully!")
            st.info(f"**Application ID:** `{result.get('_id', '')}`")
            st.write(f"**Status:** {result.get('status', '')}")
            st.write(f"**Type:** {result.get('application_type', '').replace('_', ' ').title()}")
            st.balloons()

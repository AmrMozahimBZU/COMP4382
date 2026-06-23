import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import get, post

st.title("🏅 Certificate Issuance")

# Show approved applications
data, err = get("/applications/", params={"status": "approved"})
apps = data.get("results", []) if data else []

st.write(f"**{len(apps)} approved application(s) ready for certificate issuance**")

if apps:
    for app in apps:
        with st.expander(f"✅ {app.get('applicant_name','N/A')} — Parcel {app.get('parcel_number','N/A')}"):
            st.write(f"**ID:** `{app.get('_id','')}`")
            st.write(f"**Type:** {app.get('application_type','').replace('_',' ').title()}")
            st.write(f"**Zone:** {app.get('zone','N/A')}")
            st.write(f"**Registrar Remarks:** {app.get('registrar_remarks','N/A')}")
            if st.button(f"🏅 Issue Certificate", key=f"cert_{app['_id']}", use_container_width=True):
                result, err = post(f"/applications/{app['_id']}/certificate", {})
                if err:
                    st.error(err)
                else:
                    st.success(f"Certificate issued!")
                    st.write(f"**Certificate Number:** `{result.get('certificate_number','')}`")
                    st.write(f"**QR Stub:** {result.get('qr_code_stub','')}")
                    st.balloons()
else:
    st.info("No applications approved yet.")

st.divider()
st.subheader("View Issued Certificates")
issued, err = get("/applications/", params={"status": "certificate_issued"})
if issued:
    issued_apps = issued.get("results", [])
    st.write(f"**{len(issued_apps)} certificate(s) issued**")
    for app in issued_apps:
        st.write(f"🏅 `{app.get('certificate_id','N/A')}` — {app.get('applicant_name','N/A')} — Parcel {app.get('parcel_number','N/A')}")

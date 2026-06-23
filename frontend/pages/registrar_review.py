import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import get, patch

st.title("⚖️ Registrar Review")
st.info("Review applications in Legal Review status and make approval/rejection decisions.")

data, err = get("/staff/registrar/review-queue")
if err:
    st.error(err)
    st.stop()

apps = data.get("applications", [])
st.write(f"**{len(apps)} application(s) pending review**")

if not apps:
    st.success("No applications pending legal review.")
    st.stop()

for app in apps:
    with st.expander(f"📄 {app.get('applicant_name','N/A')} — Parcel: {app.get('parcel_number','N/A')} — `{app.get('_id','')}`"):
        col1, col2 = st.columns(2)
        col1.write(f"**Type:** {app.get('application_type','').replace('_',' ').title()}")
        col1.write(f"**Zone:** {app.get('zone','N/A')}")
        col2.write(f"**Submitted:** {app.get('submitted_at','')[:10]}")
        col2.write(f"**Documents:** {len(app.get('documents',[]))} uploaded")

        if app.get("survey_report"):
            r = app["survey_report"]
            st.info(f"📐 Survey: {r.get('findings','')}")

        remarks = st.text_area(f"Registrar Remarks *", key=f"rem_{app['_id']}", placeholder="Enter your legal review decision notes...")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Approve", key=f"approve_{app['_id']}", use_container_width=True):
                if not remarks:
                    st.error("Remarks are required before approving.")
                else:
                    result, err = patch(f"/staff/registrar/{app['_id']}/decision", {"decision": "approve", "remarks": remarks})
                    st.success("Application Approved!") if not err else st.error(err)
        with col2:
            if st.button("❌ Reject", key=f"reject_{app['_id']}", use_container_width=True):
                if not remarks:
                    st.error("Remarks are required before rejecting.")
                else:
                    result, err = patch(f"/staff/registrar/{app['_id']}/decision", {"decision": "reject", "remarks": remarks})
                    st.success("Application Rejected.") if not err else st.error(err)

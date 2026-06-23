import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import post

st.title("⚠️ Submit Objection")
st.warning("Use this page to formally object to a land registration application.")

app_id = st.text_input("Application ID *", placeholder="66abc123...")
applicant_id = st.text_input("Your Applicant ID (optional)")
reason = st.text_area("Objection Reason *", placeholder="Describe your objection in detail...", height=150)
supporting_docs = st.text_input("Supporting Document URLs (comma separated)", placeholder="https://doc1.pdf, https://doc2.pdf")

if st.button("⚠️ Submit Objection", use_container_width=True):
    if not app_id or not reason:
        st.error("Application ID and reason are required.")
    else:
        docs = [d.strip() for d in supporting_docs.split(",") if d.strip()] if supporting_docs else []
        payload = {
            "applicant_id": applicant_id or None,
            "reason": reason,
            "supporting_documents": docs
        }
        result, err = post(f"/applications/{app_id}/objections", payload)
        if err:
            st.error(f"Error: {err}")
        else:
            st.success("✅ Objection submitted. Application moved to 'Under Objection' status.")
            st.write(f"**Objection ID:** `{result.get('_id','')}`")

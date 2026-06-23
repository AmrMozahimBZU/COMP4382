import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import get, patch

st.title("👥 Manage Applicants")

data, err = get("/applicants/")
if err:
    st.error(err)
    st.stop()

applicants = data if isinstance(data, list) else []
st.write(f"**{len(applicants)} registered applicant(s)**")

for ap in applicants:
    v_icon = {"verified": "✅", "unverified": "⏳", "suspended": "🔴"}.get(ap.get("verification_state",""), "⚪")
    with st.expander(f"{v_icon} {ap.get('full_name','')} — {ap.get('applicant_type','').replace('_',' ').title()}"):
        col1, col2 = st.columns(2)
        col1.write(f"**National ID:** {ap.get('national_id','')}")
        col1.write(f"**Email:** {ap.get('email','N/A')}")
        col1.write(f"**Phone:** {ap.get('phone','N/A')}")
        col2.write(f"**Verification:** {ap.get('verification_state','')}")
        col2.write(f"**Registered:** {ap.get('created_at','')[:10]}")

        new_state = st.selectbox("Change verification", ["verified", "unverified", "suspended"], key=f"vs_{ap['_id']}")
        if st.button("Update", key=f"upd_{ap['_id']}"):
            result, err = patch(f"/applicants/{ap['_id']}/verify?state={new_state}")
            st.success("Updated") if not err else st.error(err)

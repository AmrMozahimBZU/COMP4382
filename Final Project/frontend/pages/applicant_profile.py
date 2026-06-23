import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import get, post

st.title("👤 Applicant Profile")

tab1, tab2 = st.tabs(["View Profile", "Register New Applicant"])

with tab1:
    app_id = st.text_input("Enter Applicant ID", placeholder="66abc123...")
    if app_id:
        data, err = get(f"/applicants/{app_id}")
        if err:
            st.error(err)
        elif data:
            st.subheader(data.get("full_name", ""))
            col1, col2 = st.columns(2)
            col1.write(f"**National ID:** {data.get('national_id','')}")
            col1.write(f"**Type:** {data.get('applicant_type','').replace('_',' ').title()}")
            col1.write(f"**Verification:** {data.get('verification_state','')}")
            col2.write(f"**Email:** {data.get('email','N/A')}")
            col2.write(f"**Phone:** {data.get('phone','N/A')}")
            col2.write(f"**Address:** {data.get('address','N/A')}")

with tab2:
    with st.form("register_applicant"):
        st.subheader("Register as Applicant")
        full_name = st.text_input("Full Name *")
        national_id = st.text_input("National ID *")
        applicant_type = st.selectbox("Type", ["citizen", "lawyer", "company", "surveyor", "authorized_representative"],
                                      format_func=lambda x: x.replace("_", " ").title())
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        address = st.text_area("Address")
        lang = st.selectbox("Preferred Language", ["ar", "en"])
        submitted = st.form_submit_button("Register", use_container_width=True)

    if submitted:
        if not full_name or not national_id:
            st.error("Full name and National ID are required.")
        else:
            result, err = post("/applicants/", {
                "full_name": full_name, "national_id": national_id,
                "applicant_type": applicant_type, "email": email or None,
                "phone": phone or None, "address": address or None,
                "preferred_language": lang
            })
            if err:
                st.error(f"Error: {err}")
            else:
                st.success(f"✅ Registered! Your Applicant ID: `{result.get('_id','')}`")
                st.info("Save this ID — you'll need it to submit applications.")

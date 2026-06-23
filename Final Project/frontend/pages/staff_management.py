import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import get, post, patch

st.title("👷 Staff Management")

tab1, tab2 = st.tabs(["View Staff", "Add Staff"])

with tab1:
    data, err = get("/staff/")
    if err:
        st.error(err)
    else:
        staff = data if isinstance(data, list) else []
        st.write(f"**{len(staff)} staff member(s)**")
        for s in staff:
            role_icon = {"surveyor": "📐", "registrar": "⚖️", "manager": "👔"}.get(s.get("role",""), "👤")
            avail = "✅ Available" if s.get("availability") else "❌ Unavailable"
            with st.expander(f"{role_icon} {s.get('full_name','')} — {s.get('role','').title()} — {avail}"):
                st.write(f"**ID:** `{s.get('_id','')}`")
                st.write(f"**National ID:** {s.get('national_id','')}")
                st.write(f"**Email:** {s.get('email','N/A')}")
                st.write(f"**Zones:** {', '.join(s.get('coverage_zones',[]))  or 'None'}")
                st.write(f"**Skills:** {', '.join(s.get('skills',[])) or 'None'}")
                st.write(f"**Workload:** {s.get('current_workload',0)} active tasks")

                new_avail = st.checkbox("Available", value=s.get("availability", True), key=f"avail_{s['_id']}")
                if st.button("Update Availability", key=f"ua_{s['_id']}"):
                    result, err = patch(f"/staff/{s['_id']}/availability", {"available": new_avail})
                    st.success("Updated") if not err else st.error(err)

with tab2:
    with st.form("add_staff"):
        st.subheader("Add New Staff Member")
        full_name = st.text_input("Full Name *")
        national_id = st.text_input("National ID *")
        role = st.selectbox("Role *", ["surveyor", "registrar", "manager"])
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        zones = st.text_input("Coverage Zones (comma separated)", placeholder="North Ramallah, Bireh, Beitin")
        skills = st.text_input("Skills (comma separated)", placeholder="boundary_survey, cadastral")
        submitted = st.form_submit_button("Add Staff Member", use_container_width=True)

    if submitted:
        if not full_name or not national_id:
            st.error("Full name and National ID required.")
        else:
            result, err = post("/staff/", {
                "full_name": full_name,
                "national_id": national_id,
                "role": role,
                "email": email or None,
                "phone": phone or None,
                "coverage_zones": [z.strip() for z in zones.split(",") if z.strip()],
                "skills": [s.strip() for s in skills.split(",") if s.strip()]
            })
            if err:
                st.error(f"Error: {err}")
            else:
                st.success(f"✅ Staff added! ID: `{result.get('_id','')}`")

import streamlit as st

st.set_page_config(
    page_title="LRMIS - Land Registration System",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session state defaults ──
if "role" not in st.session_state:
    st.session_state.role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

st.sidebar.title("🏛️ LRMIS")
st.sidebar.markdown("Land Registration Management System")
st.sidebar.divider()

# ── Role selector (simple login simulation) ──
if st.session_state.role is None:
    st.title("Welcome to LRMIS")
    st.markdown("### Please select your role to continue")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👤 Applicant Portal", use_container_width=True):
            st.session_state.role = "applicant"
            st.rerun()
    with col2:
        if st.button("🏢 Staff / Registrar", use_container_width=True):
            st.session_state.role = "staff"
            st.rerun()
    with col3:
        if st.button("📐 Surveyor", use_container_width=True):
            st.session_state.role = "surveyor"
            st.rerun()
    st.stop()

# ── Sidebar navigation ──
role = st.session_state.role

if st.sidebar.button("🚪 Logout"):
    st.session_state.role = None
    st.rerun()

st.sidebar.markdown(f"**Role:** `{role.upper()}`")
st.sidebar.divider()

if role == "applicant":
    pages = {
        "🏠 Dashboard": "pages/applicant_dashboard.py",
        "📝 Submit Application": "pages/submit_application.py",
        "🔍 Track Application": "pages/track_application.py",
        "📎 Upload Documents": "pages/upload_documents.py",
        "⚠️ Submit Objection": "pages/submit_objection.py",
        "👤 My Profile": "pages/applicant_profile.py",
    }
elif role == "staff":
    pages = {
        "🏠 Staff Dashboard": "pages/staff_dashboard.py",
        "📋 Applications Table": "pages/applications_table.py",
        "🔎 Application Details": "pages/application_details.py",
        "⚖️ Registrar Review": "pages/registrar_review.py",
        "🏅 Issue Certificate": "pages/issue_certificate.py",
        "👥 Manage Applicants": "pages/manage_applicants.py",
    }
elif role == "surveyor":
    pages = {
        "🗂️ My Tasks": "pages/surveyor_tasks.py",
        "📍 Task Execution": "pages/task_execution.py",
        "🗺️ Live Map": "pages/live_map.py",
        "📊 Analytics": "pages/analytics.py",
        "👷 Staff Management": "pages/staff_management.py",
    }

selected = st.sidebar.radio("Navigate", list(pages.keys()))

# ── Load selected page ──
import importlib.util, os, sys

page_file = os.path.join(os.path.dirname(__file__), pages[selected])
spec = importlib.util.spec_from_file_location("page", page_file)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

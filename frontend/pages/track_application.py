import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import get

st.title("🔍 Track Application")

app_id = st.text_input("Enter Application ID", placeholder="e.g. 66abc123def456...")

STATUS_STEPS = [
    "submitted", "pre_checked", "survey_required", "surveyed",
    "legal_review", "approved", "certificate_issued", "closed"
]

def status_progress(status):
    if status in STATUS_STEPS:
        return STATUS_STEPS.index(status) + 1
    return 0

if app_id:
    data, err = get(f"/applications/{app_id}")
    if err:
        st.error(err)
    elif data:
        status = data.get("status", "unknown")

        # Status banner
        color_map = {
            "approved": "success", "rejected": "error", "on_hold": "warning",
            "certificate_issued": "success", "closed": "success"
        }
        msg_type = color_map.get(status, "info")
        getattr(st, msg_type)(f"Current Status: **{status.upper().replace('_',' ')}**")

        # Progress bar
        if status in STATUS_STEPS:
            prog = status_progress(status) / len(STATUS_STEPS)
            st.progress(prog, text=f"Step {status_progress(status)} of {len(STATUS_STEPS)}")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Application Details")
            st.write(f"**Type:** {data.get('application_type','').replace('_',' ').title()}")
            st.write(f"**Applicant:** {data.get('applicant_name','N/A')}")
            st.write(f"**Parcel Number:** {data.get('parcel_number','N/A')}")
            st.write(f"**Zone:** {data.get('zone','N/A')}")
            st.write(f"**Submitted:** {data.get('submitted_at','N/A')}")
            st.write(f"**Last Updated:** {data.get('updated_at','N/A')}")

            if data.get("rejection_reason"):
                st.error(f"❌ Rejection Reason: {data['rejection_reason']}")
            if data.get("hold_reason"):
                st.warning(f"⏸ Hold Reason: {data['hold_reason']}")
            if data.get("missing_documents"):
                st.warning(f"📄 Missing: {', '.join(data['missing_documents'])}")

        with col2:
            st.subheader("Documents")
            docs = data.get("documents", [])
            if docs:
                for doc in docs:
                    verified = "✅" if doc.get("verified") else "⏳"
                    st.write(f"{verified} **{doc.get('type','Unknown')}** — {doc.get('file_name','')}")
            else:
                st.info("No documents uploaded yet.")

            if data.get("certificate_id"):
                st.success(f"🏅 Certificate ID: `{data['certificate_id']}`")

        st.subheader("📅 Status Timeline")
        timeline = data.get("status_history", [])
        if timeline:
            for entry in reversed(timeline):
                icon = {"submitted": "📬", "approved": "✅", "rejected": "❌", "surveyed": "📐"}.get(entry.get("status",""), "📌")
                st.write(f"{icon} **{entry.get('status','').upper().replace('_',' ')}** — {entry.get('timestamp','')}  \n_{entry.get('note','')}_")
        else:
            st.info("No timeline entries yet.")

        if data.get("survey_report"):
            st.subheader("📐 Survey Report")
            report = data["survey_report"]
            st.write(f"**Title:** {report.get('title','')}")
            st.write(f"**Findings:** {report.get('findings','')}")
            st.write(f"**Uploaded:** {report.get('uploaded_at','')}")

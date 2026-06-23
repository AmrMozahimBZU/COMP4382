import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import get, patch, post

st.title("📍 Survey Task Execution")

task_id = st.text_input("Task ID", placeholder="66abc123...")
surveyor_id = st.text_input("Your Staff ID", placeholder="66abc123...")

if task_id:
    data, err = get(f"/staff/tasks/{task_id}/milestone")

    st.divider()
    st.subheader("Update Milestone")
    milestones = ["assigned", "visit_scheduled", "arrived_on_site", "survey_started", "survey_completed", "report_uploaded", "registrar_reviewed"]
    new_milestone = st.selectbox("New Milestone", milestones)
    note = st.text_input("Note (optional)")

    if st.button("✅ Update Milestone", use_container_width=True):
        result, err = patch(f"/staff/tasks/{task_id}/milestone", {"milestone": new_milestone, "note": note})
        if err:
            st.error(err)
        else:
            st.success(f"Milestone updated to: {new_milestone}")

    st.divider()
    st.subheader("📄 Upload Survey Report")
    with st.form("report_form"):
        report_title = st.text_input("Report Title *")
        findings = st.text_area("Findings *", placeholder="Describe what was found during the field survey...")
        recommendations = st.text_area("Recommendations", placeholder="Any recommendations...")
        sid = st.text_input("Surveyor Staff ID *", value=surveyor_id)
        submitted = st.form_submit_button("Upload Report", use_container_width=True)

    if submitted:
        if not report_title or not findings or not sid:
            st.error("Title, findings, and surveyor ID are required.")
        else:
            result, err = post(f"/staff/tasks/{task_id}/report", {
                "surveyor_id": sid,
                "report_title": report_title,
                "findings": findings,
                "recommendations": recommendations or None
            })
            if err:
                st.error(err)
            else:
                st.success("✅ Report uploaded! Application marked as 'Surveyed'.")
                st.write(f"**Application ID:** `{result.get('task',{}).get('application_id','')}`")

    st.divider()
    st.subheader("Add Field Notes")
    field_note = st.text_area("Field Notes")
    if st.button("Save Notes"):
        st.info("Field notes saved locally. (Full integration via PATCH /staff/tasks/{id}/notes)")

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import get, post, patch

st.title("🔎 Application Details")

app_id = st.text_input("Application ID", value=st.session_state.get("selected_app_id", ""))

if not app_id:
    st.info("Enter an application ID or select one from the Applications Table.")
    st.stop()

data, err = get(f"/applications/{app_id}")
if err:
    st.error(err)
    st.stop()

status = data.get("status", "")

# Header
st.subheader(f"{data.get('application_type','').replace('_',' ').title()} — `{status.upper().replace('_',' ')}`")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["📄 Details", "🔄 Workflow", "📎 Documents & Notes", "⚖️ Decisions"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Applicant**")
        st.write(f"Name: {data.get('applicant_name','N/A')}")
        st.write(f"National ID: {data.get('applicant_national_id','N/A')}")
        st.write(f"Applicant ID: {data.get('applicant_id','N/A')}")
    with col2:
        st.markdown("**Parcel**")
        st.write(f"Parcel No: {data.get('parcel_number','N/A')}")
        st.write(f"Block: {data.get('block_number','N/A')}")
        st.write(f"Basin: {data.get('basin_number','N/A')}")
        st.write(f"Zone: {data.get('zone','N/A')}")

    if data.get("parcel_location"):
        loc = data["parcel_location"]["coordinates"]
        st.info(f"📍 Location: Longitude {loc[0]}, Latitude {loc[1]}")

with tab2:
    st.subheader("Status Timeline")
    for entry in reversed(data.get("status_history", [])):
        icon = {"submitted": "📬", "approved": "✅", "rejected": "❌", "surveyed": "📐", "certificate_issued": "🏅"}.get(entry.get("status",""), "📌")
        st.write(f"{icon} **{entry.get('status','').upper().replace('_',' ')}** — {entry.get('timestamp','')}")
        if entry.get("note"):
            st.caption(entry["note"])

    st.divider()
    st.subheader("Transition Status")

    VALID = {
        "submitted": ["pre_checked", "missing_documents", "rejected"],
        "pre_checked": ["survey_required", "legal_review", "missing_documents"],
        "survey_required": ["surveyed", "on_hold"],
        "surveyed": ["legal_review"],
        "legal_review": ["approved", "rejected", "under_objection"],
        "approved": ["certificate_issued"],
        "certificate_issued": ["closed"],
        "missing_documents": ["pre_checked", "rejected"],
        "under_objection": ["legal_review", "rejected", "on_hold"],
        "on_hold": ["survey_required", "legal_review", "rejected"],
    }
    allowed = VALID.get(status, [])
    if allowed:
        new_status = st.selectbox("Move to", allowed)
        note = st.text_input("Transition note")
        if st.button("Apply Transition"):
            result, err = patch(f"/applications/{app_id}/transition", {"new_status": new_status, "note": note})
            if err:
                st.error(err)
            else:
                st.success(f"Moved to {new_status}")
                st.rerun()
    else:
        st.info("No further transitions available.")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        hold_reason = st.text_input("Hold Reason")
        if st.button("⏸ Place on Hold"):
            result, err = post(f"/applications/{app_id}/hold", {"reason": hold_reason})
            st.success("Placed on hold") if not err else st.error(err)
    with col2:
        reject_reason = st.text_input("Rejection Reason")
        if st.button("❌ Reject"):
            result, err = post(f"/applications/{app_id}/reject", {"reason": reject_reason})
            st.success("Application rejected") if not err else st.error(err)

    if status == "survey_required" and not data.get("survey_task_id"):
        if st.button("📐 Auto-Assign Surveyor"):
            result, err = post(f"/applications/{app_id}/auto-assign-surveyor", {})
            st.success(f"Assigned: {result.get('message','')}") if not err else st.error(err)

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Documents")
        docs = data.get("documents", [])
        if docs:
            for doc in docs:
                v = "✅" if doc.get("verified") else "⏳"
                st.write(f"{v} **{doc.get('type','')}** — {doc.get('file_name','')}")
        else:
            st.info("No documents uploaded.")

        st.markdown("**Add Document**")
        doc_type = st.selectbox("Type", ["ownership_deed","national_id_copy","survey_map","title_deed","other"])
        fname = st.text_input("File name")
        if st.button("Add Document"):
            result, err = post(f"/applications/{app_id}/documents", {"document_type": doc_type, "file_name": fname})
            st.success("Added") if not err else st.error(err)

    with col2:
        st.subheader("Internal Notes")
        notes = data.get("internal_notes", [])
        if notes:
            for note in notes:
                st.write(f"💬 **{note.get('by','')}** ({note.get('timestamp','')[:10]}): {note.get('comment','')}")
        else:
            st.info("No notes yet.")

        comment = st.text_area("Add note")
        if st.button("Add Note"):
            result, err = post(f"/applications/{app_id}/comments", {"comment": comment})
            st.success("Note added") if not err else st.error(err)

with tab4:
    st.subheader("Registrar Remarks")
    st.write(data.get("registrar_remarks") or "No remarks yet.")
    if data.get("survey_report"):
        st.subheader("Survey Report")
        r = data["survey_report"]
        st.write(f"**{r.get('title','')}**")
        st.write(f"Findings: {r.get('findings','')}")
        st.write(f"Recommendations: {r.get('recommendations','')}")

    if status == "approved" and not data.get("certificate_id"):
        if st.button("🏅 Issue Certificate"):
            result, err = post(f"/applications/{app_id}/certificate", {})
            if err:
                st.error(err)
            else:
                st.success(f"Certificate issued: `{result.get('certificate_number','')}`")
                st.balloons()

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import get

st.title("🗂️ My Survey Tasks")

surveyor_id = st.text_input("Your Staff ID", placeholder="66abc123...")

MILESTONE_ICON = {
    "assigned": "📋", "visit_scheduled": "📅", "arrived_on_site": "📍",
    "survey_started": "🔭", "survey_completed": "✔️", "report_uploaded": "📄",
    "registrar_reviewed": "✅"
}

if surveyor_id:
    data, err = get(f"/staff/{surveyor_id}/tasks")
    if err:
        st.error(err)
    elif data:
        tasks = data.get("tasks", [])
        st.write(f"**{len(tasks)} task(s) assigned to you**")

        if not tasks:
            st.info("No tasks assigned.")
        else:
            for task in tasks:
                milestone = task.get("milestone", "assigned")
                icon = MILESTONE_ICON.get(milestone, "📋")
                priority_label = {1: "🟢 Low", 2: "🟡 Medium", 3: "🔴 High"}.get(task.get("priority", 1), "🟢")
                with st.expander(f"{icon} Parcel: {task.get('parcel_number','N/A')} — {milestone.upper().replace('_',' ')} — {priority_label}"):
                    st.write(f"**Task ID:** `{task.get('_id','')}`")
                    st.write(f"**Application ID:** `{task.get('application_id','')}`")
                    st.write(f"**Zone:** {task.get('zone','N/A')}")
                    st.write(f"**Assigned:** {task.get('assigned_at','')[:10]}")
                    if task.get("scheduled_date"):
                        st.write(f"**Scheduled:** {task['scheduled_date'][:10]}")
                    if task.get("field_notes"):
                        st.write(f"**Notes:** {task['field_notes']}")

                    st.markdown("**Milestone History:**")
                    for h in task.get("milestone_history", []):
                        st.write(f"  {MILESTONE_ICON.get(h.get('milestone',''),'•')} {h.get('milestone','').replace('_',' ')} — {h.get('timestamp','')[:16]}")

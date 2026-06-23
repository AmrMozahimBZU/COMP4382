import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import get

st.title("📊 Analytics Dashboard")

data, err = get("/applications/analytics/summary")
if err:
    st.error(err)
    st.stop()

bs = data.get("by_status", {})
bt = data.get("by_type", {})
total = data.get("total_applications", 0)

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Applications", total)
col2.metric("Approved", bs.get("approved", 0) + bs.get("certificate_issued", 0) + bs.get("closed", 0))
col3.metric("Rejected", bs.get("rejected", 0))
col4.metric("Pending", bs.get("submitted", 0) + bs.get("pre_checked", 0) + bs.get("legal_review", 0))

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Applications by Status")
    if bs:
        df_status = pd.DataFrame(list(bs.items()), columns=["Status", "Count"])
        df_status["Status"] = df_status["Status"].str.replace("_", " ").str.title()
        st.bar_chart(df_status.set_index("Status"))

with col2:
    st.subheader("Applications by Type")
    if bt:
        df_type = pd.DataFrame(list(bt.items()), columns=["Type", "Count"])
        df_type["Type"] = df_type["Type"].str.replace("_", " ").str.title()
        st.bar_chart(df_type.set_index("Type"))

st.divider()
st.subheader("Surveyor Workload")
staff_data, err = get("/staff/", params={"role": "surveyor"} if False else {})
if staff_data and isinstance(staff_data, list):
    surveyors = [s for s in staff_data if s.get("role") == "surveyor"]
    if surveyors:
        df_staff = pd.DataFrame([{
            "Name": s.get("full_name",""),
            "Workload": s.get("current_workload", 0),
            "Available": "✅" if s.get("availability") else "❌",
            "Zones": ", ".join(s.get("coverage_zones", []))
        } for s in surveyors])
        st.dataframe(df_staff, use_container_width=True)
    else:
        st.info("No surveyors registered yet.")

st.divider()
st.subheader("Review Queue")
review, err = get("/staff/registrar/review-queue")
if review:
    count = review.get("pending_legal_review", 0)
    st.metric("Applications Awaiting Legal Review", count)
    if count > 5:
        st.warning("⚠️ High backlog in legal review queue!")

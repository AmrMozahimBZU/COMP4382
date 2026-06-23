import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import get

st.title("🏢 Staff Dashboard")

data, err = get("/applications/analytics/summary")
if err:
    st.warning(f"Backend: {err}")
    data = {"total_applications": 0, "by_status": {}, "by_type": {}}

bs = data.get("by_status", {})
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total", data.get("total_applications", 0))
col2.metric("Submitted", bs.get("submitted", 0))
col3.metric("Legal Review", bs.get("legal_review", 0))
col4.metric("Missing Docs", bs.get("missing_documents", 0))
col5.metric("Under Objection", bs.get("under_objection", 0))

st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("Applications by Status")
    if bs:
        import pandas as pd
        df = pd.DataFrame(list(bs.items()), columns=["Status", "Count"])
        st.bar_chart(df.set_index("Status"))
    else:
        st.info("No data yet.")

with col2:
    st.subheader("Applications by Type")
    bt = data.get("by_type", {})
    if bt:
        import pandas as pd
        df2 = pd.DataFrame(list(bt.items()), columns=["Type", "Count"])
        st.bar_chart(df2.set_index("Type"))
    else:
        st.info("No data yet.")

st.divider()
st.subheader("⚖️ Legal Review Queue")
review_data, err = get("/staff/registrar/review-queue")
if review_data:
    apps = review_data.get("applications", [])
    st.write(f"**{len(apps)} application(s) pending legal review**")
    for app in apps[:5]:
        st.write(f"• `{app.get('_id','')}` — {app.get('applicant_name','N/A')} — Parcel: {app.get('parcel_number','N/A')}")

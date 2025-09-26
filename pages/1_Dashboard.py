# pages/1_Dashboard.py
import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Dashboard — PowerScan", layout="wide")

st.title("📊 Dashboard — PowerScan Web Feature Checker")

# 🔄 Refresh button
if st.button("🔄 Refresh Data"):
    st.rerun()

# ---------------------------
# Load last scan results
# ---------------------------
if os.path.exists("scan_results.json"):
    with open("scan_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
else:
    st.info("⚠️ No scan_results.json found yet. Run a scan on the main page first.")
    st.stop()

# ---------------------------
# Summary Table
# ---------------------------
st.subheader("Summary of Last Scan")
st.dataframe(df)

# ---------------------------
# Chart: Findings per Feature
# ---------------------------
if not df.empty:
    st.subheader("Findings by Feature")
    feature_counts = df.groupby("Feature")["Count"].sum().sort_values(ascending=False)
    st.bar_chart(feature_counts)

# ---------------------------
# Top 5 Risky Features
# ---------------------------
st.subheader("Top 5 Risky Features (by count)")
top5 = (
    df.groupby(["Feature", "Severity"])["Count"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
st.table(top5)

# ---------------------------
# Chart: Severity Distribution
# ---------------------------
st.subheader("Severity Distribution")
severity_counts = df.groupby("Severity")["Count"].sum()
st.bar_chart(severity_counts)

st.success("✅ Dashboard loaded successfully!")

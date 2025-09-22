# app.py — Day 6 with Group By Severity or File
import streamlit as st
import pandas as pd
import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict

st.set_page_config(page_title="Baseline Feature Checker — Day 6", layout="wide")

# ---------------------------
# Load patterns
# ---------------------------
with open("patterns.json", "r", encoding="utf-8") as f:
    PATTERNS: List[Dict] = json.load(f)

NAME_TO_ID = {p["name"]: p["id"] for p in PATTERNS}
ID_TO_PATTERN = {p["id"]: p for p in PATTERNS}

def decode_bytes(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except Exception:
        return raw.decode("utf-8", errors="replace")

def find_matches(text: str, regex: str):
    flags = re.IGNORECASE | re.MULTILINE
    try:
        return list(re.finditer(regex, text, flags))
    except re.error:
        return []

def scan_html(text: str, pattern_ids: List[str]):
    """Parse HTML using BeautifulSoup and also run regex on script content"""
    soup = BeautifulSoup(text, "lxml")
    findings = []

    # Check each selected pattern
    for pid in pattern_ids:
        pat = ID_TO_PATTERN[pid]
        if pat["group"] == "html" and "<video" in pat["regex"]:
            videos = soup.find_all("video")
            if videos:
                findings.append({
                    "Feature": pat["name"],
                    "Severity": pat["severity"],
                    "Count": len(videos),
                    "Lines": "N/A",
                    "Snippet": str(videos[0])[:100]
                })
        elif pat["group"] == "html" and "style=" in pat["regex"]:
            styled = [tag for tag in soup.find_all(True) if tag.has_attr("style")]
            if styled:
                findings.append({
                    "Feature": pat["name"],
                    "Severity": pat["severity"],
                    "Count": len(styled),
                    "Lines": "N/A",
                    "Snippet": str(styled[0])[:100]
                })
        else:
            matches = find_matches(text, pat["regex"])
            if matches:
                snippet = text[matches[0].start():matches[0].end()+80]
                findings.append({
                    "Feature": pat["name"],
                    "Severity": pat["severity"],
                    "Count": len(matches),
                    "Lines": "approx",
                    "Snippet": snippet.strip()
                })
    return findings

def scan_file(file, pattern_ids: List[str]):
    raw = file.read()
    text = decode_bytes(raw)

    if file.name.endswith(".html"):
        findings = scan_html(text, pattern_ids)
    else:
        findings = []
        for pid in pattern_ids:
            pat = ID_TO_PATTERN[pid]
            matches = find_matches(text, pat["regex"])
            if matches:
                snippet = text[matches[0].start():matches[0].end()+80]
                findings.append({
                    "Feature": pat["name"],
                    "Severity": pat["severity"],
                    "Count": len(matches),
                    "Lines": "approx",
                    "Snippet": snippet.strip()
                })

    return file.name, round(len(raw)/1024, 2), findings

# ---------------------------
# Sidebar settings
# ---------------------------
st.sidebar.header("Scanner Settings")
all_feature_names = [p["name"] for p in PATTERNS]
selected_features = st.sidebar.multiselect("Select features", all_feature_names, default=all_feature_names)
selected_pattern_ids = [NAME_TO_ID[n] for n in selected_features]

show_snippets = st.sidebar.checkbox("Show code snippets", True)
severity_filter = st.sidebar.multiselect("Filter severities", ["major","minor"], default=["major","minor"])
selected_pattern_ids = [pid for pid in selected_pattern_ids if ID_TO_PATTERN[pid]["severity"] in severity_filter]

# --- Grouping option ---
group_by = st.sidebar.radio("Group chart by:", ["File", "Severity"], index=0)

# ---------------------------
# Main UI
# ---------------------------
st.title("🚀 Baseline Web Feature Checker — Day 6")
uploaded_files = st.file_uploader("📂 Upload .html, .css, or .js files", type=["html","css","js"], accept_multiple_files=True)

if uploaded_files:
    results = []
    chart_data = []
    severity_chart_data = []  # for severity grouping

    for file in uploaded_files:
        name, size_kb, findings = scan_file(file, selected_pattern_ids)
        total_findings = sum(f["Count"] for f in findings)

        results.append({"File": name, "Size (KB)": size_kb, "Findings": total_findings})

        # --- group by severity counts ---
        severity_counts = {}
        for f in findings:
            sev = f["Severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + f["Count"]

        for sev, cnt in severity_counts.items():
            severity_chart_data.append({"File": name, "Severity": sev, "Count": cnt})

        # old chart data (total only)
        chart_data.append({"File": name, "Total": total_findings})

        with st.expander(f"{name} — {size_kb} KB — {total_findings} findings"):
            if findings:
                df = pd.DataFrame(findings)

                def color_severity(val):
                    color = "red" if val=="major" else "orange"
                    return f"color: {color}; font-weight:bold;"

                st.dataframe(df.style.applymap(color_severity, subset=["Severity"]))

                if show_snippets:
                    for row in findings:
                        st.markdown(f"**{row['Feature']}** (Count: {row['Count']})")
                        st.code(row["Snippet"], language="html")
            else:
                st.success("No selected features found in this file.")

    # Summary table
    st.markdown("### 📊 Summary Table")
    summary_df = pd.DataFrame(results)
    st.dataframe(summary_df)

    # --- Flexible bar chart ---
    st.markdown("### 📈 Findings Chart")
    if group_by == "File":
        chart_df = pd.DataFrame(chart_data)
        st.bar_chart(chart_df.set_index("File"))
    else:
        sev_df = pd.DataFrame(severity_chart_data)
        if not sev_df.empty:
            pivot_df = sev_df.pivot_table(
                index="File",
                columns="Severity",
                values="Count",
                aggfunc="sum",
                fill_value=0
            )
            st.bar_chart(pivot_df)
        else:
            st.info("No severity data available.")

else:
    st.info("⬆️ Upload files to start scanning.")

# app.py — Day 5
import streamlit as st
import pandas as pd
import json
import re
from typing import List, Dict

st.set_page_config(page_title="Baseline Feature Checker", layout="wide")

# ---------------------------
# Load patterns dynamically
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

def scan_text(text: str, pattern_ids: List[str]):
    findings = []
    for pid in pattern_ids:
        pat = ID_TO_PATTERN[pid]
        matches = find_matches(text, pat["regex"])
        if matches:
            lines = sorted({text.count("\n", 0, m.start()) + 1 for m in matches})
            snippet = text[matches[0].start():matches[0].end()+80]
            findings.append({
                "Feature": pat["name"],
                "Severity": pat["severity"],
                "Count": len(matches),
                "Lines": ", ".join(map(str, lines)),
                "Snippet": snippet.strip()
            })
    return findings

def scan_file(file, pattern_ids: List[str]):
    raw = file.read()
    text = decode_bytes(raw)
    findings = scan_text(text, pattern_ids)
    return file.name, round(len(raw)/1024,2), findings

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

# ---------------------------
# Main UI
# ---------------------------
st.title("🚀 Baseline Web Feature Checker — Day 5")
uploaded_files = st.file_uploader("📂 Upload .html, .css, or .js files", type=["html","css","js"], accept_multiple_files=True)

if uploaded_files:
    results = []
    chart_data = []
    for file in uploaded_files:
        name, size_kb, findings = scan_file(file, selected_pattern_ids)
        total_findings = sum(f["Count"] for f in findings)
        results.append({"File": name, "Size (KB)": size_kb, "Findings": total_findings})
        chart_data.append({"File": name, "Total": total_findings})

        with st.expander(f"{name} — {size_kb} KB — {total_findings} findings"):
            if findings:
                df = pd.DataFrame(findings)
                # Apply color badges for severity
                def color_severity(val):
                    color = "red" if val=="major" else "orange"
                    return f"color: {color}; font-weight:bold;"
                st.dataframe(df.style.applymap(color_severity, subset=["Severity"]))
                if show_snippets:
                    for row in findings:
                        st.markdown(f"**{row['Feature']}** (Lines: {row['Lines']})")
                        st.code(row["Snippet"], language="html")
            else:
                st.success("No selected features found in this file.")

    # Summary table
    st.markdown("### 📊 Summary Table")
    summary_df = pd.DataFrame(results)
    st.dataframe(summary_df)

    # Bar chart
    st.markdown("### 📈 Features per File")
    chart_df = pd.DataFrame(chart_data)
    st.bar_chart(chart_df.set_index("File"))

    # Download buttons
    st.markdown("### ⬇️ Download Reports")
    st.download_button("Download JSON", data=json.dumps(results, indent=2), file_name="scan_results.json")
    st.download_button("Download CSV", data=summary_df.to_csv(index=False), file_name="scan_results.csv")

    st.success("Day 5 complete — dynamic patterns, color badges, and charts added.")
else:
    st.info("⬆️ Upload files to start scanning.")

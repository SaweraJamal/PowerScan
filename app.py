# app.py — Day 6 (Group by Severity/File + Downloads)
import streamlit as st
import pandas as pd
import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

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

    for pid in pattern_ids:
        pat = ID_TO_PATTERN[pid]
        if pat["group"] == "html" and "<video" in pat["regex"]:
            videos = soup.find_all("video")
            if videos:
                findings.append({
                    "File": None,
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
                    "File": None,
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
                    "File": None,
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
                    "File": None,
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

group_by = st.sidebar.radio("Group chart by:", ["File", "Severity"], index=0)

# ---------------------------
# Main UI
# ---------------------------
st.title("🚀 Baseline Web Feature Checker — Day 6")
uploaded_files = st.file_uploader("📂 Upload .html, .css, or .js files", type=["html","css","js"], accept_multiple_files=True)

if uploaded_files:
    results = []
    chart_data = []
    severity_chart_data = []
    all_findings_list = []

    for file in uploaded_files:
        name, size_kb, findings = scan_file(file, selected_pattern_ids)
        total_findings = sum(f["Count"] for f in findings)

        # attach file name to each finding for export
        for f in findings:
            f["File"] = name

        results.append({"File": name, "Size (KB)": size_kb, "Findings": total_findings})

        severity_counts = {}
        for f in findings:
            sev = f["Severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + f["Count"]
        for sev, cnt in severity_counts.items():
            severity_chart_data.append({"File": name, "Severity": sev, "Count": cnt})

        chart_data.append({"File": name, "Total": total_findings})

        if findings:
            df = pd.DataFrame(findings)
            all_findings_list.append(df)

        with st.expander(f"{name} — {size_kb} KB — {total_findings} findings"):
            if findings:
                df_disp = pd.DataFrame(findings)

                def color_severity(val):
                    color = "red" if val=="major" else "orange"
                    return f"color: {color}; font-weight:bold;"

                st.dataframe(df_disp.style.applymap(color_severity, subset=["Severity"]))

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

    # Flexible bar chart
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

    # ---------------------------
    # Download Buttons (Excel & PDF)
    # ---------------------------
    if all_findings_list:
        all_findings_df = pd.concat(all_findings_list, ignore_index=True)

        # Excel download
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            all_findings_df.to_excel(writer, index=False, sheet_name="Scan Results")
        st.download_button(
            label="📥 Download Excel Report",
            data=excel_buffer.getvalue(),
            file_name="scan_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # PDF download
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer)
        styles = getSampleStyleSheet()
        story = [Paragraph("Scan Results", styles["Title"]), Spacer(1, 12)]

        data = [list(all_findings_df.columns)] + all_findings_df.values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.grey),
            ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ]))
        story.append(table)
        doc.build(story)

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer.getvalue(),
            file_name="scan_results.pdf",
            mime="application/pdf"
        )

else:
    st.info("⬆️ Upload files to start scanning.")

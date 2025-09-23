# app.py — Day 8 + Excel & PDF Download
import streamlit as st
import pandas as pd
import json
import re
import io
from typing import List, Dict

# PDF libraries
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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

# ✅ Highlight matched patterns
def highlight_patterns(text: str, selected_patterns: list) -> str:
    highlighted = text
    for pat in selected_patterns:
        try:
            regex = re.compile(pat["regex"], re.IGNORECASE)
            highlighted = regex.sub(
                lambda m: f"<mark style='background:yellow;color:black;'>{m.group(0)}</mark>",
                highlighted
            )
        except re.error:
            pass
    return highlighted

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
    return file.name, round(len(raw)/1024,2), findings, text

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
show_highlighted_code = st.sidebar.checkbox("Show highlighted source", True)

# ---------------------------
# Main UI
# ---------------------------
st.title("🚀 Baseline Web Feature Checker — Day 8")
uploaded_files = st.file_uploader("📂 Upload .html, .css, or .js files", type=["html","css","js"], accept_multiple_files=True)

if uploaded_files:
    results = []
    chart_data = []
    all_findings_list = []

    for file in uploaded_files:
        name, size_kb, findings, text = scan_file(file, selected_pattern_ids)
        total_findings = sum(f["Count"] for f in findings)
        results.append({"File": name, "Size (KB)": size_kb, "Findings": total_findings})
        chart_data.append({"File": name, "Total": total_findings})

        with st.expander(f"{name} — {size_kb} KB — {total_findings} findings"):
            if findings:
                df = pd.DataFrame(findings)
                all_findings_list.append(df)

                def color_severity(val):
                    color = "red" if val=="major" else "orange"
                    return f"color: {color}; font-weight:bold;"

                st.dataframe(df.style.applymap(color_severity, subset=["Severity"]))

                if show_snippets:
                    for row in findings:
                        st.markdown(f"**{row['Feature']}** (Lines: {row['Lines']})")
                        st.code(row["Snippet"], language="html")

                # ✅ Highlighted code view
                if show_highlighted_code:
                    st.markdown("### Highlighted Source Code")
                    highlighted_html = highlight_patterns(text, [ID_TO_PATTERN[pid] for pid in selected_pattern_ids])
                    st.markdown(f"<pre>{highlighted_html}</pre>", unsafe_allow_html=True)
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

    # ---------------------------
    # Download buttons (JSON, CSV, Excel, PDF)
    # ---------------------------
    if all_findings_list:
        all_findings_df = pd.concat(all_findings_list, ignore_index=True)
        st.markdown("### ⬇️ Download Reports")

        # JSON
        st.download_button(
            "Download JSON",
            data=all_findings_df.to_json(orient="records", indent=2),
            file_name="scan_results.json"
        )

        # CSV
        st.download_button(
            "Download CSV",
            data=summary_df.to_csv(index=False),
            file_name="scan_results.csv"
        )

        # Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            all_findings_df.to_excel(writer, index=False, sheet_name="Scan Results")
        st.download_button(
            label="Download Excel",
            data=excel_buffer.getvalue(),
            file_name="scan_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # PDF
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
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
            label="Download PDF",
            data=pdf_buffer.getvalue(),
            file_name="scan_results.pdf",
            mime="application/pdf"
        )

    st.success("Day 8 complete — highlighting added + Excel/PDF downloads.")
else:
    st.info("⬆️ Upload files to start scanning.")

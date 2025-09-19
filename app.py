# app.py — Day 4
import streamlit as st
import re
import json
import pandas as pd
from typing import List, Dict

st.set_page_config(page_title="Baseline Web Feature Checker", layout="wide")

# ---------------------------
# Default pattern database
# ---------------------------
PATTERNS: List[Dict] = [
    # HTML
    {"id": "module_script", "name": "Module <script>", "regex": r'<script[^>]+type=["\']module["\']', "description": "ES module script tag (<script type='module'>).", "severity": "major", "group": "html"},
    {"id": "web_component_tag", "name": "Web Component tag", "regex": r'<[a-z0-9]+-[a-z0-9\-]*\b', "description": "Custom element / Web Component tag (contains a hyphen).", "severity": "major", "group": "html"},
    {"id": "template_slot", "name": "Template / Slot", "regex": r'<template\b|<slot\b', "description": "<template> or <slot> elements (used with Web Components).", "severity": "minor", "group": "html"},
    {"id": "dialog_elem", "name": "Dialog element", "regex": r'<dialog\b', "description": "<dialog> element (native dialog UI).", "severity": "minor", "group": "html"},
    {"id": "manifest_link", "name": "Web App Manifest", "regex": r'rel=["\']manifest["\']', "description": "Links to a web app manifest (site manifest).", "severity": "minor", "group": "html"},
    {"id": "preload_rel", "name": "preload/preconnect", "regex": r'rel=["\'](preload|modulepreload|preconnect|prefetch)["\']', "description": "Resource preloads / preconnect / prefetch hints.", "severity": "minor", "group": "html"},

    # CSS
    {"id": "css_variables", "name": "CSS Variables", "regex": r'--[a-zA-Z0-9_-]+\s*:', "description": "CSS custom properties (variables).", "severity": "minor", "group": "css"},
    {"id": "css_grid", "name": "CSS Grid", "regex": r'display\s*:\s*grid\b|grid-template', "description": "CSS Grid layout usage.", "severity": "major", "group": "css"},
    {"id": "css_flex", "name": "CSS Flexbox", "regex": r'display\s*:\s*flex\b', "description": "Flexbox usage.", "severity": "minor", "group": "css"},
    {"id": "css_keyframes", "name": "@keyframes / animations", "regex": r'@keyframes\b', "description": "CSS animations defined with @keyframes.", "severity": "minor", "group": "css"},
    {"id": "container_queries", "name": "Container queries", "regex": r'@container\b|container-type', "description": "CSS Container Queries (modern responsive feature).", "severity": "major", "group": "css"},
    {"id": "backdrop_filter", "name": "backdrop-filter", "regex": r'backdrop-filter\b', "description": "backdrop-filter (visual effect).", "severity": "minor", "group": "css"},

    # JS
    {"id": "es_modules", "name": "ES Modules (import/export)", "regex": r'^\s*(import\s+.+from\s+|export\s+)', "description": "ES module imports or exports (modern JS modules).", "severity": "major", "group": "js"},
    {"id": "dynamic_import", "name": "Dynamic import()", "regex": r'\bimport\(\s*[\'\"\`]', "description": "Dynamic import(...) usage.", "severity": "minor", "group": "js"},
    {"id": "async_await", "name": "Async / Await", "regex": r'\basync\b|\bawait\b', "description": "Async/await usage (modern async syntax).", "severity": "minor", "group": "js"},
    {"id": "arrow_fn", "name": "Arrow functions", "regex": r'=>', "description": "Arrow function syntax (=>).", "severity": "minor", "group": "js"},
    {"id": "fetch_api", "name": "Fetch API", "regex": r'\bfetch\s*\(', "description": "fetch(...) network calls.", "severity": "major", "group": "js"},
    {"id": "service_worker", "name": "Service Worker registration", "regex": r'navigator\.serviceWorker\.register', "description": "Service worker registration (PWA related).", "severity": "major", "group": "js"},
    {"id": "custom_elements_api", "name": "Custom Elements API", "regex": r'customElements\.define', "description": "customElements.define (web components).", "severity": "major", "group": "js"},
    {"id": "jquery", "name": "jQuery usage", "regex": r'\b(jQuery\(|\$\()', "description": "jQuery selector / usage.", "severity": "minor", "group": "js"},
    {"id": "react_indicator", "name": "React indicator", "regex": r'\bReactDOM\.render\b|\bfrom\s+[\'\"]react[\'\"]', "description": "Possible React usage (ReactDOM.render or import from 'react').", "severity": "major", "group": "js"},
]

# Helper: map name->pattern id and id->pattern
NAME_TO_ID = {p["name"]: p["id"] for p in PATTERNS}
ID_TO_PATTERN = {p["id"]: p for p in PATTERNS}

# ---------------------------
# Helper functions
# ---------------------------
def decode_bytes(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except Exception:
        return raw.decode("utf-8", errors="replace")

def get_snippet(text: str, start: int, end: int, context=80) -> str:
    s = max(0, start - context)
    e = min(len(text), end + context)
    snippet = text[s:e]
    # replace newlines with visible breaks for display
    return snippet.strip()

def find_matches_for_pattern(text: str, regex: str):
    flags = re.IGNORECASE | re.MULTILINE
    try:
        matches = list(re.finditer(regex, text, flags))
    except re.error:
        return []
    results = []
    for m in matches:
        start, end = m.start(), m.end()
        line_no = text.count("\n", 0, start) + 1
        snippet = get_snippet(text, start, end, context=120)
        results.append({"start": start, "end": end, "line": line_no, "snippet": snippet})
    return results

def scan_text_with_patterns(text: str, pattern_ids: List[str]):
    findings = []
    for pid in pattern_ids:
        pat = ID_TO_PATTERN.get(pid)
        if not pat:
            continue
        matches = find_matches_for_pattern(text, pat["regex"])
        if matches:
            lines = sorted({m["line"] for m in matches})
            findings.append({
                "id": pat["id"],
                "feature": pat["name"],
                "description": pat["description"],
                "severity": pat["severity"],
                "count": len(matches),
                "lines": lines,
                "sample_snippet": matches[0]["snippet"] if matches else ""
            })
    return findings

def scan_uploaded_file(uploaded_file, pattern_ids: List[str]):
    uploaded_file.seek(0)
    raw = uploaded_file.read()
    text = decode_bytes(raw if isinstance(raw, (bytes, bytearray)) else raw.encode("utf-8"))
    findings = scan_text_with_patterns(text, pattern_ids)
    return {
        "file_name": uploaded_file.name,
        "size_kb": round(len(raw) / 1024, 2) if isinstance(raw, (bytes, bytearray)) else round(len(text.encode("utf-8"))/1024,2),
        "findings": findings,
        "preview": get_snippet(text, 0, min(400, len(text)))
    }

# ---------------------------
# Sidebar: settings
# ---------------------------
st.sidebar.header("Scanner Settings")
all_feature_names = [p["name"] for p in PATTERNS]
selected_feature_names = st.sidebar.multiselect("Select features to scan", all_feature_names, default=all_feature_names)
selected_pattern_ids = [NAME_TO_ID[name] for name in selected_feature_names]
show_snippets = st.sidebar.checkbox("Show code snippets in results", value=True)
show_only_with_findings = st.sidebar.checkbox("Show only files with findings in summary", value=False)
severity_filter = st.sidebar.multiselect("Filter severities", options=["major", "minor"], default=["major", "minor"])

# Apply severity filter to selected_pattern_ids
selected_pattern_ids = [pid for pid in selected_pattern_ids if ID_TO_PATTERN[pid]["severity"] in severity_filter]

st.title("🚀 Baseline Web Feature Checker — Day 4")
st.markdown("### Upload files to scan. Use the sidebar to pick features and options.")

uploaded_files = st.file_uploader("📂 Upload one or more files (.html, .css, .js)", type=["html", "css", "js"], accept_multiple_files=True)

if uploaded_files:
    st.markdown("### 🔎 Scanning Files")
    progress = st.progress(0)
    results = []
    total = len(uploaded_files)
    for i, f in enumerate(uploaded_files):
        res = scan_uploaded_file(f, selected_pattern_ids)
        results.append(res)
        progress.progress(int((i+1)/total*100))

    # Build summary
    summary_rows = []
    for r in results:
        issues_count = sum(item["count"] for item in r["findings"])
        summary_rows.append({"file": r["file_name"], "size_kb": r["size_kb"], "issues_found": issues_count})

    summary_df = pd.DataFrame(summary_rows)
    if show_only_with_findings:
        summary_df = summary_df[summary_df["issues_found"] > 0]

    st.markdown("### 📊 Summary")
    st.dataframe(summary_df)

    # Detailed per-file results
    st.markdown("### 📝 Detailed Results")
    final_report = []
    for r in results:
        with st.expander(f"{r['file_name']} — {r['size_kb']} KB — {sum(it['count'] for it in r['findings'])} findings", expanded=False):
            if r["findings"]:
                # DataFrame of findings for this file
                df_rows = []
                for it in r["findings"]:
                    df_rows.append({
                        "Feature": it["feature"],
                        "Description": it["description"],
                        "Severity": it["severity"],
                        "Count": it["count"],
                        "Lines": ", ".join(map(str, it["lines"])),
                    })
                df_find = pd.DataFrame(df_rows)
                st.table(df_find)

                # Show snippets if requested
                if show_snippets:
                    st.markdown("**Snippets**")
                    for it in r["findings"]:
                        st.markdown(f"**{it['feature']}** (line(s): {', '.join(map(str, it['lines']))})")
                        st.code(it["sample_snippet"], language="html")
            else:
                st.success("No selected non-Baseline features detected in this file.")

            # Show content preview
            st.markdown("**Content preview (first 400 chars)**")
            st.code(r["preview"][:1000], language="html")

            final_report.append(r)

    # Downloadable report
    report_json = json.dumps(final_report, indent=2)
    st.download_button("⬇️ Download scan report (JSON)", data=report_json, file_name="baseline_scan_report.json", mime="application/json")
    st.success("Day 4 complete — scanner highlights, settings, and report download are available.")
else:
    st.info("⬆️ Upload .html, .css, or .js files to start scanning.")

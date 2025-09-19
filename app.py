import streamlit as st
import pandas as pd

# App Title
st.title("🚀 Baseline Web Feature Checker")

# Intro section
st.markdown("### 👋 Welcome!")
st.write("Upload your frontend files (.html, .css, .js) to scan for non-Baseline web features.")

# File uploader component
uploaded_files = st.file_uploader(
    "📂 Upload your frontend files here",
    type=["html", "css", "js"],
    accept_multiple_files=True
)

# --- NEW: Define a demo list of “non-Baseline” features ---
non_baseline_features = [
    "alert(",        # Example JavaScript usage
    "fetch(",        # Example JavaScript usage
    "grid-template", # Example CSS property
    "<video"         # Example HTML element
]

# --- NEW: If files uploaded, scan them ---
if uploaded_files:
    st.markdown("### 📄 Uploaded Files")
    results = []  # Will store our scan results

    for file in uploaded_files:
        content = file.read().decode("utf-8", errors="ignore")  # Read text
        size_kb = round(len(content.encode('utf-8')) / 1024, 2)

        st.write(f"**{file.name}** — {size_kb} KB")
        file.seek(0)

        # Scan for each feature
        found_features = [feat for feat in non_baseline_features if feat in content]

        # Add result to table
        results.append({
            "File Name": file.name,
            "Found Features": ", ".join(found_features) if found_features else "✅ None"
        })

    # Display the results table
    st.markdown("### 📝 Scan Results")
    df = pd.DataFrame(results)
    st.dataframe(df)

else:
    st.info("⬆️ Please upload one or more .html, .css, or .js files to begin.")

# Footer
st.write("---")
st.write("✅ **Day 3 complete.** Tomorrow we’ll improve the scanner and highlight results visually!")

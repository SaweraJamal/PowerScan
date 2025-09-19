
import streamlit as st

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

# Display uploaded file names and sizes
if uploaded_files:
    st.markdown("### 📄 Uploaded Files")
    for file in uploaded_files:
        content = file.read()
        size_kb = round(len(content) / 1024, 2)
        st.write(f"**{file.name}** — {size_kb} KB")
        file.seek(0)  # Reset file pointer for future reading
else:
    st.info("⬆️ Please upload one or more .html, .css, or .js files to begin.")

# Footer
st.write("---")
st.write("✅ **Day 2 complete.** Tomorrow we’ll begin scanning for non-Baseline features!")

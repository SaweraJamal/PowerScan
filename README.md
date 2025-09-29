# ⚡ PowerScan

**PowerScan** is an open-source, Streamlit-based **web feature scanner** that quickly scans your `.html`, `.css`, and `.js` files for predefined patterns, potential risks, and baseline compliance issues.  

---

## 🚀 Key Features

- **Instant Scanning** — Upload one or multiple files and get instant results.  
- **Pattern Matching** — Detect risky or required web features using custom regex patterns.  
- **Code Highlights & Snippets** — See exactly where matches occur in your files.  
- **Automatic Dashboard** — View your latest scan results on the Dashboard page.  
- **Downloadable Reports** — Export your findings in **JSON**, **CSV**, **Excel**, or **PDF** format.  

---

## 🖥 How to Run Locally

1. **Clone the repository**:
      ```bash
  
   git clone https://github.com/SaweraJamal/PowerScan.git
   cd PowerScan```

   ```bash
  pip install -r requirements.txt
   ```
Run the Streamlit app:

   ```bash
streamlit run app.py 
```
✅ This will automatically install all the Python libraries listed in your requirements.txt (like Streamlit, pandas, reportlab, etc.).

🌐 Live Demo
Try PowerScan online:
https://powerscan-zcdd8o88xm9bpuycz2ce24.streamlit.app/

📂 Project Structure

Baseline_checker_streamlit/
 ├── .devcontainer/           # Dev container configuration
 
 ├── pages/                   # Dashboard & other Streamlit pages
 
 ├── .gitignore               # Git ignore rules
 
 ├── LICENSE                  # Apache License 2.0
 
 ├── README.md                # Project description and instructions
 
 ├── app.py                   # Main Streamlit scanner app
 
 ├── patterns.json            # Regex patterns configuration
 
 ├── powerscan-icon.png       # App icon (PNG)

 ├── powerscan-icon.svg       # App favicon (SVG)
 
 ├── requirements.txt         # Python dependencies
 
 ├── scan_results.json        # Latest scan results storage

📝 Contributing
Pull requests are welcome!
If you’d like to add new patterns or improve the UI, open an issue or submit a PR.

## License  
This project is licensed under the Apache License 2.0 — see the LICENSE file for details.  
## Privacy Notice
Uploaded files are only scanned temporarily during the session and **are not stored or shared** permanently. PowerScan performs all scanning in real time to protect user privacy.


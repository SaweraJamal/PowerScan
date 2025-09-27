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

PowerScan/
│
├── app.py                 # Main scanner page
├── pages/
│   └── 1_Dashboard.py     # Dashboard page for last scan results
├── patterns.json          # Your regex patterns configuration
├── requirements.txt       # Python dependencies
└── README.md              # Project description
📝 Contributing
Pull requests are welcome!
If you’d like to add new patterns or improve the UI, open an issue or submit a PR.

📄 License
This project is licensed under the MIT License — see the LICENSE file for details.
## License  
This project is licensed under the Apache License 2.0 — see the LICENSE file for details.  

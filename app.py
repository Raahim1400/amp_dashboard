import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

# --- Page Config ---
st.set_page_config(
    page_title="PhytoAMP_Finder",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Branding Header ---
st.markdown("""
    <div style='text-align: center; padding: 1rem; background-color: #111;'>
        <h1 style='font-size: 3rem; color: #00BFFF;'>🧬 PhytoAMP_Finder</h1>
        <h4 style='color: #BBBBBB;'>AI-Powered Screening of Antimicrobial Peptides (AMPs) from Local Medicinal Plants</h4>
    </div>
""", unsafe_allow_html=True)

# --- Styling ---
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            background-color: #0E1117;
            color: #FFFFFF;
            font-family: 'Segoe UI', sans-serif;
            font-size: 16px;
        }
        h1, h2, h3, h4 {
            color: #00BFFF;
        }
        .stButton > button {
            background-color: #1f1f2e;
            color: white;
            border-radius: 10px;
            border: 1px solid #00BFFF;
            padding: 0.5em 1em;
        }
        .stDataFrame, .stTable {
            background-color: #1f1f2e;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Load Data ---
try:
    df = pd.read_csv("data/amp_scores.csv")
except FileNotFoundError:
    st.error("Data file not found. Please upload amp_scores.csv inside data folder.")
    st.stop()

# --- Display Table ---
st.subheader("📊 AMP Score Table")
st.dataframe(df, use_container_width=True)

# --- Bar Chart ---
st.subheader("📈 AMP Score per Plant")
fig, ax = plt.subplots()
ax.bar(df['Plant'], df['AMP Score'], color='#FF4B4B')
ax.set_xlabel("Plant")
ax.set_ylabel("AMP Score")
ax.set_title("AMP Score Comparisons")
st.pyplot(fig)

# --- Export to PDF Button ---
st.markdown("## 🖨️ Export Dashboard as PDF")
js = """<script>
function printPage() {
    window.print();
}
</script>
<button onclick="printPage()">Print / Save as PDF</button>"""
components.html(js)

# --- Footer ---
st.markdown("""
    <hr>
    <div style='text-align: center; color: gray;'>
        Made by Raahim | Project: AMP Screening Dashboard | 2025
    </div>
""", unsafe_allow_html=True)

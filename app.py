import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import base64

# --- Page Config ---
st.set_page_config(
    page_title="PhytoAMP_Finder",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Loading Spinner ---
with st.spinner("Loading Dashboard..."):
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
st.subheader("AMP Score Table")
st.dataframe(df, use_container_width=True)

# --- Bar Chart ---
st.subheader("📈 AMP Score per Plant")
fig1, ax1 = plt.subplots()
ax1.bar(df['Plant'], df['AMP Score'], color='#FF4B4B')
ax1.set_xlabel("Plant")
ax1.set_ylabel("AMP Score")
ax1.set_title("AMP Score Comparisons")
st.pyplot(fig1)

# --- Pie Chart ---
st.subheader(" AMP Score Distribution")
fig2, ax2 = plt.subplots()
ax2.pie(df['AMP Score'], labels=df['Plant'], autopct='%1.1f%%', startangle=140)
ax2.axis('equal')
st.pyplot(fig2)

# --- AI Prediction (Simple Rule-Based) ---
def predict_amp_category(score):
    if score >= 85:
        return "High Potential"
    elif score >= 70:
        return "Moderate Potential"
    else:
        return "Low Potential"

df['AMP Category'] = df['AMP Score'].apply(predict_amp_category)

st.subheader(" AI-Based AMP Category Prediction")
st.dataframe(df[['Plant', 'AMP Score', 'AMP Category']], use_container_width=True)

# --- Category-wise Download Buttons ---
st.subheader("Download Category-wise Data")
for category in df['AMP Category'].unique():
    cat_df = df[df['AMP Category'] == category]
    csv = cat_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{category}_AMPs.csv">Download {category} AMPs</a>'
    st.markdown(href, unsafe_allow_html=True)

# --- Final Summary ---
st.markdown("""
    <hr>
    <div style='text-align: center; font-size: 18px; color: #FFFFFF;'>
        <p><strong>Summary:</strong><br>
        Total Plants Tested: <span style='color: #00BFFF;'>{}</span><br>
        High Potential AMPs: <span style='color: #00FF00;'>{}</span><br>
        Moderate Potential AMPs: <span style='color: #FFA500;'>{}</span><br>
        Low Potential AMPs: <span style='color: #FF4B4B;'>{}</span></p>
    </div>
""".format(
    len(df),
    sum(df['AMP Category'] == 'High Potential'),
    sum(df['AMP Category'] == 'Moderate Potential'),
    sum(df['AMP Category'] == 'Low Potential')
), unsafe_allow_html=True)

# --- Export to PDF Button ---
st.markdown("## Export Dashboard as PDF")
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

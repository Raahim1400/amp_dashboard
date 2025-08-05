import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="AMP Score Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FILE UPLOAD ---
st.sidebar.markdown("### 📤 Upload Your AMP Data (.csv)")
user_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if user_file is not None:
    df = pd.read_csv(user_file)
    st.success("✅ Custom data uploaded successfully!")
else:
    df = pd.read_csv("data/amp_scores.csv")
    st.info("ℹ️ Using default AMP data (data/amp_scores.csv)")

# --- SIDEBAR FILTERS ---
st.sidebar.markdown("## ✨ Filter Options")

plants = st.sidebar.multiselect(
    "Select Plant(s):", options=df["Plant"].unique(), default=df["Plant"].unique()
)

score_range = st.sidebar.slider(
    "Select AMP Score Range:",
    min_value=int(df["AMP Score"].min()),
    max_value=int(df["AMP Score"].max()),
    value=(int(df["AMP Score"].min()), int(df["AMP Score"].max()))
)

# Filtered data
filtered_df = df[
    (df["Plant"].isin(plants)) &
    (df["AMP Score"] >= score_range[0]) &
    (df["AMP Score"] <= score_range[1])
]

# --- AMP Category Predictor ---
def predict_category(score):
    if score >= 80:
        return 'High AMP'
    elif score >= 60:
        return 'Moderate AMP'
    else:
        return 'Low AMP'

filtered_df['Predicted Category'] = filtered_df['AMP Score'].apply(predict_category)

# --- STYLING ---
st.markdown("""
    <style>
        body {
            background-color: #111;
            color: #f0f0f0;
        }
        .block-container {
            padding-top: 2rem;
        }
        h1, h2, h3, h4 {
            color: #e91e63;
        }
        .st-emotion-cache-10trblm {
            font-size: 1.4rem;
            color: #9cf;
        }
        .markdown-text-container, .stMarkdown, .stTable, .stDataFrame {
            font-size: 1.2rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.markdown("""
    <h1 style='text-align: center;'>🔬 AMP Score Dashboard</h1>
    <div style='text-align: center; font-size: 20px; color: #aaa;'>
        Welcome to the AMP Score Dashboard! This futuristic dashboard displays Antimicrobial Peptide (AMP) scores from local medicinal plants.<br>
        <b>How to Use:</b><br>
        • Upload your own CSV file (optional)<br>
        • Use the sidebar to filter by plant and AMP score<br>
        • Explore the table, graph, and download options below
    </div>
""", unsafe_allow_html=True)

# --- TABLE ---
st.markdown("### 📄 Filtered AMP Data")
st.dataframe(filtered_df[['Plant', 'AMP Score', 'Predicted Category']], use_container_width=True)

# --- BAR CHART ---
st.markdown("### 🌉 AMP Score per Plant")
fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(filtered_df['Plant'], filtered_df['AMP Score'], color='#03a9f4')
ax.set_xlabel("Plant", fontsize=12)
ax.set_ylabel("AMP Score", fontsize=12)
ax.set_title("AMP Score Comparison", fontsize=14, color='white')
ax.tick_params(colors='white')
fig.patch.set_facecolor('#111')
ax.set_facecolor('#222')
st.pyplot(fig)

# --- PIE CHART ---
st.markdown("### 🧁 AMP Category Distribution")
category_counts = filtered_df['Predicted Category'].value_counts()
fig2, ax2 = plt.subplots()
colors = ['#f44336', '#ff9800', '#4caf50']

ax2.pie(
    category_counts,
    labels=category_counts.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=colors,
    textprops={'color': 'white', 'fontsize': 14}
)
ax2.axis('equal')
fig2.patch.set_facecolor('#111')
st.pyplot(fig2)

# --- SUMMARY REPORT ---
st.markdown("### 📋 Summary Report")

if not filtered_df.empty:
    best_plant = filtered_df.sort_values('AMP Score', ascending=False).iloc[0]['Plant']
    avg_score = round(filtered_df['AMP Score'].mean(), 2)
    high_count = (filtered_df['Predicted Category'] == 'High AMP').sum()
    mod_count = (filtered_df['Predicted Category'] == 'Moderate AMP').sum()
    low_count = (filtered_df['Predicted Category'] == 'Low AMP').sum()

    st.markdown(f"""
    <div style='font-size: 18px;'>
    - 🥇 <b>Best Performing Plant</b>: <code>{best_plant}</code><br>
    - 📊 <b>Average AMP Score</b>: <code>{avg_score}</code><br>
    - 🧬 <b>High AMP</b>: {high_count} plant(s)<br>
    - 🌿 <b>Moderate AMP</b>: {mod_count} plant(s)<br>
    - 🌫️ <b>Low AMP</b>: {low_count} plant(s)
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No data available for summary.")

# --- DOWNLOAD BUTTON ---
st.markdown("### ⬇️ Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download CSV",
    data=csv,
    file_name='filtered_amp_data.csv',
    mime='text/csv',
    help="Click to download the current table as CSV"
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def create_pdf(dataframe):
    file_path = "amp_report.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "AMP Score Summary Report")

    # Date
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Table
    y = height - 110
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Plant     AMP Score     Category")
    y -= 20

    c.setFont("Helvetica", 10)
    for index, row in dataframe.iterrows():
        line = f"{row['Plant']}        {row['AMP Score']}            {row['Predicted Category']}"
        c.drawString(50, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    return file_path

# Add PDF download button
if not filtered_df.empty:
    if st.button("📄 Generate PDF Report"):
        pdf_path = create_pdf(filtered_df)
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Download AMP Report (PDF)",
                data=f,
                file_name="AMP_Report.pdf",
                mime="application/pdf"
            )

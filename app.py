import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
@st.cache_data
def load_data():
    return pd.read_csv("data/amp_scores.csv")

df = load_data()

# 🌐 Global Styling (HTML + CSS)
st.markdown("""
    <style>
        body {
            background-color: #f5f5f5;
        }

        .main {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
            font-family: 'Segoe UI', sans-serif;
        }

        .big-font {
            font-size: 20px !important;
            line-height: 1.6;
        }

        .section-title {
            font-size: 24px !important;
            font-weight: bold;
            color: #3A7CA5;
            margin-top: 30px;
        }

        .stApp {
            background-color: #f0f2f6;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🧬 AMP Score Dashboard")

# Instructions
st.markdown("""
<div class='main'>
<div class='big-font'>
Welcome to the <strong>AMP Score Dashboard</strong>!  
This app helps visualize and filter Antimicrobial Peptide (AMP) scores extracted from local medicinal plants.

<strong>🔧 How to Use:</strong>
<ul>
  <li>Use the sidebar to filter by plant name and AMP Score range.</li>
  <li>See filtered results in a clean table and graph.</li>
  <li>Use this output for analysis or export.</li>
</ul>
</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Filters
st.sidebar.markdown("## 🔍 Filter Options")

# Plant Filter
plants = st.sidebar.multiselect(
    "Select Plant(s):",
    options=df["Plant"].unique(),
    default=df["Plant"].unique(),
    help="Choose one or more medicinal plants"
)

# AMP Score Range Filter
min_score = float(df["AMP Score"].min())
max_score = float(df["AMP Score"].max())

score_range = st.sidebar.slider(
    "Select AMP Score Range:",
    min_value=min_score,
    max_value=max_score,
    value=(min_score, max_score),
    step=0.1,
    help="Filter AMP Scores between selected range"
)

# Filtered DataFrame
filtered_df = df[
    (df["Plant"].isin(plants)) &
    (df["AMP Score"] >= score_range[0]) &
    (df["AMP Score"] <= score_range[1])
]

# Display Filtered Table
st.markdown("<div class='section-title'>📋 Filtered AMP Data</div>", unsafe_allow_html=True)
st.dataframe(filtered_df, use_container_width=True)

# Display Bar Graph
st.markdown("<div class='section-title'>📊 AMP Score per Plant</div>", unsafe_allow_html=True)
fig, ax = plt.subplots()
ax.bar(filtered_df["Plant"], filtered_df["AMP Score"], color="seagreen")
ax.set_xlabel("Plant")
ax.set_ylabel("AMP Score")
ax.set_title("AMP Score Comparison")
st.pyplot(fig)

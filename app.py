import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
@st.cache_data
def load_data():
    return pd.read_csv("data/amp_scores.csv")

df = load_data()

# 🌐 Styling
st.markdown("""
    <style>
        .big-font { font-size: 18px !important; line-height: 1.6; }
        .section-title { font-size: 22px !important; font-weight: bold; color: #3A7CA5; margin-top: 20px; }
        .stApp { background-color: #f5f5f5; }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🧬 AMP Score Dashboard")

# Instructions
st.markdown("""
<div class='big-font'>
Welcome to the <strong>AMP Score Dashboard</strong>!  
This app helps visualize and filter Antimicrobial Peptide (AMP) scores extracted from local medicinal plants.

<b>How to Use:</b>
<ul>
  <li>Use the sidebar to filter by plant and AMP Score.</li>
  <li>View filtered results below.</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Sidebar Filters
st.sidebar.header("🔍 Filter Options")

# Multiselect
plants = st.sidebar.multiselect(
    "Select Plant(s):",
    options=df["Plant"].unique(),
    default=df["Plant"].unique()
)

# Slider
min_score = float(df["AMP Score"].min())
max_score = float(df["AMP Score"].max())

score_range = st.sidebar.slider(
    "Select AMP Score Range:",
    min_value=min_score,
    max_value=max_score,
    value=(min_score, max_score),
    step=0.1
)

# Filtered DataFrame
filtered_df = df[
    (df["Plant"].isin(plants)) &
    (df["AMP Score"] >= score_range[0]) &
    (df["AMP Score"] <= score_range[1])
]

# Table
st.markdown("<div class='section-title'>📋 Filtered AMP Data</div>", unsafe_allow_html=True)
st.dataframe(filtered_df)

# Bar Chart
st.markdown("<div class='section-title'>📊 AMP Score per Plant</div>", unsafe_allow_html=True)
fig, ax = plt.subplots()
ax.bar(filtered_df["Plant"], filtered_df["AMP Score"], color="seagreen")
ax.set_xlabel("Plant")
ax.set_ylabel("AMP Score")
ax.set_title("AMP Score Comparison")
st.pyplot(fig)

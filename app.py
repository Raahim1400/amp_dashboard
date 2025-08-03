import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="AMP Dashboard", layout="wide")

# 💡 Custom Styling
st.markdown("""
    <style>
        .stApp {
            background-color: #ffffff;
            color: #000000;
        }
        .big-font {
            font-size: 18px !important;
            line-height: 1.6;
        }
        .section-title {
            font-size: 22px !important;
            font-weight: bold;
            color: #1c1c1c;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("data/amp_scores.csv")

df = load_data()

# Title
st.title("🧬 AMP Score Dashboard")

# Description
st.markdown("""
<div class='big-font'>
Welcome to the <strong>AMP Score Dashboard</strong>!  
This app helps visualize Antimicrobial Peptide (AMP) scores extracted from medicinal plants.

<b>How to Use:</b>
<ul>
  <li>Use the sidebar to filter by plant and AMP Score.</li>
  <li>View filtered results in the table and graph.</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("🔍 Filter Options")

plants = st.sidebar.multiselect(
    "Select Plant(s):",
    options=df["Plant"].unique(),
    default=df["Plant"].unique()
)

score_min = float(df["AMP Score"].min())
score_max = float(df["AMP Score"].max())

score_range = st.sidebar.slider(
    "AMP Score Range:",
    min_value=score_min,
    max_value=score_max,
    value=(score_min, score_max)
)

# Filter data
filtered_df = df[
    (df["Plant"].isin(plants)) &
    (df["AMP Score"] >= score_range[0]) &
    (df["AMP Score"] <= score_range[1])
]

# Show data table
st.markdown("<div class='section-title'>📋 Filtered AMP Data</div>", unsafe_allow_html=True)
st.dataframe(filtered_df)

# Bar chart
st.markdown("<div class='section-title'>📊 AMP Score per Plant</div>", unsafe_allow_html=True)
fig, ax = plt.subplots()
ax.bar(filtered_df["Plant"], filtered_df["AMP Score"], color="seagreen")
ax.set_xlabel("Plant")
ax.set_ylabel("AMP Score")
ax.set_title("AMP Score Comparison")
st.pyplot(fig)

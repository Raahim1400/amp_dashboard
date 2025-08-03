import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
@st.cache_data
def load_data():
    return pd.read_csv("data/amp_scores.csv")

df = load_data()

# App Title
st.title("🧬 AMP Score Dashboard")

# Intro Instructions
st.markdown("""
Welcome to the **AMP Score Dashboard**!  
This app helps visualize and filter Antimicrobial Peptide (AMP) scores extracted from local medicinal plants.

**How to Use:**
- Use the sidebar to filter by plant name and AMP Score range.
- View filtered data in the table and graph.
- Download filtered results for your records.
""")

# Sidebar Filters
st.sidebar.header("🔍 Filter Options")

# Plant Multiselect
plants = st.sidebar.multiselect(
    "Select Plant(s):",
    options=df["Plant"].unique(),
    default=df["Plant"].unique(),
    help="Choose one or more medicinal plants to view"
)

# AMP Score Range Slider
min_score = float(df["AMP Score"].min())
max_score = float(df["AMP Score"].max())

score_range = st.sidebar.slider(
    "Select AMP Score Range:",
    min_value=min_score,
    max_value=max_score,
    value=(min_score, max_score),
    step=0.1,
    help="Filter plants between selected AMP Score range"
)

# Apply filters
filtered_df = df[
    (df["Plant"].isin(plants)) &
    (df["AMP Score"] >= score_range[0]) &
    (df["AMP Score"] <= score_range[1])
]

# Show Filtered Table
st.subheader("📋 Filtered AMP Data")
st.dataframe(filtered_df)

# Show Bar Chart
st.subheader("📊 AMP Score per Plant")
fig, ax = plt.subplots()
ax.bar(filtered_df["Plant"], filtered_df["AMP Score"], color="seagreen")
ax.set_xlabel("Plant")
ax.set_ylabel("AMP Score")
ax.set_title("AMP Score Comparison")
st.pyplot(fig)


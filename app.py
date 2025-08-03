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

# Load data
df = pd.read_csv("data/amp_scores.csv")

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
        .css-1d391kg { 
            background-color: #111 !important; 
        }
        h1, h2, h3, h4 {
            color: #e91e63;  /* red-pink accent */
        }
        .st-emotion-cache-10trblm {
            font-size: 1.3rem;
            color: #9cf;
        }
    </style>
""", unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.markdown("""
    <h1 style='text-align: center;'>🔬 AMP Score Dashboard</h1>
    <div style='text-align: center; font-size: 18px; color: #aaa;'>
        Welcome to the AMP Score Dashboard! This futuristic dashboard displays Antimicrobial Peptide (AMP) scores from local medicinal plants.<br>
        <b>How to Use:</b><br>
        • Use the sidebar to filter by plant and AMP score.<br>
        • Explore the table and graph below.
    </div>
""", unsafe_allow_html=True)

# --- TABLE ---
st.markdown("### 📄 Filtered AMP Data")
st.dataframe(filtered_df, use_container_width=True)

# --- CHART ---
st.markdown("### 🌉 AMP Score per Plant")
fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(filtered_df['Plant'], filtered_df['AMP Score'], color='#03a9f4')  # blue accent
ax.set_xlabel("Plant", fontsize=12)
ax.set_ylabel("AMP Score", fontsize=12)
ax.set_title("AMP Score Comparison", fontsize=14, color='white')
ax.tick_params(colors='white')
fig.patch.set_facecolor('#111')
ax.set_facecolor('#222')
st.pyplot(fig)

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
    st.success(" Custom data uploaded successfully!")
else:
    df = pd.read_csv("data/amp_scores.csv")
    st.info("ℹ Using default AMP data (data/amp_scores.csv)")

st.sidebar.markdown("##  Filter Options")

plants = st.sidebar.multiselect(
    "Select Plant(s):", options=df["Plant"].unique(), default=df["Plant"].unique()
)

score_range = st.sidebar.slider(
    "Select AMP Score Range:",
    min_value=int(df["AMP Score"].min()),
    max_value=int(df["AMP Score"].max()),
    value=(int(df["AMP Score"].min()), int(df["AMP Score"].max()))
)

filtered_df = df[
    (df["Plant"].isin(plants)) &
    (df["AMP Score"] >= score_range[0]) &
    (df["AMP Score"] <= score_range[1])
]

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

st.markdown("""
    <h1 style='text-align: center;'>🔬 AMP Score Dashboard</h1>
    <div style='text-align: center; font-size: 18px; color: #aaa;'>
        Welcome to the AMP Score Dashboard! This futuristic dashboard displays Antimicrobial Peptide (AMP) scores from local medicinal plants.<br>
        <b>How to Use:</b><br>
        • Upload your own CSV file (optional)<br>
        • Use the sidebar to filter by plant and AMP score<br>
        • Explore the table, graph, and download options below
    </div>
""", unsafe_allow_html=True)

st.markdown("###  Filtered AMP Data")
st.dataframe(filtered_df[['Plant', 'AMP Score', 'Predicted Category']], use_container_width=True)


st.markdown("###  AMP Score per Plant")
fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(filtered_df['Plant'], filtered_df['AMP Score'], color='#03a9f4')  # blue accent
ax.set_xlabel("Plant", fontsize=12)
ax.set_ylabel("AMP Score", fontsize=12)
ax.set_title("AMP Score Comparison", fontsize=14, color='white')
ax.tick_params(colors='white')
fig.patch.set_facecolor('#111')
ax.set_facecolor('#222')
st.pyplot(fig)

st.markdown("### ⬇️ Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download CSV",
    data=csv,
    file_name='filtered_amp_data.csv',
    mime='text/csv',
    help="Click to download the current table as CSV"
)

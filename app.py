import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AMP Dashboard", layout="centered")
st.title('🧬 Antimicrobial Peptide (AMP) Dashboard')

uploaded_file = st.sidebar.file_uploader("📤 Upload AMP Data CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Uploaded file loaded successfully!")
else:
    df = pd.read_csv('data/amp_scores.csv')
    st.info("ℹ️ Using default dataset (amp_scores.csv)")

def predict_amp_category(score):
    if score > 85:
        return "High"
    elif score >= 70:
        return "Moderate"
    else:
        return "Low"

df["Predicted Category"] = df["AMP Score"].apply(predict_amp_category)

st.sidebar.header("🔎 Filter Options")
plants = st.sidebar.multiselect("🌿 Select plant(s):", options=df['Plant'].unique(), default=df['Plant'].unique())

score_min, score_max = float(df['AMP Score'].min()), float(df['AMP Score'].max())
score_range = st.sidebar.slider("📊 Minimum AMP Score:", min_value=score_min, max_value=score_max, value=score_min)

filtered_df = df[(df['Plant'].isin(plants)) & (df['AMP Score'] >= score_range)]

st.markdown("### 📋 Filtered AMP Scores with Prediction")
st.dataframe(filtered_df[['Plant', 'AMP Score', 'Predicted Category']], use_container_width=True)

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_amp_scores.csv',
    mime='text/csv'
)

st.markdown("### 📈 AMP Score per Plant")
fig, ax = plt.subplots()
ax.bar(filtered_df['Plant'], filtered_df['AMP Score'], color='seagreen')
ax.set_xlabel('Plant')
ax.set_ylabel('AMP Score')
ax.set_title('AMP Score Comparison')
st.pyplot(fig)

st.markdown("---")
st.markdown("📘 *This dashboard is part of the AMP Screening Project (Biotech x AI)*")

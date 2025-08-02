import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load CSV data
df = pd.read_csv('data/amp_scores.csv')

# AI-style AMP prediction logic
def predict_amp_category(score):
    if score > 85:
        return "High"
    elif score >= 70:
        return "Moderate"
    else:
        return "Low"

# Apply prediction
df["Predicted Category"] = df["AMP Score"].apply(predict_amp_category)

# Streamlit app layout
st.title('AMP Score Dashboard')

# Sidebar filters
st.sidebar.header("Filter Options")

# Dropdown to select plant(s)
plants = st.sidebar.multiselect("Select plant(s):", options=df['Plant'].unique(), default=df['Plant'].unique())

# AMP Score filter
score_min, score_max = float(df['AMP Score'].min()), float(df['AMP Score'].max())
score_range = st.sidebar.slider("Minimum AMP Score:", min_value=score_min, max_value=score_max, value=score_min)

# Filtered data
filtered_df = df[(df['Plant'].isin(plants)) & (df['AMP Score'] >= score_range)]

# Show filtered table
st.subheader('Filtered AMP Scores (with Prediction)')
st.dataframe(filtered_df[['Plant', 'AMP Score', 'Predicted Category']])

# Bar Chart
st.subheader('AMP Score per Plant')
fig, ax = plt.subplots()
ax.bar(filtered_df['Plant'], filtered_df['AMP Score'], color='seagreen')
ax.set_xlabel('Plant')
ax.set_ylabel('AMP Score')
ax.set_title('AMP Score Comparison')
st.pyplot(fig)


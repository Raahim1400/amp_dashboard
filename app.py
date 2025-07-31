import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({
    'Plant': ['Neem', 'Tulsi', 'Aloe Vera', 'Mint'],
    'AMP Score': [82, 67, 90, 75]
})

st.title('AMP Score Dashboard')

st.subheader('Plant AMP Scores')
st.dataframe(df)

st.subheader('AMP Score per Plant')
fig, ax = plt.subplots()
ax.bar(df['Plant'], df['AMP Score'], color='seagreen')
ax.set_xlabel('Plant')
ax.set_ylabel('AMP Score')
ax.set_title('AMP Score Comparison')
st.pyplot(fig)

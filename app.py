import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64

# --- Page Config ---
st.set_page_config(
    page_title="PhytoAMP_Finder",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styling ---
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            background-color: #0E1117;
            color: #FFFFFF;
            font-family: 'Segoe UI', sans-serif;
            font-size: 16px;
        }
        h1, h2, h3, h4 {
            color: #00BFFF;
        }
        .stButton > button {
            background-color: #1f1f2e;
            color: white;
            border-radius: 10px;
            border: 1px solid #00BFFF;
            padding: 0.5em 1em;
        }
        .stDataFrame, .stTable {
            background-color: #1f1f2e;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
    <div style='text-align: center; padding: 1rem; background-color: #111;'>
        <h1 style='font-size: 3rem; color: #00BFFF;'>🧬 PhytoAMP_Finder</h1>
        <h4 style='color: #BBBBBB;'>AI-Powered Screening of Antimicrobial Peptides (AMPs) from Local Medicinal Plants</h4>
    </div>
""", unsafe_allow_html=True)

# --- Load Main Data ---
try:
    df = pd.read_csv("data/amp_scores.csv")
except FileNotFoundError:
    st.error("Data file not found. Please upload amp_scores.csv inside data folder.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter & Search")

search_query = st.sidebar.text_input("Search AMP (by name or sequence)", "")

min_score = float(df["AMP Score"].min())
max_score = float(df["AMP Score"].max())
score_range = st.sidebar.slider("AMP Score Range", min_score, max_score, (min_score, max_score))

all_categories = sorted(df["AMP Category"].dropna().unique()) if "AMP Category" in df else []
selected_categories = st.sidebar.multiselect("Select Categories", all_categories, default=all_categories)

# Disease filter (from mapping file if available)
try:
    df_disease = pd.read_csv("data/amp_disease_links.csv")
    all_diseases = sorted(df_disease["Target Disease"].dropna().unique())
except FileNotFoundError:
    df_disease = pd.DataFrame()
    all_diseases = []
selected_diseases = st.sidebar.multiselect("Select Diseases", all_diseases, default=all_diseases)

# --- Apply Filters to main df ---
filtered_df = df.copy()

if search_query:
    if "AMP Name" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["AMP Name"].str.contains(search_query, case=False, na=False) |
            filtered_df.get("AMP Sequence", pd.Series("", index=filtered_df.index)).str.contains(search_query, case=False, na=False)
        ]
    else:
        filtered_df = filtered_df[
            filtered_df["Plant"].str.contains(search_query, case=False, na=False)
        ]

filtered_df = filtered_df[
    (filtered_df["AMP Score"] >= score_range[0]) &
    (filtered_df["AMP Score"] <= score_range[1])
]

if selected_categories:
    filtered_df = filtered_df[filtered_df["AMP Category"].isin(selected_categories)]

if selected_diseases and not df_disease.empty:
    amps_linked = df_disease[df_disease["Target Disease"].isin(selected_diseases)]["AMP Name"].unique()
    filtered_df = filtered_df[filtered_df["AMP Name"].isin(amps_linked)] if "AMP Name" in filtered_df else filtered_df

# --- Display AMP Score Table ---
st.subheader(f"AMP Score Table — {len(filtered_df)} Records")
st.dataframe(filtered_df, use_container_width=True)

# --- Bar Chart ---
st.subheader("📈 AMP Score per Plant")
fig1, ax1 = plt.subplots()
ax1.bar(filtered_df['Plant'], filtered_df['AMP Score'], color='#FF4B4B')
ax1.set_xlabel("Plant")
ax1.set_ylabel("AMP Score")
ax1.set_title("AMP Score Comparisons")
st.pyplot(fig1)

# --- Pie Chart ---
st.subheader("🍩 AMP Score Distribution")
fig2, ax2 = plt.subplots()
ax2.pie(filtered_df['AMP Score'], labels=filtered_df['Plant'], autopct='%1.1f%%', startangle=140)
ax2.axis('equal')
st.pyplot(fig2)

# --- Category Prediction ---
def predict_amp_category(score):
    if score >= 85:
        return "High Potential"
    elif score >= 70:
        return "Moderate Potential"
    else:
        return "Low Potential"

filtered_df['AMP Category'] = filtered_df['AMP Score'].apply(predict_amp_category)

st.subheader("🔍 AI-Based AMP Category Prediction")
st.dataframe(filtered_df[['Plant', 'AMP Score', 'AMP Category']], use_container_width=True)

# --- Downloads by Category ---
st.subheader("⬇️ Download Category-wise Data")
for category in filtered_df['AMP Category'].unique():
    cat_df = filtered_df[filtered_df['AMP Category'] == category]
    csv = cat_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{category}_AMPs.csv">Download {category} AMPs</a>'
    st.markdown(href, unsafe_allow_html=True)

# --- Summary ---
st.markdown("""
    <hr>
    <div style='text-align: center; font-size: 18px; color: #FFFFFF;'>
        <p><strong>Summary:</strong><br>
        Total Plants Tested: <span style='color: #00BFFF;'>{}</span><br>
        High Potential AMPs: <span style='color: #00FF00;'>{}</span><br>
        Moderate Potential AMPs: <span style='color: #FFA500;'>{}</span><br>
        Low Potential AMPs: <span style='color: #FF4B4B;'>{}</span></p>
    </div>
""".format(
    len(filtered_df),
    sum(filtered_df['AMP Category'] == 'High Potential'),
    sum(filtered_df['AMP Category'] == 'Moderate Potential'),
    sum(filtered_df['AMP Category'] == 'Low Potential')
), unsafe_allow_html=True)

# --- AMP ↔ Disease Mapping ---
st.subheader("🧬 AMP ↔ Disease Mapping")
if not df_disease.empty:
    st.dataframe(df_disease, use_container_width=True)

    st.markdown("### 🔎 Find Effective AMPs for a Disease")
    disease_query = st.text_input("Enter disease name (e.g. Pneumonia, MRSA, Candidiasis):")
    if disease_query:
        results = df_disease[df_disease['Target Disease'].str.contains(disease_query, case=False, na=False)]
        if not results.empty:
            st.success(f"Found {len(results)} AMP(s) for '{disease_query}':")
            st.table(results[['AMP Name', 'Source Plant', 'Target Gene/Protein', 'Confidence Score']])
        else:
            st.warning("No AMP found for this disease.")
else:
    st.error("Disease dataset not found. Please add 'amp_disease_links.csv' in the data folder.")

# --- Footer ---
st.markdown("""
    <hr>
    <div style='text-align: center; color: gray;'>
        Made by Raahim | Project: AMP Screening Dashboard | 2025
    </div>
""", unsafe_allow_html=True)


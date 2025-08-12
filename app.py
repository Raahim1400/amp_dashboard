import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
import pickle
from sklearn.ensemble import RandomForestClassifier

# --- Page Config ---
st.set_page_config(
    page_title="PhytoAMP_Finder",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load and Train AI Model (Step 3) ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/amp_scores.csv")
    return df

@st.cache_resource
def train_model(df):
    # Assume df has columns: 'AMP_Score', 'Length', 'Charge', 'Category'
    X = df[['AMP_Score', 'Length', 'Charge']]
    y = df['Category']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    return model, accuracy

df = load_data()
model, accuracy = train_model(df)

# --- Sidebar ---
st.sidebar.header("🔍 Filter Options")
selected_categories = st.sidebar.multiselect("Select AMP Category", df['Category'].unique())

if selected_categories:
    df_filtered = df[df['Category'].isin(selected_categories)]
else:
    df_filtered = df

# --- Main Title ---
st.title("🧬 PhytoAMP_Finder")
st.markdown("### AI-Powered Antimicrobial Peptide Analysis from Medicinal Plants")
st.info(f"**Model Accuracy:** {accuracy*100:.2f}%")

# --- Display Data ---
st.subheader("📊 Dataset Overview")
st.dataframe(df_filtered)

# --- File Upload + Predictions ---
st.subheader("📂 Upload Your Data for AI Predictions")
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:
    user_df = pd.read_csv(uploaded_file)
    try:
        predictions = model.predict(user_df[['AMP_Score', 'Length', 'Charge']])
        user_df['Predicted_Category'] = predictions
        st.success("✅ Predictions completed successfully!")
        st.dataframe(user_df)

        # Download Button
        csv = user_df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        st.markdown(f'<a href="data:file/csv;base64,{b64}" download="predictions.csv">📥 Download Predictions</a>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error in prediction: {e}")

# --- Graph ---
st.subheader("📈 AMP Score Distribution")
fig, ax = plt.subplots()
df_filtered['AMP_Score'].hist(ax=ax, bins=20)
ax.set_title("AMP Score Distribution")
st.pyplot(fig)


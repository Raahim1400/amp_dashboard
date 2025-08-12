import os
import pickle
import pandas as pd
import streamlit as st

# --- Page Config ---
st.set_page_config(
    page_title="PhytoAMP_Finder - Disease Prediction",
    page_icon="🧬",
    layout="wide"
)

# --- Title ---
st.title("🧬 PhytoAMP_Finder: Disease-Specific AMP Prediction")

# --- Load Disease Prediction Model ---
def load_model(model_file):
    if os.path.exists(model_file):
        with open(model_file, "rb") as f:
            return pickle.load(f)
    else:
        return None

model_path = "disease_model.pkl"
model = load_model(model_path)

if model:
    st.success("✅ Model loaded successfully.")
else:
    st.error("❌ Disease model not found. Please ensure 'disease_model.pkl' exists in the app directory.")
    st.stop()

# --- File Upload ---
uploaded_file = st.file_uploader("Upload AMP Data (CSV)", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("### 📄 Uploaded Data", df.head())

        # Ensure required columns exist
        required_cols = ["AMP_score", "Hydrophobicity", "Charge", "Length"]
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            st.error(f"❌ Missing required columns: {missing_cols}")
        else:
            try:
                predictions = model.predict(df[required_cols])
                df["Predicted_Disease"] = predictions
                st.write("### 🧪 Predictions", df.head())

                # Download Predictions
                csv = df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download Predictions CSV",
                    data=csv,
                    file_name="amp_disease_predictions.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"⚠️ Prediction failed: {e}")
    except Exception as e:
        st.error(f"⚠️ Failed to read CSV file: {e}")


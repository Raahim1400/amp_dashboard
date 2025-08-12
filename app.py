import streamlit as st
import pandas as pd
import pickle

# Load the trained model
try:
    with open("model.pkl", "rb") as file:
        model = pickle.load(file)
except FileNotFoundError:
    st.error("Model file not found. Please make sure 'model.pkl' is in the same directory.")
    st.stop()

# Streamlit app title
st.title("AMP Prediction App")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file for prediction", type="csv")

if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        st.write("Uploaded Data:", data.head())

        # Check if the required features are present
        required_features = model.feature_names_in_
        if not all(feature in data.columns for feature in required_features):
            st.error(f"The uploaded CSV must contain these columns: {list(required_features)}")
        else:
            # Make predictions
            predictions = model.predict(data[required_features])
            data['Prediction'] = predictions
            st.write("Prediction Results:", data)

            # Download link for results
            csv = data.to_csv(index=False)
            st.download_button(
                label="Download Predictions as CSV",
                data=csv,
                file_name='predictions.csv',
                mime='text/csv'
            )
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")


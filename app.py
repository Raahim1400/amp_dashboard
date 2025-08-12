# Final merged PhytoAMP_Finder app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
from pyvis.network import Network
import tempfile
import os

# ML imports
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# --- Page Config ---
st.set_page_config(
    page_title="PhytoAMP_Finder",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styling (Dark Futuristic) ---
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
        .stDownloadButton>button {
            background-color: #111827;
            color: #00BFFF;
            border: 1px solid #00BFFF;
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


# -------------------------
# Utility: Normalize columns
# -------------------------
def normalize_cols(df):
    # Make a copy, normalize column names to snake_case keys
    df = df.copy()
    col_map = {}
    for col in df.columns:
        key = col.strip().lower().replace(" ", "_").replace("-", "_")
        col_map[col] = key
    df = df.rename(columns=col_map)
    return df

def ensure_cols(df, wanted):
    # return True if all wanted present in df columns
    return all(c in df.columns for c in wanted)

# -------------------------
# Load main datasets
# -------------------------
DATA_PATH = "data/amp_scores.csv"
DISEASE_PATH = "data/amp_disease_links.csv"

try:
    raw_df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error(f"Data file not found. Please upload '{DATA_PATH}' inside data folder.")
    st.stop()

df = normalize_cols(raw_df)

# Try load disease mapping
try:
    raw_df_disease = pd.read_csv(DISEASE_PATH)
    df_disease = normalize_cols(raw_df_disease)
except FileNotFoundError:
    df_disease = pd.DataFrame()

# ---------------------------------------------------
# Make best-effort column aliasing for common names
# ---------------------------------------------------
# Common alias mapping we'll try to use in code:
# amp_score -> "amp_score" or "amp_score" or "amp_score"
# amp_name -> "amp_name" or "name"
# amp_sequence -> "amp_sequence" or "sequence"
# plant -> "plant"
# length -> "length"
# charge -> "charge"
# category -> "category" or "amp_category"

# create helper to pick first available column name from candidates
def pick_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

AMP_SCORE_COL = pick_col(df, ["amp_score", "amp_score", "amp_score"])  # try these variants if you add more later
# better fallback: find any column containing 'score'
if AMP_SCORE_COL is None:
    for c in df.columns:
        if "score" in c:
            AMP_SCORE_COL = c
            break

AMP_NAME_COL = pick_col(df, ["amp_name", "name", "plant", "peptide_name"])
AMP_SEQ_COL = pick_col(df, ["amp_sequence", "sequence", "seq"])
PLANT_COL = pick_col(df, ["plant", "source_plant", "source"])
LENGTH_COL = pick_col(df, ["length", "seq_length", "peptide_length"])
CHARGE_COL = pick_col(df, ["charge", "net_charge"])
CATEGORY_COL = pick_col(df, ["category", "amp_category"])

# ensure we have minimal useful columns
if AMP_SCORE_COL is None:
    st.error("No column resembling AMP score found in amp_scores.csv (look for columns like 'AMP Score' / 'amp_score').")
    st.stop()
if PLANT_COL is None and AMP_NAME_COL is None:
    st.error("No column for plant or AMP name found. Please include 'Plant' or 'AMP Name' column.")
    st.stop()

# For display and fallback create normalized display columns
display_df = df.copy()
# create 'plant' column for plotting
if PLANT_COL:
    display_df["plant_display"] = df[PLANT_COL]
elif AMP_NAME_COL:
    display_df["plant_display"] = df[AMP_NAME_COL]
else:
    display_df["plant_display"] = df.index.astype(str)

# create amp_name col if exists
if AMP_NAME_COL:
    display_df["amp_name"] = df[AMP_NAME_COL]
else:
    display_df["amp_name"] = display_df["plant_display"]

# create amp_score numeric
display_df["amp_score_num"] = pd.to_numeric(df[AMP_SCORE_COL], errors="coerce").fillna(0)

# create seq col if exists
if AMP_SEQ_COL:
    display_df["amp_sequence"] = df[AMP_SEQ_COL]
else:
    display_df["amp_sequence"] = ""

# create category col if exists else will be predicted later
if CATEGORY_COL:
    display_df["amp_category_raw"] = df[CATEGORY_COL].astype(str)
else:
    display_df["amp_category_raw"] = None

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("🔍 Filter & Search")

search_query = st.sidebar.text_input("Search AMP (by name or sequence)", "")

min_score = float(display_df["amp_score_num"].min())
max_score = float(display_df["amp_score_num"].max())
score_range = st.sidebar.slider("AMP Score Range", min_score, max_score, (min_score, max_score))

# categories - prefer existing categories, else empty
existing_categories = []
if display_df["amp_category_raw"].notnull().any():
    existing_categories = sorted(display_df["amp_category_raw"].dropna().unique())
selected_categories = st.sidebar.multiselect("Select Categories", existing_categories, default=existing_categories)

# disease list from disease mapping file (if present)
all_diseases = []
if not df_disease.empty:
    # try pick disease column name
    disease_col = pick_col(df_disease, ["target_disease", "disease", "target"])
    if disease_col:
        all_diseases = sorted(df_disease[disease_col].dropna().unique())
selected_diseases = st.sidebar.multiselect("Select Diseases", all_diseases, default=all_diseases)

# -------------------------
# Apply Filters
# -------------------------
filtered = display_df.copy()

# search
if search_query:
    mask_name = filtered["amp_name"].str.contains(search_query, case=False, na=False)
    mask_seq = filtered["amp_sequence"].str.contains(search_query, case=False, na=False)
    filtered = filtered[mask_name | mask_seq]

# score
filtered = filtered[(filtered["amp_score_num"] >= score_range[0]) & (filtered["amp_score_num"] <= score_range[1])]

# category filter if user selected
if selected_categories:
    # check raw category column first
    if "amp_category_raw" in filtered.columns and filtered["amp_category_raw"].notnull().any():
        filtered = filtered[filtered["amp_category_raw"].isin(selected_categories)]
    else:
        # nothing to filter on
        pass

# disease filter: use df_disease mapping to find AMP names linked to selected diseases
if selected_diseases and not df_disease.empty:
    disease_col = pick_col(df_disease, ["target_disease", "disease", "target"])
    ampname_col = pick_col(df_disease, ["amp_name", "amp", "name", "amp_name"])
    if disease_col and ampname_col:
        amps_linked = df_disease[df_disease[disease_col].isin(selected_diseases)][ampname_col].unique()
        # compare against amp_name (display)
        filtered = filtered[filtered["amp_name"].isin(amps_linked)]

# -------------------------
# Category Predictor (simple rule-based fallback)
# -------------------------
def predict_amp_category(score):
    if score >= 85:
        return "High Potential"
    elif score >= 70:
        return "Moderate Potential"
    else:
        return "Low Potential"

filtered["predicted_category"] = filtered["amp_score_num"].apply(predict_amp_category)

# Prefer raw category if present, else show predicted
filtered["amp_category_final"] = filtered.apply(
    lambda r: r["amp_category_raw"] if (r["amp_category_raw"] and pd.notna(r["amp_category_raw"])) else r["predicted_category"],
    axis=1
)

# -------------------------
# Display Table & Charts
# -------------------------
st.subheader(f"AMP Score Table — {len(filtered)} Records")
st.dataframe(
    filtered[["amp_name", "plant_display", "amp_score_num", "amp_sequence", "amp_category_final"]].rename(columns={
        "amp_name": "AMP Name",
        "plant_display": "Plant",
        "amp_score_num": "AMP Score",
        "amp_sequence": "AMP Sequence",
        "amp_category_final": "AMP Category"
    }),
    use_container_width=True
)

# Bar chart: AMP Score per Plant
st.subheader("📈 AMP Score per Plant")
fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.bar(filtered["plant_display"], filtered["amp_score_num"], color="#FF4B4B")
ax1.set_xlabel("Plant")
ax1.set_ylabel("AMP Score")
ax1.set_title("AMP Score Comparisons")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
st.pyplot(fig1)

# Pie chart
st.subheader("🍩 AMP Score Distribution")
fig2, ax2 = plt.subplots(figsize=(6, 6))
ax2.pie(filtered["amp_score_num"], labels=filtered["plant_display"], autopct='%1.1f%%', startangle=140)
ax2.axis('equal')
st.pyplot(fig2)

# Histogram by category
st.subheader("📊 AMP Score Histogram (by Category)")
fig_hist, ax_hist = plt.subplots(figsize=(8, 4))
cats = filtered["amp_category_final"].unique()
for cat in cats:
    subset = filtered[filtered["amp_category_final"] == cat]
    ax_hist.hist(subset["amp_score_num"], bins=10, alpha=0.6, label=cat)
ax_hist.set_xlabel("AMP Score")
ax_hist.set_ylabel("Frequency")
ax_hist.legend()
st.pyplot(fig_hist)

# -------------------------
# Download filtered CSV
# -------------------------
def make_download_link(df_to_download, filename="filtered_amps.csv"):
    csv = df_to_download.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f"data:file/csv;base64,{b64}"

st.markdown("#### ⬇️ Download Filtered Results")
dl_link = make_download_link(filtered, "filtered_AMP_data.csv")
st.markdown(f'<a href="{dl_link}" download="filtered_AMP_data.csv">📥 Download Filtered Data (CSV)</a>', unsafe_allow_html=True)

# Category-wise downloads
st.subheader("⬇️ Download Category-wise Data")
for category in filtered['amp_category_final'].unique():
    cat_df = filtered[filtered['amp_category_final'] == category]
    csv = cat_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{category}_AMPs.csv">Download {category} AMPs</a>'
    st.markdown(href, unsafe_allow_html=True)

# -------------------------
# Summary
# -------------------------
st.markdown("""
    <hr>
    <div style='text-align: center; font-size: 16px; color: #FFFFFF;'>
        <p><strong>Summary:</strong><br>
        Total Records Shown: <span style='color: #00BFFF;'>{total}</span>  &nbsp;|&nbsp;
        High Potential: <span style='color: #00FF00;'>{high}</span>  &nbsp;|&nbsp;
        Moderate Potential: <span style='color: #FFA500;'>{mod}</span>  &nbsp;|&nbsp;
        Low Potential: <span style='color: #FF4B4B;'>{low}</span></p>
    </div>
""".format(
    total=len(filtered),
    high=sum(filtered['amp_category_final'] == 'High Potential'),
    mod=sum(filtered['amp_category_final'] == 'Moderate Potential'),
    low=sum(filtered['amp_category_final'] == 'Low Potential')
), unsafe_allow_html=True)

# -------------------------
# Network Graph: Disease <-> AMP
# -------------------------
st.subheader("🌐 Disease ↔ AMP Network Graph")
if not df_disease.empty:
    # try to find columns in disease mapping
    dc_amp = pick_col(df_disease, ["amp_name", "amp", "name", "amp_name"])
    dc_disease = pick_col(df_disease, ["target_disease", "disease", "target"])
    if not dc_amp or not dc_disease:
        st.warning("Disease mapping file loaded but expected columns not found. Expected columns like 'AMP Name' and 'Target Disease'.")
    else:
        net = Network(height="600px", width="100%", bgcolor="#0E1117", font_color="white")
        # Only include mapping rows that match the filtered AMP list (so graph syncs with filters)
        amps_in_view = set(filtered["amp_name"])
        for _, row in df_disease.iterrows():
            amp_val = row[dc_amp]
            disease_val = row[dc_disease]
            # optionally filter to amps in current filtered set (so graph matches)
            if amp_val not in amps_in_view:
                continue
            net.add_node(amp_val, label=str(amp_val), color="#00BFFF", title=str(amp_val), shape="dot", size=15)
            net.add_node(disease_val, label=str(disease_val), color="#FF4B4B", title=str(disease_val), shape="diamond", size=20)
            net.add_edge(amp_val, disease_val)
        # Save and embed
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        net.save_graph(tmp_file.name)
        with open(tmp_file.name, "r", encoding="utf-8") as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=650)
        try:
            os.unlink(tmp_file.name)
        except Exception:
            pass
else:
    st.info("No disease mapping file found. Add 'data/amp_disease_links.csv' to enable network graph and disease searches.")

# -------------------------
# Disease search box (text) that queries mapping and shows results
# -------------------------
st.markdown("### 🔎 Find Effective AMPs for a Disease")
disease_query = st.text_input("Enter disease name (e.g. Pneumonia, MRSA, Candidiasis):")
if disease_query and not df_disease.empty:
    dc_amp = pick_col(df_disease, ["amp_name", "amp", "name", "amp_name"])
    dc_disease = pick_col(df_disease, ["target_disease", "disease", "target"])
    if dc_amp and dc_disease:
        res = df_disease[df_disease[dc_disease].str.contains(disease_query, case=False, na=False)]
        if not res.empty:
            st.success(f"Found {len(res)} AMP(s) for '{disease_query}':")
            # try to show columns AMP Name, Source Plant, Target Gene/Protein, Confidence Score if they exist
            show_cols = []
            for c in ["amp_name", "source_plant", "source", "target_gene_protein", "target_gene", "confidence_score", "confidence"]:
                if c in df_disease.columns:
                    show_cols.append(c)
            if not show_cols:
                # fallback to amp and disease columns
                show_cols = [dc_amp, dc_disease]
            st.table(res[show_cols].rename(columns={dc_amp: "AMP Name", dc_disease: "Target Disease"}).head(200))
        else:
            st.warning("No AMP found for this disease in mapping file.")
    else:
        st.warning("Disease mapping file doesn't contain expected columns to search.")
elif disease_query and df_disease.empty:
    st.warning("Disease mapping file not available. Add 'data/amp_disease_links.csv' in data folder.")

# -------------------------
# Step 3: ML Model Training + Upload Predictions
# -------------------------
st.markdown("---")
st.subheader("🤖 Model Training & Predictions (Step 3)")

# We expect model features: amp_score, length, charge  (many filenames had different names)
MODEL_FEATURES = []
if AMP_SCORE_COL:
    MODEL_FEATURES.append(AMP_SCORE_COL)
if LENGTH_COL:
    MODEL_FEATURES.append(LENGTH_COL)
if CHARGE_COL:
    MODEL_FEATURES.append(CHARGE_COL)

# Train only if required columns exist and there's a category column
TRAIN_OK = False
if CATEGORY_COL and MODEL_FEATURES and ensure_cols(df, MODEL_FEATURES):
    # build X,y on the normalized df (not display_df) with those columns
    try:
        X = pd.to_numeric(df[MODEL_FEATURES[0]], errors="coerce")
        X = pd.DataFrame({MODEL_FEATURES[0]: pd.to_numeric(df[MODEL_FEATURES[0]], errors="coerce")})
        # if more features add them
        for feat in MODEL_FEATURES[1:]:
            X[feat] = pd.to_numeric(df[feat], errors="coerce")
        y = df[CATEGORY_COL].astype(str)
        # drop NA rows
        tmp = pd.concat([X, y], axis=1).dropna()
        X_clean = tmp[X.columns]
        y_clean = tmp[y.name]
        if len(X_clean) >= 10:
            X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)
            model = RandomForestClassifier(random_state=42, n_estimators=100)
            model.fit(X_train, y_train)
            accuracy = model.score(X_test, y_test)
            TRAIN_OK = True
        else:
            model = None
            accuracy = None
            st.info("Not enough rows to train ML model (need >=10 clean rows). Skipping training.")
    except Exception as e:
        model = None
        accuracy = None
        st.warning(f"Model training failed: {e}")
else:
    model = None
    accuracy = None
    st.info("ML training skipped: ensure your amp_scores.csv contains category column and features (score,length,charge).")

if TRAIN_OK:
    st.success(f"Model trained. Test accuracy: {accuracy*100:.2f}%")
else:
    st.info("Model not trained. Upload-only prediction (if you have a saved model) is still possible below.")

# File upload for user data and predictions
st.subheader("📂 Upload CSV for Predictions")
uploaded_file = st.file_uploader("Upload CSV file with feature columns for prediction (score, length, charge)", type=["csv"])
if uploaded_file is not None:
    user_df_raw = pd.read_csv(uploaded_file)
    user_df = normalize_cols(user_df_raw)
    # Build expected feature names in user_df matching our MODEL_FEATURES by fuzzy matching
    user_features = []
    for feat in MODEL_FEATURES:
        # feat is a column name in normalized df (e.g., 'amp_score' or 'length')
        candidate = pick_col(user_df, [feat, feat.replace("_", "")])
        if candidate:
            user_features.append(candidate)
        else:
            # try to find any numeric column containing same token
            token = feat.split("_")[0]
            found = None
            for c in user_df.columns:
                if token in c:
                    found = c
                    break
            if found:
                user_features.append(found)
    # final check
    if model is None:
        st.warning("No trained model available in-app. If you have an exported model file, we can add a model-load button. For now prediction won't run.")
    else:
        if len(user_features) < len(MODEL_FEATURES):
            st.error("Uploaded file doesn't contain expected features for prediction. Required: " + ", ".join(MODEL_FEATURES))
        else:
            try:
                X_user = pd.DataFrame()
                for orig_feat, user_feat in zip(MODEL_FEATURES, user_features):
                    X_user[orig_feat] = pd.to_numeric(user_df[user_feat], errors="coerce")
                X_user = X_user.fillna(0)
                preds = model.predict(X_user)
                user_df_raw["Predicted_Category"] = preds
                st.success("✅ Predictions completed successfully!")
                st.dataframe(user_df_raw)
                # download
                csv = user_df_raw.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                st.markdown(f'<a href="data:file/csv;base64,{b64}" download="predictions.csv">📥 Download Predictions (CSV)</a>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error while predicting: {e}")

# Footer
st.markdown("""
    <hr>
    <div style='text-align: center; color: gray;'>
        Made by Raahim | Project: AMP Screening Dashboard | 2025
    </div>
""", unsafe_allow_html=True)

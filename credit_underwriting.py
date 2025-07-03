import streamlit as st
import pandas as pd
import joblib

# Title
st.title("📊 Credit Underwriting Prediction System")

# Sidebar
st.sidebar.header("📁 Upload Applicant Data")

# Load model
@st.cache_resource
def load_model():
    return joblib.load("credit_model_with_validation.pkl")

model = load_model()

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

# Tips section
with st.expander("💡 Tips to Improve Your CIBIL Score"):
    tips = [
        "1. Pay credit card and loan EMIs on time.",
        "2. Keep your credit utilization below 30%.",
        "3. Maintain a mix of secured and unsecured loans.",
        "4. Avoid frequent credit inquiries or loan applications.",
        "5. Regularly check your credit report for errors."
    ]
    for tip in tips:
        st.markdown(f"- {tip}")

# When CSV is uploaded
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader("📄 Uploaded Data")
        st.dataframe(df)

        # Preprocess similar to your training script
        df.columns = df.columns.str.strip()
        df['loan_interest'] = df['loan_interest'].replace({',': '.'}, regex=True).astype(float)
        df['loan_percent_income'] = df['loan_percent_income'].replace({',': '.'}, regex=True).astype(float)

        categorical_cols = ['gender', 'marital_status', 'employee_status', 'residence_type', 'loan_purpose', 'loan_type']
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

        # Align columns with model
        model_features = model.feature_names_in_
        missing_cols = set(model_features) - set(df.columns)
        for col in missing_cols:
            df[col] = 0
        df = df[model_features]

        # Predict
        preds = model.predict(df)
        df["Prediction"] = preds
        df["Prediction"] = df["Prediction"].map({0: "Rejected", 1: "Approved"})

        st.subheader("📈 Predictions")
        st.dataframe(df)

    except Exception as e:
        st.error(f"⚠️ Error processing file: {e}")
else:
    st.info("Please upload a CSV file to get predictions.")

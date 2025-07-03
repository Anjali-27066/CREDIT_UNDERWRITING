# credit_underwriting.py

import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="AI Credit Underwriting", layout="wide")

# Load model
@st.cache_resource
def load_model():
    return joblib.load("credit_model_with_validation.pkl")

model = load_model()
submitted_data = []

# Title
st.markdown("""
    <h1 style='text-align: center; background-color: #28a745; color: white; padding: 10px;'>
        AI Predictive Methods for Credit Underwriting
    </h1>
""", unsafe_allow_html=True)

# Sidebar Navigation
page = st.sidebar.radio("Navigate", ["Personal Information", "Loan Details", "Upload Documents", "Final Decision"])

if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# Page 1: Personal Information
if page == "Personal Information":
    st.subheader("Personal Information")
    name = st.text_input("Applicant Name")
    age = st.number_input("Age", min_value=18, max_value=70, step=1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    income = st.number_input("Annual Income (in ₹)", min_value=0.0)

    if st.button("Save Personal Info"):
        if name and income > 0:
            st.session_state.user_data.update({
                "name": name, "applicant_age": age, "gender": gender, "income_annum": income
            })
            st.success("✅ Personal Info Saved")
        else:
            st.warning("Please enter valid name and income.")

# Page 2: Loan Details
elif page == "Loan Details":
    st.subheader("Loan Details")
    marital_status = st.selectbox("Marital Status", ["Single", "Married"])
    emp_status = st.selectbox("Employment Status", ["Employed", "Unemployed", "Self-Employed"])
    residence = st.selectbox("Residence Type", ["Owned", "Rented", "Mortgaged"])
    cibil = st.slider("CIBIL Score", min_value=300, max_value=900)
    loan_amount = st.number_input("Loan Amount (in ₹)", min_value=10000.0)
    loan_interest = st.number_input("Loan Interest (%)", min_value=1.0, max_value=30.0)
    loan_type = st.selectbox("Loan Type", ["House", "Vehicle", "Education", "Gold", "Personal", "Business"])
    purpose = st.text_input("Purpose of Loan")
    loan_term = st.number_input("Loan Term (in months)", min_value=6, max_value=360, value=60)
    active_loans = st.number_input("Number of Active Loans", min_value=0, step=1)

    percent_income = loan_amount / st.session_state.user_data.get("income_annum", 1) * 100

    if st.button("Save Loan Details"):
        if purpose and loan_amount < st.session_state.user_data.get("income_annum", 1) * 10:
            user_entry = {
                **st.session_state.user_data,
                "marital_status": marital_status,
                "employee_status": emp_status,
                "residence_type": residence,
                "cibil_score": cibil,
                "loan_amount": loan_amount,
                "loan_interest": loan_interest,
                "loan_percent_income": percent_income,
                "loan_type": loan_type,
                "loan_purpose": purpose,
                "loan_term": loan_term,
                "active_loans": active_loans,
                "residential_assets_value": 0,
                "commercial_assets_value": 0,
                "luxury_assets_value": 0,
                "bank_asset_value": 0
            }
            if user_entry in submitted_data:
                st.error("Duplicate application detected! ❌")
            else:
                submitted_data.append(user_entry)
                st.session_state.user_data = user_entry
                st.success("✅ Loan Info Saved")
        else:
            st.warning("Enter a valid loan purpose and ensure amount is reasonable.")

# Page 3: Upload Documents
elif page == "Upload Documents":
    st.subheader("Upload Documents")
    aadhar = st.file_uploader("Upload Aadhar Card")
    pan = st.file_uploader("Upload PAN Card")
    salary_slip = st.file_uploader("Upload Salary Slip")

    if aadhar and pan and salary_slip:
        st.success("✅ All documents uploaded successfully")
    else:
        st.info("Please upload all required documents.")

# Page 4: Final Decision
elif page == "Final Decision":
    st.subheader("Final Decision")

    if "loan_amount" not in st.session_state.user_data:
        st.warning("Please complete previous steps.")
    else:
        input_df = pd.DataFrame([st.session_state.user_data])
        input_df["loan_interest"] = input_df["loan_interest"].astype(float)
        input_df["loan_percent_income"] = input_df["loan_percent_income"].astype(float)

        cat_cols = ["gender", "marital_status", "employee_status", "residence_type", "loan_purpose", "loan_type"]
        input_df = pd.get_dummies(input_df, columns=cat_cols, drop_first=True)

        for col in model.feature_names_in_:
            if col not in input_df.columns:
                input_df[col] = 0

        input_df = input_df[model.feature_names_in_]
        pred = model.predict(input_df)[0]
        label = "Loan Approved ✅" if pred == 1 else "Loan Rejected ❌"

        st.success(label)

# Tips to Improve CIBIL Score
with st.expander("💡 Tips to Improve Your CIBIL Score"):
    tips = [
        "Pay EMIs on time.",
        "Keep credit usage below 30%.",
        "Maintain a mix of secured and unsecured loans.",
        "Avoid frequent loan applications.",
        "Check credit report regularly."
    ]
    for tip in tips:
        st.markdown(f"- {tip}")

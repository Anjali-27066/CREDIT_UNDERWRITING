# credit_underwriting.py

import streamlit as st
import pandas as pd
import joblib
import re
import uuid

st.set_page_config(page_title="AI Credit Underwriting", layout="wide")

# Load model
@st.cache_resource
def load_model():
    return joblib.load("credit_model_with_validation.pkl")

model = load_model()
submitted_data = []

st.markdown("""
    <h1 style='text-align: center; background-color: #28a745; color: white; padding: 10px;'>
        AI Predictive Methods for Credit Underwriting
    </h1>
""", unsafe_allow_html=True)

if "current_page" not in st.session_state:
    st.session_state.current_page = 0

pages = ["Personal Information", "Loan Details", "Upload Documents", "Final Decision"]
page = pages[st.session_state.current_page]

# Sidebar Chatbot and CIBIL Tips
st.sidebar.title("🤖 Finance Chatbot")
user_q = st.sidebar.text_input("Ask about loans, CIBIL, etc...")
if user_q:
    if "cibil" in user_q.lower():
        st.sidebar.info("CIBIL score is influenced by timely payments, credit usage, and inquiries.")
    elif "loan" in user_q.lower():
        st.sidebar.info("Loan eligibility depends on income, credit score, and obligations.")
    elif "interest" in user_q.lower():
        st.sidebar.info("Interest rates vary based on loan type, bank, and applicant profile.")
    else:
        st.sidebar.info("This is a basic finance assistant. For legal advice, consult a financial expert.")

st.sidebar.markdown("---")
st.sidebar.markdown("**💡 Tips to Improve Your CIBIL Score**")
st.sidebar.markdown("""
- Pay EMIs on time.
- Keep credit usage below 30%.
- Maintain a mix of secured and unsecured loans.
- Avoid frequent loan applications.
- Check credit report regularly.
""")

if "user_data" not in st.session_state:
    st.session_state.user_data = {}

if "registered_ids" not in st.session_state:
    st.session_state.registered_ids = {}

# Page 1: Personal Information
if page == "Personal Information":
    st.subheader("Personal Information")
    name = st.text_input("Applicant Name")
    age = st.number_input("Age", min_value=18, max_value=70, step=1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    income = st.number_input("Annual Income (in ₹)", min_value=0.0)
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    address = st.text_area("Permanent Address")

    def is_valid_phone(p):
        return re.fullmatch(r"[6-9][0-9]{9}", p) and p not in ["0000000000", "9999999999"]

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        save = st.button("Save Personal Info")
    with col2:
        next_pg = st.button("Next ➡️")
    with col3:
        prev = st.button("⬅️ Previous")

    if save:
        if name and income > 0 and re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", email) and is_valid_phone(phone):
            if name in st.session_state.registered_ids:
                st.warning(f"⚠️ Applicant '{name}' already registered with ID: {st.session_state.registered_ids[name]}")
            else:
                unique_id = str(uuid.uuid4())[:8]
                st.session_state.registered_ids[name] = unique_id
                st.session_state.user_data.update({
                    "applicant_id": unique_id,
                    "name": name,
                    "applicant_age": age,
                    "gender": gender,
                    "income_annum": income,
                    "email": email,
                    "phone": phone,
                    "address": address
                })
                st.success(f"✅ Personal Info Saved. Your Applicant ID is: {unique_id}")
        else:
            st.warning("❌ Enter valid name, income, email, and phone number.")

    if next_pg:
        st.session_state.current_page = 1
    if prev and st.session_state.current_page > 0:
        st.session_state.current_page -= 1

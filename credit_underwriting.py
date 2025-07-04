# credit_underwriting.py

import streamlit as st
import pandas as pd
import joblib
import re
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="AI Credit Underwriting", layout="wide")

# Load model
@st.cache_resource
def load_model():
    return joblib.load("credit_model_with_validation.pkl")

model = load_model()
submitted_data = []

# Email configuration
email_user = "your_email@gmail.com"
email_pass = "your_app_password"

def send_email(to, applicant_id):
    try:
        subject = "Loan Approval Notification"
        body = f"Dear Applicant,\n\nCongratulations! Your loan has been approved.\nYour unique Applicant ID: {applicant_id}\n\nRegards,\nCredit Underwriting Team"

        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_pass)
        text = msg.as_string()
        server.sendmail(email_user, to, text)
        server.quit()
        return True
    except Exception as e:
        st.warning("📧 Email could not be sent. Check credentials or internet.")
        return False

# Title
st.markdown("""
    <h1 style='text-align: center; background-color: #28a745; color: white; padding: 10px;'>
        AI Predictive Methods for Credit Underwriting
    </h1>
""", unsafe_allow_html=True)

if "current_page" not in st.session_state:
    st.session_state.current_page = 0

pages = ["Personal Information", "Loan Details", "Upload Documents", "Final Decision"]
page = pages[st.session_state.current_page]

# Sidebar Chatbot and Tips
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

# --- Page 1: Personal Info ---
if page == "Personal Information":
    st.subheader("Personal Information")
    name = st.text_input("Applicant Name")
    age = st.number_input("Age", min_value=18, max_value=70)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    income = st.number_input("Annual Income (₹)", min_value=0.0)
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    address = st.text_area("Permanent Address")

    def is_valid_phone(p):
        return re.fullmatch(r"[6-9][0-9]{9}", p) and p not in ["0000000000", "9999999999"]

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        save = st.button("Save Personal Info")
    with col2:
        next_pg = st.button("Next ➡️", key="next_pg_1")
    with col3:
        prev = st.button("⬅️ Previous")

    if save:
        if name and income > 0 and re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", email) and is_valid_phone(phone):
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
            st.success(f"✅ Personal Info Saved. ID: {unique_id}")
        else:
            st.warning("❌ Enter valid name, income, email, and phone number.")

    if next_pg:
        if all(key in st.session_state.user_data for key in ["name", "income_annum", "email", "phone"]):
            st.session_state.current_page = 1
        else:
            st.warning("Please save valid personal info before proceeding.")




# --- Page 2: Loan Details ---
elif page == "Loan Details":
    st.subheader("Loan Details")
    marital_status = st.selectbox("Marital Status", ["Single", "Married"])
    emp_status = st.selectbox("Employment Status", ["Employed", "Unemployed", "Self-Employed"])
    residence = st.selectbox("Residence Type", ["Owned", "Rented", "Mortgaged"])
    cibil = st.slider("CIBIL Score", min_value=300, max_value=900)
    loan_amount = st.number_input("Loan Amount (₹)", min_value=10000.0)
    loan_interest = st.number_input("Loan Interest (%)", min_value=1.0, max_value=30.0)
    loan_type = st.selectbox("Loan Type", ["House", "Vehicle", "Education", "Gold", "Personal", "Business"])
    purpose = st.text_input("Purpose of Loan")
    loan_term = st.number_input("Loan Term (months)", min_value=6, max_value=360, value=60)
    active_loans = st.number_input("Active Loans", min_value=0)
    percent_income = loan_amount / st.session_state.user_data.get("income_annum", 1) * 100

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        save_loan = st.button("Save Loan Details")
    with col2:
        next_loan = st.button("Next ➡️", key="next_pg_2")
    with col3:
        prev_loan = st.button("⬅️ Previous", key="back_pg_1")

    if save_loan:
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
                "active_loans": active_loans
            }
            st.session_state.user_data = user_entry
            submitted_data.append(user_entry)
            st.success("✅ Loan Info Saved")
        else:
            st.warning("Invalid purpose or high loan amount.")

    if next_loan:
        st.session_state.current_page = 2
    if prev_loan:
        st.session_state.current_page = 0

# --- Page 3: Upload Documents ---
elif page == "Upload Documents":
    st.subheader("Upload Documents")
    aadhar = st.file_uploader("Upload Aadhar Card")
    pan = st.file_uploader("Upload PAN Card")
    loan_type = st.session_state.user_data.get("loan_type", "").lower()

    if loan_type == "education":
        if aadhar and pan:
            st.success("✅ Documents uploaded (Salary slip not required)")
        else:
            st.info("Upload Aadhar & PAN for education loan.")
    else:
        salary_slip = st.file_uploader("Upload Salary Slip")
        if aadhar and pan and salary_slip:
            st.success("✅ All documents uploaded successfully")
        else:
            st.info("Upload Aadhar, PAN & Salary slip.")

    col1, col2 = st.columns([2, 2])
    if col1.button("⬅️ Previous", key="back_pg_2"):
        st.session_state.current_page = 1
    if col2.button("Next ➡️", key="to_final"):
        st.session_state.current_page = 3

# --- Page 4: Final Decision ---
elif page == "Final Decision":
    st.subheader("Final Decision")
    if "loan_amount" not in st.session_state.user_data:
        st.warning("Please complete previous steps.")
    else:
        df = pd.DataFrame([st.session_state.user_data])
        df["loan_interest"] = df["loan_interest"].astype(float)
        df["loan_percent_income"] = df["loan_percent_income"].astype(float)
        cat_cols = ["gender", "marital_status", "employee_status", "residence_type", "loan_purpose", "loan_type"]
        df = pd.get_dummies(df, columns=cat_cols, drop_first=True)

        for col in model.feature_names_in_:
            if col not in df.columns:
                df[col] = 0
        df = df[model.feature_names_in_]
        pred = model.predict(df)[0]
        label = "Loan Approved ✅" if pred == 1 else "Loan Rejected ❌"

        if st.button("Submit Application"):
            if pred == 1:
                st.success(label)
                send_email(st.session_state.user_data["email"], st.session_state.user_data["applicant_id"])
            else:
                st.error(label)
                st.info("Tips to improve approval chances:")
                st.markdown("""
                    - Improve your CIBIL score above 700.
                    - Keep loan amount relative to income low.
                    - Close or reduce active loans.
                    - Ensure stable income/employment.
                """)

        if submitted_data:
            st.markdown("### Previous Applicants")
            st.dataframe(pd.DataFrame(submitted_data))

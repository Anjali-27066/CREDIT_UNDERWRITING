import streamlit as st
import pandas as pd
import re
import uuid
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

st.set_page_config(page_title="AI Credit Underwriting", layout="wide")

# Dummy model for prediction
class DummyModel:
    def __init__(self):
        self.feature_names_in_ = [
            'applicant_age', 'income_annum', 'cibil_score', 'loan_amount',
            'loan_interest', 'loan_percent_income', 'loan_term', 'active_loans',
            'gender_Male', 'gender_Other',
            'marital_status_Single', 'employee_status_Self-Employed',
            'employee_status_Unemployed', 'residence_type_Owned',
            'residence_type_Rented', 'loan_type_House', 'loan_type_Personal',
            'loan_purpose_Business Expansion'
        ]

    def predict(self, X):
        return [1 if x['cibil_score'] >= 700 and x['loan_percent_income'] < 70 else 0 for _, x in X.iterrows()]

    def predict_proba(self, X):
        return [[0.2, 0.8] if self.predict(X)[i] == 1 else [0.9, 0.1] for i in range(len(X))]

model = DummyModel()
submitted_data = []

# Email simulation
def send_decision_email(to_email, applicant_name, decision, details):
    message = f"""
📧 [SIMULATION ONLY]
TO: {to_email}
APPLICANT: {applicant_name}
DECISION: {decision.upper()}
DETAILS: {details}
    """
    st.info(message)

# Phone validation
def is_valid_phone(p):
    return re.fullmatch(r"[6-9][0-9]{9}", p) and p not in ["0000000000", "9999999999"]

# OCR function
def extract_text_from_file(uploaded_file):
    poppler_path = r"C:\\Users\\anjali\\Downloads\\Release-24.08.0-0\\poppler-24.08.0\\Library\\bin"
    if uploaded_file.name.endswith(".pdf"):
        images = convert_from_bytes(uploaded_file.read(), dpi=300, poppler_path=poppler_path)
        return "".join([pytesseract.image_to_string(image) for image in images])
    else:
        image = Image.open(uploaded_file)
        return pytesseract.image_to_string(image)

# Session state
if "current_page" not in st.session_state:
    st.session_state.current_page = 0
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

pages = ["Personal Information", "Loan Details", "Upload Documents", "Final Decision"]
page = pages[st.session_state.current_page]
# --- Sidebar Chatbot Header ---
st.sidebar.markdown("## 🤖 AI Financial Chatbot")

# --- Initialize Chat History & Session Variables ---
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"role": "bot", "content": "👋 Hello! Ask about loans, EMI, credit scores, or investments!"}
    ]
if "last_topic" not in st.session_state:
    st.session_state["last_topic"] = None  
if "emi_active" not in st.session_state:
    st.session_state["emi_active"] = False  
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""  

# --- Chatbot Response System ---
def chatbot_response(user_message):
    user_message = user_message.lower().strip()
    
    responses = {
        "greetings": ["hello", "hi", "hey", "how are you"],
        "loan": ["loan", "borrow money", "finance", "lending"],
        "emi": ["emi", "monthly payment", "installment"],
        "credit_score": ["credit score", "cibil", "credit rating"]
    }
    
    loans = {
        "Personal Loan": "🏦 *Personal Loan:* ₹50K-₹25L | 10-15% Interest | No Collateral",
        "Business Loan": "💼 *Business Loan:* ₹5L-₹5Cr | 10-18% Interest | Requires Collateral",
        "Student Loan": "🎓 *Student Loan:* ₹1L-₹50L | 5-8% Interest",
        "Home Loan": "🏡 *Home Loan:* ₹10L-₹1Cr | 7-9% Interest",
        "Car Loan": "🚗 *Car Loan:* ₹1L-₹50L | 8-12% Interest"
    }
    
    if user_message in responses["greetings"]:
        return "👋 Hello! How can I assist you today?"
    
    if any(word in user_message for word in responses["loan"]):
        st.session_state["last_topic"] = "loan"
        return "📌 *Loan Help:* Select a loan type below."
    
    if st.session_state["last_topic"] == "loan":
        for key, response in loans.items():
            if key.lower() in user_message:
                st.session_state["last_topic"] = None
                return response
    
    if any(word in user_message for word in responses["emi"]):
        st.session_state["emi_active"] = True
        return "📊 *EMI Calculator Activated!* Enter loan details below."
    
    if any(word in user_message for word in responses["credit_score"]):
        return "🔍 *Credit Score Guide:\n- **750+* = Excellent ✅\n- *650-749* = Good 👍\n- *550-649* = Fair ⚠\n- *Below 550* = Poor ❌"
    
    return "🤖 Hmm, I don't have an answer for that. Try asking about loans, EMI, or investments!"

# --- Display Chat History ---
st.sidebar.markdown("### 💬 Chat History:")

for message in st.session_state["chat_messages"]:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(f"👤 *You:* {message['content']}")
    else:
        with st.chat_message("assistant"):
            st.write(f"🤖 *Bot:* {message['content']}")

# --- Loan Selection Dropdown ---
if st.session_state["last_topic"] == "loan":
    with st.sidebar:
        st.markdown("### 📌 Select a Loan Type:")
        
        loan_types = {
            "Personal Loan": "🏦 *Personal Loan:* ₹50K-₹25L | 10-15% Interest | No Collateral",
            "Business Loan": "💼 *Business Loan:* ₹5L-₹5Cr | 10-18% Interest | Requires Collateral",
            "Student Loan": "🎓 *Student Loan:* ₹1L-₹50L | 5-8% Interest",
            "Home Loan": "🏡 *Home Loan:* ₹10L-₹1Cr | 7-9% Interest",
            "Car Loan": "🚗 *Car Loan:* ₹1L-₹50L | 8-12% Interest"
        }

        selected_loan = st.selectbox("Select a Loan Type:", list(loan_types.keys()))

        if st.button("🔍 Get Loan Details"):
            # Add loan details as a bot message
            st.session_state["chat_messages"].append({"role": "bot", "content": loan_types[selected_loan]})
            st.session_state["last_topic"] = None  # Reset topic after selection
            st.rerun()


# --- User Input Field ---
user_input = st.sidebar.text_input("💬 Type your question:", value=st.session_state["user_input"], key="chat_input")

if st.sidebar.button("🚀 Send"):
    if user_input.strip():
        st.session_state["chat_messages"].append({"role": "user", "content": user_input})
        bot_reply = chatbot_response(user_input)
        st.session_state["chat_messages"].append({"role": "bot", "content": bot_reply})
        st.session_state["user_input"] = ""
        st.rerun()

# --- EMI Calculator ---
if st.session_state["emi_active"]:
    st.sidebar.markdown("### 📊 EMI Calculator")
    loan_amount = st.sidebar.number_input("Loan Amount (₹)", min_value=1000, value=500000, step=1000)
    interest_rate = st.sidebar.number_input("Interest Rate (%)", min_value=1.0, value=10.0, step=0.1)
    tenure = st.sidebar.number_input("Tenure (Years)", min_value=1, value=5, step=1)
    
    if st.sidebar.button("📊 Calculate EMI"):
        r = (interest_rate / 12) / 100
        n = tenure * 12
        emi_result = round((loan_amount * r * (1 + r) ** n) / ((1 + r) ** n - 1), 2)
        st.sidebar.success(f"📌 Your Monthly EMI: ₹{emi_result:,}")

    if st.sidebar.button("🔄 Reset EMI Calculator"):
        st.session_state["emi_active"] = False
        st.rerun()

# --- Clear Chat History Button ---
if st.sidebar.button("🗑 Clear Chat History"):
    st.session_state["chat_messages"] = []
    st.session_state["last_topic"] = None
    st.rerun()

# Personal Info Page
if page == "Personal Information":
    st.subheader("Personal Information")
    name = st.text_input("Applicant Name", value=st.session_state.user_data.get("name", ""))
    age = st.number_input("Age", 18, 70, value=st.session_state.user_data.get("applicant_age", 18))
    gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state.user_data.get("gender", "Male")))
    income = st.number_input("Annual Income (₹)", min_value=0.0, value=st.session_state.user_data.get("income_annum", 0.0))
    email = st.text_input("Email Address", value=st.session_state.user_data.get("email", ""))
    phone = st.text_input("Phone Number", value=st.session_state.user_data.get("phone", ""))
    address = st.text_area("Permanent Address", value=st.session_state.user_data.get("address", ""))

    if st.button("Save Personal Info"):
        if name and income > 0 and re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", email) and is_valid_phone(phone):
            if "applicant_id" not in st.session_state.user_data:
                st.session_state.user_data["applicant_id"] = str(uuid.uuid4())
            st.session_state.user_data.update({
                "name": name, "applicant_age": age, "gender": gender,
                "income_annum": income, "email": email, "phone": phone,
                "address": address
            })
            st.success("✅ Personal Info Saved")
        else:
            st.warning("❌ Enter valid name, income, email, and phone number.")

    if st.button("Next ➡"):
        st.session_state.current_page = 1

# Loan Details Page
elif page == "Loan Details":
    st.subheader("Loan Details")
    marital_status = st.selectbox("Marital Status", ["Single", "Married"], index=["Single", "Married"].index(st.session_state.user_data.get("marital_status", "Single")))
    emp_status = st.selectbox("Employment Status", ["Employed", "Unemployed", "Self-Employed"], index=["Employed", "Unemployed", "Self-Employed"].index(st.session_state.user_data.get("employee_status", "Employed")))
    residence = st.selectbox("Residence Type", ["Owned", "Rented", "Mortgaged"], index=["Owned", "Rented", "Mortgaged"].index(st.session_state.user_data.get("residence_type", "Owned")))
    cibil = st.slider("CIBIL Score", 300, 900, value=st.session_state.user_data.get("cibil_score", 650))
    loan_amount = st.number_input("Loan Amount (₹)", min_value=10000.0, value=st.session_state.user_data.get("loan_amount", 10000.0))
    loan_interest = st.number_input("Loan Interest (%)", min_value=1.0, max_value=30.0, value=st.session_state.user_data.get("loan_interest", 10.0))
    loan_type = st.selectbox("Loan Type", ["House", "Vehicle", "Education", "Gold", "Personal", "Business"], index=["House", "Vehicle", "Education", "Gold", "Personal", "Business"].index(st.session_state.user_data.get("loan_type", "House")))
    purpose = st.text_input("Purpose of Loan", value=st.session_state.user_data.get("loan_purpose", ""))
    loan_term = st.number_input("Loan Term (months)", 6, 360, value=st.session_state.user_data.get("loan_term", 60))
    active_loans = st.number_input("Active Loans", min_value=0, value=st.session_state.user_data.get("active_loans", 0))

    percent_income = loan_amount / max(st.session_state.user_data.get("income_annum", 1), 1) * 100

    if st.button("Save Loan Details"):
        if purpose:
            st.session_state.user_data.update({
                "marital_status": marital_status, "employee_status": emp_status,
                "residence_type": residence, "cibil_score": cibil,
                "loan_amount": loan_amount, "loan_interest": loan_interest,
                "loan_percent_income": percent_income, "loan_type": loan_type,
                "loan_purpose": purpose, "loan_term": loan_term,
                "active_loans": active_loans
            })
            submitted_data.append(st.session_state.user_data.copy())
            st.success("✅ Loan Info Saved")
        else:
            st.warning("Enter a valid loan purpose.")

    if st.button("Next ➡", key="to_docs"):
        st.session_state.current_page = 2
    if st.button("⬅ Previous", key="back1"):
        st.session_state.current_page = 0

# Upload Documents Page (Enhanced)
elif page == "Upload Documents":
    st.subheader("Upload Documents")

    # Aadhar Upload
    aadhar = st.file_uploader("Upload Aadhar Card (Image or PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])
    if aadhar:
        try:
            text = extract_text_from_file(aadhar)
            st.session_state.user_data["aadhar_text"] = text
            st.success("✅ Aadhar text extracted.")
            with st.expander("View Extracted Aadhar Text"):
                st.text(text)
        except Exception as e:
            st.warning(f"Error extracting Aadhar text: {e}")

    # PAN Upload
    pan = st.file_uploader("Upload PAN Card (Image or PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])
    if pan:
        try:
            text = extract_text_from_file(pan)
            st.session_state.user_data["pan_text"] = text
            st.success("✅ PAN card text extracted.")
            with st.expander("View Extracted PAN Text"):
                st.text(text)
        except Exception as e:
            st.warning(f"Error extracting PAN card text: {e}")

    # Salary Slip Upload
    salary = st.file_uploader("Upload Salary Slip (Image or PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])
    if salary:
        try:
            text = extract_text_from_file(salary)
            st.session_state.user_data["salary_text"] = text
            st.success("✅ Salary slip text extracted.")
            with st.expander("View Extracted Salary Slip Text"):
                st.text(text)
        except Exception as e:
            st.warning(f"Error extracting salary slip text: {e}")

    if st.button("⬅ Previous", key="back2"):
        st.session_state.current_page = 1
    if st.button("Next ➡", key="to_final"):
        st.session_state.current_page = 3

# Final Decision Page
elif page == "Final Decision":
    st.subheader("Final Decision")
    try:
        input_df = pd.DataFrame([st.session_state.user_data])
        input_df = pd.get_dummies(input_df, columns=["gender", "marital_status", "employee_status", "residence_type", "loan_purpose", "loan_type"], drop_first=True)
        for col in model.feature_names_in_:
            if col not in input_df.columns:
                input_df[col] = 0
        input_df = input_df[model.feature_names_in_]

        pred = model.predict(input_df)[0]
        proba = model.predict_proba(input_df)[0][1]

        extracted_text = st.session_state.user_data.get("aadhar_text", "").lower().replace(" ", "")
        applicant_name = st.session_state.user_data.get("name", "").lower().replace(" ", "")

        if applicant_name not in extracted_text:
            st.error("❌ Applicant name not found in uploaded Aadhar document.")
            st.stop()

        if st.button("Submit Application"):
            if pred == 1:
                approval_id = "LN-" + uuid.uuid4().hex[:8].upper()
                st.session_state.user_data["approval_id"] = approval_id
                st.success("Loan Approved ✅")
                st.markdown(f"### 🔑 Approval ID: `{approval_id}`")

                send_decision_email(
                    st.session_state.user_data.get("email", ""),
                    st.session_state.user_data.get("name", ""),
                    decision="approved",
                    details={"approval_id": approval_id}
                )
            else:
                st.error("Loan Rejected ❌")
                st.markdown("#### Tips to Improve Approval Chances")
                st.markdown("""
                - Improve your CIBIL score above 700.
                - Keep loan amount relative to your income lower.
                - Close or reduce other active loans.
                - Ensure consistent employment or income proof.
                """)
                send_decision_email(
                    st.session_state.user_data.get("email", ""),
                    st.session_state.user_data.get("name", ""),
                    decision="rejected",
                    details={"reason": "CIBIL score too low or high income-to-loan ratio."}
                )

    except Exception as e:
        st.error(f"Prediction error: {e}")

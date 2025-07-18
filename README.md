## AI Credit Underwriting System
This Streamlit-based web application simulates an AI-powered Credit Underwriting System for evaluating loan applications. It allows users to input personal and financial details, upload documents for OCR processing, and receive instant loan approval decisions using rule-based predictions.

## Features
🔹 Multi-Step Loan Application Process
Personal Information: Collects basic applicant data like name, email, income, etc.
Loan Details: Captures CIBIL score, loan amount, interest, employment details.
Document Uploads: Supports PDF/image uploads (Aadhar, PAN, Salary Slip) and extracts data using OCR.
Final Decision: Uses custom underwriting logic to approve/reject loans with simulated email feedback.

## Embedded Chatbot
A sidebar chatbot that answers queries about:
Loan types
EMI calculations
Credit scores
Financial advice

## EMI Calculator
Calculates monthly installments based on user inputs (loan amount, interest rate, tenure).

## OCR with Tesseract & Poppler
Extracts text from uploaded documents (PDFs/images).

Uses pytesseract and pdf2image for seamless text extraction.

## Prediction Logic
A dummy credit scoring model is used, which approves loans based on:
CIBIL Score ≥ 700
Loan-to-income ratio < 70%
This can easily be replaced with a real ML model for production use.

## Installation
git clone https://github.com/your-username/ai-credit-underwriting.git
cd ai-credit-underwriting
pip install -r requirements.txt
🖥 Run the App
streamlit run app.py
##  Requirements
Python 3.8+
Streamlit
PyTesseract
Poppler (for PDF OCR)
Pillow
pandas
uuid
pdf2image

## Simulated Email System
For each loan decision, a simulated email is displayed using Streamlit's st.info() for demonstration purposes.

## Future Enhancements
Integrate real ML model for credit risk prediction

Add user authentication

Use Twilio/SendGrid for real SMS/Email delivery

Save user data to a database (e.g., PostgreSQL or Firebase)

Admin dashboard for loan officer reviews

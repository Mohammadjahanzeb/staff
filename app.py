import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt

st.set_page_config(page_title="Staff Salary App", layout="wide")

# Custom UI Styling
st.markdown("""
    <style>
        .stApp { background-color: #f0fff0; }
        .css-1d391kg { background-color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# File to store data
DATA_FILE = "salary_records.csv"

# Load or initialize data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "Name", "PRN", "Designation", "Seniority Date", "Year",
        "Base Pay", "Gross Pay", "Total Deductions", "Net Salary"
    ])

# Sidebar - Staff Info
st.sidebar.header("📋 Staff Information")
name = st.sidebar.text_input("Name")
prn = st.sidebar.text_input("PRN")
designation = st.sidebar.text_input("Designation")
seniority = st.sidebar.date_input("Seniority Date")

# Base Pay & Increase
base = st.sidebar.number_input("Base Pay", value=0)
adjustment = st.sidebar.number_input("Increase/Decrease (%)", value=0)
base_adj = base * (1 + adjustment / 100)

# Other Inputs
transport = st.sidebar.number_input("Transportation Allowance", value=10010)
shift = st.sidebar.number_input("Shift Allowance", value=0)
entertainment = st.sidebar.number_input("Entertainment Allowance", value=0)
laundry = st.sidebar.number_input("Laundry Allowance", value=0)
sales = st.sidebar.number_input("Sales Allowance", value=0)
technical = st.sidebar.number_input("Technical Allowance", value=0)
special = st.sidebar.number_input("Special Allowance", value=0)
cola_percent = st.sidebar.number_input("COLA (%)", value=0.0)
has_13 = st.sidebar.checkbox("Include 13th Salary?")
income_tax = st.sidebar.number_input("Income Tax", value=0)
misc = st.sidebar.number_input("Misc Deduction", value=0)
illness = st.sidebar.number_input("Critical Illness", value=0)
cpi = st.sidebar.number_input("CPI % for future calc", value=10.0)
year = st.sidebar.selectbox("Select Year", [2025, 2026, 2027])

# Salary Logic
def calculate(base):
    housing = base * 0.45
    utility = base * 0.10
    cola = base * (cola_percent / 100)
    thirteenth = base if has_13 else 0
    pf = base * 0.10
    union = base * 0.01

    gross = sum([
        base, housing, utility, transport, shift, entertainment, laundry,
        sales, technical, special, cola, thirteenth
    ])
    deductions = pf + union + income_tax + misc + illness
    net = gross - deductions
    return round(gross), round(deductions), round(net)

gross, deduction, net = calculate(base_adj)

# Submit
if st.sidebar.button("💾 Save Record"):
    new_row = pd.DataFrame([{
        "Name": name, "PRN": prn, "Designation": designation,
        "Seniority Date": seniority, "Year": year,
        "Base Pay": base_adj, "Gross Pay": gross,
        "Total Deductions": deduction, "Net Salary": net
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("Record saved successfully!")

# Select Staff
st.subheader("🔍 Staff Record Viewer")
staff_names = df["Name"].unique().tolist()
selected = st.selectbox("Select Staff", staff_names)

if selected:
    staff_data = df[df["Name"] == selected]
    st.write(f"Showing salary records for **{selected}**")
    st.dataframe(staff_data)

    # Plot Salary
    fig, ax = plt.subplots()
    ax.plot(staff_data["Year"], staff_data["Net Salary"], marker='o', color='green')
    ax.set_title(f"Net Salary Trend for {selected}")
    ax.set_ylabel("Net Salary (PKR)")
    st.pyplot(fig)

    # PDF Generator
    if st.button("📄 Download PDF Slip"):
        latest = staff_data.sort_values("Year", ascending=False).iloc[0]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Salary Slip - {latest['Year']}", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Name: {latest['Name']}", ln=True)
        pdf.cell(200, 10, txt=f"PRN: {latest['PRN']}", ln=True)
        pdf.cell(200, 10, txt=f"Designation: {latest['Designation']}", ln=True)
        pdf.cell(200, 10, txt=f"Seniority Date: {latest['Seniority Date']}", ln=True)
        pdf.ln(5)
        pdf.cell(200, 10, txt=f"Base Pay: {latest['Base Pay']:,}", ln=True)
        pdf.cell(200, 10, txt=f"Gross Pay: {latest['Gross Pay']:,}", ln=True)
        pdf.cell(200, 10, txt=f"Total Deductions: {latest['Total Deductions']:,}", ln=True)
        pdf.cell(200, 10, txt=f"Net Salary: {latest['Net Salary']:,}", ln=True)

        path = f"{selected}_SalarySlip_{latest['Year']}.pdf"
        pdf.output(path)
        with open(path, "rb") as f:
            st.download_button("⬇️ Download Salary Slip PDF", data=f, file_name=path)

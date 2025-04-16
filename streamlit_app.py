import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import os

st.set_page_config(page_title="Orno Finance Pro Dashboard", layout="wide")
st.markdown("""
    <style>
    .main {
        background-color: #f8fcfd;
    }
    h1 {
        text-align: center;
        color: #2c3e50;
    }
    </style>
""", unsafe_allow_html=True)

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        "Date", "Registered By", "Bank Balance", "Sales", "Purchase", "Expenses",
        "Salary", "Closing Stock", "Profit", "Target Revenue %", "Required Sales",
        "Max Expenses", "Max Salary Budget", "Profit Margin Needed", "Future Value"
    ])

st.image("https://img.icons8.com/ios-filled/50/4CAF50/combo-chart.png", width=50)
st.title("Orno Finance Pro Dashboard")

with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("🗓️ Date")
        registered_by = st.text_input("👤 Registered By")
        bank_balance = st.number_input("🏦 Current Bank Balance", step=0.01)
        sales = st.number_input("📈 Sales", step=0.01)
        purchase = st.number_input("📦 Purchase", step=0.01)
        closing_stock = st.number_input("📦 Closing Stock", step=0.01)
    with col2:
        expenses = st.number_input("💸 Expenses", step=0.01)
        salary = st.number_input("👔 Salary", step=0.01)
        target_percentage = st.slider("🎯 Revenue Target (%)", min_value=0, max_value=100, value=30)

    submitted = st.form_submit_button("➕ Add Entry")

    if submitted:
        profit = sales - purchase - expenses - salary
        target_revenue = (target_percentage / 100) * bank_balance

        required_sales = round(bank_balance / (target_percentage / 100), 2)
        max_expenses = round(sales * 0.25, 2)
        max_salary_budget = round(sales * 0.2, 2)
        profit_margin_needed = round((target_revenue - bank_balance), 2)
        future_value = bank_balance + profit + closing_stock

        new_row = {
            "Date": date.strftime("%Y-%m-%d"),
            "Registered By": registered_by,
            "Bank Balance": bank_balance,
            "Sales": sales,
            "Purchase": purchase,
            "Expenses": expenses,
            "Salary": salary,
            "Closing Stock": closing_stock,
            "Profit": profit,
            "Target Revenue %": target_percentage,
            "Required Sales": required_sales,
            "Max Expenses": max_expenses,
            "Max Salary Budget": max_salary_budget,
            "Profit Margin Needed": profit_margin_needed,
            "Future Value": future_value
        }
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ Entry added successfully!")

st.markdown("### 📊 Finance Summary Table")
st.dataframe(st.session_state.df, use_container_width=True)

def generate_pdf(data):
    chart_filename = "finance_chart.png"
    
    plt.figure(figsize=(8, 4))
    plt.plot(data["Date"], data["Sales"], label="Sales", marker='o')
    plt.plot(data["Date"], data["Expenses"], label="Expenses", marker='o')
    plt.plot(data["Date"], data["Profit"], label="Profit", marker='o')
    plt.xticks(rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Amount (BDT)")
    plt.title("Sales, Expenses & Profit")
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.savefig(chart_filename)
    plt.close()

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "Orno Finance Report", ln=True, align="C")
            self.set_font("Arial", "", 10)
            self.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
            self.ln(5)

        def table(self, df):
            self.set_font("Arial", "B", 10)
            for header in ["Date", "Sales", "Expenses", "Salary", "Profit", "Target Revenue %"]:
                self.cell(40, 10, header, 1, 0, "C")
            self.ln()
            self.set_font("Arial", "", 10)
            for _, row in df.iterrows():
                self.cell(40, 10, str(row["Date"]), 1)
                self.cell(40, 10, f"{row['Sales']:.2f}", 1)
                self.cell(40, 10, f"{row['Expenses']:.2f}", 1)
                self.cell(40, 10, f"{row['Salary']:.2f}", 1)
                self.cell(40, 10, f"{row['Profit']:.2f}", 1)
                self.cell(40, 10, f"{row['Target Revenue %']}%", 1)
                self.ln()

        def add_chart(self, path):
            self.image(path, x=25, w=160)
            self.ln(10)

    pdf = PDF()
    pdf.add_page()
    pdf.table(data)
    pdf.add_chart(chart_filename)
    output_name = f"Orno_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(output_name)
    os.remove(chart_filename)
    return output_name

col1, col2 = st.columns(2)
with col1:
    if st.button("📄 Export to PDF"):
        if not st.session_state.df.empty:
            output_pdf = generate_pdf(st.session_state.df)
            with open(output_pdf, "rb") as file:
                st.download_button(label="📥 Download PDF", data=file, file_name=output_pdf, mime="application/pdf")
        else:
            st.warning("⚠️ No data to export!")

with col2:
    if st.download_button("📥 Export to Excel", data=st.session_state.df.to_csv(index=False),
                          file_name="orno_finance_data.csv", mime="text/csv"):
        st.success("✅ Excel exported.")

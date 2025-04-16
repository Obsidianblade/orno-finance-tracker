import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import os

st.set_page_config(page_title="Orno Finance Pro Dashboard", layout="wide")

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        "Date", "Registered By", "Bank Balance", "Sales", "Purchase", "Expenses",
        "Salary", "Ad Spend", "Closing Stock", "Profit", "Target Revenue",
        "Required Sales", "Max Expenses", "Max Salary Budget",
        "Profit Margin Needed", "New Hires", "Expected Expense Increase",
        "Revenue Boost", "Adjusted Profit", "Net Balance", "Future Value"
    ])

st.title("📊 Orno Finance Pro Dashboard")

with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 Date")
        registered_by = st.text_input("👤 Registered By")
        bank_balance = st.number_input("🏦 Bank Balance (BDT)", step=0.01)
        sales = st.number_input("📈 Sales (BDT)", step=0.01)
        purchase = st.number_input("📦 Purchase (BDT)", step=0.01)
        closing_stock = st.number_input("📦 Closing Stock (BDT)", step=0.01)
    with col2:
        expenses = st.number_input("💸 Expenses (BDT)", step=0.01)
        salary = st.number_input("👔 Salary (BDT)", step=0.01)
        ad_spend = st.number_input("📣 Ad Spend (BDT)", step=0.01)
        target_revenue = st.number_input("🎯 Target Revenue (BDT)", step=0.01)
        new_hires = st.slider("👥 New Hires Suggested", 0, 10, 2)

    submitted = st.form_submit_button("➕ Add Entry")

    if submitted:
        profit = sales - purchase - expenses - salary - ad_spend
        required_sales = target_revenue
        max_expenses = sales * 0.35
        max_salary = sales * 0.20
        margin_needed = target_revenue - bank_balance
        expense_increase = new_hires * 4000
        revenue_boost = new_hires * 10000
        adjusted_profit = profit + revenue_boost - expense_increase
        net_balance = bank_balance + adjusted_profit
        future_value = net_balance + closing_stock

        new_row = {
            "Date": date.strftime("%Y-%m-%d"),
            "Registered By": registered_by,
            "Bank Balance": bank_balance,
            "Sales": sales,
            "Purchase": purchase,
            "Expenses": expenses,
            "Salary": salary,
            "Ad Spend": ad_spend,
            "Closing Stock": closing_stock,
            "Profit": profit,
            "Target Revenue": target_revenue,
            "Required Sales": required_sales,
            "Max Expenses": max_expenses,
            "Max Salary Budget": max_salary,
            "Profit Margin Needed": margin_needed,
            "New Hires": new_hires,
            "Expected Expense Increase": expense_increase,
            "Revenue Boost": revenue_boost,
            "Adjusted Profit": adjusted_profit,
            "Net Balance": net_balance,
            "Future Value": future_value
        }
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ Entry added successfully!")

st.markdown("### 📋 Financial Summary")
st.dataframe(st.session_state.df, use_container_width=True)

def generate_pdf(data):
    last = data.iloc[-1]

    chart_filename = "finance_chart.png"
    plt.figure(figsize=(6, 4))
    plt.bar(["Sales", "Expenses", "Profit"], [last['Sales'], last['Expenses'], last['Profit']])
    plt.title("Sales vs Expenses vs Profit")
    plt.tight_layout()
    plt.savefig(chart_filename)
    plt.close()

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 16)
            self.cell(0, 10, "Orno Finance Report", ln=True, align="C")
            self.set_font("Arial", "", 12)
            self.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
            self.ln(10)

        def body(self):
            self.set_font("Arial", "", 12)
            self.cell(0, 10, f"Date: {last['Date']}", ln=True)
            self.cell(0, 10, f"Sales: {last['Sales']:.2f} BDT", ln=True)
            self.cell(0, 10, f"Expenses: {last['Expenses']:.2f} BDT", ln=True)
            self.cell(0, 10, f"Salary: {last['Salary']:.2f} BDT", ln=True)
            self.cell(0, 10, f"Ad Spend: {last['Ad Spend']:.2f} BDT", ln=True)
            self.cell(0, 10, f"Profit: {last['Profit']:.2f} BDT", ln=True)
            self.cell(0, 10, f"Current Bank Balance: {last['Bank Balance']:.2f} BDT", ln=True)

            self.ln(5)
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "Recommendations", ln=True)
            self.set_font("Arial", "", 12)
            self.cell(0, 10, f"Target Revenue: {last['Target Revenue']:.2f} BDT", ln=True)
            self.cell(0, 10, f"Required Sales: {last['Required Sales']:.2f} BDT", ln=True)
            self.cell(0, 10, f"Max Expenses Allowed: {last['Max Expenses']:.2f} BDT", ln=True)
            self.cell(0, 10, f"Max Salary Budget: {last['Max Salary Budget']:.2f} BDT", ln=True)
            self.cell(0, 10, f"Minimum Profit Margin Needed: {last['Profit Margin Needed']:.2f} BDT", ln=True)
            self.cell(0, 10, f"New Hires Suggested: {last['New Hires']}", ln=True)
            self.cell(0, 10, f"Expected Expense Increase: {last['Expected Expense Increase']:.2f} BDT", ln=True)
            self.cell(0, 10, f"Revenue Boost from Hires: {last['Revenue Boost']:.2f} BDT", ln=True)

            self.ln(5)
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "Financial Impact", ln=True)
            self.set_font("Arial", "", 12)
            self.cell(0, 10, f"Adjusted Profit: {last['Adjusted Profit']:.2f} BDT", ln=True)
            self.cell(0, 10, f"Net Bank Balance: {last['Net Balance']:.2f} BDT", ln=True)
            self.cell(0, 10, f"Future Value: {last['Future Value']:.2f} BDT", ln=True)

        def add_chart(self):
            self.image(chart_filename, x=25, w=160)

    pdf = PDF()
    pdf.add_page()
    pdf.body()
    pdf.add_chart()
    output_name = f"Orno_Finance_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(output_name, "F")
    os.remove(chart_filename)
    return output_name

if st.button("📄 Export PDF Report"):
    if not st.session_state.df.empty:
        output_pdf = generate_pdf(st.session_state.df)
        with open(output_pdf, "rb") as file:
            st.download_button(label="📥 Download PDF", data=file, file_name=output_pdf, mime="application/pdf")
    else:
        st.warning("⚠️ Please enter data to export.")

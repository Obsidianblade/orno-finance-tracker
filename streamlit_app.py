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
            fields = [
                ("Date", "Date"),
                ("Sales", "Sales (BDT)"),
                ("Expenses", "Expenses (BDT)"),
                ("Salary", "Salary (BDT)"),
                ("Ad Spend", "Ad Spend (BDT)"),
                ("Profit", "Profit (BDT)"),
                ("Bank Balance", "Bank Balance (BDT)"),
                ("Target Revenue", "Target Revenue (BDT)"),
                ("Required Sales", "Required Sales (BDT)"),
                ("Max Expenses", "Max Expenses (BDT)"),
                ("Max Salary Budget", "Max Salary (BDT)"),
                ("Profit Margin Needed", "Min Profit Needed (BDT)"),
                ("New Hires", "New Hires Suggested"),
                ("Expected Expense Increase", "Expected Expense (BDT)"),
                ("Revenue Boost", "Revenue Boost (BDT)"),
                ("Adjusted Profit", "Adjusted Profit (BDT)"),
                ("Net Balance", "Net Balance (BDT)"),
                ("Future Value", "Future Value (BDT)")
            ]
            for key, label in fields:
                if key in last:
                    self.cell(0, 10, f"{label}: {last[key]:.2f}" if isinstance(last[key], (int, float)) else f"{label}: {last[key]}", ln=True)

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

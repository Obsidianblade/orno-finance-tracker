import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import os

st.set_page_config(page_title="Orno Finance Tracker", layout="wide")

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        "Date", "Registered By", "Bank Balance", "Sales", "Purchase", "Expenses",
        "Salary", "Ad Spend", "Closing Stock", "Profit", "Target Revenue",
        "Turnover %", "Sales Needed", "Expense Reduction Needed", "Future Value"
    ])

st.title("📊 Orno Finance Tracker")

with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 Date")
        registered_by = st.text_input("👤 Registered By")
        bank_balance = st.number_input("🏦 Bank Balance (BDT)", step=0.01)
        sales = st.number_input("📈 Sales (BDT)", step=0.01)
        purchase = st.number_input("🛒 Purchase (BDT)", step=0.01)
        closing_stock = st.number_input("📦 Closing Stock (BDT)", step=0.01)
    with col2:
        expenses = st.number_input("💸 Expenses (BDT)", step=0.01)
        salary = st.number_input("👔 Salary (BDT)", step=0.01)
        ad_spend = st.number_input("📣 Ad Spend (BDT)", step=0.01)
        turnover_goal = st.slider("🎯 Turnover Goal (%)", 0, 100, 30)
        target_revenue = st.number_input("🎯 Target Revenue (BDT)", step=0.01)

    submitted = st.form_submit_button("➕ Add Entry")

    if submitted:
        profit = sales - purchase - expenses - salary - ad_spend
        future_value = bank_balance + profit + closing_stock
        sales_needed = target_revenue
        expense_reduction = max(0, (sales + closing_stock) - sales_needed)

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
            "Turnover %": turnover_goal,
            "Sales Needed": sales_needed,
            "Expense Reduction Needed": expense_reduction,
            "Future Value": future_value
        }
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ Entry added successfully!")

st.markdown("### 📋 Finance Table")
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
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "Orno Finance Report", ln=True, align="C")
            self.set_font("Arial", "", 10)
            self.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
            self.ln(5)

        def overview(self):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "Financial Overview", ln=True)
            self.set_font("Arial", "", 11)
            self.cell(0, 8, f"Date: {last['Date']}", ln=True)
            self.cell(0, 8, f"Sales: {last['Sales']:.2f} BDT", ln=True)
            self.cell(0, 8, f"Expenses: {last['Expenses']:.2f} BDT", ln=True)
            self.cell(0, 8, f"Salary: {last['Salary']:.2f} BDT", ln=True)
            self.cell(0, 8, f"Profit: {last['Profit']:.2f} BDT", ln=True)
            self.cell(0, 8, f"Bank Balance: {last['Bank Balance']:.2f} BDT", ln=True)
            self.ln(4)

        def target_summary(self):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "Target Summary", ln=True)
            self.set_font("Arial", "", 11)
            self.cell(0, 8, f"Target Revenue: {last['Target Revenue']:.2f} BDT", ln=True)
            self.cell(0, 8, f"Turnover Goal (%): {last['Turnover %']}%", ln=True)
            self.cell(0, 8, f"Ad Spend: {last['Ad Spend']:.2f} BDT", ln=True)
            self.ln(4)

        def forecast(self):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "Financial Forecast", ln=True)
            self.set_font("Arial", "", 11)
            self.cell(0, 8, f"Sales Needed: {last['Sales Needed']:.2f} BDT", ln=True)
            self.cell(0, 8, f"Expense Reduction Needed: {last['Expense Reduction Needed']:.2f} BDT", ln=True)
            self.cell(0, 8, f"Future Value: {last['Future Value']:.2f} BDT", ln=True)
            self.ln(5)

        def add_chart(self):
            self.image(chart_filename, x=25, w=160)

    pdf = PDF()
    pdf.add_page()
    pdf.overview()
    pdf.target_summary()
    pdf.forecast()
    pdf.add_chart()

    output_name = f"Orno_Finance_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(output_name, 'F')
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

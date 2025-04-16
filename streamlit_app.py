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
        "Salary", "Closing Stock", "Profit", "Target Net Profit", "Sales Needed",
        "Expense Reduction Needed", "Future Value"
    ])

st.title("📊 Orno Finance Pro Dashboard")
st.markdown("---")

with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("🗓️ Date")
        registered_by = st.text_input("👤 Registered By")
        bank_balance = st.number_input("🏦 Current Bank Balance", step=0.01)
        sales = st.number_input("📈 Sales", step=0.01)
        purchase = st.number_input("🛒 Purchase", step=0.01)
        closing_stock = st.number_input("📦 Closing Stock", step=0.01)
    with col2:
        expenses = st.number_input("💸 Expenses", step=0.01)
        salary = st.number_input("👔 Salary", step=0.01)
        target_net_profit = st.number_input("🎯 Target Net Profit (BDT)", step=0.01)

    submitted = st.form_submit_button("➕ Add Entry")

    if submitted:
        profit = sales - purchase - expenses - salary
        sales_needed = target_net_profit + purchase + expenses + salary
        expense_reduction = max(0, (sales + closing_stock) - sales_needed)
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
            "Target Net Profit": target_net_profit,
            "Sales Needed": sales_needed,
            "Expense Reduction Needed": expense_reduction,
            "Future Value": future_value
        }

        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ Entry added successfully!")

st.markdown("### 📋 Finance Table")
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

        def body(self, df):
            last = df.iloc[-1] if not df.empty else {}
            self.set_font("Arial", "", 10)
            self.cell(0, 10, f"👤 Registered By: {last.get('Registered By', '-')}", ln=True)
            self.cell(0, 10, f"💰 Sales Needed for Target: {last.get('Sales Needed', 0):.2f} BDT", ln=True)
            self.cell(0, 10, f"📉 Expense Reduction Suggested: {last.get('Expense Reduction Needed', 0):.2f} BDT", ln=True)
            self.cell(0, 10, f"🎯 Target Net Profit: {last.get('Target Net Profit', 0):.2f} BDT", ln=True)
            self.cell(0, 10, f"📦 Future Value: {last.get('Future Value', 0):.2f} BDT", ln=True)
            self.ln(10)

        def table(self, df):
            self.set_font("Arial", "B", 10)
            for header in ["Date", "Sales", "Expenses", "Salary", "Profit", "Target Net Profit"]:
                self.cell(40, 10, header, 1, 0, "C")
            self.ln()
            self.set_font("Arial", "", 10)
            for _, row in df.iterrows():
                self.cell(40, 10, str(row.get("Date", "")), 1)
                self.cell(40, 10, f"{row.get('Sales', 0):.2f}", 1)
                self.cell(40, 10, f"{row.get('Expenses', 0):.2f}", 1)
                self.cell(40, 10, f"{row.get('Salary', 0):.2f}", 1)
                self.cell(40, 10, f"{row.get('Profit', 0):.2f}", 1)
                self.cell(40, 10, f"{row.get('Target Net Profit', 0):.2f}", 1)
                self.ln()

        def add_chart(self, path):
            self.image(path, x=25, w=160)
            self.ln(10)

    pdf = PDF()
    pdf.add_page()
    pdf.body(data)
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

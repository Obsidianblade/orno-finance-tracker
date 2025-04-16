import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import os

st.set_page_config(page_title="Orno Finance Tracker", layout="wide")

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        "Date", "Current Balance", "Purchase", "Sales", "Sell Return", "Expenses",
        "Salary", "Profit", "Closing Stock", "Ad Spend", "Target Revenue",
        "Possible Future Value", "Net Balance"
    ])

st.title("📊 Orno Finance Tracker")

with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date")
        current_balance = st.number_input("Current Bank Balance", step=0.01)
        purchase = st.number_input("Purchase", step=0.01)
        sell_return = st.number_input("Sell Return", step=0.01)
        closing_stock = st.number_input("Closing Stock", step=0.01)
        ad_spend = st.number_input("Advertisement Budget", step=0.01)
    with col2:
        sales = st.number_input("Sales", step=0.01)
        expenses = st.number_input("Expenses", step=0.01)
        salary = st.number_input("Salary", step=0.01)
        target_revenue = st.number_input("💰 Turnover Goal (BDT)", step=0.01)

    submitted = st.form_submit_button("➕ Add Entry")

    if submitted:
        profit = sales - (purchase + expenses + salary + ad_spend)
        net_balance = current_balance + profit
        possible_future = net_balance + closing_stock

        new_row = {
            "Date": date.strftime("%Y-%m-%d"),
            "Current Balance": current_balance,
            "Purchase": purchase,
            "Sales": sales,
            "Sell Return": sell_return,
            "Expenses": expenses,
            "Salary": salary,
            "Profit": profit,
            "Closing Stock": closing_stock,
            "Ad Spend": ad_spend,
            "Target Revenue": target_revenue,
            "Possible Future Value": possible_future,
            "Net Balance": net_balance
        }

        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Entry added successfully!")

st.markdown("### 📈 Finance Table")
st.dataframe(st.session_state.df, use_container_width=True)

def generate_pdf(data):
    latest = data.iloc[-1]
    chart_filename = "finance_chart.png"

    # Bar Chart
    plt.figure(figsize=(8, 4))
    plt.bar(["Sales", "Expenses", "Salary", "Profit"], [
        latest["Sales"], latest["Expenses"], latest["Salary"], latest["Profit"]
    ])
    plt.title("Sales, Expenses, Salary, and Profit")
    plt.ylabel("Amount (BDT)")
    plt.tight_layout()
    plt.savefig(chart_filename)
    plt.close()

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 16)
            self.cell(0, 10, "Orno Finance Report", ln=True, align="C")
            self.set_font("Arial", "", 10)
            self.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
            self.ln(5)

        def financial_table(self, row):
            self.set_font("Arial", "B", 11)
            self.cell(30, 10, "Date", 1)
            self.cell(30, 10, "Sales", 1)
            self.cell(30, 10, "Expenses", 1)
            self.cell(30, 10, "Salary", 1)
            self.cell(30, 10, "Profit", 1)
            self.cell(30, 10, "Target Revenue", 1)
            self.ln()
            self.set_font("Arial", "", 10)
            self.cell(30, 10, str(row["Date"]), 1)
            self.cell(30, 10, f"{row['Sales']:.2f}", 1)
            self.cell(30, 10, f"{row['Expenses']:.2f}", 1)
            self.cell(30, 10, f"{row['Salary']:.2f}", 1)
            self.cell(30, 10, f"{row['Profit']:.2f}", 1)
            self.cell(30, 10, f"{row['Target Revenue']:.2f}", 1)
            self.ln(15)

        def recommendations(self, row):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "📌 Business Suggestions", ln=True)

            req_sales = row["Target Revenue"]
            max_salary = req_sales * 0.15
            max_expense = req_sales * 0.25
            min_profit_margin = req_sales * 0.25
            new_hires = int(row["Salary"] / 10000)
            rev_boost = new_hires * 5000
            exp_increase = new_hires * 3000

            self.set_font("Arial", "", 10)
            self.multi_cell(0, 8,
                f"• Required Sales to hit target: {req_sales:.2f} BDT\n"
                f"• Max Expense Allowed: {max_expense:.2f} BDT\n"
                f"• Max Salary Budget: {max_salary:.2f} BDT\n"
                f"• Minimum Profit Margin Needed: {min_profit_margin:.2f} BDT\n"
                f"• Number of New Hires: {new_hires}\n"
                f"• Expected Expense Increase: {exp_increase:.2f} BDT\n"
                f"• Revenue Boost from Hires: {rev_boost:.2f} BDT\n"
                f"\n💼 Projected Net Balance: {row['Net Balance']:.2f} BDT"
                f"\n📦 Future Value (with stock): {row['Possible Future Value']:.2f} BDT"
            )

        def add_chart(self, path):
            self.image(path, x=25, w=160)
            self.ln(10)

    pdf = PDF()
    pdf.add_page()
    pdf.financial_table(latest)
    pdf.recommendations(latest)
    pdf.add_chart(chart_filename)
    output_name = f"Orno_Finance_Report_Pro_Clean.pdf"
    pdf.output(output_name)
    os.remove(chart_filename)
    return output_name

col1, col2 = st.columns(2)
with col1:
    if st.button("📄 Generate Professional PDF"):
        if not st.session_state.df.empty:
            output_pdf = generate_pdf(st.session_state.df)
            with open(output_pdf, "rb") as file:
                st.download_button(label="📥 Download Report", data=file,
                                   file_name=output_pdf, mime="application/pdf")
        else:
            st.warning("No data to export!")

with col2:
    if st.download_button("📥 Export as CSV", data=st.session_state.df.to_csv(index=False),
                          file_name="orno_finance_data.csv", mime="text/csv"):
        st.success("✅ CSV exported.")


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import os

st.set_page_config(page_title="Orno Finance Tracker Pro", layout="wide")

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        "Date", "Current Bank Balance", "Purchase", "Sales", "Sell Return", "Expenses",
        "Salary", "Profit", "Closing Stock", "Current Balance", "Turnover",
        "Target Liquidity (%)", "Ad Budget (20%)",
        "Possible Future Value", "Target Future Value", "Target Revenue"
    ])

st.title("📊 Orno Finance Tracker Pro")

with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date")
        current_bank_balance = st.number_input("Current Bank Balance", step=0.01)
        purchase = st.number_input("Purchase", step=0.01)
        sell_return = st.number_input("Sell Return", step=0.01)
        closing_stock = st.number_input("Closing Stock", step=0.01)
    with col2:
        sales = st.number_input("Sales", step=0.01)
        expenses = st.number_input("Expenses", step=0.01)
        salary = st.number_input("Salary", step=0.01)

    target_percent = st.slider("Liquidity Target % of Turnover", 10, 100, 70)
    target_revenue = st.number_input("Your Target Revenue (Optional)", step=0.01)

    submitted = st.form_submit_button("➕ Add Entry")

    if submitted:
        profit = sales - purchase - expenses - salary
        current_balance = current_bank_balance + profit - sell_return
        turnover = sales + sell_return
        liquidity = turnover * (target_percent / 100)
        ad_budget = turnover * 0.20
        possible_future = current_balance + closing_stock
        target_future = liquidity + ad_budget

        new_row = {
            "Date": date.strftime("%Y-%m-%d"),
            "Current Bank Balance": current_bank_balance,
            "Purchase": purchase,
            "Sales": sales,
            "Sell Return": sell_return,
            "Expenses": expenses,
            "Salary": salary,
            "Profit": profit,
            "Closing Stock": closing_stock,
            "Current Balance": current_balance,
            "Turnover": turnover,
            "Target Liquidity (%)": liquidity,
            "Ad Budget (20%)": ad_budget,
            "Possible Future Value": possible_future,
            "Target Future Value": target_future,
            "Target Revenue": target_revenue
        }

        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Entry added successfully!")

st.markdown("### 📈 Finance Table")
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
            headers = ["Date", "Sales", "Expenses", "Salary", "Profit", "Target Revenue"]
            for header in headers:
                self.cell(32, 10, header, 1, 0, "C")
            self.ln()
            self.set_font("Arial", "", 10)
            for _, row in df.iterrows():
                self.cell(32, 10, str(row["Date"]), 1)
                self.cell(32, 10, f"{row['Sales']:.2f}", 1)
                self.cell(32, 10, f"{row['Expenses']:.2f}", 1)
                self.cell(32, 10, f"{row['Salary']:.2f}", 1)
                self.cell(32, 10, f"{row['Profit']:.2f}", 1)
                self.cell(32, 10, f"{row['Target Revenue']:.2f}", 1)
                self.ln()

        def add_chart(self, path):
            self.image(path, x=25, w=160)
            self.ln(10)

    pdf = PDF()
    pdf.add_page()
    pdf.table(data)
    pdf.add_chart(chart_filename)
    output_name = f"Orno_Finance_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
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
            st.warning("No data to export!")

with col2:
    if st.download_button("📥 Export to Excel", data=st.session_state.df.to_csv(index=False),
                          file_name="orno_finance_data.csv", mime="text/csv"):
        st.success("Excel exported.")

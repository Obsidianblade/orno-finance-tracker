def generate_pdf(data):
    chart_filename = "finance_chart.png"

    # Generate chart
    plt.figure(figsize=(8, 4))
    plt.plot(data["Date"], data["Sales"], label="Sales", marker='o')
    plt.plot(data["Date"], data["Expenses"], label="Expenses", marker='o')
    plt.plot(data["Date"], data["Profit"], label="Profit", marker='o')
    plt.xticks(rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Amount (BDT)")
    plt.title("📊 Sales, Expenses & Profit")
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.savefig(chart_filename)
    plt.close()

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 16)
            self.cell(0, 10, "📄 Orno Finance Report", ln=True, align="C")
            self.set_font("Arial", "", 10)
            self.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
            self.ln(5)

        def financial_summary(self, row):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, f"📌 Summary for {row['Date']}", ln=True)
            self.set_font("Arial", "", 11)
            self.multi_cell(0, 10, f"""
👤 Registered By: {row['Registered By']}
🏦 Bank Balance: {row['Bank Balance']} BDT
📈 Sales: {row['Sales']} BDT
📦 Purchase: {row['Purchase']} BDT
💸 Expenses: {row['Expenses']} BDT
👔 Salary: {row['Salary']} BDT
📦 Closing Stock: {row['Closing Stock']} BDT
💰 Profit: {row['Profit']} BDT
🎯 Revenue Target: {row['Target Revenue %']}%
📊 Required Sales: {row['Required Sales']} BDT
🧮 Max Expenses Allowed: {row['Max Expenses']} BDT
💼 Max Salary Budget: {row['Max Salary Budget']} BDT
📉 Minimum Profit Needed: {row['Profit Margin Needed']} BDT
📈 Future Value Projection: {row['Future Value']} BDT
""")

        def add_chart(self, path):
            self.image(path, x=25, w=160)
            self.ln(10)

    pdf = PDF()
    pdf.add_page()

    # Latest entry summary
    latest = data.iloc[-1]
    pdf.financial_summary(latest)
    pdf.ln(5)

    # Add chart
    pdf.add_chart(chart_filename)

    output_name = f"Orno_Finance_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(output_name)
    os.remove(chart_filename)
    return output_name

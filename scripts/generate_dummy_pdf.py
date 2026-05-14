from fpdf import FPDF
import os

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=15)
pdf.cell(200, 10, txt="Agriculture Schemes Document", ln=1, align='C')

pdf.set_font("Arial", size=12)
pdf.multi_cell(0, 10, txt="1. Rice Subsidy Scheme: Farmers growing rice in Karnataka are eligible for a 50% subsidy on fertilizers and a direct cash transfer of Rs. 5000 per acre under the Krishi Vikas Yojana.")
pdf.multi_cell(0, 10, txt="2. Akki Bele Yojane: This scheme supports rice farmers in Mandya and Mysore regions with free seeds and pesticide discounts up to 30%. Note: The actual Kannada text is transliterated here due to font limitations in basic fpdf, but the AI will process and return Kannada.")
pdf.multi_cell(0, 10, txt="3. Tractor Loan Scheme: A low-interest loan of 4% per annum is available for purchasing new tractors for farmers with more than 5 acres of land.")

output_dir = os.path.join("data", "govt_schemes")
os.makedirs(output_dir, exist_ok=True)
pdf.output(os.path.join(output_dir, "dummy_schemes.pdf"))
print("Generated dummy PDF.")

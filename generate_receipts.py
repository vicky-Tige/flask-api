from fpdf import FPDF
from cloudinary_service import upload_pdf
def create_pdf(payment_data,transaction_code):
    pdf=FPDF()
    pdf.add_page()
    pdf.set_font('Arial',size=12)
    pdf.multi_cell(200,10,txt=payment_data,align='C')
    pdf.output(f'receipts/{transaction_code}.pdf')
# create_pdf("Transaction Code : UFGTG854944, Amount :1, Date : 15/10/2026",'UFGTG854944')
    print("This is create pdf----")
    # uploading pdf to cloudinary 
    upload_pdf(transaction_code)



import fitz
import pandas as pd
import pdfquery

pdf_path = 'sample_pdf.pdf'

doc = fitz.open(pdf_path)

paragraphs = []
for page in doc:
    blocks = page.get_text('blocks')
    paragraph = ' '.join([bl[-3] for bl in blocks])
    paragraphs.append(paragraph)

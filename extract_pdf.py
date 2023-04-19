import pandas as pd
import pdfquery
import fitz

pdf_path = '/Users/sebastian/Desktop/TODAI/Yoshida-sensei/References/kajikawa2009.pdf'

import fitz
import pandas as pd 

doc = fitz.open(pdf_path)

paragraphs = []
for page in doc:
    blocks = page.get_text('blocks')
    paragraph = ' '.join([bl[-3] for bl in blocks])
    paragraphs.append(paragraph)
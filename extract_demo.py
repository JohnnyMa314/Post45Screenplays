import pdfminer
from pdfminer.high_level import extract_text_to_fp
from pdfminer.high_level import extract_text
from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams


source = 'data/2005/JUNO.pdf'

with open(source, 'rb') as fin, open('out.html', 'wb') as fout:
    extract_text_to_fp(fin, fout, laparams=LAParams(),
                        output_type='html', code=None)

with open('out.txt', 'w') as f:
    f.write(extract_text(source))


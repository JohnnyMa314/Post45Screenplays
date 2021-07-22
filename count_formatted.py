import pdfminer
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.pdfdocument import PDFEncryptionError
from collections import Counter
import os, re, json

valid_check = {}

def format_percent(pages):
    '''
    Given a pdfminer pages object, returns a boolean indicating if it is well-formatted.
    '''
    coords = []
    for layout in pages:
        for element in layout:
            if isinstance(element, pdfminer.layout.LTTextContainer):
                for line in element:
                    if isinstance(line, pdfminer.layout.LTTextLine):
                        coords.append(line.x0)

    indent_count = Counter(coords)
    top3_valid_check = [v for (k, v) in indent_count.most_common(3)]
    all_valid_check = [v for (k, v) in indent_count.items()]

    try:
        proportion = sum(top3_valid_check) / sum(all_valid_check)
        print(proportion)
        return proportion
    except ZeroDivisionError:
        return 0

#test = 'data/2014/Boston Strangler.pdf'
#pages = list(extract_pages(test))

#test = 'data/2005/ARMORED.pdf'
#full_text = extract_text(test)

for folder in os.scandir('data'):

    valid_check[folder.name] = {}

    for file in os.scandir(folder.path):

        if 'black list' in file.name.lower() or not file.name.endswith('.pdf'):
            continue
        
        try:
            full_text = extract_text(file.path)
        except PDFEncryptionError:
            full_text = ''
        if not re.search(r'\S+', full_text):

            valid_check[folder.name][file.name] = None
        
        else:

            valid_check[folder.name][file.name] = format_percent(extract_pages(file.path))


        print(f'Finished {file.name}')
    print(f'Finished {folder.name}')

with open('format_valid_check.json', 'w') as f:
    json.dump(valid_check, f, indent=4)
        


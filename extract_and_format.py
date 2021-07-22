import pdfminer
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer

from collections import Counter

import re, os


'''
Definition of bbox coordinates, for reference:

x0: the distance from the left of the page to the left edge of the box.
y0: the distance from the bottom of the page to the lower edge of the box.
x1: the distance from the left of the page to the right edge of the box.
y1: the distance from the bottom of the page to the upper edge of the box.

Clean script margins (in characters):
Scene description: 11-71
Character name: starts at 33
Dialogue: 24-54
Dialogue description: 28-44

'''


def line_indent_count(pages):
    '''
    Given a pdfminer pages object, returns line counts of unique indentation levels 
    across the entire document.
    '''
    coords = []
    for layout in pages:
        for element in layout:
            if isinstance(element, LTTextContainer):
                for line in element:
                    if hasattr(line, 'x0'):
                        coords.append(round(line.x0))

    indent_count = Counter(coords)
    return indent_count



def build_format(indent_count):
    '''
    Given line-indent counts, returns a dict that assigns a number of spaces to each
    line x-coordinate that appears in the document.
    Hardcodes the three main screenplay roles: scene description, dialogue, character name.
    Other spacing is inferred based on the location of the line in the page.
    '''

    top3 = sorted([k for (k, v) in indent_count.most_common(3)])
    xcoords = sorted([k for (k, v) in indent_count.items()])

    script_format = {
        top3[0] : ' ' * 11, # scene description
        top3[1] : ' ' * 24, # dialogue
        top3[2] : ' ' * 33, # character name
    }
    right_max = xcoords[-1]
    script_format[right_max] = ' ' * 70
    for xcoord in xcoords:
        if xcoord not in script_format:
            num_spaces = round(70 * (xcoord / right_max))
            script_format[xcoord] = ' ' * num_spaces

    return script_format



def standardize_document(pages, script_format):
    '''
    Given a pdfminer pages object and a formatting dict, converts line x-coords
    to appropriate spacing.
    '''
    output = ''
    for layout in pages:
        prev_y0 = None
        for element in layout:
            if isinstance(element, LTTextContainer):
                for line in element:
        
                    if hasattr(line, 'x0'):
                        spaces = script_format[round(line.x0)]
                        text = line.get_text()

                        # skip lines composed of only scene or page numbers
                        if re.search(r'^[\d\. \n\*]+$', text):
                            continue

                        # we use line heights to infer if we should add a blank space
                        height = line.y1 - line.y0
                        if prev_y0:
                            if (prev_y0 - line.y0) > (1.5 * height):
                                output += '\n'

                        output += spaces + text
                        prev_y0 = line.y0

    return output

if __name__ == '__main__':

    # source = 'data/2005/JUNO.pdf'
    # params = pdfminer.layout.LAParams(boxes_flow=None) # ensures order is based on vertical position alone
    # pages = list(extract_pages(source, laparams=params))
    # indent_count = line_indent_count(pages)
    # script_format = build_format(indent_count)
    # output = standardize_document(pages, script_format)
    # print(output)
    # print(pdfminer.high_level.extract_text(source))

    params = pdfminer.layout.LAParams(boxes_flow=None)
    for folder in os.scandir('data'):

        if os.path.isdir(folder.path):

            for file in os.scandir(folder.path):

                if file.name.endswith('.pdf'):

                    # first check if it has any text at all
                    try:
                        plain_text = extract_text(file.path)
                    except:
                        continue
                    if re.search(r'\S+', plain_text) and len(plain_text) > 2000:
                        
                        pages = list(extract_pages(file.path, laparams=params))
                        indent_count = line_indent_count(pages)

                        # in rare cases, the format step will fail due to poorly-formatted/empty PDF
                        try:
                            script_format = build_format(indent_count)
                        except IndexError:
                            continue
                        
                        output_text = standardize_document(pages, script_format)
                        
                        dest_folder = os.path.join('screenplays', folder.name)
                        if not os.path.exists(dest_folder):
                            os.makedirs(dest_folder)

                        new_filename = file.name.split('.pdf')[0] + '.txt'
                        dest_path = os.path.join(dest_folder, new_filename)
                        with open(dest_path, 'w') as f:
                            f.write(output_text)
                            print(f'Saved {dest_path}')



                



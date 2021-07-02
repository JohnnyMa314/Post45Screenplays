import pdfminer
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

from collections import Counter


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
                    coords.append(line.x0)

    indent_count = Counter(coords)
    return indent_count

def build_format(indent_count, min_lines=10):
    '''
    Given line-indent counts, returns a dict that assigns an x-coordinate to the three main
    screenplay roles: scene description, dialogue, character name.
    '''

    top_3 = indent_count.most_common(3)
    xcoords = sorted([k for (k, v) in top_3])

    script_format = {
        'scene_description' : xcoords[0],
        'dialogue' : xcoords[1],
        'character_name' : xcoords[2]
    }

    return script_format

def standardize_document(pages, script_format):
    '''
    Given a pdfminer pages object and a formatting dict, converts line x-coords
    to appropriate spacing.
    '''

    return

if __name__ == '__main__':

    source = 'data/2014/Boston Strangler.pdf'
    pages = extract_pages(source)
    count = line_indent_count(pages)
    print(build_format(count))


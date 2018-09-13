
"""
STEP 1. Create a sample of the big osm file
"""

import xml.etree.cElementTree as ET
from helper_functions import *

k = 100  # Parameter: take every k-th element

print "Sampling every", k, "th element of raw file"

with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(SOURCE_FILE, tags = ('node', 'way', 'relation', 'nd', 'member', 'tag'))):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')
	

print "Sampling done. Output store in " + SAMPLE_FILE + "."
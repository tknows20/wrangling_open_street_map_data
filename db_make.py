'''
3. Prepare database
'''
from helper_functions import *

# Make sure the fields order in the csvs matches the column order in the sql table schema
street_type_re = re.compile(r'[a-zA-Z]+[^0-9]\b\.?$', re.IGNORECASE)
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


mapping_street = { "St": "Street",
                   "Ave" : "Avenue",
                   "Avebue" : "Avenue",
                   "Dr" : "Drive",  
                   "Rd" : "Road",
                 }


def clean_tag(src_tag):
    """Clean and return tag values"""
    value_cleaned = src_tag.get('v')
    
    if src_tag.attrib['k'][0:4] == "addr":
        
        if is_postcode(src_tag):
            pc_val = src_tag.get('v')
            pc_val = pc_val.strip() # remove leading and ending spaces
            pc_val = pc_val.replace(" ", "") # remove spaces
            if pc_val[0].lower() == 's': # remove tags with leading S
                pc_val = pc_val[1:]
            if len(pc_val) == 5: # adding 0 to postcode with 5 digits
                pc_val = '0' + pc_val 
            value_cleaned = pc_val
            
        if is_city_name(src_tag):
            city_val = src_tag.get('v')
            city_val = city_val.strip() # remove leading and ending spaces
            city_val = city_val.replace(" ", "") # remoave spaces
            if 'singapore' in city_val.lower(): # remove extra letters, non-capitalized 'S'
                city_val = 'Singapore'
            value_cleaned = city_val
            
        if is_street_name(src_tag): 
            st_val = src_tag.get('v')
            st_val = st_val.strip() # remove leading and ending spaces
            m = street_type_re.search(st_val) #find last street name
            if m:
                old_type = m.group()
                if old_type in mapping_street.keys():
                    st_val = st_val.replace(old_type, mapping_street[old_type])
            st_val = string.capwords(st_val) # capitalize first letter of each word
            value_cleaned = st_val
            
    return value_cleaned
	
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
        for node_descp in NODE_FIELDS:
            node_attribs[node_descp] = element.get(node_descp)

        for node_tag in element:
            if node_tag.tag == 'tag' and not PROBLEMCHARS.search(node_tag.get('k')):
                tag_val = clean_tag(node_tag)
                #tag_val = node_tag.get('v')
                if LOWER_COLON.search(node_tag.get('k')):
                    temp_key = node_tag.get('k')
                    tags.append({ \
                                'id':  node_attribs['id'], \
                                'key': temp_key[temp_key.find(':')+1:], \
                                'value': tag_val, \
                                'type': temp_key[0:temp_key.find(':')] \
                                })
                else:
                    tags.append({ \
                                'id': node_attribs['id'], \
                                'key': node_tag.get('k'), \
                                'value': tag_val, \
                                'type': 'regular' \
                                })
        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        for way_descp in WAY_FIELDS:
            way_attribs[way_descp] = element.get(way_descp)

        counter = 0
        for indiv_tag in element:
            if indiv_tag.tag == 'tag' and not PROBLEMCHARS.search(indiv_tag.get('k')):
                tag_val = clean_tag(indiv_tag)
                if LOWER_COLON.search(indiv_tag.get('k')):
                    temp_key = indiv_tag.get('k')
                    tags.append({ \
                                'id':  way_attribs['id'], \
                                'key': temp_key[temp_key.find(':')+1:], \
                                'value': tag_val, \
                                'type': temp_key[0:temp_key.find(':')] \
                                })
                else:
                    tags.append({ \
                                'id': way_attribs['id'], \
                                'key': indiv_tag.get('k'), \
                                'value': tag_val, \
                                'type': 'regular' \
                                })

            if indiv_tag.tag == 'nd':
                way_nodes.append({'id': way_attribs['id'], \
                                'node_id': indiv_tag.get('ref'), \
                                'position': counter})
                counter += 1

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            #print el
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


process_map(SOURCE_FILE, validate=True)

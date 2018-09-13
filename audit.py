"""
Step 2. Audit address tags
"""



import xml.etree.cElementTree as ET
import pprint

from collections import defaultdict
from helper_functions import *

street_type_re = re.compile(r'[a-zA-Z]+[^0-9]\b\.?$', re.IGNORECASE)
postcode_re = re.compile(r'[^0-9]{1,6}$')
street_types = defaultdict(set)


expected_street = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", \
            "Trail", "Parkway", "Commons", "Central", "Close"]


def audit_street_type(street_types, street_name):
    """Add street type to dictionary  if unexpected"""
	
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected_street:
            street_types[street_type].add(street_name)

def audit_city_name(city_names, city_name):
	"""Add city names to set"""
    city_names.add(city_name)

def audit_country_name(country_names, country_name):
	"""Add country names to set"""
    country_names.add(country_name)

def audit_postcode_num(postcode_nums, postcode_num):
	"""Add postcode to set if it's less than 6 digits"""
	"""	or contain non-digit values"""
	
    if len(postcode_num) != 6:
            postcode_nums.add(postcode_num)
    try:
        pc_num = int(postcode_num)
    except ValueError:
        postcode_nums.add(postcode_num)

            
def audit(osmfile):
	""" Check and display unexpected addr tag values """
	
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    city_names = set()
    country_names = set()
    postcode_nums = set()
    problem_postcodes = {}
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        
        if elem.tag == "node" or elem.tag == "way":
            exist_st = 0
            exist_pc = 0
            for tag in elem.iter("tag"):
                
                if tag.attrib['k'][0:4] == "addr":
                    if is_street_name(tag):
                        st_value = tag.attrib['v']
                        exist_st = 1
                    elif is_postcode(tag):
                        pc_value = tag.attrib['v']
                        exist_pc = 1
                if exist_st == 1 and exist_pc ==1:
                    if len(pc_value) < 6:
                        problem_postcodes[st_value]= pc_value
                   
                if is_street_name(tag):
                    st_value = tag.attrib['v']
                    audit_street_type(street_types, tag.attrib['v'])
                elif is_city_name(tag):
                    audit_city_name(city_names, tag.attrib['v'])
                elif is_country_name(tag):
                    audit_country_name(country_names, tag.attrib['v'])
                elif is_postcode(tag):
                    audit_postcode_num(postcode_nums, tag.attrib['v'])
                    
    osm_file.close()
    return street_types, city_names, country_names, postcode_nums, problem_postcodes


street_types, city_names, country_names, postcode_nums, problem_postcodes = audit(SOURCE_FILE)
pprint.pprint(dict(street_types))
print ''
print city_names
print ''
print country_names
print ''
pprint.pprint(dict(problem_postcodes))
print ''
pprint.pprint(dict(problem_postcodes))
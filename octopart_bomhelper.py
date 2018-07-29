# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import json
import urllib.request as ur
import urllib.parse as up


orig_mpn = input("Part #? ")
min_quant = int(input("Quantity Required? "))                 
url1 = 'http://octopart.com/api/v3/parts/match?'
url1 += '&apikey=dfb8e0ac'
url1 += ('&queries=[{"mpn":"%s"}]'% orig_mpn)
# GRM155R71C104KA88D
url1 += "&include[]=specs"
url1 += "&include[]=short_description"

# urllib.request.urlopen(url) as ll
data = ur.urlopen(url1).read()
response = json.loads(data)

#min_quant = 1
max_results = 10            
# print request time (in milliseconds)
#print("request time: ", response['msec'], "ms")

def get_part_type(specs):
    part_type = 0
    if 'capacitance' in specs:
        part_type = 1
    elif 'resistance' in specs: 
        part_type = 2  
    return part_type

def available_from_mouser_digikey(item):
    avail = 0
    for offer in item['offers']:
#        print(offer['seller']['name'])
        if((offer['seller']['name'] == 'Digi-Key') and (offer['in_stock_quantity'] >= min_quant)):
            avail = max(avail,offer['in_stock_quantity'])
        elif ((offer['seller']['name'] == 'Mouser') and (offer['in_stock_quantity'] >= min_quant)):
            avail = max(avail,offer['in_stock_quantity'])
    return avail

def get_search_args_caps(specs):
    cap_args = specs['capacitance']['display_value'] + " "
#    cap_args += specs['capacitance_tolerance']['display_value'] + " "
    cap_args += specs['case_package']['display_value'] + " "
#    cap_args +=specs['dielectric_material']['display_value'] + " "
    cap_args +=specs['mounting_style']['display_value'] + " "
    cap_args += specs['voltage_rating_dc']['display_value'] + " "
    return cap_args

def get_search_args_resistor(specs):
    resistor_args = specs['resistance']['display_value'] + " "
    resistor_args += specs['resistance_tolerance']['display_value'] + " "
    resistor_args += specs['case_package']['display_value'] + " "
    resistor_args +=specs['mounting_style']['display_value'] + " "
    return resistor_args


def run_parametric_search(search_args):         
    args = [
   ('q', search_args),
   ('start', 0),
   ('limit', max_results)
   ]
    url2 = 'http://octopart.com/api/v3/parts/search?'
    url2 += '&apikey=dfb8e0ac'
    url2 += '&' + up.urlencode(args)
    new_data = ur.urlopen(url2).read()
    new_response = json.loads(new_data)
    paramsearch_items = []
    for result in new_response['results']:
        item = result['item']
        paramsearch_items.append(item)
    return paramsearch_items



print("Searching for part %s" % orig_mpn)
# print mpn's
for result in response['results']:
    avail = 0
    for item in result['items']:
        avail = max(avail,available_from_mouser_digikey(item))
    print("Available from Mouser or Digi-Key: ",avail)
    item = (next(iter(result['items'])))
    if (avail == 0):
        short_descript = item['short_description']
        specs = item['specs']
        part_type = get_part_type(specs)
        if (part_type == 1):
            search_args = get_search_args_caps(specs)
        elif (part_type == 2):
            search_args = get_search_args_resistor(specs)
        else:
            search_args = short_descript
        new_items = run_parametric_search(search_args)
        replacements = []
        for new_item in new_items:
            avail = max(avail,available_from_mouser_digikey(new_item))
            if(avail > min_quant):
                replacements.append(new_item['mpn'])
        if(replacements != []):
            print("Here are replacement parts: ")
            print(*replacements, sep = "\n")
        else:
            print("No suitable replacements found :( but you can search manually:")
            print(search_args)
            

#%%
#        print("%s - %s" % (item['brand']['name'], item['mpn']))
                    
#            for seller in offers['seller']:
#                print(seller['name'])
#            print(offers['in_stock_quantity'])
#        if 'lifecycle_status' in item['specs']:
#            lifecycle_status = item['specs']['lifecycle_status']['value'][0]
#        else:
#            lifecycle_status = 'Unknown'
#        brand_name = item['brand']['name']
#        mpn = item['mpn']
#        
#        print("\t%s %s: %s, In stock: %d" % (brand_name, mpn, lifecycle_status,instock))
#
#        for offers in item['offers']:
#            print(offers['in_stock_quantity'])

## print mpn's
#for result in response['results']:
#    print("Reference: %s" % result['reference'])
#    for item in result['items']:
#        # get lifecycle status
#        if 'lifecycle_status' in item['specs']:
#            lifecycle_status = item['specs']['lifecycle_status']['value'][0]
#        else:
#            lifecycle_status = 'Unknown'
#
#        brand_name = item['brand']['name']
#        mpn = item['mpn']
#        print("\t%s %s: %s" % (brand_name, mpn, lifecycle_status))
    #    print(sellers)
#    if (('Mouser' or 'Digikey') in sellers) and (offers['in_stock_quantity'] > 0):
#        return offers['in_stock_quantity'] 
#    else: return 0
            #%%
#caps: ['capacitance','display_value',]
#key1 = next(iter(specs.keys())
            #        url2 += '&' + up.urlencode(search_args)
#        new_data = ur.urlopen(url2).read()
#        new_response = json.loads(new_data)
#        for result in new_response['results']:
#           item = result['item']
#           print("%s - %s" % (item['brand']['name'], item['mpn']))
        
#        if(available_from_mouser_digikey(item) > 0):
#            print('yay!')
#            specs = item['specs']
#            
#        else:
#            print('Part not available from Mouser or Digikey')
#            short_descript = item['short_description']
#            specs = item['specs']
##        
#        sellers = []
#        for offers in item['offers']:
#            sellers.append(offers['seller']['name'])
#        if (('Mouser' or 'Digikey') in sellers) and (offers['in_stock_quantity'] > 0):
#            print('yep')
#        else:
#            print('Part not available from Mouser or Digikey')
#            short_descript = item['short_description']
#            specs = item['specs']
#            print(short_descript) 
# %%
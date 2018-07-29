#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib
import json
#import urllib.request as ur
#import urllib.parse as up

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def bom_helper(orig_mpn):
#    orig_mpn = input("Part #? ")
#    min_quant = int(input("Quantity Required? ")) 
                    
    min_quant = 10
    url1 = 'http://octopart.com/api/v3/parts/match?'
    url1 += '&apikey=dfb8e0ac'
    url1 += ('&queries=[{"mpn":"%s"}]'% orig_mpn)
    # GRM155R71C104KA88D
    url1 += "&include[]=specs"
    url1 += "&include[]=short_description"
    
    # urllib.request.urlopen(url) as ll
    #data = ur.urlopen(url1).read()
    data = urllib.urlopen(url1).read()
    response = json.loads(data)
    
    #min_quant = 1
    max_results = 10            
    # #print request time (in milliseconds)
    ##print("request time: ", response['msec'], "ms")
    #print("Searching for part %s" % orig_mpn)
    # #print mpn's
    for result in response['results']:
        avail = 0
        for item in result['items']:
            avail = max(avail,available_from_mouser_digikey(item))
        #print("Available from Mouser or Digi-Key: ",avail)
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
           # if(replacements != []):
                #print("Here are replacement parts: ")
                #print(*replacements, sep = "\n")
            # else:
                #print("No suitable replacements found :( but you can search manually:")
                #print(search_args)
    return replacements

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
#        #print(offer['seller']['name'])
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
    url2 += '&' + urllib.urlencode(args)
    #up.urlencode
#    new_data = ur.urlopen(url2).read()
    new_data = urllib.urlopen(url2).read()
    new_response = json.loads(new_data)
    paramsearch_items = []
    for result in new_response['results']:
        item = result['item']
        paramsearch_items.append(item)
    return paramsearch_items



# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)


# [START greeting]
class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END greeting]


# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
# [END main_page]


# [START guestbook]
class Guestbook(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

       	greeting.content = self.request.get('content')
        #orig_mpn = self.request.get('content')


        greeting.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))
# [END guestbook]


# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)
# [END app]
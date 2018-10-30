# This HTML_Gen is used in conjunction with Jinja2 to extract information out a txt file

# Uses input_text.txt to generate the page content
# Heirachy: Section (Title) - SubSection (Subject) - Description
# Seperate lists with ",," / Lists work like [LIST: a, b, c]
# Links work like (LINK:(www),title)

#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#
import os
import re
import sys
import webapp2
import jinja2
import generate_html_methods
import cgi
import urllib
import urllib2
from xml.dom import minidom
from string import letters
import logging


from google.appengine.api import users
from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader( template_dir), autoescape = True)


html = generate_html_methods.openraw ('input_html.txt') # reads the input_html.txt file
toc = generate_html_methods.generate_TOC (html) # generates the table of contents with links
body = generate_html_methods.generate_HTML (generate_html_methods.listify(generate_html_methods.linkify(html))) # generates the body text compelete with links

# Used to create output into a text file if needed
# totalHtml = toc + body
# generate_html_methods.process_html (totalHtml, 'output_html.txt')

#######

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

guestbook_name = "Guestbook" # Sets the entities to the Guestbook parent

def guestbook_key (wall_name=DEFAULT_GUESTBOOK_NAME):
	return ndb.Key('Guestbook', guestbook_name)

def validation (input): # Validates user input using strip function
	input = input.strip()
	if input == "":
		return False


#### GMAPS

IP_URL = "http://api.hostip.info/?ip="
def get_coords(ip):
	url = IP_URL + ip
	content = None
	try:
		content = urllib2.urlopen(url).read()
	except URLError:
		return
	if content:
		d = minidom.parseString(content)
		coords = d.getElementsByTagName("gml:coordinates")
		if coords and coords[0].childNodes[0].nodeValue:
			lon, lat = coords[0].childNodes[0].nodeValue.split(',')
			return ndb.GeoPt(lat, lon)
GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=480x480&sensor=false"

def gmaps_img(points):
	markers = '&'.join('markers=%s,%s' % (p.lat, p.lon) for p in points)
	return GMAPS_URL + markers

#####



class Comments(ndb.Model): # Creates the instance of the Comments that includes the date, user, and post content to put into the comment box
	user = ndb.StringProperty(indexed=True)
	post_content = ndb.StringProperty (indexed = False)
	date = ndb.DateProperty(auto_now_add=True)
	time = ndb.TimeProperty(auto_now_add=True)
	datetime = ndb.DateTimeProperty (auto_now_add=True)
	coords = ndb.GeoPtProperty() 






##### Handler

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a,**kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class MainPage(Handler): # Sets the main page to the front page, when the user requests the page, the program reads the input_html.txt file and adds all appropriate tags
	def get(self):
		guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME) 
		comments = cgi.FieldStorage()
		comments_query = Comments.query(ancestor = guestbook_key(guestbook_name)).order(-Comments.date).order(-Comments.time)
		comments =  comments_query.fetch()
		logging.info("Loaded")

		points = []
		for a in comments:
			if a.coords:
				points.append(a.coords)


		img_url = gmaps_img(points)	

		sign_query_params = urllib.urlencode({'guestbook_name': guestbook_name})
		status = self.request.get('status')
		self.render("all_html.html", toc = toc , body = body, comments=comments, status = status, img_url = img_url)
		print "Success"

	
class Guestbook (Handler): # Handles the comment feature
	def post(self):
		guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)
		comment = Comments(parent=guestbook_key(guestbook_name))
		comment.post_content = self.request.get('post_content') # grabs the post content
		comment.user = self.request.get('user') # grabs the user name

		if self.request.remote_addr:
				coords = self.request.remote_addr
				logging.info("GOT IP %s", str(coords) )

		coords = get_coords(self.request.remote_addr)

		if coords:
			comment.coords = coords

		status =""
		if validation (comment.post_content) == False or validation (comment.post_content) == False:
		 	status = "Please Enter Text Before Submitting"
		 	self.redirect('/?status=' + status)
		else:
			coords = get_coords(self.request.remote_addr)
			if coords:
				comment.coords = coords
			self.redirect('/')
			comment.put() # updates the GAE Datastore with name, comments, and geolocation





app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/sign', Guestbook),
], debug=True)
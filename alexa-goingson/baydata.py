#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import re
import sys
import pandas as pd

class BAYDATA(object):
	'''
	Class for pulling data from DoTheBay.

	This class queries the landing page for DoTheBay, extracts
	the categories and associated subpages, then loops through
	each to scrape event data. To reduce server queries and
	application load times, this will be used sparingly to
	populate the event database. It may be used independently
	to fetch events and deposit them into a csv file.

	Queries within categories can be extended across multiple
	subpages and will run till options are exhausted.

	Example
	--------
	bd = BAYDATA()
	bd.load_all(page_limit=2)

	Categories
	----------
	Activism, Comedy, Film, Food & Drink, LGBTQ, Music,
	Outdoor & Recreation, Sports, The Arts

	Parameters
	----------
	categories : dict
		Keys are categories and values are the subpage links
	events : list
		List of event dictionaries
 	'''


	URL = 'https://dothebay.com'
	HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X ' + 
	'10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 ' + 
	'Safari/537.36'}

	def __init__(self):

		self.categories = {}
		self.events = []

	def load_all(self, page_limit=1, category_list=None):
		'''Loops through each category to pull events

		Parameters
		----------
		page_limit : int
			Number of pages to loop through per category
		category_list : list or None
			List of categories to query, default None loops through all.
			Acceptable categories are listed in the main class docstring.

		Returns
		-------
		None
		'''

		# Pull categories
		self.categories = self.pull_categories()

		# Make Category Query
		if category_limit == None:
			category_list = self.categories.keys()

		for cat in category_list:
			self.category_query(category=cat, pages=page_limit)

		return None

	def make_request(self, url, headers=None, params=None):
		'''Generates GET response response object from requests package

		Parameters
		----------
		url : str
			URL of website to scrape
		headers : dict or None
			Dictionary of headers for GET request
		params : dict or None
			Dictionary of parameters to add to URL for request

		Returns
		-------
		response object
		'''

		response = requests.get(url, headers=headers, params=params)

		try:
			response.status_code == 200
		except:
			print('Error - Expected Response Status Code 200, Instead ' +
				'Received {}'.format(response.status_code))

		return response

	def pull_categories(self):
		'''Extract major categories from DoTheBay

		Returns
		-------
		category_dict : dict
			Keys are categories and values are the subpage links
		'''

		# Print Status
		self.stdoutWrite(message='Downloading Available Categories', 
			success=None)

		# Response Request
		response = self.make_request(self.URL, headers=self.HEADERS)

		# Soup
		soup = BeautifulSoup(response.content, 'html.parser')

		# Extract categories
		category_dict = {x.text:x['href'] for x in soup.find_all('a', 
			attrs={'class':'ga-tracking', 'data-ga-action':'CATEGORIES'})}

		# Print Status
		self.stdoutWrite(message='Downloading Available Categories', 
			success=True)

		return category_dict

	def category_query(self, category, pages=1):
		'''Runs event queries over category till exhuastion

		Parameters
		----------
		category : str
			Category to query
		pages : int
			Number of pages to query per category
		'''

		# Initialize Current Page and Next Page Exists Condition
		current_page = 1
		next_page_exists = True
		current_events_size = len(self.events)

		# Print Status
		self.stdoutWrite(message='Collecting Events For {}'.format(category), 
			success=None)

		while (current_page < pages+1) and next_page_exists:

			self.stdoutWrite(message='Collecting Events For {}'.format(category), 
			success=None, current_value=current_page, max_value=pages)

			# Make Request
			response = self.make_request(self.URL+self.categories[category],
				params={'page':current_page})

			# Put Into Soup
			soup = BeautifulSoup(response.content, 'html.parser')

			# Get Proper event category code
			class_category = re.sub('(\/|events|today|\d)','',
				self.categories[category])

			# Extract Events and Next Page (if exists)
			events=soup.find_all('div', 
				attrs={'class':'ds-listing event-card ds-event-category-'+
				class_category})
			next_page_exists = type(soup.find('a', 
				attrs={'class':'ds-next-page'})) == type(None)

			# Parse Events and deposit
			self.events+=[self.parse_event(event,class_category) for event 
			in events]

			# Increase iterator
			current_page+=1

		# Print Status if Events have been added
		if len(self.events) > current_events_size:
			self.stdoutWrite(message='Collecting Events For {}'.format(category), 
				success=True)
		else:
			self.stdoutWrite(message='Collecting Events For {}'.format(category), 
				success=True)

		return None

	def parse_event(self, event, category):
		'''Parses event class within DoTheBay HTML

		Parameters
		----------
		event : soup object
			BeautifulSoup object for single event
		category : str
			Category of event

		Returns
		-------
		values : dict
			Dictionary of all event information
		'''

		values = {
		'fulltitle':None,
		'title':None,
		'streetAddress':None,
		'addressLocality':None,
		'addressRegion':None,
		'postalCode':None,
		'venue':None,
		'latitude':None,
		'longitude':None,
		'starttime':None,
		'startDate':None,
		'influencer_count':None,
		'upvote':None,
		'tickets':None,
		'category':category,
		}

		# Title
		try:
			values['fulltitle'] = event.find('span', 
				attrs={'class':'ds-byline'}).text.strip() + ' ' +\
			event.find('span', attrs={'class':
				'ds-listing-event-title-text'}).text.strip()
			
			values['title'] = event.find('span', attrs={'class':
				'ds-listing-event-title-text'}).text.strip()
		except:
			pass

		# Address
		for key in ['streetAddress', 'addressLocality', 
			'addressRegion', 'postalCode']:
			try:
				values[key] = event.find('meta', 
					attrs={'itemprop':key})['content'] 
			except:
				pass

		# Venue
		try:
			values['venue'] = event.find('a', attrs={'itemprop':'url',
				'href':re.compile('\/venues\/')}).text.strip()
		except:
			pass

		# Latitude and Longitude
		try:
			values['latitude'] = event.find('meta', 
				attrs={'itemprop':'latitude'})['content']
			values['longitude'] = event.find('meta', 
				attrs={'itemprop':'longitude'})['content']
		except:
			pass

		# Start Time and Date
		try:
			values['starttime'] = re.search('[\d,:,PM,AM]*',event.find('div', 
				attrs={'class':'ds-event-time dtstart'}).text.strip())[0]
			values['startDate'] = event.find('meta', 
				attrs={'itemprop': 'startDate'})['datetime']
		except:
			pass

		# Influencer Count
		try:
			values['influencer_count'] = event.find('div', 
				attrs={'class':'ds-listing-influencer-count'}).text.strip()
		except:
			pass

		# Upvotes
		try:
			values['upvote'] = event.find('span', 
				attrs={'class':'ds-upvote-default'}).text
		except:
			pass

		# Ticket Links
		try: 
			values['tickets'] = event.find('a', 
				attrs={'title':'BUY TICKETS'})['href']
		except:
			pass

		return values

	def write_csv(self, outdir):
		'''Write out results to a csv file

		Parameters
		----------
		outdir : str
			Output directory for results
		'''

		# Put into Pandas DataFrame
		df = pd.DataFrame(self.events)

		# Sort by UpVote and Group
		df = df.sort_values(by=['category','upvote'])

		# Write out without index
		df.to_csv(outdir+'dothebay.csv', index=False)

		return None

	def stdoutWrite(self, success, message, current_value=None, max_value=None):
		'''
		Writes colored status to stdout.
		Parameters
		----------
		success : bool or None
			Boolean indicates completion/failure of operation.  None
			leaves status box empty
		'''

		if type(success) == type(None) and current_value==None:
			sys.stdout.write("[%-2s] %s" % ('', message))
			sys.stdout.flush()
		elif type(success) and success == True and current_value==None:
			sys.stdout.write('\r')
			sys.stdout.write("[%-2s] %s\n" % ('\033[92m' + 'ok' +
			 '\033[0m', message))
			sys.stdout.flush()
		elif type(success) and success == False and current_value==None:
			sys.stdout.write('\r')
			sys.stdout.write("[%-4s] %s\n" % ('\033[91m' + 'fail' +
			 '\033[0m', message))
			sys.stdout.flush()
		else:
			sys.stdout.write('\r')
			sys.stdout.write("[  ] {} ... \033[94m{} of {}\033[0m".format(
				message, current_value, max_value))
			sys.stdout.flush()

		return None

	def printSection(self, section='start', output=None):
		'''
		Writes section title to stdout.

		Cosmetic function to help user visualize status of web scrapes.

		Parameters
		----------
		CATEGORY : str
			String takes either "start", "end", or global CATEGEORY variable
		'''

		if section == 'start':
			sys.stdout.write("\n%s\n" % ('-' * len('DoTheBay San Francisco')) +
				"DoTheBay \u001b[41;1mSan Francisco\033[0m\n" +
				"%s\n\n" % ('-' * len('GDoTheBay San Francisco')))

		elif section == 'end':
			message = 'File Saved to ' + output + 'dothebay.csv'
			sys.stdout.write("\n%s\n%s\n%s\n\n" % ('-'*len(message), message, 
				'-'*len(message)))

		else:
			sys.stdout.write("\n%-20s\n" % ('-'*((20-len(' ' + section + 
				' '))/2) + ' ' + section + ' ' + 
			'-'*((20-len(' ' + section + ' '))/2)))

		return None


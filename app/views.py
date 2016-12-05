### newest version

from facebook import get_user_from_cookie, GraphAPI
from flask import g, render_template, redirect, request, session, url_for

from app import app, db
from models import User
from keys import *
# Facebook app details


import tweepy
import requests
from watson_developer_cloud import AlchemyLanguageV1
import json
import operator
import facebook

class TwitterHelper(object):
	def __init__(self):
		"""
		input: none
		graph is access to facebook api
		alchemy_language is access to alchemy api
		"""
		# authentication
		self.auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
		self.auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
		# twitter api
		self.api = tweepy.API(self.auth)
		# alchemy api
		self.alchemy_language = AlchemyLanguageV1(api_key=ALCHEMY_KEY)

	def searchUsers(self, query):
		relevant_keys = ['name', 'screen_name', 'location', 'profile_image_url', 'description', 'followers_count']
		# maximum of 20 users can be displayed
		full_dict = self.api.search_users(q=query)
		ret = []
		for i in range(len(full_dict)):
			temp_dict = {}
			temp_dict['name'] = full_dict[i].name
			temp_dict['screen_name'] = full_dict[i].screen_name
			temp_dict['location'] = full_dict[i].location
			temp_dict['profile_image_url'] = full_dict[i].profile_image_url
			temp_dict['description'] = full_dict[i].description
			temp_dict['followers_count'] = full_dict[i].followers_count
			ret.append(temp_dict)
		return ret

	def getTimeline(self, screen_name):
		return self.api.user_timeline(screen_names=screen_name, count=3200)[0]

	def getTimelineAndRetweets(self, screen_name):
		return self.api.user_timeline(screen_names=screen_name, since_id=0, count=200, include_rts=1)

	def TweetSentAnalysis(self, max_items=10):
		"""
		input: max_items - the number of entities to extract from all posts of the searched person
		output: json holding information about sentiment and emotions associated with the entities
		"""
		# get FB data
		rawTweets = ''
		pass

		# return self.performSentimentAnalysis(rawStatusUpdateString, max_items)

	def performSentimentAnalysis(self, text, max_items=10):
		"""
		input: text to analyze
		output: json holding analysis of entities
		"""
		return json.dumps(
		  self.alchemy_language.entities(
		    text=text,
		    sentiment=1,
			emotion=1,
			linked_data=0,
			disambiguate=0,
		    max_items=max_items),
		  indent=2)
		  

class FacebookHelper(object):
	def __init__(self, access_token):
		"""
		input: facebook access token
		graph is access to facebook api
		alchemy_language is access to alchemy api
		"""
		self.access_token = access_token
		self.graph = facebook.GraphAPI(access_token)
		self.alchemy_language = AlchemyLanguageV1(api_key=ALCHEMY_KEY)

	def getBasicInfo(self):
		"""
		output: basic info on ego user
		"""
		return self.graph.get_object('me?fields=name,picture{url},about,education,location')

	def FBSentAnalysis(self, max_items=10):
		"""
		input: max_items - the number of entities to extract from all status updates of the user
		output: json holding information about sentiment and emotions associated with the entities
		"""
		# get FB data
		rawStatusUpdateString = ''
		page = self.graph.get_object('me/posts')
		while len(page['data']) != 0:
			for post in page['data']:
				try:
					statusUpdate = post['message']
					if statusUpdate[-1] not in ['!', '?', '.']:
						statusUpdate += '.'
					statusUpdate += '\n'
					rawStatusUpdateString += statusUpdate
				except Exception as e:
					pass
			page = requests.get(page['paging']['next']).json()
		# perform sentiment on all of the status updates
		raw = self.performSentimentAnalysis(rawStatusUpdateString, max_items)
		# strips the output and returns it
		return self.stripOutput(raw)

	def stripOutput(self, raw):
		ret = []
		# strip/format the raw response
		for entity in raw['entities']:
			stripped_entitity = {}
			stripped_entitity['text'] = entity['text']
			max_emotion = max(entity['emotions'].iteritems(), key=operator.itemgetter(1))
			stripped_entitity['emotion'] = {'type': max_emotion[0], 'value': max_emotion[1]}
			ret.append(stripped_entitity)
		return ret

	def performSentimentAnalysis(self, text, max_items=10):
		"""
		input: text to analyze
		output: json holding analysis of entities
		"""
		return self.alchemy_language.entities(
		    text=text,
			emotion=1,
			linked_data=0,
			disambiguate=0,
		    max_items=max_items)
			
			

@app.route('/')
def index():
    # If a user was set in the get_current_user function before the request,
    # the user is logged in.
    #print(g.user)
    #if g.user:
		#return render_template('search.html')
      #  return render_template('index.html', app_id=FB_APP_ID,
       #                        app_name=FB_APP_NAME, user=g.user)
    # Otherwise, a user is not logged in.
    return render_template('login.html', app_id=FB_APP_ID, name=FB_APP_NAME)


@app.route("/search", methods=['GET', 'POST'])
def search():
	if request.method == 'POST':
		input_name = request.form.get('search')
		#return render_template('search.html', name)
		return results(input_name)
	else:
		return render_template('search.html')
	#search=request.form.get('searchterm')
	
#@app.route("/results", methods=['GET','POST'])
def results(input_name):
	helper = TwitterHelper()
	returned = helper.searchUsers(input_name)
	return render_template('results.html', search = returned[0])
	#return render_template('results.html', search = input_name)
	
	
@app.route("/profile/<string:handle>", methods=['GET'])
def profile(handle):
	helper = TwitterHelper()
	tsentiment = helper.TweetSentAnalysis(handle)
	tprofile = helper.searchUsers(handle)
	return render_template('profile.html', userhandle = handle, usersentiment = tsentiment, userinfo = tprofile[0])
	
@app.route("/fbprofile/<string:name>", methods=['GET'])
def fbprofile(name):
	## this is where the oath token associated with the user logged in through facebook will go
	helper = FacebookHelper('EAAZAx4mZAxoJkBAHpaNkBdv02FxvBbjWfsyQ7jvZCdWg19FTc42TzBZAE1IfRdlhJpve8Qhw5DHZCX8psa3f2IZCsqg4iIhAGhdTZCfV1G6E2FIySZCzquZBNFSgRavlaQzXS79DJeDZC0yMJDrL3WvIZC9iMclbRy9wBdzqkrDQwyVggZDZD')
	test = helper.FBSentAnalysis()
	return render_template('fbprofile.html',user = test)
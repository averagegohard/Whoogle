from facebook import get_user_from_cookie, GraphAPI
from flask import g, render_template, redirect, request, session, url_for

from app import app, db
from models import User

import tweepy
import requests
from watson_developer_cloud import AlchemyLanguageV1
import json


from keys import *
# Facebook app details

import operator
import facebook


class TwitterHelper(object):
	def __init__(self):
		"""
		input: none
		self.api: access to twitterAPI
		self.alchemy_language: access to AlchemyAPI
		"""
		# authentication
		self.auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
		self.auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
		# twitter api
		self.api = tweepy.API(self.auth)
		# alchemy api
		self.alchemy_language = AlchemyLanguageV1(api_key=ALCHEMY_KEY)


	def TweetSentAnalysis(self, twitter_handle, max_items=10):
		""" gets sentiment analysis on last 3200 tweets of user
		input: max_items - the number of entities to extract from all posts of the searched person
		output: json holding information about sentiment and emotions associated with the entities (10 by default)
		"""
		# get twitter data
		data = self.getTimelineAndRetweets(twitter_handle)
		# perform sentiment analysis
		raw = json.loads(self.performSentimentAnalysis(data))
		return self.stripOutput(raw)


	def searchUsers(self, query):
		""" searches for users
		input: query
		output: stripped json with relevant information
		"""
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

	def stripOutput(self, raw):
		"""
		helper function
		"""
		ret = []
		# strip/format the raw response
		for entity in raw['entities']:
			stripped_entitity = {}
			stripped_entitity['text'] = entity['text']
			max_emotion = max(entity['emotions'].iteritems(), key=operator.itemgetter(1))
			stripped_entitity['emotion'] = {'type': max_emotion[0], 'value': max_emotion[1]}
			ret.append(stripped_entitity)
		return ret

	def getTimelineAndRetweets(self, screen_name):
		"""
		helper function
		"""
		rawTweets = ''
		for status in tweepy.Cursor(self.api.user_timeline, screen_name=screen_name, count=200).items():
			# process status here
			if status.text[-1] not in ['!', '?', '.']:
				status.text += '.'
			status.text += '\n'
			rawTweets += status.text
		return rawTweets

	def performSentimentAnalysis(self, text, max_items=10):
		"""
		helper function
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
		  
		  
"""
    If you are using the JavaScript SDK, you can use the
    get_user_from_cookie() method below to get the OAuth access token
    for the active user from the cookie saved by the SDK.
"""

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
    if g.user:
		#return render_template('search.html')
        return render_template('index.html', app_id=FB_APP_ID,
                               app_name=FB_APP_NAME, user=g.user)
    # Otherwise, a user is not logged in.
    return render_template('login.html', app_id=FB_APP_ID, name=FB_APP_NAME)


@app.route('/logout')
def logout():
    """Log out the user from the application.

    Log out the user from the application by removing them from the
    session.  Note: this does not log the user out of Facebook - this is done
    by the JavaScript SDK.
    """
    session.pop('user', None)
    return redirect(url_for('index'))


@app.before_request
def get_current_user():
    """Set g.user to the currently logged in user.

    Called before each request, get_current_user sets the global g.user
    variable to the currently logged in user.  A currently logged in user is
    determined by seeing if it exists in Flask's session dictionary.

    If it is the first time the user is logging into this application it will
    create the user and insert it into the database.  If the user is not logged
    in, None will be set to g.user.
    """

    # Set the user in the session dictionary as a global g.user and bail out
    # of this function early.
    if session.get('user'):
        g.user = session.get('user')
        return

    # Attempt to get the short term access token for the current user.
    result = get_user_from_cookie(cookies=request.cookies, app_id=FB_APP_ID,
                                  app_secret=FB_APP_SECRET)

    # If there is no result, we assume the user is not logged in.
    if result:
        # Check to see if this user is already in our database.
        user = User.query.filter(User.id == result['uid']).first()

        if not user:
            # Not an existing user so get info
            graph = GraphAPI(result['access_token'])
            profile = graph.get_object('me')
            if 'link' not in profile:
                profile['link'] = ""

            # Create the user and insert it into the database
            user = User(id=str(profile['id']), name=profile['name'],
                        profile_url=profile['link'],
                        access_token=result['access_token'])
            db.session.add(user)
        elif user.access_token != result['access_token']:
            # If an existing user, update the access token
            user.access_token = result['access_token']

        # Add the user to the current session
        session['user'] = dict(name=user.name, profile_url=user.profile_url,
                               id=user.id, access_token=user.access_token)

    # Commit changes to the database and set the user as a global g.user
    db.session.commit()
    g.user = session.get('user', None)
	
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
	
	
@app.route("/profile/<string:name>", methods=['GET'])
def profile(name):
	return render_template('profile.html', user = name)
	
@app.route("/fbprofile/<string:name>", methods=['GET'])
def fbprofile(name):
	return render_template('fbprofile.html',user = name)
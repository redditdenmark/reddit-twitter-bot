# -*- coding: utf-8 -*-

'''
Copyright 2015 Randal S. Olson

This file is part of the reddit Twitter Bot library.

The reddit Twitter Bot library is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

The reddit Twitter Bot library is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
License for more details. You should have received a copy of the GNU General
Public License along with the reddit Twitter Bot library.
If not, see http://www.gnu.org/licenses/.
'''

import praw
import json
import requests
import tweepy
import time
import os
from glob import glob
import urllib

# Place your Twitter API keys here
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''

# Place the subreddit you want to look up posts from here
SUBREDDIT_TO_MONITOR = 'Denmark'

# Place the name of the folder where the images are downloaded
IMAGE_DIR = 'img'

# Place the name of the file to store the IDs of posts that have been posted
POSTED_CACHE = 'posted_posts.txt'

# Place the string you want to add at the end of your tweets (can be empty)
TWEET_SUFFIX = ' - Via /r/Denmark'

# Specific hash tag for /r/Denmark submissions with flairs
TWEET_DKPOL = ' #dkpol'
TWEET_AMA = ' #AMA'
TWEET_NEWS = ' #dknews #dkmedier"'

# Place the maximum length for a tweet
TWEET_MAX_LEN = 270

# Place the time you want to wait between each tweets (in seconds)
DELAY_BETWEEN_TWEETS = 30

# Place the lengths of t.co links (cf https://dev.twitter.com/overview/t.co)
T_CO_LINKS_LEN = 24

def setup_connection_reddit(subreddit):
	''' Creates a connection to the reddit API. '''
	print('[bot] Setting up connection with reddit')
	reddit_api = praw.Reddit('reddit Twitter tool monitoring {}'.format(subreddit))
	return reddit_api.get_subreddit(subreddit)


def tweet_creator(subreddit_info):
	''' Looks up posts from reddit and shortens the URLs to them. '''
	post_dict = {}
	post_ids = []

	print('[bot] Getting posts from reddit')

	# You can use the following "get" functions to get posts from reddit:
	#   - get_top(): gets the most-upvoted posts (ignoring post age)
	#   - get_hot(): gets the most-upvoted posts (taking post age into account)
	#   - get_new(): gets the newest posts
	#
	# "limit" tells the API the maximum number of posts to look up

	for submission in subreddit_info.get_hot(limit=10):
		if not already_tweeted(submission.id):
			# This stores a link to the reddit post itself
			# If you want to link to what the post is linking to instead, use
			# "submission.url" instead of "submission.permalink"
			post_dict[submission.title] = {}
			post = post_dict[submission.title]
			post['link'] = submission.permalink

			# Store the url the post points to (if any)
			post['flair'] = ''
			
			# Get the Submission link flair
			if submission.link_flair_text is not None:
				post['flair'] = submission.link_flair_text.strip().lower();

			post_ids.append(submission.id)
		else:
			print('[bot] Already tweeted: {}'.format(str(submission)))
			
			
	# Get new, for tweeting announcements
	for submission in subreddit_info.get_new(limit=20):
			if not already_tweeted(submission.id):
				if submission.distinguished is not None:
					if submission.id not in post_ids:
						# This stores a link to the reddit post itself
						# If you want to link to what the post is linking to instead, use
						# "submission.url" instead of "submission.permalink"
						post_dict[submission.title] = {}
						post = post_dict[submission.title]
						post['link'] = submission.permalink
						post['flair'] = ''					
						# Get the Submission link flair
						if submission.link_flair_text is not None:
							post['flair'] = submission.link_flair_text.strip().lower();

						post_ids.append(submission.id)
					else:
						print('[bot] Alrady in top 10: {}'.format(str(submission)))
				else:
					print('[bot] Not a distuingished post: {}'.format(str(submission)))
			else:
				print('[bot] Already tweeted: {}'.format(str(submission)))
			

	return post_dict, post_ids


def already_tweeted(post_id):
	''' Checks if the reddit Twitter bot has already tweeted a post. '''
	found = False
	with open(POSTED_CACHE, 'r') as in_file:
		for line in in_file:
			if post_id in line:
				found = True
				break
	return found


def strip_title(title, num_characters):
	''' Shortens the title of the post to the 140 character limit. '''

	# How much you strip from the title depends on how much extra text
	# (URLs, hashtags, etc.) that you add to the tweet
	# Note: it is annoying but some short urls like "data.gov" will be
	# replaced by longer URLs by twitter. Long term solution could be to
	# use urllib.parse to detect those.
	if len(title) <= num_characters:
		return title
	else:
		return title[:num_characters - 1] + '…'

def tweeter(post_dict, post_ids):
	''' Tweets all of the selected reddit posts. '''
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
	api = tweepy.API(auth)

	for post, post_id in zip(post_dict, post_ids):


		extra_text = ' ' + post_dict[post]['link'] + TWEET_SUFFIX
		extra_text_len = 1 + T_CO_LINKS_LEN + len(TWEET_SUFFIX)
		
		# Add #dkpol to submissions flaired with politics
		if post_dict[post]['flair'] == 'politics':
			extra_text = extra_text + TWEET_DKPOL
			extra_text_len += len(TWEET_DKPOL)
		if post_dict[post]['flair'] == 'ama':
			extra_text = extra_text + TWEET_AMA
			extra_text_len += len(TWEET_AMA)
		if post_dict[post]['flair'] == 'news':
			extra_text = extra_text + TWEET_NEWS
			extra_text_len += len(TWEET_NEWS)


		post_text = strip_title(post, TWEET_MAX_LEN - extra_text_len) + extra_text
		print('[bot] Posting this link on Twitter')
		print(post_text)
		api.update_status(status=post_text)
		log_tweet(post_id)
		time.sleep(DELAY_BETWEEN_TWEETS)


def log_tweet(post_id):
	''' Takes note of when the reddit Twitter bot tweeted a post. '''
	with open(POSTED_CACHE, 'a') as out_file:
		out_file.write(str(post_id) + '\n')


def main():
	''' Runs through the bot posting routine once. '''
	# If the tweet tracking file does not already exist, create it
	if not os.path.exists(POSTED_CACHE):
		with open(POSTED_CACHE, 'w'):
			pass

	subreddit = setup_connection_reddit(SUBREDDIT_TO_MONITOR)
	post_dict, post_ids = tweet_creator(subreddit)
	tweeter(post_dict, post_ids)


if __name__ == '__main__':
	main()

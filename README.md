# Reddit Twitter Bot

A Python bot that looks up posts from reddit and automatically posts them on Twitter.
This bot is fork that in this repo, is specifically configured for the subreddit /r/Denmark posts.
This bot also has added flair detection and can add hashtags based on flairs.


## Dependencies

You will need to install Python's [tweepy](https://github.com/tweepy/tweepy) and [PRAW](https://praw.readthedocs.org/en/) libraries first:

    pip install tweepy
    pip install praw==3.6.0
    
You will also need to create an app account on Twitter: [[instructions]](https://dev.twitter.com/apps)

1. Sign in with your Twitter account
2. Create a new app account
3. Modify the settings for that app account to allow read & write
4. Generate a new OAuth token with those permissions
5. Manually edit this script and put those tokens in the script

## Usage

Once you edit the bot script to provide the necessary API keys and the subreddit you want to tweet from, you can run the bot on the command line:

    python3 reddit_twitter_bot.py
 
Look into the script itself for configuration options of the bot.

from datetime import datetime
import pandas as pd
import tweepy
import json
import csv

def tweet_extract():
    consumer_key = 'consumer_key'
    consumer_secret = 'consumer_secret'
    access_key= 'access_key'
    access_secret = 'access_secret'
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth,wait_on_rate_limit=False)
    search_words = "Herdsmen" or 'Killer Herdsmen' or 'Pastoralists' or 'Pastoralist' or 'Fulani Herdsmen' or 'Fulani Pastoralist' or 'Fulani killer' or 'Miyetti' or 'Miyetti Allah' or 'MACBAN'or 'Cattle Breeders' or 'Cattle Rustlers'
    new_search = search_words + " -filter:retweets"
    tweets = tweepy.Cursor(api.search_tweets,q=new_search,count=200,lang="en",since_id=0).items()

    list_tweets = []
    for tweet in tweets:
        refined_tweet = {"id": tweet.id,
			                  "created_at":tweet.created_at,
                        'tweet' : tweet.text.encode('utf-8'),
                        'location' : tweet.user.location.encode('utf-8')
                        }
        
        list_tweets.append(refined_tweet)

    df = pd.DataFrame(list_tweets)
    df.to_csv('herds.csv',index = False)

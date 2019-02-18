##extract only those tweets which are replies

import sys
import pprint
import datetime
import re
import csv
import ast
import os
import math
import json
import string

from shapely.geometry import Point
from shapely.geometry import box
from shapely.geometry import Polygon, LinearRing, LineString

from textblob import TextBlob

    
def get_at(text):
    mentions = []
    
    for m in re.finditer("@", text, flags=0):
        g = m.start()
        name = text[g:].split()[0][1:];
        if len(name) > 0:
            mentions.append(name)

    return mentions;
                
def get_mentions(tweet):

    #if 'extended_tweet' in tweet:
    #    mentions = get_at(tweet['extended_tweet']['full_text']);
    #else:
    #    mentions = get_at(tweet['text']);
    mentions = []
    if 'user_mentions' in tweet['entities']:
        for t in tweet['entities']['user_mentions']:
            mentions.append( (t['id_str'], t['screen_name']) )
                
    return mentions

def clean_text(tweet):
    if 'extended_tweet' in tweet:
        text = tweet['extended_tweet']['full_text'];
    else:
        text = tweet['text'];
    ##I hate regexes: sub anything after an @symbol, any character not in the 2nd bracked, or any url with " "
    clean_text = " ".join(re.sub("(@[A-Za-z0-9_]+)|([^0-9A-Za-z\'\?\!\-\‘\’\. \t\n])|(\w+:\/\/\S+)", " ", text).split())
    return clean_text
    
def get_polarity(text):
    tb = TextBlob(text)
    try:
        pol = tb.polarity;
    except:
        pol = 0;
    return pol;
    
    
infilename = sys.argv[1];
outfilename = sys.argv[2];
#statsfilename = sys.argv[3];

##US
target = box(-125, 24.5, -67, 49.5);
    
geo_ind = [];
user_names = {};


output_file = open(outfilename, 'w');

if not os.path.isfile(infilename):
    print( "didn't find", infilename );
    sys.stdout.flush()
    sys.exit(1);
    
    
num_tweets = 0;
num_target_tweets = 0;
num_replies = 0;
num_mentions = 0
num_place = 0;
num_place_use = 0;
duplicates = 0;
replyandmention = 0;


tweet_ids = set();

sources = {};
with open(infilename, 'r') as data_file:
    print( "found", infilename );
    for line in data_file:        
        try:
            tweets = [json.loads(line)];
        except ValueError as e: #weird bug in input. 2 tweets on same line????
            print("Double tweet!")
            if line.find("}{") > -1:
                line = line.replace("}{", "}\n{")
                st = line.splitlines()
                tweets = [ json.loads(l) for l in st ]        
            
        for tweet in tweets:
            if 'place' not in tweet.keys():
                continue
            num_tweets += 1;
            if tweet['place'] == None: continue;
            num_place += 1;
                
            #if data_type == "reply":
            #    mentions = [ (tweet['in_reply_to_user_id'], tweet['in_reply_to_screen_name']) ]
            #else:
            mentions = get_mentions( tweet );
            if len(mentions) == 0: continue;
            #if is_reply or has_mention:
            num_mentions += 1;
            if(num_mentions % 100 == 0):
                print(num_tweets, "tweets", num_mentions, "mention tweets", duplicates, "duplicates");
                sys.stdout.flush()
                                    
            if tweet['place']['place_type'] not in ['admin', 'country']:
                co = tweet['place']['bounding_box']['coordinates'][0];
                poly = box(co[0][0], co[0][1], co[2][0], co[2][1]);
                if target.intersects(poly):
                    
                    if tweet["id_str"] not in tweet_ids:
                        
                        text = clean_text(tweet);
                        pol = get_polarity(text);    
                        output_file.write( 
                            str( [text, tweet['place']['full_name'], co, tweet['user']['screen_name'], tweet['user']['id'], 
                            pol,
                            mentions ] ) + "\n" );            

                            
                        num_place_use += 1
                        
                        tweet_ids.add( tweet["id_str"] );
                        
                    else:
                        duplicates += 1
            
        #if(num_tweets > 10000): break;    
output_file.close();
        
#with open(statsfilename, 'w') as ofile:
print( str(num_tweets) + " tweets" );
print( str(num_mentions) + " tweets that mention others" );
print( str(num_place) + " tweets with place tags" );
print( str(num_place_use) + " tweets with mentions originating in target" );
print( str(duplicates) + " duplicate tweets" );

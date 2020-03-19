##extract only those tweets which are replies or mentions
##text, tweet['place']['full_name'], co-ordinate, tweet['user']['screen_name'], tweet['user']['id'], pol, mentions
##mentions = [ (user_id, user_name), ... ]
								
import sys
import re
import os
import json

from shapely.geometry import box

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
    

def extract_mentions(infilename, outfilename, target, stats_file=None):
	    
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

	with open(infilename, 'r') as data_file:
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
				if 'place' not in tweet.keys(): continue;
				num_tweets += 1;
				if tweet['place'] == None: continue;
				num_place += 1;
					

				mentions = get_mentions( tweet );
				if len(mentions) == 0: continue;
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
				
	output_file.close();
	
	print("###extract.py",file=stats_file)		
	print( str(num_tweets) + " tweets",file=stats_file );
	print( str(num_mentions) + " tweets that mention others",file=stats_file );
	print( str(num_place) + " tweets with place tags",file=stats_file );
	print( str(num_place_use) + " tweets with mentions originating in target",file=stats_file );
	print( str(duplicates) + " duplicate tweets",file=stats_file );

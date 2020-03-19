import sys
import ast
import json
import csv
from collections import Counter
from setup_target import *
from find_communities import make_graph
import networkx as nx


def generate_nodeinfo(boxfilename, indexfilename, confilename, tweetcountfilename, outfilename, size=30, county=None):

	index_to_place = {}
	with open(indexfilename, 'r') as infile:
		for line in infile:
			index_to_place = json.loads(line);

	tweet_count = {}
	with open(tweetcountfilename, 'r') as infile:
		for line in infile:
			tweet_count = json.loads(line);
	
	total_tweets = 0
	box_to_totaltweets = Counter()
	for t in tweet_count:
		total_tweets += tweet_count[t];
		bx = ast.literal_eval(t);
		box_to_totaltweets[ bx[0]*size + bx[1] ] += tweet_count[t]
		
	print(total_tweets, "total tweets")
				
	##user -> box map
	box_to_user = Counter()
	box_to_tweet = Counter()

	G = make_graph(confilename)
	#sum_degrees = 0;
	for u in G: 
		#sum_degrees += G.degree(weight='weight')[u];
		box_to_tweet[  int(u)  ] = G.degree(weight='weight')[u];
	#print(sum_degrees, "sum degrees")
	
	num_users = 0;
	with open(boxfilename, 'r') as datafile:
		for x in datafile:
			words = ast.literal_eval(x);
			if len(words) < 2:
				print(x)
				sys.exit(1);
			if county:
				print("Not implemented"); sys.exit(1);		
			else:
				for w in words[1:]:
					num_users += 1;
					box_to_user[  w[0]*(size)+w[1]  ] += 1
	print(num_users, "num users")

	with open(outfilename, 'w') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for boxid in index_to_place: 
			N = 0; 
			if int(boxid) in box_to_user: 
				NU = box_to_user[ int(boxid) ];
				NT = box_to_tweet[ int(boxid) ];
				NTT = box_to_totaltweets[ int(boxid) ];
				A = flatten_poly_area(index_to_place[boxid], ptype='aea')
				x = 0.5*(index_to_place[boxid][0][0] + index_to_place[boxid][1][0])
				y = 0.5*(index_to_place[boxid][0][1] + index_to_place[boxid][1][1])
				csvwriter.writerow([ boxid, NU, NT, NTT, A , y, x ])
   


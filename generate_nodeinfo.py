import sys
import ast
import json
import csv
from collections import Counter
from setup_target import *

def generate_nodeinfo(boxfilename, indexfilename, outfilename, size=30, county=None):

	index_to_place = {}
	with open(indexfilename, 'r') as infile:
		for line in infile:
			index_to_place = json.loads(line);
	

	##user -> box map
	box_to_user = Counter()
	#bx_map = {}; bxc = 0
	with open(boxfilename, 'r') as datafile:
		for x in datafile:
			words = ast.literal_eval(x);
			bxs = [];
			if len(words) < 2:
				print(x)
				sys.exit(1);
			if county:
				print("Not implemented"); sys.exit(1);
				#user_boxes[ words[0] ] = words[1:]
				#for w in words[1:]: 
				#	if w not in bx_map:
				#		bx_map[w] = bxc;
				#		bxc += 1;			
			else:
				for w in words[1:]:
					box_to_user[  w[0]*(size)+w[1]  ] += 1

	with open(outfilename, 'w') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for boxid in index_to_place: 
			N = 0; 
			if int(boxid) in box_to_user: N = box_to_user[ int(boxid) ];
			x = 0.5*(index_to_place[boxid][0][0] + index_to_place[boxid][1][0])
			y = 0.5*(index_to_place[boxid][0][1] + index_to_place[boxid][1][1])
			csvwriter.writerow([ boxid, N, y, x ])
   


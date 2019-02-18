#locate users at their most common tweeting location. If multiple, report all
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

from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import box
from shapely.ops import cascaded_union

import numpy as np
from setup_target import *
from county_lookup import *

infilename = sys.argv[1];
outfilename = sys.argv[2];
dbfilename = sys.argv[3];


###############################################
##Ignore everything outside this bounding box##
###############################################
border=0;
simplify_tolerance=0

target = box(-125, 24.5, -67, 49.5);

xmin = target.bounds[0]-border; xmax = target.bounds[2]+border;
ymin = target.bounds[1]-border; ymax = target.bounds[3]+border;

target2, dims = get_target()

outfile = open(outfilename, 'w');

##############################
##Set up target polygon plot##
##############################
county = county_lookup(dbfilename);
county.load_all();
county_bounding_boxes = {};
for place in county.county_dict:
	c = MultiPolygon(county.county_dict[place])
	county_bounding_boxes[place] = box(c.bounds[0], c.bounds[1], c.bounds[2], c.bounds[3])


#check each user
num_users = 0;
num_usersi = 0;
num_points = 0;
num_boxes = 0;
num_isec = 0;
with open(infilename, 'r') as datafile:
	for x in datafile:
		num_users += 1;

		dt = ast.literal_eval(x);
		name = dt[0];
		locs = dt[1:];
		squares = {}

		for ll in locs:
			words = ast.literal_eval(ll[0])
			count = ll[1]

			#box boundaries
			if len(words) == 2:
				ll_xmin = words[0]; ll_xmax = words[0];
				ll_ymin = words[1]; ll_ymax = words[1];		
			else:		
				#ll_xmin = max(xmin, words[0][0]); ll_xmax = min( xmax, words[2][0] );
				ll_xmin = words[0][0]; ll_xmax = words[2][0];
				#ll_ymin = max(ymin, words[0][1]); ll_ymax = min( ymax, words[2][1] );
				ll_ymin = words[0][1]; ll_ymax = words[2][1];

			#make a polygon
			if ll_xmin == ll_xmax and ll_ymin == ll_ymax:
				mp = Point(ll_xmin, ll_ymin); 	##include sea points
			else:
				mp = box(ll_xmin, ll_ymin, ll_xmax, ll_ymax);


			#get the county
			place_list = []
			if mp.geom_type == "Point":
				num_points += 1
				for place in county.county_dict:
					found=False;
					for poly in county.county_dict[place]:
						if poly.contains(mp):
							found = True
							place_list.append(place);
							break;
					if found: break;		
			
			
			else:
				num_boxes += 1
				
				tmp_list = [];
				for place in county_bounding_boxes:
					if county_bounding_boxes[place].intersects(mp): ## faster to check boxes first
						tmp_list.append(place);
						
				for place in tmp_list:							##check shortlist
				#for place in county.county_dict:			
					for poly in county.county_dict[place]:
						if poly.intersects(mp):
							place_list.append(place);
				
			for p in place_list:
				if p in squares:
					squares[p] += count
				else:
					squares[p] = count

		if len(squares) == 0: continue;
			
		#output most likely square
		best = 0;
		out_squares = []			
		for s in sorted(squares, key = squares.get, reverse=True):
			if squares[s] >= best:
				best = squares[s]
				out_squares.append(s);
			else:
				break;
		if( len(out_squares) < 1 ):
			print("No box found")
			print(x)
			sys.exit(1);
		
		num_usersi += 1;	
		outfile.write( str( [name] + out_squares) + "\n" )	
		if num_users %100 == 0:
			print(num_users);			
outfile.close();


#with open(statsfilename, 'w') as ofile:
print( str(num_users) + " users" );
print( str(num_usersi) + " users included" );
print( str(num_points) + " point locations" );
print( str(num_boxes) + " box locations" );
print( str(num_isec) + " locations not contained in target" );
	

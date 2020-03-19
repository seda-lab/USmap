#locate users at their most common tweeting location. If multiple, report all
import sys
import ast
import json

from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import box
from shapely.ops import cascaded_union

from setup_target import *
import numpy as np
from collections import Counter;

def locate_users(infilename, outfilename, indexfilename, squaresfilename, target2, dims, size=30, county=None, stats_file=None):

	if not county:
		xmin = dims[0]; ymin = dims[1]; xmax = dims[2]; ymax = dims[3];
		grid_points_x = size
		grid_points_y = grid_points_x;
		xvals = np.linspace(xmin, xmax, grid_points_x+1); 
		yvals = np.linspace(ymin, ymax, grid_points_y+1);
		xstep = (xmax - xmin)/(grid_points_x);
		ystep = (ymax - ymin)/(grid_points_y);
		boxarea = xstep*ystep;
	else:
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
	num_tweets = 0;
	outfile = open(outfilename, 'w');

	tweet_count = Counter()
	with open(infilename, 'r') as datafile:
		for x in datafile:
			num_users += 1;
			
			dt = ast.literal_eval(x);
			name = dt[0];
			locs = dt[1:];
			squares = {}
			square_counts = {}
			
			nt = 0;
			for ll in locs:
				words = ast.literal_eval(ll[0])
				count = ll[1]
				num_tweets += count;
				nt += count;
				
				#box boundaries
				if len(words) == 2: #point
					ll_xmin = words[0]; ll_xmax = words[0];
					ll_ymin = words[1]; ll_ymax = words[1];		
				else:				#box
					ll_xmin = words[0][0]; ll_xmax = words[2][0];
					ll_ymin = words[0][1]; ll_ymax = words[2][1];

				#make a polygon
				if ll_xmin == ll_xmax and ll_ymin == ll_ymax:
					mp = Point(ll_xmin, ll_ymin); 	##include sea points
				else:
					mp = box(ll_xmin, ll_ymin, ll_xmax, ll_ymax);
				
				if not county:
		
					#get the poly bounds
					if mp.geom_type == "Point":
						num_points += 1
						idx_min = int( abs(ll_xmin - xmin)/(xstep) );
						idy_min = int( abs(ll_ymin - ymin)/(ystep) );
						idx_max = idx_min;
						idy_max = idy_min
					else:
						num_boxes += 1
						pxmin = mp.bounds[0]; pxmax = mp.bounds[2];
						pymin = mp.bounds[1]; pymax = mp.bounds[3];

						idx_min = int( abs(pxmin - xmin)/(xstep) );
						idy_min = int( abs(pymin - ymin)/(ystep) );
						idx_max = int( abs(pxmax - xmin)/(xstep) );
						idy_max = int( abs(pymax - ymin)/(ystep) );
						
						if idx_max >= size or idy_max >= size:
							if pxmax == xmax: idx_max = size-1;
							elif pymax == ymax: idy_max = size-1;
							elif pxmin == xmin: idx_min = 0;
							elif pymin == ymin: idy_min = 0;
							else:
								mp = target2.intersection(mp);
								pxmin = mp.bounds[0]; pxmax = mp.bounds[2];
								pymin = mp.bounds[1]; pymax = mp.bounds[3];

								idx_min = int( abs(pxmin - xmin)/(xstep) );
								idy_min = int( abs(pymin - ymin)/(ystep) );
								idx_max = int( abs(pxmax - xmin)/(xstep) );
								idy_max = int( abs(pymax - ymin)/(ystep) );
						

					snorm = 0;
					for i in range(idx_min, idx_max+1):
						for j in range(idy_min, idy_max+1):
							snorm += 1;
							if (i,j) in squares:
								squares[(i,j)] += count
							else:
								squares[(i,j)] = count
				
					for i in range(idx_min, idx_max+1):
						for j in range(idy_min, idy_max+1):
							if (i,j) in square_counts:
								square_counts[(i,j)] += count/snorm
							else:
								square_counts[(i,j)] = count/snorm
				
				else: #county plot
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
							for poly in county.county_dict[place]:
								if poly.intersects(mp):
									place_list.append(place);
					
					for p in place_list:
						if p in squares:
							squares[p] += count
						else:
							squares[p] = count
							
			if len(squares) == 0: continue;
			#compute tweet totals
			for s in squares: tweet_count[ str(s) ] += square_counts[s];
			
				
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
	
	checksum = sum(tweet_count.values())
	print("###locate_users.py",file=stats_file)		
	print( str(num_tweets) + " tweets",file=stats_file );
	print( str(checksum) + " check tweets",file=stats_file );
	print( str(num_users) + " users",file=stats_file );
	print( str(num_usersi) + " users included",file=stats_file );
	print( str(num_points) + " point locations",file=stats_file );
	print( str(num_boxes) + " box locations",file=stats_file );
	print( str(num_isec) + " locations not contained in target",file=stats_file );
		

	index_to_place = {}	
	if not county:
		for box_id, box_number, mp in generate_land(dims, target2, size, contains=False):
			index_to_place[ str(box_id) ] = ((mp.bounds[0],mp.bounds[1]),(mp.bounds[2],mp.bounds[3])); ##make it a string for later compatability with county
	else:
		print("not implemented");
		sys.exit(1);
		
	with open(indexfilename, 'w') as ofile:
		jsoned = json.dumps(index_to_place);
		ofile.write( jsoned )	

	with open(squaresfilename, 'w') as ofile:
		jsoned = json.dumps(tweet_count);
		ofile.write( jsoned )		



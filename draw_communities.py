#draw the map!
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
import ast
import copy
import importlib
import gc

from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import box
from shapely.ops import cascaded_union

import numpy as np
from proc_polystr import poly_to_coords

import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import matplotlib.cm as cm
import matplotlib as mpl

from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import box
from shapely.ops import cascaded_union

from matplotlib.patches import Polygon as pgn
from matplotlib.collections import PatchCollection




from setup_target import *
from figure_helper import *
from random_color import *
from county_lookup import *

import networkx as nx
import community
import itertools
from operator import itemgetter
from networkx.algorithms import community as cm

def draw_map(partition, output, poly_type, target_poly=None):

	infilename = partition
	outfilename = output
	dbfilename = "";
	try:
		size = int(poly_type);	
		#print("interpreting", poly_type, "as gridsize");
	except:
		dbfilename = poly_type;
		#print("interpreting", poly_type, "as polygon database");
		county = county_lookup(dbfilename);

	target, dims = get_target("United Kingdom")

	if target_poly:
		targetfilename = target_poly;
		target2, dims = get_place(targetfilename)
	else:
		target2, dims = get_target("United Kingdom")
	
		
	best_partition = {}
	if isinstance(infilename, str):
		with open(infilename, 'r') as infile:
			for line in infile:
				best_partition = json.loads(line);
	else:
		best_partition = infilename
		
	vmax = float(len(set(best_partition.values())))
	vmin = 0;

	
		
	############
	##plotting##
	############

	fig = plt.figure()
	ax = fig.add_subplot(111)
	setup_figure(ax, dims, target, zorder = 1)
	plt.axis("off")			

	
	##############
	##rectangles##
	##############
	cols = [ 'r', 'g', 'b', 'yellow', 'm', 'c', 'lightpink', 'saddlebrown', 'orange', 'olive', 'moccasin', 'chartreuse', 'violet', 'chocolate', 'teal', 'grey' ]

	if dbfilename == "":
		for box_id, box_number, mp in generate_land(dims, target2, size, contains=False):

			xmin, ymin, xmax, ymax = box_to_coords(mp)

			if str(box_id) in best_partition:
				pn = best_partition[ str(box_id) ];
				if pn < len(cols):
					col = cols[ pn ];
				else:
					col = get_random_color();

				##draw costal edges
				if target2.contains(mp):
					#patch = mpl.patches.Rectangle( (xmin, ymin) , (xmax-xmin), (ymax-ymin), edgecolor='none', facecolor=col, alpha=1, zorder=0  );
					patch = mpl.patches.Rectangle( (xmin, ymin) , (xmax-xmin), (ymax-ymin), edgecolor='k', facecolor=col, alpha=1, zorder=0  );
					ax.add_patch(patch)
				else:
					poly = target2.intersection(mp)
					polys = poly_to_coords(poly)
					for p in polys:
						
						#patch = pgn(p[0], edgecolor='none', facecolor=col, alpha=1, zorder=2  );
						patch = pgn(p[0], edgecolor='k', facecolor=col, alpha=1, zorder=2  );
						ax.add_patch(patch)
						
					
					#pols = poly_to_coords(poly)
					#for p in pols:
					#	patch = pgn(p, edgecolor='none', facecolor=col, alpha=1, zorder=0  );
					#	ax.add_patch(patch)
	else:
		for place in best_partition:
		
			pn = best_partition[place]
			if pn < len(cols):
				col = cols[ pn ];
			else:
				col = get_random_color();	
				
			mp = MultiPolygon(county.lookup(place));

			#pols = poly_to_coords(mp)
			#for p in pols:
			#	patch = pgn(p, edgecolor='none', facecolor=col, alpha=1, zorder=0  );
			#	ax.add_patch(patch)

			polys = poly_to_coords(mp)
			for p in polys:
				
				patch = pgn(p[0], edgecolor='none', facecolor=col, alpha=1, zorder=2  );
				ax.add_patch(patch)
				
				#draw interior
				for ip in p[1]:
					patch = pgn(ip, edgecolor='none', facecolor='white', alpha=1, zorder=1  );
					ax.add_patch(patch)
				
	plt.savefig(outfilename)	
	plt.close();
	

if __name__ == "__main__":
	if len(sys.argv) <= 4:
		draw_map(sys.argv[1], sys.argv[2], sys.argv[3]);
	else:
		draw_map(sys.argv[1], sys.argv[2], sys.argv[3], target_poly=sys.argv[4]);

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
from draw_communities import *

import networkx as nx
import community
import itertools
from operator import itemgetter
from networkx.algorithms import community as cm
import whereami

infilename = sys.argv[1]
outfilebase = sys.argv[2]
dbfilename = "";
try:
	size = int(sys.argv[3]);	
	print("interpreting", sys.argv[3], "as gridsize");
except:
	dbfilename = sys.argv[3];
	print("interpreting", sys.argv[3], "as polygon database");
	county = county_lookup(dbfilename);


if len(sys.argv) > 4:
	targetfilename = sys.argv[4];
	target2, dims = get_place(targetfilename)
else:
	target2, dims = get_target(whereami.meta_location)


best_partition = {}
with open(infilename, 'r') as infile:
	for line in infile:
		best_partition = json.loads(line);
		if "data" in best_partition:
			tmp = {}
			for k in best_partition["data"]: tmp[k] = best_partition["data"][k];
			for k in best_partition["extrap"]: tmp[k] = best_partition["extrap"][k];
			best_partition = tmp;
			
			
vmax = int(len(set(best_partition.values())))
vmin = 0;

com_polys = { i:[] for i in range(vmax) }	
com_boxes = { i:[] for i in range(vmax) }	

if dbfilename == "":

	for box_id, box_number, mp in generate_land(dims, target2, size, contains=False):
		if str(box_id) in best_partition:
			##draw costal edges
			if target2.contains(mp):
				com_polys[ best_partition[str(box_id)] ].append( mp.buffer(0.0001) );
			else:
				com_polys[ best_partition[str(box_id)] ].append( target2.intersection(mp).buffer(0.0001) )
			com_boxes[ best_partition[str(box_id)] ].append( str(box_id) );
	
else:
	for place in best_partition:
		
		mp = MultiPolygon(county.lookup(place));
		if target2.contains(mp):
			com_polys[ best_partition[place] ].append( mp.buffer(0.0001) );
		else:
			com_polys[ best_partition[place] ].append( target2.intersection(mp).buffer(0.0001) )
		com_boxes[ best_partition[place] ].append( place );
		
for i in range(vmax):
	
	if len(sys.argv) <= 4:
		draw_map({place:0 for place in com_boxes[i]}, outfilebase + str(i) , sys.argv[3]);
	else:
		draw_map({place:0 for place in com_boxes[i]}, outfilebase + str(i) , sys.argv[3], target_poly=sys.argv[4]);


	poly = cascaded_union( com_polys[i] );
	with open(outfilebase  + str(i) + ".txt", 'w') as outfile:
		
		if poly.geom_type == "Polygon":
			lons, lats = poly.exterior.coords.xy
			x,y=(lons, lats);
			exterior=list(zip(x,y))
			interior = []
			for p in poly.interiors:
				lons, lats = p.coords.xy;
				x,y=(lons, lats);
				interior.append( list(zip(x,y)) )
			print([ exterior, interior ],file=outfile)
			
			
		if poly.geom_type == "MultiPolygon":
			for p in poly:
				lons, lats = p.exterior.coords.xy
				x,y=(lons, lats);
				exterior=list(zip(x,y))
				interior = []
				for ip in p.interiors:
					lons, lats = ip.coords.xy;
					x,y=(lons, lats);
					interior.append( list(zip(x,y)) )
				print([ exterior, interior ],file=outfile)

	

	

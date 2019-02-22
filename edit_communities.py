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

import networkx as nx
import community
import itertools
from operator import itemgetter
from networkx.algorithms import community as cm
import random

def heaviest(G):
	u, v, w = max(G.edges(data='weight'), key=itemgetter(2))
	return (u, v)
 
G=nx.Graph()
	
partfilename = sys.argv[1];
outfilename = sys.argv[2];
dbfilename = "";
size = 0
try:
	size = int(sys.argv[3]);	
	print("interpreting", sys.argv[3], "as gridsize");
except:
	dbfilename = sys.argv[3];
	print("interpreting", sys.argv[3], "as polygon database");
	county = county_lookup(dbfilename);
	county.load_all();
	for p in county.county_dict:
		county.county_dict[p] = cascaded_union(MultiPolygon(county.county_dict[p])).buffer(0.001);

if len(sys.argv) > 4:
	targetfilename = sys.argv[4];
	target2, dims = get_place(targetfilename)
else:
	target2, dims = get_target("United States")		

		


best_partition = {}
with open(partfilename, 'r') as infile:
	for line in infile:
		best_partition = json.loads(line);

vmax = int(len(set(best_partition.values())))
vmin = 0;
		

neighbours = {}
if dbfilename == "":

	for box_id, box_number, mp in generate_land(dims, target2, size, contains=False):
		#if str(box_id) in best_partition:			
		neighbours[ str(box_id) ] = [];
		i, j = box_id_to_ij(box_id, size)
		for h in range(-1,2):
			for v in range(-1,2):
				if h == 0 and v == 0: continue;
				nbr_id = ij_to_box_id(i+h,j+v,size)
				#if str(nbr_id) in best_partition:
				neighbours[ str(box_id) ].append( str(nbr_id) );

else:
	
	for place in best_partition:
		neighbours[ place ] = [];
		mp = county.county_dict[place];
		for p in county.county_dict:
			if p!=place and mp.intersects(county.county_dict[p]):
				neighbours[ place ].append(p);
				

if dbfilename == "":

	###Add empty space to community
	print("Adding empty space")

	for box_id, box_number, mp in generate_land(dims, target2, size, contains=False):
		if str(box_id) not in best_partition:
			nbr_com = {}
			for nbr in neighbours[ str(box_id) ]:
				if nbr in best_partition:
					if best_partition[ nbr ] in nbr_com:
						nbr_com[ best_partition[ nbr ] ] += 1
					else:
						nbr_com[ best_partition[ nbr ] ] = 1
			if len(nbr_com) > 0:
				best_partition[str(box_id)] = max(nbr_com, key=nbr_com.get);	
			else:
				best_partition[str(box_id)] = random.randint(0,vmax-1);	


	##get largest cpt
	com_polys = { i:[] for i in range(vmax) }	
	com_boxes = { i:[] for i in range(vmax) }	

	for box_id, box_number, mp in generate_land(dims, target2, size, contains=False):
		if True: #str(box_id) in best_partition:
			##draw costal edges
			if target2.contains(mp):
				com_polys[ best_partition[str(box_id)] ].append( mp.buffer(0.0001) );
			else:
				com_polys[ best_partition[str(box_id)] ].append( target2.intersection(mp).buffer(0.0001) )
			com_boxes[ best_partition[str(box_id)] ].append( str(box_id) );
	
	##find the boxes not connected to the largest component
	skipped_boxes = []
	for i in range(vmax):
		poly = cascaded_union( com_polys[i] );
		if poly.geom_type == "MultiPolygon":
			poly = max(poly, key=lambda x: x.area)
		
		for b in range( len(com_boxes[ i ]) ):
			if not poly.intersects( com_polys[i][b] ):
				skipped_boxes.append( com_boxes[ i ][ b ] )

				
	##reassign orphan boxes
	cit = 0;
	change = True;
	while change:
		cit += 1;
		print("reassign orphans", cit);
		change = False;
		for box_id in skipped_boxes:

			nbr_com = {};
			for nbr in neighbours[ box_id ]:
				if nbr in best_partition:
					if best_partition[ nbr ] in nbr_com:
						nbr_com[ best_partition[ nbr ] ] += 1
					else:
						nbr_com[ best_partition[ nbr ] ] = 1

			#print( best_partition[box_id], nbr_com)
			#print(best_partition[box_id], ":", box_id, nbr_com, neighbours[ box_id ])
			if len(nbr_com) > 0:
				old_com = best_partition[box_id];
				best_partition[box_id] = max(nbr_com, key=nbr_com.get);	
				if old_com != best_partition[box_id]:
					change = True;


with open(outfilename, 'w') as ofile:
	jsoned = json.dumps(best_partition);
	ofile.write( jsoned )	


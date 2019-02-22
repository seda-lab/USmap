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

def heaviest(G):
	u, v, w = max(G.edges(data='weight'), key=itemgetter(2))
	return (u, v)
 
G=nx.Graph()
	
confilename = sys.argv[1];
partfilename = sys.argv[2];
outfilename = sys.argv[3];
dbfilename = "";
size = 0
try:
	size = int(sys.argv[4]);	
	print("interpreting", sys.argv[4], "as gridsize");
except:
	dbfilename = sys.argv[4];
	print("interpreting", sys.argv[4], "as polygon database");
	county = county_lookup(dbfilename);
	county.load_all();
	for p in county.county_dict:
		county.county_dict[p] = cascaded_union(MultiPolygon(county.county_dict[p])).buffer(0.001);

if len(sys.argv) > 5:
	targetfilename = sys.argv[5];
	target2, dims = get_place(targetfilename)
else:
	target2, dims = get_target("United States")		

		
connections = {}
with open(confilename, 'r') as infile:
	for line in infile:
		connections = json.loads(line);

best_partition = {}
with open(partfilename, 'r') as infile:
	for line in infile:
		best_partition = json.loads(line);

vmax = int(len(set(best_partition.values())))
vmin = 0;
		

################
##set up graph##
################
min_self = 0
min_connection = 0;

for i in connections: 

	##eliminate nodes with no self connections (usually sparsely populated)
	if (i not in connections[i]) or (connections[i][i] <= min_self): continue;

	for j in connections[i]:
		if j != i:
			if not G.has_edge(i,j): #symmetric

				##don't join to eliminated nodes
				if (j not in connections) or (j not in connections[j]) or (connections[j][j] <= min_self): continue;
				ew = connections[i][j];
				if (j in connections) and (i in connections[j]):
					ew += connections[j][i]
				if ew <= min_connection: continue;	
						
				G.add_edge( i, j, weight = ew )

solitary=[ n for n,d in G.degree if d==0 ] #should be 0
G.remove_nodes_from(solitary)


mod = community.modularity(best_partition, G);
best_mod = mod;
print("modularity = ", best_mod);

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
				if str(nbr_id) in best_partition:
					neighbours[ str(box_id) ].append( str(nbr_id) );

else:
	
	for place in best_partition:
		neighbours[ place ] = [];
		mp = county.county_dict[place];
		for p in county.county_dict:
			if p!=place and mp.intersects(county.county_dict[p]):
				neighbours[ place ].append(p);
				


change = True;
cit = 0;
while change:	
	cit += 1;
	print("refine iteration", cit);	
	change = False;		
	for box_id in neighbours:
		if box_id in best_partition:
			com = best_partition[box_id];
			surrounded = 0;
			nbr_com = {};
			for nbr in neighbours[ box_id ]:
				if com != best_partition[ nbr ]:
					surrounded += 1;
					if best_partition[ nbr ] in nbr_com:
						nbr_com[ best_partition[ nbr ] ] += 1
					else:
						nbr_com[ best_partition[ nbr ] ] = 1

			if surrounded > 0: #== len(neighbours[ box_id ]):
				##print(surrounded, box_id_to_ij(box_id, size), nbr_com, best_partition[box_id], "change to", max(nbr_com))
				##try to change community
				old_com = best_partition[box_id];
				for new_com in sorted(nbr_com):
					best_partition[box_id] = new_com;
					mod = community.modularity(best_partition, G);
					if mod >= best_mod:
						best_mod = mod;
						change = True;
						print("new mod", best_mod);
						break;
					else:
						best_partition[box_id] = old_com;

	
with open(outfilename, 'w') as ofile:
	jsoned = json.dumps(best_partition);
	ofile.write( jsoned )	


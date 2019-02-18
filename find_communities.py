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
outfilename = sys.argv[2];
indfilename = sys.argv[3];
#statsfilename = sys.argv[4];
#size = int(sys.argv[4])
palg = "louvain"
res = 1; #float(sys.argv[7])

"""
connections = {}
with open(confilename, 'r') as infile:
	for line in infile:
		connections = ast.literal_eval(line);
connections = np.array(connections);
sizex, sizey = connections.shape
print("sizes of connections = ", connections.shape)
"""
connections = {}
with open(confilename, 'r') as infile:
	for line in infile:
		connections = json.loads(line);

		
target2, dims = get_target()


################
##set up graph##
################
min_self = 0
min_connection = 0;

for i in connections: 

	##eliminate nodes with no self connections (usually sparsely populated)
	#if (i not in connections[i]) or (connections[i][i] <= min_self): continue;

	for j in connections[i]:
		if j != i:
			if not G.has_edge(i,j): #symmetric

				##don't join to eliminated nodes
				#if (j not in connections) or (j not in connections[j][j]) or (connections[j][j] <= min_self): continue;
				ew = connections[i][j];
				if (j in connections) and (i in connections[j]):
					ew += connections[j][i]
				if ew <= min_connection: continue;	
						
				G.add_edge( i, j, weight = ew )

print("size of constructed graph = ", len(G.edges))

        
solitary=[ n for n,d in G.degree if d==0 ] #should be 0
G.remove_nodes_from(solitary)
print(len(G.edges), "edges", len(G.nodes), "nodes", len(solitary), "solitary nodes")


max_mod = -np.inf
best_partition = {}
Nr = 1;
if palg == "louvain" or palg == "async":
	Nr = 100;
for i in range(Nr):
	importlib.reload(community)
	if palg == "louvain":
		partition = community.best_partition(G, randomize=True, resolution=res)
	elif palg == "async":
		part = cm.asyn_lpa_communities(G, weight='weight')
		partition = {};
		lab = 0;
		for p in part:
			for n in p:
				partition[n] = lab;
			lab += 1;
	elif palg == "kl":
		p2 = cm.kernighan_lin_bisection(G);
		partition = {};
		for i,p in enumerate(p2):
			for b in p:
				partition[b] = i;
	else:
		print("Not implemented", palg);
		sys.exit(1);

	gc.collect()
	mod = community.modularity(partition, G);
	if mod > max_mod:
		max_mod = mod;
		best_partition = copy.deepcopy(partition);
		
	print(100-i, mod, max_mod)
	#sys.exit(1);
	
vmax = float(len(set(best_partition.values())))
vmin = 0;

#with open(statsfilename, 'w') as ofile:
print( str(vmax) + "communities" );
print( str( max_mod ) +" best modularity" );
print( str(len(G.edges)) +  " edges")
print( str(len(G.nodes)) +  " nodes")
print( "density " + str(len(G.edges)/( 0.5*(len(G.nodes)-1)*len(G.nodes))) )
print( "mean degree " + str(1.0*sum([ d for n,d in G.degree ])/len(G.nodes)) )
print( "mean weighted degree " + str(1.0*sum([ d for n,d in G.degree(weight="weight") ])/len(G.nodes)) )

with open(outfilename, 'w') as ofile:
	jsoned = json.dumps(best_partition);
	ofile.write( jsoned )	

iG = community.induced_graph(best_partition, G, weight='weight')

iconnections = {}
for u, v, w in iG.edges(data='weight'):
	if u in iconnections:
		iconnections[u][v] = w;
	else:
		iconnections[u] = { v : w }
	
with open(indfilename, 'w') as ofile:
	jsoned = json.dumps(iconnections);
	ofile.write( jsoned )		
	

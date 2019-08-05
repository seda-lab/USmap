import csv
import numpy as np
from collections import Counter
import sys
import math
from geopy import distance
from find_communities import make_graph
import networkx as nx
import json

def myround(x, b=5):
    return b * round(x/b)


def construct_null(csvfilename, confilename, nullfilename, labelfilename, graphfilename, base=5):

	##read the graph (using original labels)
	G = make_graph(confilename)
    
    ##read the node info  (using original labels)
	node_info = {}
	with open(csvfilename, 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in spamreader:
			if row[0] in G.nodes():
				node_info[ row[0] ] = {"N":float(row[1]), "coord":np.array([float(row[2]), float(row[3])]) }		

	##relabel the nodes
	ordered_nodes = sorted([int(k) for k in node_info])
	labels = {  l:i for i, l in enumerate(ordered_nodes)  };
	nodemap = {  i:l for i, l in enumerate(ordered_nodes)  };

	##output the graph in gen-louvain format
	with open(graphfilename, 'w') as outfile:
		for i,u in enumerate(ordered_nodes):
			for j,v in enumerate(ordered_nodes[i:]):
				if G.has_edge(str(u), str(v)):
					outfile.write("{} {} {}\n".format(labels[u], labels[v], G[str(u)][str(v)]["weight"]) )
				#else:
				#	outfile.write("{} {} {}\n".format(labels[u], labels[v], 0) )

	##output the label map
	with open(labelfilename, 'w') as outfile:	
		jsoned = json.dumps(nodemap);
		outfile.write( jsoned )	
						
	d = {}
	allowed_d = set();
	for i in ordered_nodes:	
		print("Calculating distaces from", i) 
		d[ labels[i] ] = {}
		for j in ordered_nodes:
			d_ij = myround( distance.distance(node_info[str(i)]["coord"] , node_info[str(j)]["coord"]).km, base )
			d[ labels[i] ][ labels[j] ] = d_ij;
			allowed_d.add(d_ij)


	##The distance function
	f = Counter();
	norm = Counter();
	for dist in allowed_d: #so f has a value for every d
		f[dist] = 0;
		norm[dist] = 0;

	for i in ordered_nodes:
		for j in ordered_nodes:
			if G.has_edge( str(i), str(j) ):
				f[ d[ labels[i] ][ labels[j] ] ] += G[str(i)][str(j)]["weight"]
			norm[ d[ labels[i] ][ labels[j] ] ] += node_info[str(i)]["N"] * node_info[str(j)]["N"]
	for key in f:
		f[key] /= norm[key]
	
	with open(nullfilename, 'w') as outfile:
		for i,u in enumerate(ordered_nodes):
			for j,v in enumerate(ordered_nodes[i:]):
				outfile.write("{} {} {}\n".format(labels[u],labels[v],  node_info[str(u)]["N"] * node_info[str(v)]["N"] * f[ d[ labels[u] ][ labels[v] ] ]) )





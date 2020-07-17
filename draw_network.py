#draw the map!
import sys
import json
from find_communities import make_graph
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import networkx as nx

from figure_helper import *
from setup_target import *
from random_color import *

def heaviest(G):
	u, v, w = max(G.edges(data='weight'), key=itemgetter(2))
	return (u, v)

	
def draw_network(confilename, partfilename, outfilename, dims, target2, gparams, size, gadm, county, place):
	
	max_node = gparams['max_node']
	node_factor = gparams['node_factor']
	min_self = gparams['min_self']
	min_connection = gparams['min_connection']
	edge_w = gparams['edge_w']
	
	connections = {}
	with open(confilename, 'r') as infile:
		for line in infile:
			connections = json.loads(line);
			
	G = make_graph(confilename, min_self=min_self, min_connection=min_connection, use_self=True)
	partition = {}
	with open(partfilename, 'r') as infile:
		for line in infile:
			partition = json.loads(line);
	vmax = int(len(set(partition.values())))
	vmin = 0;	
	
	#print(len(G.nodes), "nodes in G");
	#print( "mean degree " + str(1.0*sum([ d for n,d in G.degree ])/len(G.nodes)) )
	#print( "mean weighted degree " + str(1.0*sum([ d for n,d in G.degree(weight="weight") ])/len(G.nodes)) )
	#print( str(len(G.edges)) +  " edges " + str(len(G.nodes)) +  " nodes")
	#print( "density " + str(len(G.edges)/( 0.5*(len(G.nodes)-1)*len(G.nodes))))


	emap = cm.binary
	ews = [ G[u][v]['weight'] for u,v in G.edges()]
	sedges = sorted(ews)
	max_edge = sedges[-1]
	min_edge = sedges[0];

	cols = [ 'r', 'g', 'b', 'yellow', 'm', 'c', 'lightpink', 'saddlebrown', 'orange', 'grey', 'k'] 


	fig = plt.figure(figsize=(12, 12))
	ax = fig.add_subplot(111)
	setup_figure(ax, dims, target2, zorder=1, place=place, gadm=gadm)
	plt.axis("off")	
	
	node_size = [];
	node_list = [];
	edge_list = [];
	node_color = [];
	pos = {}

	for box_id, box_number, mp in generate_land(dims, target2, size, contains=False):

		if str(box_id) in partition and str(box_id) in G.nodes:
			
			xmin, ymin, xmax, ymax = box_to_coords(mp)
			if target2.intersects(mp):
				pos[str(box_id)] = np.array([ 0.5*(xmin+xmax), 0.5*(ymin+ymax)])

				n = str(box_id);
				node_list.append(n)
				if n in G:
					if n in G[n]:
						node_size.append( min( max_node, node_factor*(G[n][n]['weight']) ) );
					else:
						node_size.append(0);
				else:
					node_size.append(0);

				node_color.append( cols[ partition[ str(n) ] % len(cols) ]  );

	for n in node_list:
		for j in G[n]:
			if j in node_list:
				edge_list.append( (n, j) )


	nx.draw_networkx_edges(G, pos, width=edge_w, edgelist=edge_list)
	nx.draw_networkx_nodes(G, pos, nodelist=node_list, node_size=node_size, node_color=node_color)

	plt.savefig(outfilename);
	plt.close();



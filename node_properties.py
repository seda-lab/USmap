import sys
import json
from find_communities import make_graph
import networkx as nx

property_names = set([
"degree", "degreecentrality", "betweennesscentrality"
])

if len(sys.argv) < 3:
	print("Usage: python3 node_properties.py confilename property")
	print("property is one of", property_names)
	sys.exit(1);
	
confilename = sys.argv[1]
prop = sys.argv[2];
if prop not in property_names:
	print(prop, "not in", property_names)
	sys.exit(1);
	
G = make_graph(confilename)
if prop == "degree":
	for n in G:
		print( n, G.degree[n] )
if prop == "degreecentrality":
	dc = nx.degree_centrality(G)
	for n in dc:
		print(n, dc[n])
if prop == "betweennesscentrality":
	dc = nx.betweenness_centrality(G, weight="weight")
	for n in dc:
		print(n, dc[n])


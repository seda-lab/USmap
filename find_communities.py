import sys
import json
import copy
import importlib
import gc
import networkx as nx
import community
from networkx.algorithms import community as cm
import numpy as np

from setup_target import *

def make_graph(confilename, min_self=0, min_connection=0):
	
	G=nx.Graph()

	connections = {}
	with open(confilename, 'r') as infile:
		for line in infile:
			connections = json.loads(line);
			
	################
	##set up graph##
	################
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
	
	return G;
	
def find_communities(confilename, outfilename, palg="louvain", res=1):
	
	G = make_graph(confilename)

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
			
		print(100-i, mod, int(len(set(partition.values()))), max_mod, int(len(set(best_partition.values()))))
		
	vmax = float(len(set(best_partition.values())))
	vmin = 0;

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



def get_neighbours( best_partition,  dims, target2, size, county):
	
	neighbours = {}
	if not county:

		#find box neighbours
		for box_id, box_number, mp in generate_land(dims, target2, size, contains=False):

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
					
	return neighbours;

	
def refine_communities(confilename, partfilename, outfilename, dims, target2, size=30, county=None):
	
	G = make_graph(confilename)
	best_partition = {}
	with open(partfilename, 'r') as infile:
		for line in infile:
			best_partition = json.loads(line);
	vmax = int(len(set(best_partition.values())))
	vmin = 0;	


	mod = community.modularity(best_partition, G);
	best_mod = mod;
	print("modularity = ", best_mod);

	neighbours = get_neighbours( best_partition, dims, target2, size, county);
	
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

				if surrounded > 0: 
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


def edit_communities(confilename, partfilename, outfilename, nbrs, dims, target2, size=30, county=None):
	
	G = make_graph(confilename)
	best_partition = {}
	with open(partfilename, 'r') as infile:
		for line in infile:
			best_partition = json.loads(line);
	vmax = int(len(set(best_partition.values())))
	vmin = 0;	

	neighbours = get_neighbours( best_partition, dims, target2, size, county);

					

	if not county:

		###Add empty space to community map
		print("Adding empty space")

		fill_boxes = {}
		swapped_boxes = {}
		for box_id, box_number, mp in generate_land(dims, target2, size, contains=False):
			if str(box_id) not in best_partition:
				nbr_com = {}
				nnb = 0;
				for nbr in neighbours[ str(box_id) ]:
					if nbr in best_partition:
						nnb += 1;
						if best_partition[ nbr ] in nbr_com:
							nbr_com[ best_partition[ nbr ] ] += 1
						else:
							nbr_com[ best_partition[ nbr ] ] = 1
							
				if nnb > nbrs:
					fill_boxes[str(box_id)] = max(nbr_com, key=nbr_com.get);	
				elif nbrs == 0:
					fill_boxes[str(box_id)] = random.randint(0,vmax-1);	

		##get largest cpt
		com_polys = { i:[] for i in range(vmax) }	
		com_boxes = { i:[] for i in range(vmax) }	

		for box_id, box_number, mp in generate_land(dims, target2, size, contains=False):

			cid = None;
			if str(box_id) in best_partition: cid = best_partition[str(box_id)];
			if str(box_id) in fill_boxes: cid = fill_boxes[str(box_id)];
			
			if cid is not None:
				##draw costal edges
				if target2.contains(mp):
					com_polys[ cid ].append( mp.buffer(0.0001) );
				else:
					com_polys[ cid ].append( target2.intersection(mp).buffer(0.0001) )
				com_boxes[ cid ].append( str(box_id) );
		
		
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
					cid = None;
					if nbr in best_partition: cid = best_partition[ nbr ];
					if nbr in fill_boxes: cid = fill_boxes[ nbr ];
					
					if cid is not None:
						if cid in nbr_com:
							nbr_com[ cid ] += 1
						else:
							nbr_com[ cid ] = 1


				if len(nbr_com) > 0:
					
					if box_id in best_partition: 
						old_com = best_partition[ box_id ];
						best_partition[box_id] = max(nbr_com, key=nbr_com.get);	
						if old_com != best_partition[box_id]:
							swapped_boxes[ box_id ] = best_partition[box_id];
							change = True;
							
					if box_id in fill_boxes: 
						old_com = fill_boxes[ box_id ];
						fill_boxes[box_id] = max(nbr_com, key=nbr_com.get);	
						if old_com != fill_boxes[box_id]:
							change = True;
					

	for b in swapped_boxes:
		del best_partition[b];
		
	with open(outfilename, 'w') as ofile:
		total = { "data":best_partition, "extrap":fill_boxes, "swap":swapped_boxes };
		jsoned = json.dumps(total);
		ofile.write( jsoned )	
	

	
"""
	##Plot induced graph
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
"""	

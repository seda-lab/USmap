#draw the map!
import sys
import json

import numpy as np
from proc_polystr import poly_to_coords

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as pgn

from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import box
from shapely.ops import cascaded_union


from setup_target import *
from figure_helper import *
from draw_communities import draw_map
from find_communities import get_neighbours

def is_isolate(neighbours, best_partition, box_id, nbrs=8):
	com = best_partition[box_id];
	surrounded = 0;
	for nbr in neighbours[ box_id ]:
		if (nbr in best_partition) and (com != best_partition[ nbr ]):
			surrounded += 1;
	return (surrounded >= nbrs);
	
def map_communities(infilename, outfilebase, dims, target2, size=30, county=None, drop_isolates=False, use_largest=False):

	best_partition = {}
	with open(infilename, 'r') as infile:
		for line in infile:
			best_partition = json.loads(line);
			if "data" in best_partition:
				tmp = {}
				for k in best_partition["data"]: tmp[k] = best_partition["data"][k];
				for k in best_partition["extrap"]: tmp[k] = best_partition["extrap"][k];
				for k in best_partition["swap"]: tmp[k] = best_partition["swap"][k];
				best_partition = tmp;
				
				
	vmax = int(len(set(best_partition.values())))
	vmin = 0;

	com_polys = { i:[] for i in range(vmax) }	
	com_boxes = { i:[] for i in range(vmax) }	

	if drop_isolates:
		neighbours = get_neighbours(best_partition,  dims, target2, size, county);
		
	if not county:

		for box_id, box_number, mp in generate_land(dims, target2, size, contains=False):
			if str(box_id) in best_partition:
				if (not drop_isolates) or (drop_isolates and not is_isolate(neighbours, best_partition, str(box_id))):
								
					##draw costal edges
					if target2.contains(mp):
						com_polys[ best_partition[str(box_id)] ].append( mp.buffer(0.0001) );
					else:
						com_polys[ best_partition[str(box_id)] ].append( target2.intersection(mp).buffer(0.0001) )
					com_boxes[ best_partition[str(box_id)] ].append( str(box_id) );
		
	else:
		for place in best_partition:
			if (not drop_isolates) or (drop_isolates and not is_isolate(neighbours, best_partition, place)):
				mp = MultiPolygon(county.lookup(place));
				if target2.contains(mp):
					com_polys[ best_partition[place] ].append( mp.buffer(0.0001) );
				else:
					com_polys[ best_partition[place] ].append( target2.intersection(mp).buffer(0.0001) )
				com_boxes[ best_partition[place] ].append( place );
	
			
				
	for i in range(vmax):
		if use_largest:
			poly = cascaded_union( com_polys[i] );
			if poly.geom_type == "MultiPolygon":
				poly = max(poly, key=lambda x: x.area)
			
			tmp_polys = []
			tmp_boxes = []
			for b in range( len(com_polys[ i ]) ):
				if poly.intersects( com_polys[i][b] ):
					tmp_boxes.append( com_boxes[ i ][ b ] )
					tmp_polys.append( com_polys[ i ][ b ] )
			
			com_polys[i] = tmp_polys;
			com_boxes[i] = tmp_boxes;
			
		draw_map({place:0 for place in com_boxes[i]}, outfilebase + str(i) + ".png", dims, target2, size=size, county=county)

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

	

	

#draw the map!
import sys
import json
from collections import Counter;

from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import box
from shapely.ops import cascaded_union

import numpy as np
from proc_polystr import poly_to_coords

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as pgn
from matplotlib.patches import Rectangle 

from figure_helper import *
from setup_target import *
from random_color import *

def read_partition(infilename, edited):

	best_partition = {};
	if isinstance(infilename, str):
		if not edited:
			best_partition['data'] = {};
			with open(infilename, 'r') as infile:
				for line in infile:
					best_partition['data'] = json.loads(line);
		else:
			with open(infilename, 'r') as infile:
				for line in infile:
					best_partition = json.loads(line);
	else:
		best_partition['data'] = infilename;
	
	return best_partition;	
	
def draw_map(infilename, outfigname, dims, target2, size=30, county=None, gadm=None, place='none', edited=False):

	best_partition = read_partition(infilename, edited);
	vmax = float(len(set(best_partition["data"].values())))
	vmin = 0;
	partition_alpha = { "data":1.0, "extrap":0.75, "swap":0.75}
	partition_edge = { "data":"none", "extrap":'k', "swap":'k' }
	partition_z = { "data":0, "extrap":5, "swap":5 }
	
	############
	##plotting##
	############
	fig = plt.figure()
	ax = fig.add_subplot(111)
	setup_figure(ax, dims, target2, zorder=1, place=place, gadm=gadm)
	plt.axis("off")			

	##############
	##rectangles##
	##############
	cols = [ 'r', 'g', 'b', 'yellow', 'm', 'c', 'lightpink', 'saddlebrown', 'orange', 'grey', 'k'] 
	#, 'olive', 'moccasin', 'chartreuse', 'violet', 'chocolate', 'teal',  ]
	partition_sizes = Counter();
	for node in best_partition["data"]:
		partition_sizes[ best_partition["data"][node] ] += 1;
	colour_map = {}
	for i,comm in enumerate( partition_sizes.most_common() ):
		if comm[1] < 20:
			colour_map[comm[0]] = 'k';
		else:
			if i < len(cols):
				colour_map[comm[0]] = cols[i];
			else:
				colour_map[comm[0]] = get_random_color(pastel_factor = 1);
			
	print(partition_sizes.most_common())
	print(colour_map)

	if not county:
		
		for box_id, box_number, mp in generate_land(dims, target2, size, contains=False):

			xmin, ymin, xmax, ymax = box_to_coords(mp)
			for k in best_partition:
	
				if str(box_id) in best_partition[k]:
					pn = best_partition[k][ str(box_id) ];
					col = colour_map[pn]

					##draw costal edges
					if target2.contains(mp):
						patch = Rectangle( (xmin, ymin) , (xmax-xmin), (ymax-ymin), edgecolor=partition_edge[k], facecolor=col, alpha=partition_alpha[k], zorder=0+partition_z[k]);
						ax.add_patch(patch)
					else:
						poly = target2.intersection(mp)
						polys = poly_to_coords(poly)
						for p in polys:
							
							patch = pgn(p[0], edgecolor=partition_edge[k], facecolor=col, alpha=partition_alpha[k], zorder=2+partition_z[k]  );
							ax.add_patch(patch)

	else:
		for k in best_partition:
			for place in best_partition[k]:
			
				pn = best_partition[k][place]
				if pn < len(cols):
					col = cols[ pn ];
				else:
					col = get_random_color();	
					
				mp = MultiPolygon(county.lookup(place));

				polys = poly_to_coords(mp)
				for p in polys:
					
					patch = pgn(p[0], edgecolor=partition_edge[k], facecolor=col, alpha=partition_alpha[k], zorder=2+partition_z[k]  );
					ax.add_patch(patch)
					
					#draw interior
					for ip in p[1]:
						patch = pgn(ip, edgecolor=partition_edge[k], facecolor='white', alpha=partition_alpha[k], zorder=1+partition_z[k]  );
						ax.add_patch(patch)
					
	plt.savefig(outfigname)	
	plt.close();
	

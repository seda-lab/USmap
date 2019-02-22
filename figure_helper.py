from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import box
from shapely.ops import cascaded_union

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Polygon as pgn
from matplotlib.patches import Rectangle as rect
from matplotlib.collections import PatchCollection
from matplotlib.collections import PolyCollection

import numpy as np
from proc_polystr import *
from setup_target import *

def simple_poly_to_coords(poly):

	pols = [];
	if poly.geom_type == "Polygon":
		lons, lats = poly.exterior.coords.xy
		x,y=(lons, lats);
		pols.append( list(zip(x,y)) )
		
	if poly.geom_type == "MultiPolygon":
		for p in poly:
			lons, lats = p.exterior.coords.xy
			x,y=(lons, lats);
			pols.append( list(zip(x,y)) )
				
	return pols;
					
def setup_figure(ax, dims, target2, zorder, regions=None):

	ax.set_xlim(dims[0], dims[2]);
	ax.set_ylim(dims[1], dims[3]);
	ax.set_xticklabels([])
	ax.set_yticklabels([])
	
	#pols, ipols = poly_to_coords( box(dims[0], dims[1], dims[2], dims[3]) ); 
	#coll = PolyCollection(pols,facecolors='none',zorder=zorder)
	#ax.add_collection(coll)
	#patch = rect( (dims[0], dims[1]) , (dims[2]-dims[0]), (dims[3]-dims[1]), edgecolor='k', facecolor='none', alpha=1, zorder=zorder  );
	#ax.add_patch(patch)

	if regions is not None:
		for r in regions:
			t = regions[r]
			pols = poly_to_coords(t); 
			coll = PolyCollection(pols,facecolors='none',zorder=zorder,alpha=0.25)
			ax.add_collection(coll)		
		
	if target2 is not None:
		#for t in target2:
			#pols = poly_to_coords(t); 
			#coll = PolyCollection(pols,facecolors='none',zorder=zorder,alpha=0.75)
			#ax.add_collection(coll)

		polys = poly_to_coords(target2);

		for p in polys:
			
			patch = pgn(p[0], edgecolor='black', facecolor='white', alpha=1, zorder=0  );
			ax.add_patch(patch)
			
			#draw interior
			for ip in p[1]:
				patch = pgn(ip, edgecolor='black', facecolor='white', alpha=1, zorder=1  );
				ax.add_patch(patch)



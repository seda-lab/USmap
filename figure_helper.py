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
		for t in target2:
			pols = poly_to_coords(t); 
			coll = PolyCollection(pols,facecolors='none',zorder=zorder,alpha=0.75)
			ax.add_collection(coll)


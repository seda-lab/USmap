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
import whereami

from gadm_lookup import *
gadm = gadm_lookup(whereami.gadm_location + "gadm.db");


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

	if whereami.meta_location == "United States+":
		states = ["Alabama", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
		regions = { s:max(gadm.lookup(s,level=1), key=lambda x: x.area) for s in states };
	
	elif whereami.meta_location == "London":
		boroughs = ["London","Westminster","Kensington and Chelsea","Hammersmith and Fulham","Wandsworth","Lambeth","Southwark","Tower Hamlets","Hackney","Islington","Camden","Brent","Ealing","Hounslow","Richmond upon Thames","Kingston upon Thames","Merton","Sutton","Croydon","Bromley","Lewisham","Greenwich","Bexley","Havering","Barking and Dagenham","Redbridge","Newham","Waltham Forest","Haringey","Enfield","Barnet","Harrow","Hillingdon"]
		regions = { b:target2.intersection( MultiPolygon( gadm.lookup(b) ) )  for b in boroughs}


			
	if regions is not None:
		for r in regions:
			polys = poly_to_coords(regions[r]); 
			for p in polys:
			
				patch = pgn(p[0], edgecolor='black', facecolor='white', fill=False, alpha=1, zorder=1000  );
				ax.add_patch(patch)
				
				#draw interior
				for ip in p[1]:
					patch = pgn(ip, edgecolor='black', facecolor='white', fill=False, alpha=1, zorder=1001  );
					ax.add_patch(patch)
				
		
	elif target2 is not None:

		polys = poly_to_coords(target2);

		for p in polys:
			
			patch = pgn(p[0], edgecolor='black', facecolor='white', alpha=1, zorder=0  );
			ax.add_patch(patch)
			
			#draw interior
			for ip in p[1]:
				patch = pgn(ip, edgecolor='black', facecolor='white', alpha=1, zorder=1  );
				ax.add_patch(patch)


def draw_poly(ax, target2, zorder):	
		
	if target2 is not None:

		polys = poly_to_coords(target2);

		for p in polys:
			
			patch = pgn(p[0], edgecolor='black', facecolor='white', alpha=1, zorder=zorder  );
			ax.add_patch(patch)
			
			#draw interior
			for ip in p[1]:
				patch = pgn(ip, edgecolor='black', facecolor='white', alpha=1, zorder=zorder  );
				ax.add_patch(patch)

if __name__ == "__main__":
	fig = plt.figure()
	ax = fig.add_subplot(111)
	
	target2, dims = get_target(whereami.meta_location)
	
	setup_figure(ax, dims, target2, zorder = 1)
	plt.axis("off")	
	plt.show();
	

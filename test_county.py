from county_lookup import *
from proc_polystr import poly_to_coords

import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import matplotlib.cm as cm

from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import box
from shapely.ops import cascaded_union

from matplotlib.patches import Polygon as pgn

import numpy as np
import random
def random_colour():
	cols = ['r', 'g', 'b', 'm', 'y', 'c']
	return cols[ random.randint(0,5) ];

if len(sys.argv) < 2:
	print("usage: test_country.py filepath");
	sys.exit(1);
filepath = sys.argv[1]	

print("county_lookup")
print(county_lookup.__doc__);
county = county_lookup(filepath);
county.load_all();

fig = plt.figure()
ax = fig.add_subplot(111)


#######################
##Draw the outlines  ##
#######################	
min_lat = np.inf;
min_lon = np.inf;
max_lat = -np.inf;
max_lon = -np.inf;

for place in county.county_dict:

	mp = MultiPolygon( county.county_dict[place] );
	
	if mp.bounds[0] < min_lat: min_lat = mp.bounds[0];
	if mp.bounds[1] < min_lon: min_lon = mp.bounds[1];
	if mp.bounds[2] > max_lat: max_lat = mp.bounds[2];
	if mp.bounds[3] > max_lon: max_lon = mp.bounds[3];
	
	
	pols2 = poly_to_coords( mp ); 
	for p in pols2:
		
		patch = pgn(p[0], edgecolor='black', facecolor='white', alpha=1, zorder=0  );
		ax.add_patch(patch)
		
		#draw interior
		for ip in p[1]:
			patch = pgn(ip, edgecolor='black', facecolor='white', alpha=1, zorder=10  );
			ax.add_patch(patch)

border = 0;
ax.set_xlim(min_lat-border,max_lat+border);
ax.set_ylim(min_lon-border,max_lon+border);
ax.set_xticklabels([])
ax.set_yticklabels([])
	
plt.savefig(filepath.split(".")[0] + ".png")
plt.close();




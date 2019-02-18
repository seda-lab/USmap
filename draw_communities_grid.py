#draw the map!
import sys
import pprint
import datetime
import re
import csv
import ast
import os
import math
import json
import string
import ast
import copy
import importlib
import gc

from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import box
from shapely.ops import cascaded_union

import numpy as np
from proc_polystr import poly_to_coords

import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import matplotlib.cm as cm
import matplotlib as mpl

from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import box
from shapely.ops import cascaded_union

from matplotlib.patches import Polygon as pgn
from matplotlib.collections import PatchCollection




from setup_target import *
from figure_helper import *
from random_color import *

import networkx as nx
import community
import itertools
from operator import itemgetter
from networkx.algorithms import community as cm

infilename = sys.argv[1]
outfilename = sys.argv[2]
size = int(sys.argv[3])

target = box(-125, 24.5, -67, 49.5);
target2, dims = get_target()

best_partition = {}
with open(infilename, 'r') as infile:
	for line in infile:
		best_partition = json.loads(line);

vmax = float(len(set(best_partition.values())))
vmin = 0;

	
	
############
##plotting##
############

fig = plt.figure()
ax = fig.add_subplot(111)
setup_figure(ax, dims, target2, zorder = 1)
#com_lab = add_uk_towns(ax, best_partition, dims, target2, size,  zorder=2);
plt.axis("off")			

##############
##rectangles##
##############
cols = [ 'r', 'g', 'b', 'yellow', 'm', 'c', 'lightpink', 'saddlebrown', 'orange', 'olive', 'moccasin', 'chartreuse', 'violet', 'chocolate', 'teal', 'grey' ]


for box_id, box_number, mp in generate_land(dims, target2, size, contains=False):

	xmin, ymin, xmax, ymax = box_to_coords(mp)

	if str(box_id) in best_partition:
		pn = best_partition[ str(box_id) ];
		if pn < len(cols):
			col = cols[ pn ];
		else:
			col = get_random_color();
		#col = col_map[ com_lab[best_partition[ str(box_id) ]] ]
		##draw costal edges
		mp = box(xmin, ymin, xmax, ymax);
		if target2.contains(mp):
			patch = mpl.patches.Rectangle( (xmin, ymin) , (xmax-xmin), (ymax-ymin), edgecolor='none', facecolor=col, alpha=1, zorder=0  );
			ax.add_patch(patch)
		else:
			poly = target2.intersection(mp)
			pols = poly_to_coords(poly)
			for p in pols:
				patch = pgn(p, edgecolor='none', facecolor=col, alpha=1, zorder=0  );
				ax.add_patch(patch)

plt.savefig(outfilename)
plt.close();
	

	

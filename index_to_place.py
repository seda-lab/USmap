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

import networkx as nx
import community
import itertools
from operator import itemgetter
from networkx.algorithms import community as cm
import random
import whereami


	
outfilename = sys.argv[1];
dbfilename = "";
size = 0
try:
	size = int(sys.argv[2]);	
	print("interpreting", sys.argv[2], "as gridsize");
except:
	dbfilename = sys.argv[2];
	print("interpreting", sys.argv[2], "as polygon database");
	county = county_lookup(dbfilename);
	county.load_all();
	for p in county.county_dict:
		county.county_dict[p] = cascaded_union(MultiPolygon(county.county_dict[p])).buffer(0.001);

if len(sys.argv) > 3:
	targetfilename = sys.argv[3];
	target2, dims = get_place(targetfilename)
else:
	target2, dims = get_target(whereami.meta_location)		

index_to_place = {}	
if dbfilename == "":

	for box_id, box_number, mp in generate_land(dims, target2, size, contains=False):
		index_to_place[ str(box_id) ] = ((mp.bounds[0],mp.bounds[1]),(mp.bounds[2],mp.bounds[3]));		

	with open(outfilename, 'w') as ofile:
		jsoned = json.dumps(index_to_place);
		ofile.write( jsoned )	
	


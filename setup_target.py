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

from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import box
from shapely.ops import cascaded_union

import numpy as np
from country_lookup import *

country = country_lookup("country.db");
	
def get_target():
	

	target = box(-125, 24.5, -67, 49.5);
	
	xmin = target.bounds[0]; xmax = target.bounds[2];
	ymin = target.bounds[1]; ymax = target.bounds[3];

	target2 = cascaded_union( country.lookup("United States") );

	target2 = target2.simplify(0, preserve_topology=False);
	if target2.geom_type=="Polygon": target2 = MultiPolygon([target2]);
	target2 = target.intersection( target2 );
	lt = []; 
	for i,t in enumerate(target2):
		lt.append(t);
		if i == 1: break;
	target2 = MultiPolygon(lt)

	return target2, [xmin, ymin, xmax, ymax]


def generate_land(dims, target2, size, contains=False):
	box_id = 0;
	box_number = 0;
	xvals = np.linspace(dims[0], dims[2], size+1); 
	yvals = np.linspace(dims[1], dims[3], size+1);
	xstep = (dims[2] - dims[0])/(size);
	ystep = (dims[3] - dims[1])/(size);

	for i in range(len(xvals)-1):
		for j in range(len(yvals)-1):
			xmin = xvals[i]
			ymin = yvals[j]
			xmax = xvals[i+1]
			ymax = yvals[j+1]
			
			mp = box(xmin, ymin, xmax, ymax);
			
			if contains: 
				if target2.contains( mp ):
					yield box_id, box_number, mp;	
					box_number += 1;
			else:
				if target2.intersects( mp ):
					yield box_id, box_number, mp;	
					box_number += 1;
					
			box_id += 1;
			
def box_id_to_ij(box_id, size):
	j = box_id % size;
	i = int((box_id - j)/size);
	return (i,j)
					
				
def box_to_coords(mp):
	x, y = mp.exterior.coords.xy
	x = list(x); y = list(y);	
	return min(x), min(y), max(x), max(y);
	

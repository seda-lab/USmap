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
from proc_polystr import poly_to_coords

import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import matplotlib.cm as cm
import matplotlib as mpl
from matplotlib.patches import Polygon as pgn
from matplotlib.collections import PatchCollection
import whereami

from country_lookup import *
country = country_lookup("country.db");

from county_lookup import *
fgs = county_lookup("fgs.db");

from gadm_lookup import *
gadm = gadm_lookup(whereami.gadm_location + "gadm.db");

def draw_place(target):
	
	fig = plt.figure()
	ax = fig.add_subplot(111)

	dims = target.bounds
	polys = poly_to_coords(target);

	for p in polys:
		
		patch = pgn(p[0], edgecolor='black', facecolor='white', alpha=1, zorder=0  );
		ax.add_patch(patch)
		
		#draw interior
		for ip in p[1]:
			patch = pgn(ip, edgecolor='black', facecolor='white', alpha=1, zorder=1  );
			ax.add_patch(patch)

	ax.set_xlim(dims[0], dims[2]);
	ax.set_ylim(dims[1], dims[3]);

	plt.axis("off")			
	plt.show();
	plt.close();
	
	
def get_place(filename):
	target = []
	with open(filename, 'r') as infile:
		for line in infile:
			pols, ipols = ast.literal_eval(line);
			poly = Polygon(pols, ipols);
			target.append(poly);
	target = cascaded_union( MultiPolygon(target) );
	
	xmin = target.bounds[0]; xmax = target.bounds[2];
	ymin = target.bounds[1]; ymax = target.bounds[3];

	return target, [xmin, ymin, xmax, ymax]
			
def get_target(place=whereami.meta_location):
	
	if place == "United States":
		target = box(-125, 24.5, -67, 49.5);
		target2 = cascaded_union( country.lookup("United States") );
		target2 = target.intersection( target2 );
	elif place == "United Kingdom":
		target = box(-5.8, 49.9, 1.8, 55.9 );
		fgs.load_all()
		regions = {}
		target2 = []
		for p in fgs.county_dict:
			regions[p] = cascaded_union( fgs.county_dict[p] );
			target2.append(regions[p].buffer(0.0001) );
		target2 = cascaded_union( target2 );
	elif place == "United States+":
		target = box(-125, 24.5, -67, 49.5);
		target2 = cascaded_union( country.lookup("United States") );
		target2 = target.intersection( target2 );
	
	elif place == "London":
		target = box(-0.52, 51.2, 0.34, 51.7)
		boroughs = ["London","Westminster","Kensington and Chelsea","Hammersmith and Fulham","Wandsworth","Lambeth","Southwark","Tower Hamlets","Hackney","Islington","Camden","Brent","Ealing","Hounslow","Richmond upon Thames","Kingston upon Thames","Merton","Sutton","Croydon","Bromley","Lewisham","Greenwich","Bexley","Havering","Barking and Dagenham","Redbridge","Newham","Waltham Forest","Haringey","Enfield","Barnet","Harrow","Hillingdon"]
		target2 = []
		for b in boroughs:
			target2.append( target.intersection( MultiPolygon( gadm.lookup(b) ).buffer(0.0001) ) );
		target2 = cascaded_union( target2 );
			
	xmin = target.bounds[0]; xmax = target.bounds[2];
	ymin = target.bounds[1]; ymax = target.bounds[3];

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
					
def ij_to_box_id(i,j, size):
	return i*size + j;
					
def box_to_coords(mp):
	x, y = mp.exterior.coords.xy
	x = list(x); y = list(y);	
	return min(x), min(y), max(x), max(y);
	

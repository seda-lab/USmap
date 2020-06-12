import ast

from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import box
from shapely.ops import cascaded_union

import numpy as np
from proc_polystr import poly_to_coords

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as pgn
from gadm_lookup import *
from country_lookup import *

import shapely.ops as ops
from shapely.geometry.polygon import Polygon
from functools import partial
import pyproj

def flatten_poly_area( coords, ptype='aea' ):

	poly = box(coords[0][0], coords[0][1], coords[1][0], coords[1][1])
	#'aea': 'Albers Equal Area',
	#'cea': 'Equal Area Cylindrical',
	#'laea': 'Lambert Azimuthal Equal Area',
	#'leac': 'Lambert Equal Area Conic',
	#'tcea': 'Transverse Cylindrical Equal Area',
	if poly.geom_type == "Polygon" or poly.geom_type == "MultiPolygon":
		poly_flat = ops.transform(
		partial(
			pyproj.transform,
			pyproj.Proj('EPSG:4326'),	#GPS ellipsoid
			pyproj.Proj(
				proj=ptype,					#equal area conical projection
				lat_1=poly.bounds[1],
				lat_2=poly.bounds[3]
				)),
		poly);
		return poly_flat.area/1000000.0; #km2

	return 0
	
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
			
def get_target(place, country, gadm, tolerance):
	
	if place == "United States":
		target = box(-125, 24.5, -67, 49.5);
		target2 = cascaded_union( country.lookup("United States") );
		target2 = target.intersection( target2 );
	elif place == "England and Wales":
		target = box(-5.8, 49.9, 1.8, 55.9 );
		target2 = cascaded_union( gadm.lookup("England",level=1) + gadm.lookup("Wales",level=1) );
		target2 = target.intersection( target2 );
	elif place == "Devon":
		target = box(-5.8, 49.9, 1.8, 55.9 );
		target2 = cascaded_union( gadm.lookup("Devon",level=2));
		target2 = target.intersection( target2 );
	elif place == "United States+":
		target = box(-125, 24.5, -67, 49.5);
		target2 = cascaded_union( country.lookup("United States") );
		target2 = target.intersection( target2 );
	elif place == "London+":
		target = box(-0.52, 51.2, 0.34, 51.7)
		boroughs = ["London","Westminster","Kensington and Chelsea","Hammersmith and Fulham","Wandsworth","Lambeth","Southwark","Tower Hamlets","Hackney","Islington","Camden","Brent","Ealing","Hounslow","Richmond upon Thames","Kingston upon Thames","Merton","Sutton","Croydon","Bromley","Lewisham","Greenwich","Bexley","Havering","Barking and Dagenham","Redbridge","Newham","Waltham Forest","Haringey","Enfield","Barnet","Harrow","Hillingdon"]
		target2 = []
		for b in boroughs:
			target2.append( target.intersection( MultiPolygon( gadm.lookup(b) ).buffer(0.0001) ) );
		target2 = cascaded_union( target2 );
	else:
		target2 = MultiPolygon( gadm.lookup(place) )
		target = box(target2.bounds[0], target2.bounds[1], target2.bounds[2], target2.bounds[3]);
		
	if tolerance > 0: target2 = target2.simplify(tolerance, preserve_topology=False);
			
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
	
if __name__ == "__main__":
	

	gadm = gadm_lookup("/data/Tweets/tmp/gadm.db");
	country = country_lookup("country.db");

	target2, dims = get_target("England and Wales", country, gadm, 0.01)
	draw_place(target2)

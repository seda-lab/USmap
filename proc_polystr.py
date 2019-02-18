import ast
import sys
import numpy
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.ops import cascaded_union

def poly_to_coords(poly):

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
	
def proc_polystr(polys, llcrnrlat, llcrnrlon, urcrnrlat, urcrnrlon, tolerance=-1):
	"""Process a string into a shapely polygon
	@param polys: string from shapefile
	@param llcrnrlat: min latitude
	@param llcrnrlon: min longitude
	@param urcrnrlat: max latitude
	@param urcrnrlon: max longitude
	@return: list of polygons
	"""
	
	if len(polys) == 0:
		return []

	all_polys = []	

	for i in polys:
		ji = ast.literal_eval(i[0])
		for p in ji['coordinates']:
			if isinstance(p[0], list):
				for x in p:
					if len(x) == 1:
						poly = Point(x[0]);
					else:
						poly = Polygon(x);

					if poly.bounds[0] > llcrnrlat and poly.bounds[1] > llcrnrlon and poly.bounds[2] < urcrnrlat and poly.bounds[3] < urcrnrlon:
						if poly.is_valid:
							all_polys.append( poly );
						else:
							all_polys.append( poly.buffer(0) );
			else:	
				if len(p) == 1:
					poly = Point(p[0]);
				else:		
					poly = Polygon(p);

				if poly.bounds[0] > llcrnrlat and poly.bounds[1] > llcrnrlon and poly.bounds[2] < urcrnrlat and poly.bounds[3] < urcrnrlon:
					if poly.is_valid:
						all_polys.append( poly );
					else:
						all_polys.append( poly.buffer(0) );
	
	all_polys = cascaded_union(all_polys);	
	if tolerance > 0: all_polys = all_polys.simplify(tolerance, preserve_topology=False);

	if all_polys.geom_type == "MultiPolygon":
		return [p for p in all_polys if p.geom_type == "Polygon"];
		
	if all_polys.geom_type == "GeometryCollection":
		return [ p for p in all_polys ];
			
	return [all_polys];
	

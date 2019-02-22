# -*- coding: utf-8 -*-

import sqlite3
import fiona
import sys
import ast
from bng_to_latlong import *

def str_or_none(st):
    if st is None:
        return None
    return str(st)

def proc_polystr(geom):

	lpoly = [];
	for p in geom['coordinates']:
		if isinstance(p[0], list):
			for bx in p:
				lpoly.append( [ OSGB36toWGS84(b[0], b[1])[::-1] for b in bx ] )				
		else:
			lpoly.append( [ OSGB36toWGS84(b[0], b[1])[::-1]  for b in p ] )				
	
	geom['coordinates'] = [lpoly];    
    
if len(sys.argv) < 2:
	print("usage: fgsadder.py filepath");
	print("creates an SQL database in fgs.db")
	sys.exit(1);
	
filepath = sys.argv[1]
print("Writing db to", "fgs.db" );

conn = sqlite3.connect("fgs.db")
c = conn.cursor()
c.execute('''CREATE TABLE county (n0 TEXT COLLATE NOCASE, n1 TEXT COLLATE NOCASE, n2 TEXT COLLATE NOCASE, n3 TEXT COLLATE NOCASE, n4 TEXT COLLATE NOCASE, n5 TEXT COLLATE NOCASE, poly BLOB)''')
for i in range(0, 6):
    c.execute('CREATE INDEX county' + str(i) + ' ON county (n' + str(i) + ')')
conn.commit()

fi = fiona.open(filepath + "FGS_Counties.shp", 'r')

count = 0
while True:
    try:
        a = fi.next()
    except:
        break

    count += 1
    county = a['properties']['COUNTY_STR'];
    if county[:2] == "W ": county = county.replace("W ", "West ");
    if county[:2] == "E ": county = county.replace("E ", "East ");
    if county[:2] == "S ": county = county.replace("S ", "South ");
    if county[:2] == "N ": county = county.replace("N ", "North ");
    if county[:2] == "NW": county = county.replace("NW", "North West");
    if county[:2] == "NE": county = county.replace("NE", "North East");
    if county[:2] == "SW": county = county.replace("SW", "South West");
    if county[:2] == "NE": county = county.replace("SE", "South East");
    if county[:3] == "Gtr": county = county.replace("Gtr", "Greater");
    county = county.replace("&", "and");
    county = county.lower();
    if county == "kingston upon hull" or county == "bristol":
        county += ", city of"
    if county == "rhondda cynon taff":
	    county = "rhondda, cynon, taff"
    if county == "vale of glamorgan":
        county = "the vale of glamorgan"

    a['properties']['COUNTY_STR'] = county;
    proc_polystr( a['geometry'] );

    c.execute("INSERT INTO county VALUES (:n0, :n1, :n2, :n3, :n4, :n5, :poly)", {
        'n0': str_or_none(a['properties']['COUNTY_STR']),
        'n1': str_or_none(a['properties']['SNAC_GOR']),
        'n2': str_or_none(a['properties']['COUNTRY']),
        'n3': str_or_none(a['properties']['Region_ID']),
        'n4': str_or_none(a['properties']['Update_ID']),
        'n5': str_or_none(a['properties']['PMS_REGION']),
        'poly': str_or_none(a['geometry'])
    })

conn.commit()


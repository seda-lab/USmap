import sqlite3
import fiona
import sys
import urllib.request
import os
import zipfile

def str_or_none(st):
    if st is None:
        return None
    return str(st).lower()
    
url = 'https://biogeo.ucdavis.edu/data/gadm3.6/gadm36_shp.zip'

if len(sys.argv) < 2:
	print("usage: gadmadder.py filepath");
	print("Downloads GADM database from", url )
	print("and creates an SQL database in filepath+gadm.db")
	sys.exit(1);
	
filepath = sys.argv[1]
print("Writing db to", filepath+"gadm.db" );

if not os.path.isfile(filepath + 'gadm36_shp.zip') and not os.path.isfile(filepath + 'gadm36_shp'):
	print("Downloading...");
	urllib.request.urlretrieve(url, filepath + 'gadm36_shp.zip')

if not os.path.isfile(filepath + 'gadm36.shp'):
	print("Unzipping...");
	with zipfile.ZipFile(filepath + 'gadm36_shp.zip','r') as zip_ref:
		zip_ref.extractall(filepath)

conn = sqlite3.connect(filepath+"gadm.db")
c = conn.cursor()
c.execute('''CREATE TABLE gadm (n0 TEXT COLLATE NOCASE, n1 TEXT COLLATE NOCASE, 
n2 TEXT COLLATE NOCASE, n3 TEXT COLLATE NOCASE, n4 TEXT COLLATE NOCASE, n5 TEXT COLLATE NOCASE, poly BLOB)''')
for i in range(0, 6):
    c.execute('CREATE INDEX gadm' + str(i) + ' ON gadm (n' + str(i) + ')')
conn.commit()

fi = fiona.open(filepath + 'gadm36.shp', 'r')

count = 0
while True:
	try:
		a = fi.next()
	except:
		break

	
	n0 = str_or_none(a['properties']['NAME_0'])
	n1 = str_or_none(a['properties']['NAME_1'])
	n2 = str_or_none(a['properties']['NAME_2'])
	n3 = str_or_none(a['properties']['NAME_3'])
	n4 = str_or_none(a['properties']['NAME_4'])
	n5 = str_or_none(a['properties']['NAME_5'])
		
	count += 1
	
	c.execute("INSERT INTO gadm VALUES (:n0, :n1, :n2, :n3, :n4, :n5, :poly)", {
		'n0': n0,
		'n1': n1,
		'n2': n2,
		'n3': n3,
		'n4': n4,
		'n5': n5,
		'poly': str_or_none(a['geometry'])
	})

	if count % 1000 == 0:
		print (count, "/ 339000" )

conn.commit()

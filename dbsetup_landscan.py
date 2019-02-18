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
    
if len(sys.argv) < 2:
	print("usage: equalpopsetup.py infilename outfilename");
	print("Creates an SQL database from infilename in outfilename")
	print("infilename should be a shapefile (.shp)")
	sys.exit(1);
	
infilename = sys.argv[1]
outfilename = sys.argv[2]
print("Writing db to", outfilename );


conn = sqlite3.connect(outfilename)
c = conn.cursor()
c.execute('''CREATE TABLE uscounty (n0 TEXT COLLATE NOCASE, n1 TEXT COLLATE NOCASE, n2 TEXT COLLATE NOCASE, n3 TEXT COLLATE NOCASE, n4 TEXT COLLATE NOCASE, n5 TEXT COLLATE NOCASE, poly BLOB)''')
for i in range(0, 6):
   c.execute('CREATE INDEX uscounty' + str(i) + ' ON uscounty (n' + str(i) + ')')
conn.commit()

fi = fiona.open(infilename, 'r')

count = 0
while True:
	try:
		a = fi.next()
	except:
		break

	n0 = str_or_none(a['properties']['UID'])
	n1 = str_or_none(a['properties']['gridcode'])
	n2 = str_or_none(a['properties']['Id'])
	n3 = str_or_none(a['properties']['SUM'])
		
	count += 1
	
	c.execute("INSERT INTO uscounty VALUES (:n0, :n1, :n2, :n3, :n4, :n5, :poly)", {
		'n0': n0,
		'n1': n1,
		'n2': n2,
		'n3': n3,
		'n4': None,
		'n5': None,
		'poly': str_or_none(a['geometry'])
	})


conn.commit()

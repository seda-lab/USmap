import sys
import os

if len(sys.argv) < 4:
	print( "usage: python3 run_all.py infile gridsize counties" )
	print( "infile = location of the tweet file (expects one tweet json on each line)." )
	print( "gridsize = X. Divide the map (continental US) into an X by X grid" )
	print( "counties = 5m/EqualPop. If 5m divide the map (continental US) using census counties and ignore gridsize.\n\
	If EqualPop use the equal population shapefile. Otherwise will default to using the uniform grid." )
	sys.exit(1);

infile, gridsize, counties = sys.argv[1:]

dbfilename = ""
use_counties = False;
if counties == "5m":
	use_counties = True;
	dbfilename = "2010_us_050_00_20m.db"
	print("Using", dbfilename)
elif counties == "EqualPop":
	use_counties = True;
	dbfilename = "UnitedStates_grid.db"
	print("Using", dbfilename)

	
##run extract.py
if not os.path.isfile("extract.out"): 
	print( "Extracting useable tweets..." )
	os.system('python3 extract.py {} {}'.format(infile, "extract.out"));
else:
	print("Using existing extract.out");
	
##run split_users.py	
if not os.path.isfile("userloc.out"): 
	print( "Creating the user/location map..." )
	os.system('python3 split_users.py {} {}'.format("extract.out", "userloc.out"));
else:
	print("Using existing userloc.out");
	

##run locate_users.py	
if use_counties:
	if not os.path.isfile("boxes.out"): 
		print( "Creating the location to grid map..." )
		os.system('python3 locate_users_county.py {} {} {}'.format("userloc.out", "boxes.out", dbfilename));
	else:
		print("Using existing boxes.out");
else:
	if not os.path.isfile("boxes.out"): 
		print( "Creating the location to grid map..." )
		os.system('python3 locate_users_grid.py {} {} {}'.format("userloc.out", "boxes.out", gridsize));
	else:
		print("Using existing boxes.out");

		
##run locate_replies_all.py	
if use_counties:
	if not os.path.isfile("labelled.out"): 
		print( "Creating the box network..." )
		os.system('python3 locate_replies_all.py {} {} {} {} {} {} {}'.format("extract.out", "boxes.out", "labelled.out", "connections.out", "sentiment.out", gridsize, dbfilename));
	else:
		print("Using existing labelled.out");
else:
	if not os.path.isfile("labelled.out"): 
		print( "Creating the box network..." )
		os.system('python3 locate_replies_all.py {} {} {} {} {} {}'.format("extract.out", "boxes.out", "labelled.out", "connections.out", "sentiment.out", gridsize));
	else:
		print("Using existing labelled.out");

	
##run find_communities.py	
if not os.path.isfile("communities.out"): 
	print( "Finding communities in the box network..." )
	os.system('python3 find_communities.py {} {} {}'.format("connections.out", "communities.out", "induced.out"));
else:
	print("Using existing communities.out");
	
##run draw_communities.py
if use_counties:
	if not os.path.isfile("communities.png"): 
		print( "Drawing communities of the box network..." )
		os.system('python3 draw_communities_county.py {} {} {}'.format("communities.out", "communities.png", dbfilename));
	else:
		print("Using existing communities.png");
else:
	if not os.path.isfile("communities.png"): 
		print( "Drawing communities of the box network..." )
		os.system('python3 draw_communities_grid.py {} {} {}'.format("communities.out", "communities.png", gridsize));
	else:
		print("Using existing communities.png");



print("Done!")

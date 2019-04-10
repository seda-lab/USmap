import sys
import os

if len(sys.argv) < 5:
	print( "usage: python3 run_all.py infile gridsize counties level comm" )
	print( "infile = location of the tweet file (expects one tweet json on each line)." )
	print( "gridsize = X. Divide the map (continental US) into an X by X grid" )
	print( "counties = database file. If the file does not exist, defaults to using a grid" )
	print( "level = l. For l=-1 finds communities using whole map. For l>=0 finds communities at that level." )
	print( "comm = c. For l=-1 ignored, otherwise use the community c found at level l." )
	sys.exit(1);

infile, gridsize, counties, level, comm = sys.argv[1:]


level = int(level);
if not os.path.isfile(counties):
	print('"'+counties+'"', "database not found, using a", gridsize, "x", gridsize, "grid. Did you mean this?");
	counties=gridsize;
	
filetag = ""
argtag = "";
if level >= 0:
	argtag = " map_level" + str(level) + "_comm" + comm + ".txt";
	filetag = "_level" + str(level) + "_comm" + comm;
	
	
##run extract.py
if not os.path.isfile("extract.out"): 
	print( "Extracting useable tweets..." )
	if not os.path.isfile(infile):
		print(infile, "not found");
		sys.exit(1);
	os.system('python3 extract.py {} {}'.format(infile, "extract.out"));
else:
	print("Using existing extract.out");
	
	
##run split_users.py	
if not os.path.isfile("userloc" + filetag + ".out"): 
	print( "Creating the user/location map..." )
	os.system('python3 split_users.py {} {}'.format("extract.out", "userloc" + filetag + ".out") + argtag);
else:
	print("Using existing userloc" + filetag + ".out");


##run locate_users.py	
if not os.path.isfile("boxes" + filetag + ".out"): 
	print( "Creating the location to grid map..." )
	os.system('python3 locate_users.py {} {} {}'.format("userloc" + filetag + ".out", "boxes" + filetag + ".out", counties) + argtag);
else:
	print("Using existing boxes" + filetag + ".out");

	

##run locate_replies_all.py	
if not os.path.isfile("connections" + filetag + ".out"): 
	print( "Creating the box network..." )
	os.system('python3 locate_replies_all.py {} {} {} {} {} {}'.format("extract.out", "boxes" + filetag + ".out", "labelled" + filetag + ".out", "connections" + filetag + ".out", "sentiment" + filetag + ".out", counties));
else:
	print("Using existing connections" + filetag + ".out");


##run find_communities.py	
if not os.path.isfile("communities" + filetag + ".out"): 
	print( "Finding communities in the box network..." )
	os.system('python3 find_communities.py {} {} {}'.format("connections" + filetag + ".out", "communities" + filetag + ".out", "induced" + filetag + ".out"));
else:
	print("Using existing communities" + filetag + ".out");
	
##run index_to_place.py
if not os.path.isfile("boxids" + filetag + ".out"): 
	print( "Mapping box_ids to co-ordinates..." )
	os.system('python3 index_to_place.py {} {}'.format("boxids" + filetag + ".out", counties) + argtag);
else:
	print("Using existing boxids" + filetag + ".out");


##run draw_communities.py
if not os.path.isfile("communities" + filetag + ".png"): 
	print( "Drawing communities of the box network..." )
	os.system('python3 draw_communities.py {} {} {}'.format("communities" + filetag + ".out", "communities" + filetag, counties) + argtag);
else:
	print("Using existing communities" + filetag + ".png");

##run refine_communities.py	
if not os.path.isfile("refinedcommunities" + filetag + ".out"): 
	print( "Refining communities in the box network..." )
	os.system('python3 refine_communities.py {} {} {} {}'.format("connections" + filetag + ".out", "communities" + filetag + ".out", "refinedcommunities" + filetag + ".out", counties) + argtag);
else:
	print("Using existing refinedcommunities" + filetag + ".out");
		
##run draw_communities.py
if not os.path.isfile("refinedcommunities" + filetag + ".png"): 
	print( "Drawing refined communities of the box network..." )
	os.system('python3 draw_communities.py {} {} {}'.format("refinedcommunities" + filetag + ".out", "refinedcommunities" + filetag, counties) + argtag);
else:
	print("Using existing refinedcommunities" + filetag + ".png");


##run edit_communities.py	
if not os.path.isfile("editedcommunities" + filetag + ".out"): 
	print( "Editing communities in the box network..." )
	os.system('python3 edit_communities.py {} {} {} {}'.format("refinedcommunities" + filetag + ".out", "editedcommunities" + filetag + ".out", counties, 4) + argtag);
else:
	print("Using existing editedcommunities" + filetag + ".out");

		
##run draw_communities.py
if not os.path.isfile("editedcommunities" + filetag + ".png"): 
	print( "Drawing edited communities of the box network..." )
	os.system('python3 draw_editedcommunities.py {} {} {}'.format("editedcommunities" + filetag + ".out", "editedcommunities" + filetag, counties) + argtag);
else:
	print("Using existing editedcommunities" + filetag + ".png");

##run map_communities.py
if not os.path.isfile("map_level" + str(level+1) + "_comm0.txt"): 
	print( "Output mapped communities..." )
	os.system('python3 map_communities.py {} {} {}'.format("editedcommunities" + filetag + ".out", "map_level" + str(level+1) + "_comm", counties) + argtag);
else:
	print("Using existing map_level" + str(level+1) + "_comm0.txt");


print("Done!")




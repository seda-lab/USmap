import sys
import os
import configparser

from setup_target import *
from extract import extract_mentions
from split_users import split_users
from locate_users import locate_users
from generate_nodeinfo import generate_nodeinfo
from construct_null import construct_null
from build_network import build_network
from find_communities import find_communities, refine_communities, edit_communities
from draw_communities import draw_map
from map_communities import map_communities
from run_louvain import run_louvain_null
from draw_network import draw_network

if len(sys.argv) < 2:
	print( "usage: python3 twitter_map.py settings.ini" )
	sys.exit(1);

config_fpath = sys.argv[1]
config = configparser.ConfigParser(allow_no_value=True)
config.read(config_fpath)




######################
## Country database
######################
from country_lookup import *
country = country_lookup(config.get("global", "country_location"));

######################
## GADM database
######################
from gadm_lookup import *
gadm = gadm_lookup(config.get("global", "gadm_location"));

#############################
## Size or County database
#############################
from county_lookup import *
county = None;
if config.getboolean("global", "use_counties"):
	county = county_lookup( config.get("global", "county_location") );
size = None
if config.getboolean("global", "use_grid"):
	size = config.getint("global", "grid_size");

if (not size) and (not county):
	print("Set either use_size or use_counties to True");
	sys.exit(1);
if size and county:
	print("Set one of use_size or use_counties to False");
	sys.exit(1);

	
level = config.get("global", "level");
comm = config.get("global", "comm");
try: 
	level = int(level);
except:
	level = -1;
try:
	comm = int(comm);
except:
	comm = -1;	

iodir = config.get("global", "iodir")

#############################
##target2 = detailed polygon;   dims = box corners;   target = Bounding box;
#############################
meta_location = config.get("global", "meta_location")
tolerance = config.getfloat("global", "tolerance")
filetag = ""	
if level >= 0:
	place = config.get("global", "map_filename")
	if place == "":
		place = "map_level" + str(level) + "_comm" + str(comm) + ".txt";
	place = iodir + place;
	target2, dims = get_place(place);
	filetag = "_level" + str(level) + "_comm" + str(comm);
else:
	target2, dims = get_target(meta_location, country, gadm, tolerance)
target = box(dims[0], dims[1], dims[2], dims[3]);

stats_filename = config.get("global", "stats_filename")
if stats_filename == "": stats_filename = "stats.out";
stats_file = open(stats_filename, 'w');
img_type = config.get("global", "img_type")

#########################
# Extract Tweets
#########################
infilename = config.get("extract", "input_file")
outfilename = iodir + "extract.out"
if not config.getboolean("extract", "default_filenames"):
	outfilename = config.get("extract", "output_file")
	
if config.getboolean("extract", "regen") or (not os.path.isfile(outfilename)):
	extract_mentions(infilename, outfilename, target, stats_file)
else:
	print("Using existing", outfilename);



#########################
# Extract Places
#########################
infilename = outfilename
outfilename = iodir + "userloc" + filetag + ".out"
if not config.getboolean("split", "default_filenames"):
	infilename = config.get("split", "input_file")
	outfilename = config.get("split", "output_file")

if config.getboolean("split", "regen") or (not os.path.isfile(outfilename)):
	split_users(infilename, outfilename, target2, config.getfloat("split", "max_place"), stats_file )
else:
	print("Using existing", outfilename);



#########################
# Put users in boxes
#########################
infilename = outfilename
outfilename = iodir + "boxes" + filetag + ".out"
indexfilename = iodir + "boxids" + filetag + ".json"
tweetcountfilename = iodir + "boxcount" + filetag + ".json"
if not config.getboolean("locate", "default_filenames"):
	infilename = config.get("locate", "input_file")
	outfilename = config.get("locate", "output_file")
	indexfilename = config.get("locate", "index_file")
	tweetcountfilename = config.get("locate", "tweetcount_file")

if config.getboolean("locate", "regen") or (not os.path.isfile(outfilename)):
	locate_users(infilename, outfilename, indexfilename, tweetcountfilename, target2, dims, size=size, county=county, stats_file=stats_file)
else:
	print("Using existing", outfilename);



#########################
# make the network
#########################
infilename = iodir + "extract.out"
boxfilename = iodir + "boxes" + filetag + ".out"
outfilename = iodir + "connections" + filetag + ".out"
senfilename = iodir + "sentiment" + filetag + ".out"
graphfilename = iodir + "graph" + filetag + ".txt"
if not config.getboolean("network", "default_filenames"):
	infilename = config.get("network", "input_file")
	boxfilename = config.get("network", "box_file")
	outfilename = config.get("network", "con_file")
	senfilename = config.get("network", "sen_file")
	graphfilename = config.get("network", "graph_file")

if config.getboolean("network", "regen") or (not os.path.isfile(outfilename)):
	build_network(infilename, boxfilename, outfilename, senfilename, graphfilename, size=size, county=county, stats_file=stats_file, randchoice=False)
else:
	print("Using existing", outfilename);



#########################
# find communities
#########################
infilename = iodir + "connections" + filetag + ".out"
graphfilename = iodir + "graph" + filetag + ".txt"
outfilename = iodir + "communities" + filetag + ".out"
if not config.getboolean("findcom", "default_filenames"):
	infilename = config.get("findcom", "input_file")
	graphfilename = config.get("findcom", "graph_file")
	outfilename = config.get("findcom", "find_file")

if config.getboolean("findcom", "regen") or (not os.path.isfile(outfilename)):
	find_communities(infilename, graphfilename, outfilename,stats_file=stats_file);
else:
	print("Using existing", outfilename);



#########################
# draw communities
#########################
infilename = iodir + "communities" + filetag + ".out"
outfilename = iodir + "communities" + filetag + "." + img_type
if not config.getboolean("drawcom", "default_filenames"):
	infilename = config.get("drawcom", "find_file")
	outfilename = config.get("drawcom", "output_find_file")

if config.getboolean("drawcom", "regen") or (not os.path.isfile(outfilename)):
	draw_map(infilename, outfilename, dims, target2, size=size, gadm=gadm, county=county, place=meta_location)
else:
	print("Using existing", outfilename);



if config.getboolean("null", "runprop"):
	bindist = float(config.get("null", "bindist"));
	ut = 1;
	uts = str(ut);
	
	#########################
	# Generate nodeinfo
	#########################
	boxfilename = iodir + "boxes" + filetag + ".out"
	indexfilename = iodir + "boxids" + filetag + ".json"
	confilename = iodir + "connections" + filetag + ".out"
	tweetcountfilename = iodir + "boxcount" + filetag + ".json"
	csvfilename = iodir + "nodeinfo" + filetag + ".csv"
	if not config.getboolean("null", "default_filenames"):
		boxfilename = config.get("locate", "output_file")
		indexfilename = config.get("locate", "index_file")
		csvfilename = config.get("null", "csv_file")
	
	if config.getboolean("null", "regen") or (not os.path.isfile(csvfilename)):
		generate_nodeinfo(boxfilename, indexfilename, confilename, tweetcountfilename, csvfilename, size=size, county=county)
	else:
		print("Using existing", csvfilename);


	#########################
	# Generate null
	#########################
	csvfilename = iodir + "nodeinfo" + filetag + ".csv"
	confilename = iodir + "connections" + filetag + ".out"
	nullfilename = iodir + "null" + "_" + str(bindist)+ "_" + uts + filetag + ".txt"
	labelfilename = iodir + "labels" + "_" + str(bindist)+ "_" + uts + filetag + ".json"
	graphfilename = iodir + "nullgraph" + "_" + str(bindist)+ "_" + uts + filetag + ".txt" 
	fdistfilename = iodir + "fdist" + "_" + str(bindist)+ "_" + uts + filetag + ".txt" 
	if not config.getboolean("null", "default_filenames"):
		csvfilename = config.get("null", "csv_file")
		confilename = config.get("network", "con_file")
		nullfilename = config.get("null", "null_file")	
		labelfilename = config.get("null", "label_file")	
		graphfilename = config.get("null", "graph_file")	
		fdistfilename = config.get("null", "fdist_file")	
		
	if config.getboolean("null", "regen") or (not os.path.isfile(nullfilename)):
		construct_null(csvfilename, confilename, nullfilename, labelfilename, graphfilename, fdistfilename, users=ut, base=bindist)		
	else:
		print("Using existing", nullfilename);
	


	
	#########################
	# find communities
	#########################
	infilename = iodir + "connections" + filetag + ".out"
	graphfilename = iodir + "nullgraph" + "_" + str(bindist)+ "_" + uts + filetag + ".txt"
	nullfilename = iodir + "null" + "_" + str(bindist)+ "_" + uts + filetag + ".txt"
	labelfilename = iodir + "labels" + "_" + str(bindist)+ "_" + uts + filetag + ".json"
	outfilename = iodir + "nullcommunities" + "_" + str(bindist)+ "_" + uts + filetag + ".out"
	if not config.getboolean("null", "default_filenames"):
		infilename = config.get("network", "con_file")
		graphfilename = config.get("null", "graph_file")	
		nullfilename = config.get("null", "null_file")	
		labelfilename = config.get("null", "label_file")	
		outfilename = config.get("null", "communities_file")	
		
	if config.getboolean("null", "regen") or (not os.path.isfile(outfilename)):
		find_communities(infilename, graphfilename, outfilename, nullfilename=nullfilename, labelfilename=labelfilename, stats_file=stats_file);
	else:
		print("Using existing", outfilename);

	
	#########################
	# draw communities
	#########################
	infilename = iodir + "nullcommunities" + "_" + str(bindist)+ "_" + uts + filetag + ".out"
	outfilename = iodir + "nullcommunities" + "_" + str(bindist)+ "_" + uts + filetag + "." + img_type
	if not config.getboolean("null", "default_filenames"):
		infilename = config.get("network", "communities_file")
		outfilename = config.get("null", "communities_plot_file")	
		
	if config.getboolean("null", "regen") or (not os.path.isfile(outfilename)):
		draw_map(infilename, outfilename, dims, target2, size=size, gadm=gadm, county=county, place=meta_location)
	else:
		print("Using existing", outfilename);
	



#########################
# refine communities
#########################
infilename = iodir + "connections" + filetag + ".out"
partfilename = iodir + "communities" + filetag + ".out"
outfilename = iodir + "refinedcommunities" + filetag + ".out"
if not config.getboolean("findcom", "default_filenames"):
	infilename = config.get("findcom", "input_file")
	partfilename = config.get("findcom", "find_file")
	outfilename = config.get("findcom", "refine_file")

if config.getboolean("findcom", "regen") or (not os.path.isfile(outfilename)):
	refine_communities(infilename, partfilename, outfilename, dims, target2, size=size, county=county);
else:
	print("Using existing", outfilename);

	

#########################
# draw refined communities
#########################
infilename = iodir + "refinedcommunities" + filetag + ".out"
outfilename = iodir + "refinedcommunities" + filetag + "." + img_type
if not config.getboolean("drawcom", "default_filenames"):
	infilename = config.get("drawcom", "refine_file")
	outfilename = config.get("drawcom", "output_refined_file")

if config.getboolean("drawcom", "regen") or (not os.path.isfile(outfilename)):
	draw_map(infilename, outfilename, dims, target2, size=size, gadm=gadm, county=county, place=meta_location)
else:
	print("Using existing", outfilename);


#########################
# edit communities
#########################
infilename = iodir + "connections" + filetag + ".out"
partfilename = iodir + "communities" + filetag + ".out"
outfilename = iodir + "editedcommunities" + filetag + ".out"
if not config.getboolean("findcom", "default_filenames"):
	infilename = config.get("findcom", "input_file")
	partfilename = config.get("findcom", "find_file")
	outfilename = config.get("findcom", "edited_file")

if config.getboolean("findcom", "regen") or (not os.path.isfile(outfilename)):
	edit_communities(infilename, partfilename, outfilename, config.getint("findcom", "nbrs"), dims, target2, size=size, county=county);
else:
	print("Using existing", outfilename);



#########################
# draw edited communities
#########################
infilename = iodir + "editedcommunities" + filetag + ".out"
outfilename = iodir + "editedcommunities" + filetag + "." + img_type
if not config.getboolean("drawcom", "default_filenames"):
	infilename = config.get("drawcom", "edited_file")
	outfilename = config.get("drawcom", "output_edited_file")

if config.getboolean("drawcom", "regen") or (not os.path.isfile(outfilename)):
	draw_map(infilename, outfilename, dims, target2, size=size, gadm=gadm, county=county, place=meta_location, edited=True)
else:
	print("Using existing", outfilename);
			
#########################
# draw edited communities
#########################
infilename = iodir + "editedcommunities" + filetag + ".out"
outfilebase = iodir + "map_level" + str(level+1) + "_comm";
if not config.getboolean("mapcom", "default_filenames"):
	infilename = config.get("mapcom", "input_file")
	outfilebase = config.get("mapcom", "output_base")

outfilename = outfilebase + "0.txt"
if config.getboolean("mapcom", "regen") or (not os.path.isfile(outfilename)):
	map_communities(infilename, outfilebase, dims, target2, size=size, county=county, drop_isolates=config.getboolean("mapcom", "drop_isolates"), use_largest=config.getboolean("mapcom", "use_largest"))
else:
	print("Using existing", outfilename);

#########################
# draw network map 
#########################
infilename = iodir + "connections" + filetag + ".out"
partfilename = iodir + "refinedcommunities" + filetag + ".out"
outfilename = iodir + "networkplot" + filetag + "." + img_type
if not config.getboolean("networkplot", "default_filenames"):
	infilename = config.get("networkplot", "input_file")
	partfilename = config.get("networkplot", "find_file")
	outfilename = config.get("networkplot", "output_file")


gparams = {
'max_node':config.getfloat("networkplot", "max_node"),
'node_factor':config.getfloat("networkplot", "node_factor"),
'min_self':config.getfloat("networkplot", "min_self"),
'min_connection':config.getfloat("networkplot", "min_connection"),
'edge_w':config.getfloat("networkplot", "edge_w")
}
if config.getboolean("networkplot", "regen") or (not os.path.isfile(outfilename)):
	draw_network(infilename, partfilename, outfilename, dims, target2, gparams=gparams, size=size, gadm=gadm, county=county, place=meta_location)
else:
	print("Using existing", outfilename);


print("Done!")



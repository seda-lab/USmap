#give every user together with a list of places that user has tweeted from
import sys
import ast
from shapely.geometry import box

def split_users(infilename, outfilename, target2, max_place, stats_file=None):

	num_tweets = 0;
	skipped = 0;
	used = 0;
	user_locations = {}; # user : {loc1 : count, loc2 : count, ... }

	with open(infilename,'r') as datafile:
		for x in datafile:
			
			words = ast.literal_eval(x);

			num_tweets += 1;
			if num_tweets % 10000 == 0:
				print(num_tweets, "tweets", skipped, "skipped", used, "used")
				
			name = words[4] #user id
			if type(name) == dict:
				name = int(name["$numberLong"]);
			
			##skip big boxes
			if not( (words[2][2][0] - words[2][0][0]) < max_place and (words[2][2][1] - words[2][0][1]) < max_place ):
				skipped += 1;
				continue;

			mp = box(words[2][0][0], words[2][0][1], words[2][2][0], words[2][2][1]);			
			if not target2.intersects(mp):
				skipped += 1;
				continue;
				
			ll = str(words[2])		
			if name not in user_locations:
				user_locations[name] = {}
				user_locations[name][ll] = 1
			else:
				if ll not in user_locations[name]:
					user_locations[name][ll] = 1
				else:
					user_locations[name][ll] += 1 
			used += 1;
			
	with open(outfilename, 'w') as outfile:
		for name in user_locations:
			out = [name]
			for ll in user_locations[name]:
				out.append( [ll , user_locations[name][ll]] );	
			outfile.write(str(out) + "\n")

	print("###split_users.py",file=stats_file)		
	print( str(num_tweets) + " tweets",file=stats_file );
	print( str(skipped) + " skipped tweets",file=stats_file );
	print( str(used) + " used tweets",file=stats_file );
	print( str(len(user_locations)) + " users",file=stats_file );
			

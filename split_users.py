#give every user is together with a list of places that user has tweeted from
import sys
import ast
from setup_target import *
import whereami	

tweet_file = sys.argv[1]
outfilename = sys.argv[2];
#statsfilename = sys.argv[3];

	
num_tweets = 0;
skipped = 0;
used = 0;
user_locations = {}; # user : {loc1 : count, loc2 : count, ... }

if len(sys.argv) > 3:
	targetfilename = sys.argv[3];
	target2, dims = get_place(targetfilename)
else:
	target2, dims = get_target(whereami.meta_location)


with open(tweet_file,'r') as datafile:
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

#with open(statsfilename, 'w') as ofile:
print( str(num_tweets) + " tweets" );
print( str(skipped) + " skipped tweets" );
print( str(used) + " used tweets" );
print( str(len(user_locations)) + " users" );
		

import sys
import ast
import json

def build_network(tweet_file, userfilename, confilename, senfilename, graphfilename, size=30, county=None, stats_file=None):

	##user -> box map
	user_boxes = {};
	bx_map = {}; bxc = 0
	with open(userfilename, 'r') as datafile:
		for x in datafile:
			words = ast.literal_eval(x);
			bxs = [];
			if len(words) < 2:
				print(x)
				sys.exit(1);
			if county:
				user_boxes[ words[0] ] = words[1:]
				for w in words[1:]: 
					if w not in bx_map:
						bx_map[w] = bxc;
						bxc += 1;			
			else:
				for w in words[1:]:
					idx = w[0]*(size)+w[1]
					bxs.append(idx);
				user_boxes[ words[0] ] = bxs;
		
	connections = {}; 
	sentiment = {};
			
	num_tweets = 0;
	used_tweets = 0;
	self_mention = 0;
	out_mention = 0;
	skipped=0;
	used_mention = 0;
	mentioners = set(); ##who does the mentioning
	mentionees = set(); ##who is mentioned

	with open(tweet_file,'r') as datafile:
		for x in datafile:
			num_tweets += 1;
			if num_tweets %10000 == 0:
				print("num tweeets", num_tweets,"skipped", skipped, "self", self_mention, "out", out_mention, "used mention", used_mention, "used tweets", used_tweets);
				
			words = ast.literal_eval(x);
			user_name = words[4] #user id
			pol = float(words[5])
			if type(user_name) == dict:
				user_name = int(user_name["$numberLong"]);
			if (user_name not in user_boxes): 
				continue;

			#check is a connection in target		
			use_reply_name = [];
			for m in words[6]:		
				cname = int(m[0]); 
				if cname == user_name: 
					self_mention += 1;
					continue; 				#no self mentions
				if cname not in user_boxes: 
					out_mention += 1
					continue;			#correspondant in target area
				use_reply_name.append(cname);
				used_mention += 1
			

			if len(use_reply_name) == 0: 
				skipped += 1
				continue; 
		
			mentioners.add(user_name);
			for r_name in use_reply_name:
				mentionees.add(r_name);
				
				##TODO does this work for counties?!
				##Treats every county equally
				tot = len(user_boxes[user_name]) * len(user_boxes[r_name]); #number of boxes to spread the mention across
				for u in user_boxes[user_name]:
					for r in user_boxes[r_name]:

						if u in connections:
							if r in connections[u]:
								connections[ u ][ r ] += 1.0/tot;
								sentiment[ u ][ r ] += pol/tot;
							else:
								connections[ u ][ r ] = 1.0/tot;
								sentiment[ u ][ r ] = pol/tot;
						else:
							connections[u] = {};
							sentiment[u] = {};
							connections[ u ][ r ] = 1.0/tot;
							sentiment[ u ][ r ] = pol/tot;
						
			used_tweets += 1;


	with open(confilename, 'w') as outfile:
		jsoned = json.dumps(connections);
		outfile.write( jsoned )	
		
	with open(senfilename, 'w') as outfile:	
		jsoned = json.dumps(sentiment);
		outfile.write( jsoned )	
	
	with open(graphfilename, 'w') as outfile:
		for u, v, w in G.edges.data('weight'):
			outfile.write("{} {} {}\n".format(u,v,w) )
				
	print("###build_network.py",file=stats_file)		
	print( str(num_tweets) + " tweets",file=stats_file );
	print( str(self_mention) + " self mentions",file=stats_file );
	print( str(out_mention) + " out of bounds mentions",file=stats_file );
	print( str(used_mention) + " used mentions",file=stats_file );
	print( str(skipped) + " skipped tweets",file=stats_file );
	print( str(used_tweets) + " used tweets",file=stats_file );
	print( str(len(mentioners)) + " users mentioning someone else",file=stats_file );
	print( str(len(mentionees)) + " users mentioned by someone else",file=stats_file );


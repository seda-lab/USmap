# USmap
Mapping the regions of the US with tweets. To setup you first have to compile the community detection code
```
cd gen-louvain
make
```
You run the code using
```
python3 twitter_map.py settings.ini
```
Runs the whole thing. There are a number of scripts. 

 - `extract.py` - Take a big JSON of tweets, only keep the useful ones and discard the useless fields.
 - `split_users.py` - Create a map  { user_id : [user_location1, user_location2, ...] }
 - `locate_users.py` - Create a map { user_id : [best_location] }
 - `build_network.py` - Create the communication network { box1 : {box_1, box2, box3, ...}, box2:{ box1, box2, box10, ...} }
 - `find_communities.py` - Run the Louvain algorithm and find communities in the communication network.
 - `refine_communities.py` - Attempt to increase modularity (community-ness) by re-assigning isolated boxes
 - `edit_communities.py` - Heuristic smothing.  Attempts to reassign 'orphan' tiles and empty tiles based on community assignment of neighbours.
 - `map_communities.py` - Print out some files which can be used to start at a lower hierarchical level.

Edit the settings file (or create a new one) to alter default settings (mostly filenames and polygons).

 

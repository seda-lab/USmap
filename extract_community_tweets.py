#!/usr/bin/env python
# coding: utf-8

# In[155]:


import ast
import configparser
import sys
import pandas as pd
import numpy as np
from shapely.geometry import box,point
from shapely.ops import cascaded_union


if len(sys.argv) < 2:
    print( "usage: python3 extract_community_tweets.py settings.ini")
    sys.exit(1);

config_fpath = sys.argv[1]
config = configparser.ConfigParser(allow_no_value=True)
config.read(config_fpath)

userfilename = "boxes.out"
county = None

# TODO adapt for counties
# if config.getboolean("global", "use_counties"):
#     county = county_lookup( config.get("global", "county_location") )

size = config.getint("global", "grid_size");

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
    datafile.close()

print("step 1")


# In[156]:


user = pd.DataFrame.from_dict(user_boxes, orient='index').reset_index().melt(id_vars = 'index')

print("step 2")


# In[157]:


user.drop(columns = 'variable',inplace = True)
user.dropna(inplace = True)
user.value=user.value.astype(int)

print("step 3")



nodelist = pd.read_csv('nodelist.csv')


print("step 4")



usermap = pd.merge(user,nodelist, how ='left',left_on='value',right_on='Id')

print("step 5")

# In[162]:


boxids = pd.read_json('boxids.json',orient= 'index').reset_index().rename(columns = {'index':'value',0:"box1",1:"box2"})
boxids.dropna(subset = ['box1','box2'],inplace = True)

print("step 6")


usermap=pd.merge(usermap,boxids,how = 'left',on='value')
usermap.dropna(subset = ['box1','box2'],inplace = True)

print("step 7")



usermap['box']= usermap.apply(lambda x: box(x["box1"][0],x["box1"][1],x["box2"][0],x["box2"][1]),axis = 1)

usermap.drop(columns = ['Id'],inplace = True)

usermap.dropna(subset = ['Label'],inplace = True)

print("step 8")


# In[210]:


def create_polygon(df,communitycol:str,boxcol:str):
    mapping = dict()
    for i in df[communitycol].unique():
        print(i)
        bounds = cascaded_union(usermap[df[communitycol]==i][boxcol])
        mapping.update({int(i):bounds})
    return mapping

def extract_community_tweets():

    for i in mapping.keys():
        print(f'extracting tweets for community {i}')
        with open(f'extract_community_tweets_{i}.out', 'w') as communitytweet:
            communitytweet.seek(0)
            with open('extract.out') as usertweets:

                for z in usertweets.readlines():
                    k =ast.literal_eval(z)
                    if sum([mapping[i].contains(point.asPoint(x)) for x in k[2]])>0:
                        communitytweet.write(k[0]+"\n")
                print(f'tweets extracted to extract_community_tweets_{i}.out')
                usertweets.close()

            communitytweet.close()

# In[234]:

if __name__ == "__main__":

    mapping = create_polygon(usermap,'Label','box')
    print("step 9")

    extract_community_tweets()




# In[ ]:





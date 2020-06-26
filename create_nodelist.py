#!/usr/bin/env python
# coding: utf-8

# In[41]:


import json
import pandas as pd


f = open("communities.out")
k = json.loads(f.read())

data = pd.DataFrame(k.values(),index = k.keys())

data.to_csv("nodelist.csv")


# In[ ]:





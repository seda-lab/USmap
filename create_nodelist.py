#!/usr/bin/env python
# coding: utf-8

# In[41]:


import json
import pandas as pd


f = open("communities.out")
k = json.loads(f.read())

data = pd.DataFrame(k.values(),index = k.keys()).reset_index()
data.columns = ['Id','Label']
data.set_index('Id',inplace = True)
data.to_csv("nodelist.csv")


# In[ ]:





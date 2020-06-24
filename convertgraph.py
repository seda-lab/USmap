#!/usr/bin/env python
# coding: utf-8

# In[40]:


import sys, getopt
import re
def main(argv):
    
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print('Input file is ', inputfile)
    print('Output file is ', outputfile)

    if(all(x in dict(opts).keys() for x in ['-i','-o'])):


        f = open(inputfile, 'r')
        outfile = open(outputfile,'w')
        outfile.seek(0)
        outfile.write("Source,Target,Weight \n")
        data = f.readlines()
        for i in data:
            i = re.sub(' ',',',i)
            outfile.write(i)
    else:
        print("missing inputs and/or outputs")

if __name__ == "__main__":
    main(sys.argv[1:])


# In[ ]:





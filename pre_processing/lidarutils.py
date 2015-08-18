# Code built by Gorgens E. B. and Assis M.
# Brazil, Aug 2015

# Dependencies: numpy, laspy, math
# coding: utf-8

# Environment setting

# In[3]:

import os.path
import time
import argparse
import numpy as np
import math
from laspy import file
import warnings

def saveCloud(fname,header,cloud):
    outFile = file.File(fname, mode = "w", header = header)
    outFile.points = cloud
    outFile.close()

def splitInCelsParseCmdLine():
    parser = argparse.ArgumentParser(description="Some useful features to deal with LiDAR files.")
    parser.add_argument("inputfname",help="las file to be process.")
    parser.add_argument("-t","--task",choices=['a'], required=True, help="define task to be done.\r\n 'a' cut the file generating cellsize square clouds")
    parser.add_argument("-c","--cellsize", type= float, help="size of the cells that will be processed.", default = 50)
    parser.add_argument("-s","--silent", type=int, help="hide processing messages.", default = False)
    args = parser.parse_args()
    if (not args.silent):
        print("Processing: {0}".format(args.inputfname))
        print("Cellsize: {0}".format(args.cellsize))
    return args

def checkParams(args):
    if not os.path.exists(args.inputfname):
        Exception("File {0} doesn't exists.".format(args.inputfname))
    
def splitincells(inputfname, cellsize=50, silent=False):
    start = time.time()
    
    inFile = file.File(inputfname, mode = "r")
    accepted_logic = []              # List to save the true/false for each looping
    maxStep = []                     # List to save the number of cells in X and Y dimension of original data
    warningMsg = []    
    
    xmin = inFile.x.min()
    xmax = inFile.x.max()
    ymin = inFile.y.min()
    ymax = inFile.y.max()
    
    maxStep.append(math.ceil((xmax - xmin) / cellsize))
    maxStep.append(math.ceil((ymax - ymin) / cellsize))
    if not silent:
        print("The original cloud was divided in {0} by {1} cells.".format(maxStep[0],maxStep[1]))

# In[44]:

    n = 0
    for stepX in range(int(maxStep[0])):                 # Looping over the lines
        for stepY in range(int(maxStep[1])):             # Looping over the columns
            # Step 1 - Filter data from the analized cell
            # Return True or False for return inside the selected cell

            X_valid = np.logical_and((xmin + (stepX * cellsize) <= inFile.x),
                                 (xmin + ((stepX + 1) * cellsize) > inFile.x))
            Y_valid = np.logical_and((ymin + (stepY * cellsize) <= inFile.y),
                                 (ymin + ((stepY + 1) * cellsize) > inFile.y))
            logicXY = np.logical_and(X_valid, Y_valid)
            validXY = np.where(logicXY)

            # show progress before 'continue'
            n += 1
            if(not silent):
                 percent = n/(maxStep[0] * maxStep[1])
                 hashes = '#' * int(round(percent * 20))
                 spaces = ' ' * (20 - len(hashes))
                 print("\r[{0}] {1:.2f}%".format(hashes + spaces, percent * 100)),

            if(len(validXY[0]) == 0):
                accepted_logic.append(False)
                if(not silent):
                    warningMsg.append("Cell {0},{1} has no points, corresponding file was not created.".format(stepX,stepY))
                continue
            
            fnametile = "{0}_{1}_{2}".format(stepX,stepY,os.path.basename(inputfname))
            saveCloud(fnametile,inFile.header,inFile.points[logicXY])
# In[48]:
    if(not silent):
        print
        if (len(warningMsg) > 0):
            print
            print("Warnings:")
            print("{0}".format("\r\n".join(str(i) for i in warningMsg)))
        print
        print("Done in {0}s.".format(int(time.time()-start)))

def main():
    warnings.simplefilter("error", RuntimeWarning)
    args=splitInCelsParseCmdLine()
    checkParams(args)
    print args
    if(args.task == 'a'):
        splitincells(args.inputfname,args.cellsize,args.silent)
# In[ ]:

if __name__ == "__main__":
    main()

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

def parseCmdLine():
    parser = argparse.ArgumentParser(description="Process outlier filter in LAS files.")
    parser.add_argument("inputfname",help="las file to be process.")
    parser.add_argument("-o","--outputfname", help="las output file.")
    parser.add_argument("-c","--cellsize", type=float, help="size of the cells that will be processed.", default = 50)
    parser.add_argument("-t","--tolerance", type= float, help="number of std deviations will be considered not outlier.",default = 3.0)
    parser.add_argument("-r","--removedcloud", help="create a new LAS file storing removed points", action='store_true', default = False)
    parser.add_argument("-s","--silent", help="hide processing messages.", default = False)
    args = parser.parse_args()
    if (not args.silent):
        print("Processing: {0}".format(args.inputfname))
        print("Cellsize: {0}".format(args.cellsize))
        print("Tolerance: {0}".format(args.tolerance))   # The deviation from the mean to be considered outlier
    return args

def checkParams(args):
    if not os.path.exists(args.inputfname):
        Exception("File {0} doesn't exists.".format(args.inputfname))

#        
#def saveCloud(fname,header,cloud):
#    outFile = file.File(fname, mode = "w", header = header)
#    outFile.points = cloud
#    outFile.close()
    

def outlier(inputfname, outputfname=None, cellsize=50, tolerance=3.0, removedcloud=False, silent=False):
    start = time.time()
    
    inFile = file.File(inputfname, mode = "r")
    accepted_logic = []              # List to save the true/false for each looping
    maxStep = []                     # List to save the number of cells in X and Y dimension of original data
    
    xmin = inFile.x.min()
    xmax = inFile.x.max()
    ymin = inFile.y.min()
    ymax = inFile.y.max()
    
    maxStep.append(math.ceil((xmax - xmin) / cellsize))
    maxStep.append(math.ceil((ymax - ymin) / cellsize))
    if not silent:
        print("The original cloud was divided in {0} by {1} cells.".format(maxStep[0],maxStep[1]))

    # 1. Find return of the cell of interest
    # 2. Compute standard deviation
    # 3. Determine the outliers based on the tolerance * standard deviation

# In[44]:

    #stepX = 2         # Select specific line to analise
    #stepY = 1         # Select specific column to analise


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
                continue
                        
            # Step 2 - Compute the standard deviation
            #print np.std(inFile.z), np.std(inFile.z[validXY])
            
            try:
            # Step 3 - Determine the outliers
                Z_valid = np.logical_and((np.mean(inFile.z[validXY]) - tolerance * np.std(inFile.z[validXY]) <= inFile.z),
                                 (np.mean(inFile.z[validXY]) + tolerance * np.std(inFile.z[validXY]) > inFile.z))
                logicXYZ = np.logical_and(logicXY, Z_valid)

            except Exception, e:
                if (not silent):
                    print("Error {0} in tile: {1}, {2}".format(e.args, stepX,stepY))
        
            accepted_logic.append(logicXYZ)

            # Select from the original cloud the good returns.
# In[46]:

    print("")
    acceptedXYZ = np.zeros((len(inFile.x)), dtype=bool)
    for i in range(int(maxStep[0] * maxStep[1])):
        acceptedXYZ = np.logical_or(acceptedXYZ, accepted_logic[i])
        
    if(not silent):
        print("There are {0} returns in the original cloud.\r\n{1} returns were removed based on the outlier rule.".format(len(inFile.z),len(inFile.z) - len(inFile.z[acceptedXYZ]))) 

# In[48]:

    if(not silent):
        print("Saving {0} points...".format(len(inFile.z[acceptedXYZ])))
    outputfname = outputfname if not(outputfname == None) else "noOutlier_"+os.path.basename(inputfname)
    saveCloud(outputfname,inFile.header,inFile.points[acceptedXYZ])

    if(removedcloud):
        print("Saving removed cloud...")
        outputfname = outputfname.replace("noOutlier_","outlier_")
        saveCloud(outputfname,inFile.header,inFile.points[np.logical_not(acceptedXYZ)])
    
    if(not silent):
        print("Done in {0}s.".format(int(time.time()-start)))

def main():
    warnings.simplefilter("error", RuntimeWarning)
    args=parseCmdLine()
    checkParams(args)
    outlier(args.inputfname,args.outputfname,args.cellsize,args.tolerance,args.removedcloud,args.silent)
# In[ ]:

if __name__ == "__main__":
    main()

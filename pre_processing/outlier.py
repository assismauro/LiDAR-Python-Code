# Code built by Gorgens E. B. and Assis M.
# Brazil, Aug 2015

# Dependencies: numpy, laspy, math
# coding: utf-8

# Environment setting

# In[3]:

import os.path
import argparse
import numpy as np
import math as m
from laspy import file

def parseCmdLine():
    parser = argparse.ArgumentParser(description="Process outlier filter in LAS files.")
    parser.add_argument("inputfname",help="las file to be process ('.LAS' is not mandatory).")
    parser.add_argument("-o","--outputfname", help="las output file ('.LAS' is not mandatory).")
    parser.add_argument("-c","--cellsize", help="size of the cells that will be processed.", default = 50)
    parser.add_argument("-t","--tolerance", type= float, help="number of std deviations will be considered not outlier.",default = 3.0)
    parser.add_argument("-s","--silent", type= float, help="hide processing messages.",default = False)
    args = parser.parse_args()
    if (not args.silent):
        print("Processing:",args.inputfname)
        print("Cellsize:",args.cellsize)    # Define the cell size of the grid
        print("Tolerance:",args.tolerance)   # The deviation from the mean to be considered outlier
    return args

def checkParams(args):
    if not os.path.exists(args.inputfname):
        Exception("File {0} doesn't exists.".format(args.inputfname))

def outlier(inputfname, outputfname=None, cellsize=50, tolerance=3.0, silent=False):
    inputfname=inputfname if inputfname.lower().endswith(".las") else inputfname+".las"
    inFile = file.File(inputfname, mode = "r")
    filtered_logic = []              # List to save the true/false for each looping
    maxStep = []                     # List to save the number of cells in X and Y dimension of original data
    maxStep.append(m.ceil((inFile.x.max() - inFile.x.min()) / cellsize))
    maxStep.append(m.ceil((inFile.y.max() - inFile.y.min()) / cellsize))
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
            X_valid = np.logical_and((inFile.x.min() + (stepX * cellsize) <= inFile.x),
                                 (inFile.x.min() + ((stepX + 1) * cellsize) > inFile.x))
            Y_valid = np.logical_and((inFile.y.min() + (stepY * cellsize) <= inFile.y),
                                 (inFile.y.min() + ((stepY + 1) * cellsize) > inFile.y))
            logicXY = np.logical_and(X_valid, Y_valid)
            validXY = np.where(logicXY)

            # Step 2 - Compute the standard deviation
            #print np.std(inFile.z), np.std(inFile.z[validXY])

            # Step 3 - Determine the outliers
            Z_valid = np.logical_and((np.mean(inFile.z[validXY]) - tolerance * np.std(inFile.z[validXY]) <= inFile.z),
                                 (np.mean(inFile.z[validXY]) + tolerance * np.std(inFile.z[validXY]) > inFile.z))
            logicXYZ = np.logical_and(logicXY, Z_valid)
            validXYZ = np.where(logicXYZ)
            #print str(len(validXY[0]) - len(validXYZ[0])) + ' returns removed'
        
            filtered_logic.append(logicXYZ)
            n += 1
            if(not silent):
                print("\r{0:.2f} % processed.".format(round(n/(maxStep[0] * maxStep[1])*100, 2))), 

            # Select from the original cloud the good returns.
# In[46]:

    print
    validXYZ = np.zeros((len(inFile.x)), dtype=bool)
    for i in range(stepX * stepY):
        validXYZ = np.logical_or(validXYZ, filtered_logic[i])
    
    print("{0} returns were removed based on the outlier rule".format(len(inFile.z) - len(inFile.z[validXYZ]))) 


# In[48]:
    outputfname = outputfname if not(outputfname == None) else "noOutlier_"+os.path.basename(inputfname)
    outputfname = outputfname if outputfname.lower().endswith(".las") else outputfname+".las"
    if(not silent):
        print("Saving...")
    outFile1 = file.File(outputfname, mode = "w",
                     header = inFile.header)
    outFile1.points = inFile.points[validXYZ]
    outFile1.close()
    if(not silent):
        print("Done.")

def main():
    args=parseCmdLine()
    checkParams(args)
    outlier(args.inputfname,args.outputfname,args.cellsize,args.tolerance,args.silent)
# In[ ]:

if __name__ == "__main__":
    main()

# Code built by Gorgens E. B. and Assis M.
# Brazil, Aug 2015

# Dependencies: numpy, laspy, math
# coding: utf-8

# Environment setting

# In[3]:

import os.path
import time
import argparse
from argparse import RawTextHelpFormatter
import numpy as np
import math
from laspy import file
import warnings

def saveCloud(fname,header,cloud):
    outFile = file.File(fname, mode = "w", header = header)
    outFile.points = cloud
    outFile.close()

def ParseCmdLine():
    parser = argparse.ArgumentParser(description="Some useful features to deal with LiDAR files.",formatter_class=RawTextHelpFormatter)
    parser.add_argument("inputfname",help="las file to be process.")
    parser.add_argument("-t","--task",choices=['p','b','d','x','s','t','f'], required=True, 
        help="""
define task to be done.
  'd' display information about LAS file.
  'f' create new file with z coord = floor parameter
  't' create one slice from top, with p percent 
  'b' create one slice from bottom, with p percent 
  'p' split LAS file generating cellsize squared clouds.
  's' slices file in 'ns' slices.
  'x' export LAS points to csv file.
        """)
    parser.add_argument("-o","--outputfname", help="output file name.", default = None)
    parser.add_argument("-c","--cellsize", type= float, help="size of the cells that will be processed.", default = 50)
    parser.add_argument("-f","--floor", type=float,help="floor value for toFloor function")
    parser.add_argument("-ns","--nslices",type=int,help="number of slices",default=5)
    parser.add_argument("-p","--percent", type=float,help="percent value for t or b function")    
    parser.add_argument("-v","--verbose", type=int, help="show processing messages.", default = True)
    args = parser.parse_args()
    return args
    
def checkParams(args):
    if not os.path.exists(args.inputfname):
        Exception("File {0} doesn't exists.".format(args.inputfname))

def displayHeader(header):
    print("Header:")
    print("File signature : {0}".format(header.file_signature))
    print("File source id : {0}".format(header.file_source_id))
    print("Global encoding: {0}".format(header.global_encoding))
    print("Project id     : {0}".format(header.project_id))
    print("Version        : {0}".format(header.version))
    print("System id      : {0}".format(header.system_id))
    print("Software id    : {0}".format(header.software_id))
    print("Date           : {0}".format(header.date))    
    print("Points count   : {0}".format(header.point_records_count))
    print("Scale x,y,z    : {0}".format(header.scale))
    print("Offset x,y,z   : {0}".format(header.offset))
    print("Max Values     : {0}".format(header.max))
    print("Min Values     : {0}".format(header.min))
    
def splitCells(inputfname, cellsize=50, verbose=False):
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
    if verbose:
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
            if(verbose):
                 percent = n/(maxStep[0] * maxStep[1])
                 hashes = '#' * int(round(percent * 20))
                 spaces = ' ' * (20 - len(hashes))
                 print("\r[{0}] {1:.2f}%".format(hashes + spaces, percent * 100)),

            if(len(validXY[0]) == 0):
                accepted_logic.append(False)
                if(verbose):
                    warningMsg.append("Cell {0},{1} has no points, corresponding file was not created.".format(stepX,stepY))
                continue
            
            fnametile = "{0}_{1}_{2}".format(stepX,stepY,os.path.basename(inputfname))
            saveCloud(fnametile,inFile.header,inFile.points[logicXY])
# In[48]:
    if(verbose):
        print
        if (len(warningMsg) > 0):
            print
            print("Warnings:")
            print("{0}".format("\r\n".join(str(i) for i in warningMsg)))
        print
        print("Done in {0}s.".format(int(time.time()-start)))

def slices(inputfname,nslices,verbose):
    start = time.time()

    warningMsg = []    

    inFile = file.File(inputfname, mode = "r")
    zmin = inFile.z.min()
    zmax = inFile.z.max()
    hn = (zmax-zmin)/nslices
    accepted_logic = []              # List to save the true/false for each looping
    for stepZ in range(nslices):
        Z_valid = np.logical_and((zmin + (stepZ * hn) <= inFile.z),
                                 (zmin + ((stepZ + 1) * hn) > inFile.z))
        validZ = np.where(Z_valid)
        
        # show progress before 'continue'
        if(verbose):
            percent = float(stepZ+1)/nslices
            hashes = '#' * int(round(percent * 20))
            spaces = ' ' * (20 - len(hashes))
            print("\r[{0}] {1:.2f}%".format(hashes + spaces, percent * 100)),
        if(len(validZ[0]) == 0):
            accepted_logic.append(False)
            if(verbose):
                warningMsg.append("Slice {0} has no points, corresponding file was not created.".format(stepZ))
            continue
             
        fnameslice = "slice{0}_{1}".format(stepZ,os.path.basename(inputfname))
        saveCloud(fnameslice,inFile.header,inFile.points[validZ])               
    
    if(verbose):
        print
        if (len(warningMsg) > 0):
            print
            print("Warnings:")
            print("{0}".format("\r\n".join(str(i) for i in warningMsg)))
        print
        print("Done in {0}s.".format(int(time.time()-start)))    

def toFloor(inputfname,outputfname="",floor=0,verbose=True):
    inFile = file.File(inputfname, mode = "rw")
    z=inFile.z
    z.fill(floor);
    inFile.z=z
    outputfname = outputfname if not(outputfname == None) else "toFloor_"+os.path.basename(inputfname)
    saveCloud(outputfname,inFile.header,inFile.points)

def topBottom(command,inputfname,outputfname="",percent=5.0,verbose=True):
    inFile = file.File(inputfname, mode = "rw")
    r=(inFile.z.max() - inFile.z.min()) * percent / 100.0 + inFile.z.min()
    if(command == 'b'):
        Z_valid = np.logical_and(inFile.z <= r,True)
        strFunc='bottom_'
    else: # top
        r=inFile.z.max()-r
        Z_valid = np.logical_and(inFile.z >= r,True)
        strFunc='top_'
    validZ = np.where(Z_valid)
    outputfname = outputfname if not(outputfname == None) else strFunc+os.path.basename(inputfname)
    saveCloud(outputfname,inFile.header,inFile.points[validZ])
        
    
def exportToCSV(inputfname,outputfname="",delimiter=";",verbose=True):
    inFile = file.File(inputfname, mode = "r")
    if(outputfname == ""):
        outputfname = inputfname.rsplit(".",1)[0]+".csv"
    headercsv = ""
    for spec in inFile.point_format:
        headercsv += "{0}{1}".format(spec.name,delimiter)
    headercsv = headercsv[:-1]
    
    output = open(outputfname,"w")
    
    output.write(headercsv+"\n")
    
    for data_tile in inFile.points:
        txtline=""
        for line in data_tile:
            for value in line:
                txtline+="{0}{1}".format(value,delimiter)
            output.write(txtline[:-1]+"\n")
    output.close()
    
def displayInfo(inputfname,verbose):
    inFile = file.File(inputfname, mode = "r")    
    displayHeader(inFile.header)
    print("\r\nPoint format:")
    for spec in inFile.point_format:
        print(spec.name)

def main():
    warnings.simplefilter("error", RuntimeWarning)
    args=ParseCmdLine()
    checkParams(args)
    if(args.task == 'p'):
        splitCells(args.inputfname,args.cellsize,args.verbose)
    elif(args.task == 's'):
        slices(args.inputfname,args.nslices,args.verbose)
    elif(args.task == 'd'):
        displayInfo(args.inputfname,args.verbose)
    elif(args.task == 'x'):
        exportToCSV(args.inputfname,args.outputfname,";",args.verbose)
    elif(args.task == 'f'):
        toFloor(args.inputfname,args.outputfname,args.floor)
    elif((args.task == 'b') or (args.task == 't')):
        topBottom(args.task,args.inputfname,args.outputfname,args.percent,args.verbose)
        
        
# In[ ]:

if __name__ == "__main__":
    main()

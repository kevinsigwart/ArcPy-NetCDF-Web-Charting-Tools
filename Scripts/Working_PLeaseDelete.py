################################################################################
# TempStatsToMosaicDataset_Noman.py.py
# Description: Create Mosaic Datasets for all temperature statistics variables
# Requirement: Spatial Analyst Extension
# Author: Nawajish Noman
# Version: 1.0
#Last update: 11/09/2011
################################################################################
# Assumptions
# 1. NetCDF files and the boundary featureclass are in netcdffile folder
# 2. There is a output and a scratch folders (must be empty)
# 3. This script, the netcdffile, output, and scratch folders are all at the same
#    level in a folder
################################################################################
# TODO: By Dan Z or NGC
# 0. Look for NSN:REMOVE and remove code segment to make script work on full set
# 1. Add try except block as needed
# 2. Add a loop to loop through netCDF files from the netcdffile folder
################################################################################
# Import system modules
import os
import sys
import shutil
import arcpy
import string
import time
from arcpy import env
from arcpy.sa import *


inNetCDF = arcpy.GetParameterAsText(0)
#master_dir = "C:\dzimble\Climate\\"
list_of_files = []
#for root, dirs, files in os.walk(master_dir):
#    for file in files:
#        if file.endswith('.nc'):
#            list_of_files.append(os.path.abspath(os.path.join(root,file)))
list_of_files.append(inNetCDF)
#print list_of_files
#print len(list_of_files)

################################################################################
# Input parameters <<<UPDATE this block>>>>
for inNetCDFFile in list_of_files:
    print "Current file: " + inNetCDFFile
    #inNetCDFFile = "C:\dzimble\Climate\\frost_days\d03_frost_days_echam_current.nc"

    #use the path from the input netcdf file to create output directory
    o_path = os.path.dirname(inNetCDFFile)
    base = os.path.basename(inNetCDFFile)
    spl = base.split('.')


    ncXDim = "west_east"
    ncYDim = "south_north"
    ncTimeDim = "time"

    ncXDimAuCoord = "lon"
    ncYDimAuCoord = "lat"

    #inNetCDFBndFc = "TempStatBnd.shp" #Create this bnd manually (for now)
    # If you don't have a boundary feature class then comment out clipping below.
    ################################################################################
    # Make data path relative and update

    #netcdflilePath = sys.path[0] + os.sep 
    outPath = o_path + os.sep + spl[0] + "_output"
    scratchPath = sys.path[0] + os.sep + "scratch"

    if not os.path.exists(scratchPath):
    #    shutil.rmtree(scratchPath)
        os.makedirs(scratchPath)

    #time.sleep(120)
    #if os.path.exists(scratchPath):
    #    for root, dirs, files in os.walk(scratchPath, topdown=False):
    #        for name in files:
    #            os.remove(os.path.join(root, name))
            #for name in dirs:
            #    os.rmdir(os.path.join(root, name))
    #os.makedirs(scratchPath)

    if not os.path.exists(outPath):
    #    shutil.rmtree(outPath)
        os.makedirs(outPath)
    
    #if os.path.exists(outPath):
    #    for root, dirs, files in os.walk(outPath, topdown=False):
    #        for name in files:
    #            os.remove(os.path.join(root, name))
            #for name in dirs:
            #    os.rmdir(os.path.join(root, name))
    #os.makedirs(outPath)
    
    #time.sleep(10)
    #inNetCDFFile = netcdflilePath + os.sep + inNetCDFFile
    #inNetCDFBndFc = netcdflilePath + os.sep + inNetCDFBndFc

    # arcpy environment settings
    env.workspace = scratchPath
    env.overwriteOutput = 1

    # Check out the ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")

    ##==============================================================================
    #Loop through files from here
    ##==============================================================================
    # Find out all variables that share dimension ncX, ncY, and ncTimeDim
    # and the size of the time dimension

    ncFileProp = arcpy.NetCDFFileProperties(inNetCDFFile)
    ncVarsXDim = ncFileProp.getVariablesByDimension(ncXDim)
    ncVarsYDim = ncFileProp.getVariablesByDimension(ncYDim)
    ncVarsTimeDim = ncFileProp.getVariablesByDimension(ncTimeDim)
    ncVarsXYTimeDim = list(set(ncVarsXDim) & set(ncVarsYDim) & set(ncVarsTimeDim))

    print ncVarsXYTimeDim #NSN:REMOVE
    #[u'T2_AVE_INTERANNUAL_VARIANCE', u'T2_MIN', u'T2_MAX_INTERANNUAL_VARIANCE',
    # u'T2_AVE', u'T2_MIN_DAILY_VARIANCE', u'T2_MAX_DAILY_VARIANCE', u'T2_MAX_STDERR',
    # u'T2_AVE_STDERR', u'T2_MIN_INTERANNUAL_VARIANCE', u'T2_MAX',
    # u'T2_AVE_DAILY_VARIANCE', u'T2_MIN_STDERR']

    #ncVarsXYTimeDim = ['T2_MIN', 'T2_MAX'] #NSN:REMOVE
    #print ncVarsXYTimeDim #NSN:REMOVE

    # Find out the size of ncTimeDim
    ncXDimSize = ncFileProp.getDimensionSize(ncXDim)
    ncYDimSize = ncFileProp.getDimensionSize(ncYDim)
    ncTimeDimSize = ncFileProp.getDimensionSize(ncTimeDim)
    #print ncXDimSize, ncYDimSize, ncTimeDimSize #NSN:REMOVE
    #ncTimeDimSize = 2 #NSN:REMOVE

    ##==============================================================================
    # Make lon and lat tables to get distances between points
    # Minimum interval will be used to compute cellsize

    ncXDimAuCoordTableView = "ncXDimAuCoordTableView"
    result = arcpy.MakeNetCDFTableView_md(inNetCDFFile,ncXDimAuCoord,
             ncXDimAuCoordTableView,ncXDim)

    searchCursor = arcpy.da.SearchCursor(ncXDimAuCoordTableView,[ncXDimAuCoord])
    ncXDimAuCoordValues = [row[0] for row in searchCursor]
    ncXDimAuCoordInterval = min(abs(ncXDimAuCoordValues[1]-ncXDimAuCoordValues[0]),
                                abs(ncXDimAuCoordValues[ncXDimSize-1]-
                                    ncXDimAuCoordValues[ncXDimSize-2]))

    ncYDimAuCoordTableView = "ncYDimAuCoordTableView"
    result = arcpy.MakeNetCDFTableView_md(inNetCDFFile,ncYDimAuCoord,
             ncYDimAuCoordTableView,ncYDim)

    searchCursor = arcpy.da.SearchCursor(ncYDimAuCoordTableView,[ncYDimAuCoord])
    ncYDimAuCoordValues = [row[0] for row in searchCursor]
    ncYDimAuCoordInterval = min(abs(ncYDimAuCoordValues[1]-ncYDimAuCoordValues[0]),
                                abs(ncYDimAuCoordValues[ncYDimSize-1]-
                                ncYDimAuCoordValues[ncYDimSize-2]))

    #print ncXDimAuCoordInterval, ncYDimAuCoordInterval #NSN:REMOVE

    ##==============================================================================
    # For each variable and timesteps, create netCDF feature layer and create
    # a raster using an interpolation method (using Natural Neighbor)
    # Clip the output from interpolation

    for ncVar in ncVarsXYTimeDim:
        print "Processing variable " + ncVar #NSN:REMOVE
        ncVarFolderPath = scratchPath + os.sep + ncVar.lower()
        if not os.path.exists(ncVarFolderPath):
            os.makedirs(ncVarFolderPath) #TODO: Check if exist, delete if necessary

        for t in range(ncTimeDimSize):
            outNcFeatureLayer = "outNcFeatureLayer"
            rowDimensions = str(ncXDim + ';' + ncYDim)
            ncTimeDimValue = str(ncTimeDim + ' ' + str(t))
            valueSelectionMethod = "BY_INDEX"
            #print rowDimensions, ncTimeDimValue #NSN:REMOVE

            #Execute MakeNetCDFFeatureLayer
            result = arcpy.MakeNetCDFFeatureLayer_md(inNetCDFFile,ncVar,
                     ncXDimAuCoord,ncYDimAuCoord,outNcFeatureLayer,rowDimensions,
                     "","",ncTimeDimValue,valueSelectionMethod)

            rasSuffix = str(t).zfill(len(str(ncTimeDimSize)))
            outRasName = ncVar.lower() + rasSuffix + ".img" #Creating grid, add .tif for tiff
            outRasName = ncVarFolderPath + os.sep + outRasName
            print outRasName #NSN:REMOVE

            # Execute NaturalNeighbor and save it
            cellSize = min(ncXDimAuCoordInterval, ncYDimAuCoordInterval)/2 #0.052 adjust if necessary
            outRas = NaturalNeighbor(outNcFeatureLayer,ncVar,cellSize)
            outRas.save(outRasName) #TODO: Uncomment this if you comment out clipping
            
            spRef = arcpy.Describe(outRasName).spatialReference
            #print spRef.name, spRef.domain #NSN:REMOVE
            ####del outRasName
            
            # Check if file can be opened, and close if necessary, not working due to other process running
            #fd = os.open(outRasName, os.O_RDWR + os.O_EXCL)
            #os.close(fd);

            #Please uncomment outRas.save(outRasName) if you comment out clipping
            #Clip it using the boundary
            #result = arcpy.Clip_management(outRas,"",outRasName,
                     #inNetCDFBndFc,"","ClippingGeometry")

    ##==============================================================================
    # For each variable create a filegeodatabase and a mosaic dataset
    # Add rasters to mosaic dataset, calculate statistics
    # Add time field and add index



    ncTimeTableView = ncTimeDim + "TableView"
    result = arcpy.MakeNetCDFTableView_md(inNetCDFFile,ncTimeDim,
             ncTimeTableView,ncTimeDim)

    for ncVar in ncVarsXYTimeDim:
        ncVarFolderPath = scratchPath + os.sep + ncVar.lower()

        result = arcpy.CreateFileGDB_management(outPath,ncVar)
        fgdbPath = outPath + os.sep + ncVar + ".gdb"
        result = arcpy.CreateMosaicDataset_management(fgdbPath,ncVar,spRef)
        mosaicDatasetPath = fgdbPath + os.sep + ncVar

        result = arcpy.SetMosaicDatasetProperties_management(mosaicDatasetPath,"",
                 "","","","","","","","","","","","","","","","","","","",ncTimeDimSize)
        result = arcpy.AddRastersToMosaicDataset_management(mosaicDatasetPath,
                 "Raster Dataset",ncVarFolderPath)
        del ncVarFolderPath
        result = arcpy.CalculateStatistics_management(mosaicDatasetPath)

        mosaicTableView = ncVar + "TableView"
        result = arcpy.MakeTableView_management(mosaicDatasetPath,mosaicTableView)
        result = arcpy.JoinField_management(mosaicTableView,"OBJECTID",
                 ncTimeTableView,"OID",ncTimeDim)
        result = arcpy.AddIndex_management(mosaicDatasetPath,ncTimeDim,ncTimeDim,
                 "UNIQUE","ASCENDING")
        print "Done with variable " + ncVar #NSN:REMOVE



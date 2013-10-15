import os
import sys
import shutil
import arcpy
import string
import time
import scipy.io.netcdf as netcdf

from arcpy import env
from arcpy.sa import *

#inNetCDF = arcpy.GetParameterAsText(0)
inNetCDF = "C:\Sandbox\python\NetCDF\Data\d03_frost_days_echam_current.nc"
ncXDim = "west_east"
ncYDim = "south_north"
ncTimeDim = "time"

ncXDimAuCoord = "lon"
ncYDimAuCoord = "lat"


arcpy.CheckOutExtension("Spatial")

ncFileProp = arcpy.NetCDFFileProperties(inNetCDF)

ncVarsXDim = ncFileProp.getVariablesByDimension(ncXDim)
ncVarsYDim = ncFileProp.getVariablesByDimension(ncYDim)
ncVarsTimeDim = ncFileProp.getVariablesByDimension(ncTimeDim)
ncVarsXYTimeDim = list(set(ncVarsXDim) & set(ncVarsYDim) & set(ncVarsTimeDim))

ncXDimSize = ncFileProp.getDimensionSize(ncXDim)
ncYDimSize = ncFileProp.getDimensionSize(ncYDim)
ncTimeDimSize = ncFileProp.getDimensionSize(ncTimeDim)

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
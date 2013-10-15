import os
import sys
import math
import arcpy

inNetCDF = "C:/Sandbox/python/NetCDF/Data/norfolk_slr_1m.nc"
ncFileProp = arcpy.NetCDFFileProperties(inNetCDF)
variables = ncFileProp.getVariables();
dimensions = ncFileProp.getDimensions();

timeVariable = ncFileProp.getVariablesByDimension("time")

from netCDFFile import NetCDFFile

print NetCDFFile.isNetCDF(inNetCDF)

netcdfFile = NetCDFFile(inNetCDF)


print netcdfFile.getDimensions()
print netcdfFile.getVariables()
print netcdfFile.getLatDimension()
print netcdfFile.getLonDimension()


print str(variables)
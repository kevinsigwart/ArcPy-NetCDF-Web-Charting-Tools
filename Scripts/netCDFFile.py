'''
All rights reserved under the copyright laws of the United States.

You may freely redistribute and use this sample code, with or without modification.  
The sample code is provided without any technical support or updates.

Disclaimer OF Warranty: THE SAMPLE CODE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
INCLUDING THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR 
NONINFRINGEMENT ARE DISCLAIMED. IN NO EVENT SHALL ESRI OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED 
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) SUSTAINED BY YOU OR A THIRD PARTY, HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT ARISING IN ANY WAY OUT OF THE USE OF THIS SAMPLE 
CODE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  THESE LIMITATIONS SHALL APPLY NOTWITHSTANDING 
ANY FAILURE OF ESSENTIAL PURPOSE OF ANY LIMITED REMEDY.

For additional information contact: Environmental Systems Research Institute, Inc.
Attn: Contracts Dept.
380 New York Street
Redlands, California, U.S.A. 92373 
Email: contracts@esri.com
'''

import arcpy
import os
import time

class NetCDFFile(object):
    """-------------------------------------------------------------------------------------
    Class Name: NetCDFFile
    Creation Date: 3/1/2012
    Creator: KSigwart
    Description: This is a helper class that extends the NetCDFFile Properties to be more in
                 line with tools that let users interact with a netCDF file in forms of
                 lat/lon points.  
    Inputs:
            netCDF file path:  The location of a netCDF file
    -------------------------------------------------------------------------------------"""  
    
    #Class Parameters
    __sourceLocation = ''
    __variables = list()
    __dimensions = list()
    __latDimension = 'lat'
    __lonDimension = 'lon'
    __latValue = 0
    __lonValue = 0
    
    
    def __init__(self,netCDFloc):
        '''
         Defines the Class Properties based off the the NetCDF File Properties inputed
        '''        
        ncFileProp = arcpy.NetCDFFileProperties(netCDFloc)
        self.__ncFileProperties = ncFileProp
        
        self.__sourceLocation = netCDFloc;
        self.__determineDimensions()
        self.__determineVariables()

        
    def __determineDimensions(self):
        '''
         We only want the dimensions that are not lat and lon.  The lat, lon 
         dimensions are already being described by the point that will be mapped 
         by the user.
        '''
        dimensions = self.__ncFileProperties.getDimensions();     
        
        #Storing lat and lon dimensions to get the varables associated with both
        dimList = list(dimensions)
        newDimList = list()
        for dim in dimList:
            #if str(dim).lower().startswith('lat'):
            if 'lat' in str(dim).lower():
                self.__latDimension = str(dim)
            #elif str(dim).lower().startswith('lon'):
            elif 'lon' in str(dim).lower():
                self.__lonDimension = str(dim)
            else:
                newDimList.append(dim);   
        
        self.__dimensions = newDimList         
        return newDimList
    
    def __determineVariables(self):
        '''
         We only want variables that have a lat and long dimensions b/c we are
         mapping the variable to a point.  Also, lat and lon are already described
         by the point.
        '''
        latVariables = list(self.__ncFileProperties.getVariablesByDimension(self.__latDimension))
        lonVariables = list(self.__ncFileProperties.getVariablesByDimension(self.__lonDimension))
        
        variables = list()
        
        for variable in latVariables:
            if (variable != self.__latDimension and variable != self.__lonDimension) and variable in lonVariables:
                variables.append(variable)        
                
        self.__variables = variables    
        
        return variables
    
    def __is0to360(self):
        '''
        We need to check to get the Min and Max lon values to determine if
        the dataset goes from 0 - 360 or -180 - 180
        '''
        
        is0to360 = False
        
        netCDFProp = self.__ncFileProperties;
        dimLen = netCDFProp.getDimensionSize(self.__lonDimension);
        
        #Determining the min and max dim.  Looking for values less than 0 and/or greater
        #than 180
        minLon = 360
        maxLon = -180
        start = time.time()
        
        for index in range(0,dimLen):
            
            value = netCDFProp.getDimensionValue(self.__lonDimension,index)
            elapsed = (time.time() - start)
            arcpy.AddMessage("Get Dimension Value for index: " + str(index) + "...." +  str(elapsed))
            
            
            if value < minLon:
                minLon = value;
            if value > maxLon:
                maxLon = value;
        
        arcpy.AddMessage("Min Lon Value: " + str(minLon))  
        arcpy.AddMessage("Max Lon Value: " + str(maxLon))  
        
        #Checking if the min and or max values fall in the right range
        if minLon >= 0 and maxLon > 180:
            is0to360 = True
        
        arcpy.AddMessage("Is 0 to 360" + str(is0to360))  
        
        return is0to360
    
    def getDimensions(self):
        return self.__dimensions
    
    def getVariables(self):
        return self.__variables
    
    def getLatDimension(self):
        return self.__latDimension
    
    def getLonDimension(self):
        return self.__lonDimension
    
    def getLatValue(self):
        return self.__latValue
    
    def getLonValue(self):
        return self.__lonValue   
    
    def makeNetCDFTable(self,inpnt,variableName, rowDim, outTableView):
        '''
         Method Name:  makeNetCDFTable
         Description:  Creates a netCDF Table view from the first point selected
                       on the map, the variable choosen and the row dimension.  The
                       table contains every variable value at that particular point
                       for each slice of the row dimension.  For example: Every sea
                       temperature (Variable) value at each elevation(Row Dimension)
                       for a particular point(Input Point) in sea.
         Input:        
                       inpnt:         The selected Point
                       variableName:  The variable to get each value
                       rowDim:        How to slice up the netCDF file
                       outTableView:  The table being outputed
        '''          
        
        netCDFSource = str(self.__sourceLocation)

        lonVar = self.getLonDimension()
        latVar = self.getLatDimension()
        
        #Printing out the inputs 
        arcpy.AddMessage("Input NetCDF: " + netCDFSource)
        arcpy.AddMessage("Variable Name: " + str(variableName))
        arcpy.AddMessage("Row Dim: " + str(rowDim))
        arcpy.AddMessage("Lat Dim: " + latVar)
        arcpy.AddMessage("Lon Dim: " + lonVar)  
        
        copyStartTime = time.time()
                
        arcpy.CopyFeatures_management(inpnt, r'in_memory\updateFeat')

        elapsedTime = (time.time() - copyStartTime)
        arcpy.AddMessage("Copy Features " + str(elapsedTime))
        
        is0to360 = self.__is0to360()
                                        
        #Only getting the first point.  Others ignored
        with arcpy.da.SearchCursor('in_memory\updateFeat', ('SHAPE@X','SHAPE@Y')) as cursor:
            for row in cursor:  
                
                # Store x,y coordinates of current point
                if is0to360:
                    self.__lonValue = row[0] + 180
                else:
                    self.__lonValue = row[0]
                    
                self.__latValue = row[1]    
                
                arcpy.AddMessage(lonVar + ": " +  str(self.__lonValue) + " " + latVar + ": " + str(self.__latValue))        
        
        netCDFStartTime = time.time()                                
        arcpy.MakeNetCDFTableView_md(netCDFSource, variableName, outTableView, rowDim, lonVar + " " + str(self.__lonValue) + ";" + latVar + " " + str(self.__latValue), "BY_VALUE")        
        
        elapsedNetCDFTime = (time.time() - copyStartTime)
        arcpy.AddMessage("Make netCDF Table Time: " + str(elapsedNetCDFTime))
    
    @staticmethod
    def isNetCDF(netCDFLoc):
        '''
         Method Name:  isNetCDF
         Description:  Checks to see if the file is a netCDF by checking that it ends
                       with '.nc'
         Input:        NetCDF File location
         Output:       True/False if the file is a NetCDF File
        '''        
        isNetCDFBool = True
        
        if not str(netCDFLoc).endswith(".nc"):
            isNetCDFBool = false  
            
        return isNetCDFBool
    
    @staticmethod
    def getNetCDFPathfromLayer(netCDFLayer):
        '''
         Method Name:  getNetCDFPathfromLayer
         Description:  The data source of a NetCDF Raster layer contains some sort of 
                       additional text that represents the raster in memory.
                       We want to strip that piece off so that we only have the
                       exact loaction of the netCDF file
         Input:        NetCDF Raster Layer
         Output:       String: The path to the NetCDF File
        '''           
        datasource = str(netCDFLayer.dataSource)
        return datasource.replace('\\' + netCDFLayer.datasetName,'')        
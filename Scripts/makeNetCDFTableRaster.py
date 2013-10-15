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

#Libraries Needed
import os
import arcpy
from netCDFFile import NetCDFFile 

class NetCDFTableRasterLayer(object):   
    """-------------------------------------------------------------------------------------
    Class Name: MakeNetCDFTableRasterLayer
    Creation Date: 3/1/2012
    Creator: KSigwart
    Description: This tool lets a user select a netCDF raster layer added to ArcGIS Desktop
                 by using the MultiDimensional Tool NetCDF to Raster Layer, then choose which 
                 variable, and which row dimension (i.e. time).  The user then plots
                 a point on the map.  The table returned shows all values within each
                 slice at that particular point.
    Inputs:
            Input netCDF Raster Layer:  A netCDF Raster Layer added to ArcGIS Desktop 
                                        using the NetCDF to Raster Layer 
                                        multidimensional tool.
                                        
            Variable:                   The Variable used for each slice based on the 
                                        Row Dimension.  For example, Sea Surface Temp
                                        over time.  Sea Surface Temp is the
                                        variable, time is the row dimension.
                                        
            Dimension:                  The Row Dimension.  How we slice up the data.
                                        For example, Sea Surface Temp over time.  
                                        Sea Surface Temp is the variable, time is the 
                                        row dimension.
                                        
            Input Point:                The point used to create the table.  The point
                                        is used to query each dimension slice for the
                                        variable value.  For example, if I select the
                                        point at (52,72) there would be a sea surface temp
                                        of 25 degrees on 12/1/2012.
                                        
    Output:
            Out Table:                  The table that is outputed.
    -------------------------------------------------------------------------------------"""    

    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Make NetCDF Table from Point"
        self.description = ("Geoprocessing tool that generates a " +
                            "table of values within a netCDF raster layer from a point " +
                            " selected on the map")
        self.canRunInBackground = True   
                

    def getParameterInfo(self):
        """Define parameter definitions"""
        # First parameter
        paramNetCDFFile = arcpy.Parameter(
            displayName="Input netCDF Raster Layer",
            name="netCDF Raster Layer",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        # Second Parameter: Variable
        variable = arcpy.Parameter(
        displayName="Variable",
        name="in_variable",
        datatype="GPString",
        parameterType="Required",
        direction="Input")
        
        # Third Parameter: Dimension
        dimension = arcpy.Parameter(
        displayName="Row Dimension",
        name="in_dimension",
        datatype="GPString",
        parameterType="Required",
        direction="Input")        
        
        # Fourth Paramter:  Plotted Point
        inpnt = arcpy.Parameter(
        displayName="InputPnt",
        name="InputPnt",
        datatype="GPFeatureRecordSetLayer",
        parameterType="Required",
        direction="Input")           
                
        # Use __file__ attribute to find the .lyr file (assuming the
        # .pyt and .lyr files exist in the same folder).
        inpnt.value = os.path.join(os.path.dirname(__file__),
                            '..', 'Layer', 'InPnt.lyr')   
                
        #Fifth Paramater:  Output Table
        paramOutTable = arcpy.Parameter(
            displayName="table",
            name="table",
            datatype="GPTableView",
            parameterType="Optional",
            direction="Output")
        
        paramOutTable.value = "outTable"

        params = [paramNetCDFFile, variable,dimension,inpnt, paramOutTable]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True # tool can be executed

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed.
        We want to populate the variables and dimensions dropdown list with all dimensions
        that are not lat, lon and only variables that contain lat/lon dimensions.  The lat
        lon are already going to be represented from the point selected on the map"""
        try:
            
            layer = parameters[0].value;
            
            if layer is not None:
                
                #Getting the netCDF DataSource Path from the netCDF raster layer
                netCDFSource = NetCDFFile.getNetCDFPathfromLayer(layer)            
                
                #Making sure that the layers source is a netCDF file
                if NetCDFFile.isNetCDF(netCDFSource):
                    
                    #NetCDFFile class deteremines the dimensions and variables that 
                    #applies to a lat/lon point
                    netCDFFile = NetCDFFile(netCDFSource)

                    #Getting Avalable Dimensions besides besides lat & lon                                     
                    dimensions = netCDFFile.getDimensions()
                    
                    parameters[2].filter.list = dimensions
                    #if dimensions.count > 0:
                        #parameters[2].value = dimensions[0]    
                    
                    #Getting Variables that apply to lat & lon                  
                    variables = netCDFFile.getVariables()
                    
                    parameters[1].filter.list = variables 
                        
                    #if variables.count > 0:
                        #parameters[1].value = variables[0]                    

        except Exception:
            pass
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation.
        We are just checking that the datasource of the selected raster layer
        is a netCDF file.  If the layer has already been added to ArcGIS Desktop
        we can assume that it contains proper lat/lon values and is regularly spaced"""
        try:
                        
            if parameters[0].valueAsText is not None:
                #Getting the netCDF DataSource Path from the netCDF raster layer
                netCDFLoc = NetCDFFile.getNetCDFPathfromLayer(parameters[0].value)

                #Making sure that the datasource is a netCDF file.
                if not NetCDFFile.isNetCDF(netCDFSource):
                    parameters[0].setErrorMessage("Invalid input file. "
                                                  "A netCDF(.nc) "
                                                  "is expected.")
        except Exception:
            pass
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        #Getting the netCDF DataSource Path from the netCDF raster layer
        netCDFSource = NetCDFFile.getNetCDFPathfromLayer(parameters[0].value)
        
        #Making sure that the datasource is a netCDF file.
        if NetCDFFile.isNetCDF(netCDFSource):
            
            netCDFFile = NetCDFFile(netCDFSource)
            
            #Get Input Parameters
            variableName = parameters[1].value
            rowDim = parameters[2].value   
            inpnt = parameters[3].value
            
            #Output Parameters
            outTableView = parameters[4].value; 
            
            #Create Table from selected point
            netCDFFile.makeNetCDFTable(inpnt,variableName,rowDim,outTableView);

            arcpy.AddMessage("Process Completed")   
        else:
            arcpy.AddMessage("In valid inputs")  
        
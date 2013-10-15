# ArcPy NetCDF Web Charting Tools

This template provides the ability to view a time-enabled netCDF Map Service from an ArcGIS Server and graph values at a point. 
This template can be configured by defining the map, title, subtitle and GP Service querying the netCDF file.

## Features
A series of Geoprocessing Tools that let you query a netCDF file from an input point to get all the 
values for each time slice.  There are three tools.
### Make NetCDF Table from Disk
This tool lets the user select a NetCDF Raster Dataset from disk, select a point on the map, then choose the variable 
and the row dimension.  The output is a table with every variable value at that point location for each dimension
slice.
### Make NetCDF Table from Point
This tool lets the user select a NetCDF Raster Layer within the map, select a point on the map, then choose the variable 
and the row dimension.  The output is a table with every variable value at that point location for each dimension
slice.  This tool also works great as a GP Service.  The GP Service created can be used within the 
[NetCDF Web Mapping and Charting Application Template] (https://github.com/kevinsigwart/AGOL_MultiDimTemplate) .
### Graph NetCDF Raster Layer Point
This tool lets the user select a NetCDF Raster Layer within the map, select a point on the map, then choose the variable 
and the row dimension.  The output is a chart with the dimension value on the X axis and the variables values on the 
Y axis. 

## Instructions
1. Clone the repo.
2. Add NetCDF File to ArcMap using Multi-Dimensional Tools-->NetCDF to Raster Layer
3. Run the tool

 [New to Github? Get started here.](https://github.com/)
 
### Instructions for publishing Make NetCDF Table From Point to use within NetCDF Web Mapping and Charting Application Template
1. Make sure netCDF dataset is not in a registered folder within ArcGIS Server.  In Amazon AWS, the netCDF file
must copy to server.
2. Run Tool
3. Within Results Window, Right Click and Share As GeoProcessing Service
4. For Input netCDF Raster Layer choose Input Mode: Constant Value
5. For Variable Choose Constant Value
6. For Row Dimension Choose Constant Value
7. Publish Service.

## Requirements

* ArcGIS Desktop (Basic, Standard, Advanced)
* ArcGIS Server: For Publishing Only
* [NetCDF Web Mapping and Charting Application Template] (https://github.com/kevinsigwart/AGOL_MultiDimTemplate) for charting on the web

## Resources

* [A quick tour of ArcPy](http://resources.arcgis.com/en/help/main/10.2/index.html#//000v00000001000000)
* [What is a Python Toolbox] (http://resources.arcgis.com/en/help/main/10.2/index.html#/What_is_a_Python_toolbox/001500000022000000/)
* [ArcGIS Blog](http://blogs.esri.com/esri/arcgis/)


## Issues

Find a bug or want to request a new feature?  Please let us know by submitting an issue.

## Contributing

Anyone and everyone is welcome to contribute. :)

## Licensing
Copyright 2012 Esri

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

A copy of the license is available in the repository's [license.txt](https://github.com/kevinsigwart/ArcPy-NetCDF-Web-Charting-Tools/master/license.txt) file.

[](Esri Language: Python)

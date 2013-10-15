import sys
import os
import arcpy
myScripts = os.path.join(os.path.dirname(__file__), "Scripts")
sys.path.append(myScripts)

from makeNetCDFTableRaster import NetCDFTableRasterLayer
from graphNetCDFRasterLayer import NetCDFGraphRasterLayer
from makeNetCDFTable import MakeNetCDFTable


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "NetCDF Supplemental Tools"
        self.alias = "nst"

        # List of tool classes associated with this toolbox
        self.tools = [NetCDFTableRasterLayer,NetCDFGraphRasterLayer,MakeNetCDFTable]




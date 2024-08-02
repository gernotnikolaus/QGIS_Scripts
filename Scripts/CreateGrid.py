import os
from osgeo import gdal
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsVectorLayer, QgsField, QgsVectorFileWriter
import processing
import pandas as pd
import csv
from PyQt5.QtCore import QVariant

def createGrid(raster_layer):
    ext = raster_layer.extent()
    
    # Create the grid
    result = processing.run("native:creategrid", {
        'TYPE': 2,
        'EXTENT': ext,
        'HSPACING': 0.25,
        'VSPACING': 0.25,
        'HOVERLAY': 0,
        'VOVERLAY': 0,
        'CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })
    
    # Extract the grid layer directly
    grid = result['OUTPUT']
        
    # Add the grid layer to the project
    QgsProject.instance().addMapLayer(grid)
    
    #print("Grid with longitude, latitude, and layer name attributes was created")

project = QgsProject.instance()
raster_name = project.mapLayersByName('ESACCI-SEALEVEL-L4-MSLA-MERGED-20000115000000-fv02')[0]

createGrid(raster_name)

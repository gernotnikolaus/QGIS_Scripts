# Author: Gernot Nikolaus
# Date: 2024-07-29
# Description: Script to hande specific geoprosessing tools for specific usecase

import os
from osgeo import gdal
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsVectorLayer
import processing
import pandas as pd

# Folder path
folder_path = f"C:/Users/nikolaus/Desktop/Script_testing/KfW_script/"

class processingTool:
    """
    A class to handle specific GIS operations.

    Attributes
    ----------
    project : QgsProject
        The active QGIS project instance.
    country_layer : QgsVectorLayer
        The vector layer representing the country.
    raster_layer : QgsRasterLayer
        The raster layer to be processed.
    grid : QgsVectorLayer
        The grid layer created for analysis.
    gridIntersect : QgsVectorLayer
        The intersection of the grid and country layers.
    zonal_stats_results : list
        A list to store paths to the CSV files of zonal statistics results.
    """
    # Getting active project
    project = QgsProject.instance()

    # manually for now
    # give the name of the country shp and the raster needed
    country_name = "Ghana — gadm41_GHA_2_dissolved"
    raster_name = "tas_AFR-44_MPI-M-MPI-ESM-LR_rcp26_r1i1p1_SMHI-RCA4_v1_day_20060101-20101231 — tas"

    def __init__(self):
        """
        Initializes the KfW class with the specified country and raster layers.
        """
        self.country_layer = self.loadFile(self.country_name)
        self.raster_layer = self.loadFile(self.raster_name)
        self.grid = None
        self.gridIntersect = None
        self.zonal_stats_results = []
        print(f"country_layer {self.country_layer}")
        print(f"raster_layer {self.raster_layer}")

    def loadFile(self, layer_name):
        """Loads a layer by its name from the QGIS project.

        Parameters
        ----------
        layer_name : str
            The name of the layer to load.

        Returns
        -------
        QgsVectorLayer or QgsRasterLayer.
        """
        # Getting the country layer
        print(f"{layer_name} loaded")
        return self.project.mapLayersByName(layer_name)[0]

    def reproject(self):
        """
        Reprojects the raster layer to EPSG:4326 if it is not already in that CRS.
        """
        # Check if its the right CRS
        if self.raster_layer.crs().authid == 'EPSG:4326':
            print(f"The {self.raster_layer.name()} has the right projection")
        else: # Reproject the image
            print(f"The {self.raster_layer.name()} has not the right projection")
           # output_path = f"C:/Users/nikolaus/Desktop/Script_testing/KfW_script/test.tif"
            
            self.raster_layer = processing.runAndLoadResults("gdal:warpreproject", {
                'INPUT': self.raster_layer,
                'SOURCE_CRS':None,
                'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                'RESAMPLING':0,
                'NODATA':None,
                'TARGET_RESOLUTION':None,
                'OPTIONS':'',
                'DATA_TYPE':0,
                'TARGET_EXTENT':None,
                'TARGET_EXTENT_CRS':None,
                'MULTITHREADING':False,
                'EXTRA':'',
                'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            
    # Create the grid
    def createGrid(self):
        """
        Creates a grid over the extent of the country layer.
        """
        ext = self.country_layer.extent()
        
        self.grid = processing.runAndLoadResults("native:creategrid", {
            'TYPE':2,
            'EXTENT': ext,
            'HSPACING':0.232,
            'VSPACING':0.232,
            'HOVERLAY':0,
            'VOVERLAY':0,
            'CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
            'OUTPUT':'TEMPORARY_OUTPUT'
        })
            
        print("Grid was created")
    
    # Create the intersection grid
    def intersectGridToCountry(self):
        """
        Intersects the created grid with the country layer.
        """
        if not self.grid:
            print("Grid not created")
            return
            
        self.gridIntersect = processing.runAndLoadResults("native:intersection", {
            'INPUT': self.grid['OUTPUT'],
            'OVERLAY': self.country_layer,
            'INPUT_FIELDS':[],
            'OVERLAY_FIELDS':[],
            'OVERLAY_FIELDS_PREFIX':'',
            'OUTPUT':'TEMPORARY_OUTPUT',
            'GRID_SIZE':None
        })
            
        print("Intersection done")

    def zoonalStatistic(self):
        """
        Calculates zonal statistics for each band of the raster layer.
        """
        raster_bands = gdal.Open(self.raster_layer['OUTPUT'])
        raster_bands = raster_bands.RasterCount
    
        for band in range(1, raster_bands + 1):
            self.gridValue = processing.run("native:zonalstatisticsfb", { #runAndLoadResults
                'INPUT':self.gridIntersect['OUTPUT'],
                'INPUT_RASTER': self.raster_layer['OUTPUT'],
                'RASTER_BAND':band,
                'COLUMN_PREFIX':'_',
                'STATISTICS':[0,1,2],
                'OUTPUT':'TEMPORARY_OUTPUT',
                'OUTPUT_LAYER_NAME':f'zoonalStatistic_{band}'
            })
            # Export the QgsVectorLayer to a CSV file
            output_csv_path = os.path.join(folder_path, f'zonal_statistic_band_{band}.csv')
            QgsVectorFileWriter.writeAsVectorFormat(self.gridValue['OUTPUT'], output_csv_path, 'utf-8', self.gridValue['OUTPUT'].crs(), 'CSV')
            self.zonal_stats_results.append(output_csv_path)
            print(f"Zoonal statistic was successful for band {band}")

    def saveCSV(self):
        """
        Combines all zonal statistics results into a single CSV file.
        """
        # Combine all the zonal statistics results into a single DataFrame
        combined_df = pd.concat([pd.read_csv(output) for output in self.zonal_stats_results])
        combined_csv_path = os.path.join(folder_path, 'combined_zonal_statistics.csv')
        combined_df.to_csv(combined_csv_path, index=False)
        print(f"CSV was saved at {combined_csv_path}")
        
# Test running
processingTool = processingTool()
processingTool.reproject()
processingTool.createGrid()
processingTool.intersectGridToCountry()
processingTool.zoonalStatistic()
processingTool.saveCSV()

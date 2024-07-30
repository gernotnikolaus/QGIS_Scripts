# Author: Gernot Nikolaus
# Date: 2024-07-30
# Description: ...

import os
from osgeo import gdal
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsVectorLayer, QgsField, QgsVectorFileWriter
import processing
import pandas as pd
import csv
from PyQt5.QtCore import QVariant

# Folder path
folder_path = f"C:/Users/nikolaus/Desktop/Script_testing/KfW_script/"

class ProcessingTool:
    """
    A class to process geospatial data, including loading layers, reprojecting rasters, creating grids, 
    performing intersections, extracting grids, calculating zonal statistics, and saving results to CSV.

    Attributes:
    -----------
    country_name : str
        The name of the country layer.
    raster_name : str
        The name of the raster layer.
    project : QgsProject
        The QGIS project instance.
    country_layer : QgsVectorLayer
        The loaded country vector layer.
    raster_layer : QgsRasterLayer
        The loaded raster layer.
    grid : QgsVectorLayer
        The created grid layer.
    gridIntersect : QgsVectorLayer
        The intersected grid layer.
    gridExtract : QgsVectorLayer
        The extracted grid layer.
    zonal_stats_results : list
        List of file paths to the zonal statistics results.

    Methods:
    --------
    __init__(self, country_name, raster_name):
        Initializes the ProcessingTool with the given country and raster names.

    loadFile(self, layer_name):
        Loads a layer by its name from the QGIS project.

    reproject(self):
        Reprojects the raster layer to EPSG:4326 if it is not already in that CRS.

    createGrid(self):
        Creates a grid over the extent of the country layer and adds longitude, latitude, and layer name attributes.

    intersectGridToCountry(self):
        Intersects the created grid with the country layer.

    extractGrid(self):
        Extracts the grid cells that intersect with the country layer.

    zonalStatistic(self):
        Calculates zonal statistics for each band of the raster layer and saves the results to CSV files.

    saveCSV(self):
        Combines the individual CSV files from zonal statistics into a single CSV file.
    """
    
    def __init__(self, country_name, raster_name):
        self.project = QgsProject.instance()
        self.country_name = country_name
        self.raster_name = raster_name
        self.country_layer = self.loadFile(self.country_name)
        self.raster_layer = self.loadFile(self.raster_name)
        self.grid = None
        self.gridIntersect = None
        self.gridExtract = None
        self.zonal_stats_results = []
        print(f"country_layer {self.country_layer}")
        print(f"raster_layer {self.raster_layer}")

    def loadFile(self, layer_name):
        """
        Loads a layer by its name from the QGIS project.

        Parameters:
        -----------
        layer_name : str
            The name of the layer to load.

        Returns:
        --------
        QgsVectorLayer or QgsRasterLayer
            The loaded layer.
        """
        layers = self.project.mapLayersByName(layer_name)
        if not layers:
            raise ValueError(f"Layer {layer_name} not found")
        print(f"{layer_name} loaded")
        return layers[0]

    def reproject(self):
        """
        Reprojects the raster layer to EPSG:4326 if it is not already in that CRS.
        """
        if self.raster_layer.crs().authid() == 'EPSG:4326':
            print(f"The {self.raster_layer.name()} has the right projection")
        else:
            print(f"The {self.raster_layer.name()} has not the right projection")
            self.raster_layer = processing.runAndLoadResults("gdal:warpreproject", {
                'INPUT': self.raster_layer,
                'SOURCE_CRS': None,
                'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
                'RESAMPLING': 0,
                'NODATA': None,
                'TARGET_RESOLUTION': None,
                'OPTIONS': '',
                'DATA_TYPE': 0,
                'TARGET_EXTENT': None,
                'TARGET_EXTENT_CRS': None,
                'MULTITHREADING': False,
                'EXTRA': '',
                'OUTPUT': 'TEMPORARY_OUTPUT'
            })['OUTPUT']

    def createGrid(self):
        """
        Creates a grid over the extent of the country layer and adds longitude, latitude, and layer name attributes.
        """
        ext = self.country_layer.extent()
        
        # Create the grid
        result = processing.run("native:creategrid", {
            'TYPE': 2,
            'EXTENT': ext,
            'HSPACING': 0.232,
            'VSPACING': 0.232,
            'HOVERLAY': 0,
            'VOVERLAY': 0,
            'CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'OUTPUT': 'TEMPORARY_OUTPUT'
        })
        
        # Extract the grid layer directly
        self.grid = result['OUTPUT']
        
        # Add longitude, latitude, and layer name fields
        self.grid.startEditing()
        self.grid.dataProvider().addAttributes([
            QgsField('longitude', QVariant.Double),
            QgsField('latitude', QVariant.Double),
            QgsField('layer_name', QVariant.String)
        ])
        self.grid.updateFields()
        
        # Iterate through and set the long, lat, and layer name values
        for feature in self.grid.getFeatures():
            geom = feature.geometry()
            centroid = geom.centroid().asPoint()
            feature['longitude'] = centroid.x()
            feature['latitude'] = centroid.y()
            feature['layer_name'] = self.country_layer.name()
            self.grid.updateFeature(feature)
        
        self.grid.commitChanges()
        
        # Add the grid layer to the project
        QgsProject.instance().addMapLayer(self.grid)
        
        print("Grid with longitude, latitude, and layer name attributes was created")


    def intersectGridToCountry(self):
        """
        Intersects the created grid with the country layer.
        """
        if not self.grid:
            print("Grid not created")
            return
        self.gridIntersect = processing.runAndLoadResults("native:intersection", {
            'INPUT': self.grid,
            'OVERLAY': self.country_layer,
            'INPUT_FIELDS': [],
            'OVERLAY_FIELDS': [],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'GRID_SIZE': None
        })['OUTPUT']
        print("Intersection done")

    def extractGrid(self):
        """
        Extracts the grid cells that intersect with the country layer.
        """
        if not self.grid:
            print("Grid not created")
            return
        self.gridExtract = processing.runAndLoadResults("native:extractbylocation", {
            'INPUT': self.grid,
            'PREDICATE': [0],
            'INTERSECT': self.country_layer,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        })['OUTPUT']
        print("Extraction done")

    def zonalStatistic(self):
        """
        Calculates zonal statistics for each band of the raster layer and saves the results to CSV files.
        """
        new_folder_path = os.path.join(folder_path, 'individual_csv')
        os.makedirs(new_folder_path, exist_ok=True)
    
        raster_bands = gdal.Open(self.raster_layer).RasterCount
        for band in range(1, raster_bands + 1):
            self.gridValue = processing.run("native:zonalstatisticsfb", {
                'INPUT': self.gridExtract,
                'INPUT_RASTER': self.raster_layer,
                'RASTER_BAND': band,
                'COLUMN_PREFIX': '_',
                'STATISTICS': [0, 1, 2],
                'OUTPUT': 'TEMPORARY_OUTPUT',
                'OUTPUT_LAYER_NAME': f'zonalStatistic_{band}'
            })['OUTPUT']
            output_csv_path = os.path.join(new_folder_path, f'{self.country_name}_zonal_statistic_band_{band}.csv')
            QgsVectorFileWriter.writeAsVectorFormat(self.gridValue, output_csv_path, 'utf-8', self.gridValue.crs(), 'CSV')
            with open(output_csv_path, 'r') as infile, open(output_csv_path + '_temp', 'w', newline='') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                headers = next(reader)
                writer.writerow(headers + ['month'])
                for row in reader:
                    writer.writerow(row + [band])
            os.replace(output_csv_path + '_temp', output_csv_path)
            self.zonal_stats_results.append(output_csv_path)
            print(f"Zonal statistic was successful for band {band}")

    def saveCSV(self):
        """
        Combines the individual CSV files from zonal statistics into a single CSV file.
        """
        combined_df = pd.concat([pd.read_csv(output) for output in self.zonal_stats_results])
        fields_to_keep = ['month', 'latitude', 'longitude', '_count', '_sum', '_mean']
        filtered_df = combined_df[fields_to_keep]
        combined_csv_path = os.path.join(folder_path, f'{self.country_name}_FROM_{self.raster_name}.csv')
        filtered_df.to_csv(combined_csv_path, index=False)
        print(f"CSV was saved at {combined_csv_path}")

# Example usage
project = QgsProject.instance()

group_layer_name = "Priority Countries AF44"
group_layer = project.layerTreeRoot().findGroup(group_layer_name)

group_raster_name = "CORDEX data"
group_raster = project.layerTreeRoot().findGroup(group_raster_name)

for layer in group_layer.children():
    shapefile_layer_name = layer.name()
    
    for raster in group_raster.children():
        give_raster_name = raster.name()
        
        processing_tool = ProcessingTool(shapefile_layer_name, give_raster_name)
        processing_tool.reproject()
        processing_tool.createGrid()
        processing_tool.extractGrid()
        # processing_tool.intersectGridToCountry()
        processing_tool.zonalStatistic()
        processing_tool.saveCSV()
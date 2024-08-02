import os
import re
from osgeo import gdal
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsVectorLayer, QgsField, QgsVectorFileWriter
import processing
import pandas as pd
import csv
from PyQt5.QtCore import QVariant

# Folder path
folder_path = f"C:/Users/nikolaus/Documents/KfW Project/Data/02_PostData/LYB"

class GridCalculationToCSV:
    def __init__(self, shapefile_layer_name, raster_name):
        self.project = QgsProject.instance()
        self.raster_name = raster_name
        self.shapefile_layer_name = shapefile_layer_name
        self.raster_layer = self.loadFile(self.raster_name)
        self.grid = self.loadFile(self.shapefile_layer_name)
        self.gridIntersect = None
        self.gridExtract = None
        self.zonal_stats_results = []
        self.date = self.extract_date(self.raster_name)
        
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
        
    def extract_date(self, string):
        """
        Extracts the date part from the raster name.

        Parameters:
        -----------
        string : str
            The raster name string.

        Returns:
        --------
        str
            The extracted date part.
        """
        match = re.search(r'MERGED-(.*?)-fv02', string)
        if match:
            return match.group(1)[:6]
        return None

    def zonalStatistic(self):
        new_folder_path = os.path.join(folder_path, 'individual_csv')
        os.makedirs(new_folder_path, exist_ok=True)
    
        self.gridValue = processing.run("native:zonalstatisticsfb", {
            'INPUT': self.grid,
            'INPUT_RASTER': self.raster_layer,
            'RASTER_BAND': 1,
            'COLUMN_PREFIX': f'{self.date}_', #output is {self.date}_mean'
            'STATISTICS': [2],
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'OUTPUT_LAYER_NAME': f'zonalStatistic_{self.raster_name}'
        })['OUTPUT']
            
        output_csv_path = os.path.join(new_folder_path, f'{self.shapefile_layer_name}_{self.raster_name}.csv')
        QgsVectorFileWriter.writeAsVectorFormat(self.gridValue, output_csv_path, 'utf-8', self.gridValue.crs(), 'CSV')
        
        # Filter the output CSV for the specified fields
        fields_to_keep = ['adm_0', 'Lat', 'Lon', f'{self.date}_mean']
        df = pd.read_csv(output_csv_path)
        df_filtered = df[fields_to_keep]
        df_filtered.to_csv(output_csv_path, index=False)

        self.zonal_stats_results.append(output_csv_path)
        print(f"Zonal statistic was successful for {self.raster_name}")
    
    def combine_csv_files(self):
        # Path to the folder containing individual CSV files
        new_folder_path = os.path.join(folder_path, 'individual_csv')

        # Initialize an empty dataframe for merging
        combined_df = None

        # Iterate over all CSV files in the folder
        for file_name in os.listdir(new_folder_path):
            if file_name.endswith('.csv'):
                file_path = os.path.join(new_folder_path, file_name)
                df = pd.read_csv(file_path)
                
                if combined_df is None:
                    combined_df = df
                else:
                    combined_df = pd.merge(combined_df, df, on=['adm_0', 'Lat', 'Lon'], how='outer')

        # Save the combined dataframe to a new CSV file
        combined_csv_path = os.path.join(folder_path, 'combined_output.csv')
        combined_df.to_csv(combined_csv_path, index=False)
        print(f"Combined CSV file saved as {combined_csv_path}")

# Example usage
project = QgsProject.instance()

group_layer_name = "Grid"
group_layer = project.layerTreeRoot().findGroup(group_layer_name)

group_raster_name = "2000-2015"
group_raster = project.layerTreeRoot().findGroup(group_raster_name)

for layer in group_layer.children():
    shapefile_layer_name = layer.name()
    
    for raster in group_raster.children():
        give_raster_name = raster.name()
        
        grid_calculation = GridCalculationToCSV(shapefile_layer_name, give_raster_name)
        # processing_tool.intersectGridToCountry()
        grid_calculation.zonalStatistic()
        grid_calculation.combine_csv_files()
        #grid_calculation.saveCSV()

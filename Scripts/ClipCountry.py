# Author: Gernot Nikolaus
# Date: 2024-07-25
# Description: This script iterates through shapefiles in a specified group within a QGIS project, clips a raster layer using each shapefile,  and saves the output to a specified directory.

import os
### Script running though shapefiles and cliiping raster based on the current shp
# Getting active project
project = QgsProject.instance()

# group name where shps are
group_name = "Countries"

# Getting the group layer
group_layer = project.layerTreeRoot().findGroup(group_name)
layer_name = "erosion"

# Get the raster layer which has to be clipped
raster_layer = QgsProject.instance().mapLayersByName(layer_name)[0]

def clipCountry(group_name, group_layer, layer_name, raster_layer):
    """
    Iterates through the layers in the specified group, clips a raster layer using each shapefile, and saves the output.

    Parameters:
    group_name (str): The name of the group containing the shapefiles.
    group_layer (QgsLayerTreeGroup): The group layer object containing the shapefiles.
    layer_name (str): The name of the raster layer to be clipped.
    raster_layer (QgsRasterLayer): The raster layer object to be clipped.

    Returns:
    None
    """
    
    # iterating through the group layers
    for layer in group_layer.children():
        if isinstance(layer, QgsLayerTreeLayer) and layer.layer().type() == QgsMapLayer.VectorLayer:
            # Get the shapefile layer
            shapefile_layer = layer.layer()
            
            shapefile_layer_name = str(shapefile_layer)
            
            start = shapefile_layer_name.find(": <QgsVectorLayer: '") + len(": <QgsVectorLayer:'")
            end = shapefile_layer_name.find("' (ogr)>")
            extracted_string_country = shapefile_layer_name[start:end]
            
            print(extracted_string_country)
            
            # Define the output path for the clipped raster
            folder_path = f"C:/Users/nikolaus/Desktop/Script_testing/ClipCountry/{extracted_string_country}"
            
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Directory {folder_path} was created.")
            
            """
            output_path = f"C:/Users/nikolaus/Desktop/Script_testing/ClipCountry/{extracted_string_country}/{extracted_string_country}_{raster_layer}.nc"

            # Clip the raster using the shapefile layer
            processing.run("gdal:cliprasterbymasklayer", {
                'INPUT': raster_layer,
                'MASK': shapefile_layer,
                'SOURCE_CRS': raster_layer.crs(),
                'TARGET_CRS': raster_layer.crs(),
                'NODATA': None,
                'ALPHA_BAND': False,
                'CROP_TO_CUTLINE': True,
                'KEEP_RESOLUTION': True,
                'OPTIONS': '',
                'DATA_TYPE': 0,
                'OUTPUT': output_path
            })
            
            # confirmation that the shape as saved
            print(f"Raster clipped for {shapefile_layer.name()}. Output saved as {output_path}")
            """
            
clipCountry(group_name, group_layer, layer_name, raster_layer)
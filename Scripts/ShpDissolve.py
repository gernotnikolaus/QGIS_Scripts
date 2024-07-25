# Author: Gernot Nikolaus
# Date: 2024-07-25
# Description: This script iterates through shapefiles in a specified group within a QGIS project, dissolves each shapefile, and saves the output to a specified directory.

import os

# Getting active project
project = QgsProject.instance()

# group name where shps are
group_name = "Countries"
# Getting the group layer
group_layer = project.layerTreeRoot().findGroup(group_name)


def dissolveLoop(group_name, group_layer):
    """Iterates through the layers in the specified group, dissolves each shapefile, and saves the output.

    Parameters
    ----------
        group_name (str): The name of the group containing the shapefiles.
        group_layer (QgsLayerTreeGroup): The group layer object containing the shapefiles.

    Returns
    ------
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
            
            # Print the extracted country name
            print(extracted_string_country)
            
            # Define the output path for the folder, up manually
            folder_path = f"C:/Users/nikolaus/Desktop/Script_testing/Countries Dissolve/{extracted_string_country}"
            
            # if the folder does not exist, create it
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Directory {folder_path} was created.")
            
            # define the output path, go into the folder and save it there
            output_path = f"{folder_path}/{extracted_string_country}_dissolved.shp"

            # run the dissovle function
            processing.run("native:dissolve", {
                'INPUT':shapefile_layer,
                'FIELD':[],
                'SEPARATE_DISJOINT':False,
                'OUTPUT': output_path
            })
            
            # confirmation that the shape was saved
            print(f"Shp dissolved for {shapefile_layer.name()}. Output saved as {output_path}")
            
# Call the dissolveLoop function
dissolveLoop(group_name, group_layer)
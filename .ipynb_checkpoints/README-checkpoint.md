Here's the GitHub documentation for the two scripts you provided:

---

## QGIS Scripts for Processing Shapefiles and Raster Layers

### Author: Gernot Nikolaus
### Date: 2024-07-25

This repository contains two Python scripts designed to be used within QGIS. The first script iterates through shapefiles in a specified group, dissolves each shapefile, and saves the output to a specified directory. The second script clips a raster layer using each shapefile in a specified group and saves the output to a specified directory.

---

### Script 1: Dissolve Shapefiles

#### Description
This script iterates through shapefiles in a specified group within a QGIS project, dissolves each shapefile, and saves the output to a specified directory. The dissolved shapefiles are then added to a new group within the QGIS project.

#### Usage
1. Ensure you have QGIS installed and the necessary shapefiles loaded into a group named "Countries".
2. Update the `group_name` variable if your group has a different name.
3. Run the script within the QGIS Python console.

#### Script
```python
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

            # run the dissolve function
            result = processing.run("native:dissolve", {
                'INPUT':shapefile_layer,
                'FIELD':[],
                'SEPARATE_DISJOINT':False,
                'OUTPUT': output_path
            })
            
            # confirmation that the shape was saved
            print(f"Shp dissolved for {shapefile_layer.name()}. Output saved as {output_path}")
            
            # Define the group where the dissolved layers will be added
            dissolved_group_name = "Dissolved Layers"
            dissolved_group_layer = project.layerTreeRoot().findGroup(dissolved_group_name)

            # If the group does not exist, create it
            if not dissolved_group_layer:
                dissolved_group_layer = project.layerTreeRoot().addGroup(dissolved_group_name)
                        
            # Load the dissolved shapefile into the project
            dissolved_layer = QgsVectorLayer(result['OUTPUT'], f"{extracted_string_country}_dissolved", "ogr")
            if not dissolved_layer.isValid():
                print(f"Failed to load the dissolved layer for {extracted_string_country}")
            else:
                # Add the dissolved layer to the dissolved group
                project.addMapLayer(dissolved_layer, False)
                dissolved_group_layer.addLayer(dissolved_layer)
                print(f"Shp dissolved for {shapefile_layer.name()}. Output saved as {output_path}")
            
            
# Call the dissolveLoop function
dissolveLoop(group_name, group_layer)
```

---

### Script 2: Clip Raster by Shapefiles

#### Description
This script iterates through shapefiles in a specified group within a QGIS project, clips a raster layer using each shapefile, and saves the output to a specified directory.

#### Usage
1. Ensure you have QGIS installed and the necessary shapefiles loaded into a group named "Dissolved Layers".
2. Update the `group_name` and `layer_name` variables if your group or raster layer has different names.
3. Run the script within the QGIS Python console.

#### Script
```python
import os

# Getting active project
project = QgsProject.instance()

# group name where shps are
group_name = "Dissolved Layers"

# Getting the group layer
group_layer = project.layerTreeRoot().findGroup(group_name)
layer_name = "erosion"

# Get the raster layer which has to be clipped
raster_layer = QgsProject.instance().mapLayersByName(layer_name)[0]

# folder path, a specific folder will be created here in the function for each layer
folder_path = f"C:/Users/nikolaus/Desktop/Script_testing/ClipCountry/"

def clipCountry(group_name, group_layer, layer_name, raster_layer, fp):
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
            folder_path = f"{fp}/{extracted_string_country}"
            
            
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Directory {folder_path} was created.")
            
            
            output_path = f"C:/Users/nikolaus/Desktop/Script_testing/ClipCountry/{extracted_string_country}/test.tif"

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
 
 
clipCountry(group_name, group_layer, layer_name, raster_layer, folder_path)
```

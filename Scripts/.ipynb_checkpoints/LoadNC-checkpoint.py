import os
from qgis.core import QgsProject, QgsRasterLayer

# Set the directory containing the .nc files
directory = f"C:/Users/nikolaus/Documents/KfW Project/Data/01_PreData/Sea Leve Raise data/ESA Sea Level Climate Change Initiative (Sea_Level_cci) Time series of gridded Sea Level Anomalies (SLA), Version 2.0/2015"

# Get a list of all .nc files in the directory
nc_files = [f for f in os.listdir(directory) if f.endswith('.nc')]

# Loop through the files in reverse order
for filename in reversed(nc_files):
    filepath = os.path.join(directory, filename)
    
    # Create a raster layer
    raster_layer = QgsRasterLayer(filepath, filename)
    
    # Check if the layer is valid
    if raster_layer.isValid():
        # Add the raster layer to the project
        QgsProject.instance().addMapLayer(raster_layer)
    else:
        print(f"Failed to load {filename}")

print("All valid raster layers have been loaded in reverse order.")

## PyQGIS for processing shp and raster Layers
### Date: 2024-07-29

---
## Main script (processingTool)
This script handles specific geoprocessing tools for a specific use case using QGIS and Python. It includes functions to load layers, reproject raster layers, create grids, intersect grids with country layers, calculate zonal statistics, and save the results to a CSV file.

## Script Description

### processingTool Class

A class to handle specific GIS operations.

#### Attributes

- `project`: The active QGIS project instance.
- `country_layer`: The vector layer representing the country.
- `raster_layer`: The raster layer to be processed.
- `grid`: The grid layer created for analysis.
- `gridIntersect`: The intersection of the grid and country layers. [OPTIONAL]
- `gridExtracted`: The extraction of features of the grid with the country layer.
- `zonal_stats_results`: A list to store paths to the CSV files of zonal statistics results.

#### Methods

- `__init__(self)`: Initializes the processingTool class with the specified country and raster layers.
- `loadFile(self, layer_name)`: Loads a layer by its name from the QGIS project.
- `reproject(self)`: Reprojects the raster layer to EPSG:4326 if it is not already in that CRS.
- `createGrid(self)`: Creates a grid over the extent of the country layer.
- `intersectGridToCountry(self)`: Intersects the created grid with the country layer. [OPTIONAL, gridExtracted is recommended]
- `extractGrid(self)`: Extract the rectangles which intersect with the country layer.
- `zoonalStatistic(self)`: Calculates zonal statistics for each band of the raster layer.
- `saveCSV(self)`: Combines all zonal statistics results into a single CSV file.

## Example

```python
# Test running
processingTool = processingTool()
processingTool.reproject()
processingTool.createGrid()
#processingTool.intersectGridToCountry()
processingTool.extractGrid()
processingTool.zoonalStatistic()
processingTool.saveCSV()
```
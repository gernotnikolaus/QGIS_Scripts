project = QgsProject.instance()
grid = project.mapLayersByName('LYB')[0]

# Start editing the grid layer
grid.startEditing()

# Add longitude, latitude, and layer name fields
grid.dataProvider().addAttributes([
    QgsField('id', QVariant.Int),
    QgsField('Lon', QVariant.Double),
    QgsField('Lat', QVariant.Double),
    QgsField('adm_0', QVariant.String)
])
grid.updateFields()

# Iterate through and set the long, lat, and layer name values
for i, feature in enumerate(grid.getFeatures(), start=1):
    geom = feature.geometry()
    centroid = geom.centroid().asPoint()
    feature['Lon'] = centroid.x()
    feature['Lat'] = centroid.y()
    feature['adm_0'] = grid.name()
    feature['id'] = i
    grid.updateFeature(feature)

# Commit changes
grid.commitChanges()

# Add the grid layer to the project
QgsProject.instance().addMapLayer(grid)

print("Grid with longitude, latitude, and layer name attributes was created")

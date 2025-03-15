from pyproj import Transformer

# Define transformation from EPSG:3035 to EPSG:4326
transformer = Transformer.from_crs("EPSG:3035", "EPSG:4326", always_xy=True)

# Convert coordinates
lon, lat = transformer.transform(4555500, 3272500)
print(f"{lat} {lon}")
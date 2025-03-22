from pyproj import Transformer

# Define transformation from EPSG:3035 to EPSG:4326
transformer = Transformer.from_crs("EPSG:3035", "EPSG:4326", always_xy=True)

# Convert coordinates
lon, lat = transformer.transform(4554500, 3269500)
print(f"{lat} {lon}")

#4530562 3258133, 4531622 3292434, 4578342 3293175, 4575481 3252386, 4530562 3258133 BERLIN
#3999588 3603683, 4708121 3606406, 4737277 2723042, 3976925 2671151, 3999588 3603683 DEUTSCHLAND
import psycopg2
import h3.api.basic_str as h3
import json
from shapely.geometry import Polygon, shape, Point
import geopandas as gpd

# Подключение к базе данных
conn = psycopg2.connect(
    dbname="openalmaty2",
    user="postgres",
    password="t$hZw!Kz",
    host="localhost",
    port="5433"
)
cur = conn.cursor()

cur.execute("""
    UPDATE appeals_appeal
    SET hexagon_id = NULL, boundary_coords = NULL
""")
conn.commit()
print("Старые данные hexagon_id и boundary_coords очищены.")

boundary = gpd.read_file("export.geojson")
city_boundary = boundary.unary_union

center_lat, center_lon = 43.238949, 76.889709
resolution = 8
k_ring_radius = 15

center_hex = h3.latlng_to_cell(center_lat, center_lon, resolution)
hexagons = list(h3.grid_disk(center_hex, k_ring_radius))

filtered_hexagons = []
for hex_id in hexagons:
    boundary_coords = h3.cell_to_boundary(hex_id)
    boundary_coords = [(lng, lat) for lat, lng in boundary_coords]
    hex_polygon = Polygon(boundary_coords)

    if city_boundary.contains(hex_polygon.centroid) or city_boundary.intersects(hex_polygon):
        filtered_hexagons.append((hex_id, boundary_coords))

print(f"Количество хексов внутри границ: {len(filtered_hexagons)}")

for hex_id, boundary_coords in filtered_hexagons:
    boundary_coords_geojson = [[lng, lat] for lng, lat in boundary_coords]

    if boundary_coords_geojson[0] != boundary_coords_geojson[-1]:
        boundary_coords_geojson.append(boundary_coords_geojson[0])

    polygon_wkt = f"POLYGON(({', '.join([f'{lng} {lat}' for lng, lat in boundary_coords_geojson])}))"

    cur.execute("""
        UPDATE appeals_appeal
        SET hexagon_id = %s, boundary_coords = %s
        WHERE ST_Contains(
            ST_SetSRID(ST_GeomFromText(%s), 4326), 
            location
        )
    """, (hex_id, json.dumps(boundary_coords_geojson), polygon_wkt))

conn.commit()

cur.close()
conn.close()

print("Хексы успешно сохранены в базе данных.")

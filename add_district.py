import psycopg2
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

conn = psycopg2.connect(
    dbname="openalmaty2",
    user="postgres",
    password="t$hZw!Kz",
    host="localhost",
    port="5433"
)
cur = conn.cursor()

districts = gpd.read_file("district.geojson")
districts = districts.to_crs(epsg=4326)

cur.execute("""
    UPDATE appeals_appeal
    SET district_name = NULL, district_boundary = NULL
""")
conn.commit()
print("Старые данные district_name и district_boundary очищены.")

for _, district in districts.iterrows():
    district_name = district["name"]
    district_geometry = district["geometry"]

    if isinstance(district_geometry, MultiPolygon):
        district_geometry = list(district_geometry.geoms)[0]

    district_wkt = district_geometry.wkt

    cur.execute("""
        UPDATE appeals_appeal
        SET district_name = %s, district_boundary = ST_SetSRID(ST_GeomFromText(%s), 4326)
        WHERE ST_Contains(ST_SetSRID(ST_GeomFromText(%s), 4326), location)
    """, (
        district_name,
        district_wkt,
        district_wkt
    ))
    print(f"Обновлены точки для района: {district_name}")

conn.commit()
print("Данные успешно обновлены!")

cur.close()
conn.close()

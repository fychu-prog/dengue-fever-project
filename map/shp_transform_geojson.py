import geopandas as gpd

# 讀取你的 SHP
gdf = gpd.read_file(r"map/data_raw/TOWN_MOI_1140318.shp")

# 看前幾筆
print(gdf.head())

# 轉成 GeoJSON
gdf.to_file("taiwan_township.geojson", driver="GeoJSON")


import plotly.express as px
import json

# 讀取 GeoJSON
with open("taiwan_township.geojson", encoding="utf-8") as f:
    geo = json.load(f)

# 用 gdf，不是 df
fig = px.choropleth(
    gdf,
    geojson=geo,
    locations="TOWNNAME",
    featureidkey="properties.TOWNNAME",
    color=None,     # 先不要 color（等下我會教你怎麼上 cases）
)

fig.update_geos(fitbounds="locations", visible=False)
fig.show()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from pathlib import Path

geo = json.load(open('website/static/data/taiwan_township.geojson', 'r', encoding='utf-8'))
kaohsiung = [f for f in geo['features'] if f['properties'].get('COUNTYNAME') == '高雄市']

print(f'找到 {len(kaohsiung)} 個高雄市行政區')
if kaohsiung:
    feat = kaohsiung[0]
    print(f'第一個行政區: {feat["properties"]["TOWNNAME"]}')
    geom = feat['geometry']
    print(f'幾何類型: {geom["type"]}')
    coords = geom['coordinates']
    print(f'座標結構: {type(coords).__name__}')
    if isinstance(coords, list) and len(coords) > 0:
        print(f'第一層長度: {len(coords)}')
        if isinstance(coords[0], list) and len(coords[0]) > 0:
            print(f'第二層長度: {len(coords[0])}')
            if isinstance(coords[0][0], list) and len(coords[0][0]) > 0:
                print(f'第三層長度: {len(coords[0][0])}')
                print(f'範例座標點: {coords[0][0][0]}')


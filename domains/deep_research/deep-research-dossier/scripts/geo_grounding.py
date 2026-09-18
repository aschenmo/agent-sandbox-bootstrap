#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geo Grounding Engine (地图空间接地引擎)
支持高德地图 (Amap Web API) 与 百度地图 (Baidu Web API)
用于空间逆地理编码、卫星/静态地图抓取、大车进场路径推演与建材供应链 POI 探测。
"""

import os
import sys
import json
import requests
from typing import Dict, Any, Optional, List

class GeoGroundingEngine:
    def __init__(self, amap_key: Optional[str] = None, baidu_ak: Optional[str] = None):
        self.amap_key = amap_key or os.environ.get("AMAP_API_KEY", "")
        self.baidu_ak = baidu_ak or os.environ.get("BAIDU_MAP_AK", "")

    def geocode(self, address: str) -> Dict[str, Any]:
        """高德逆地理编码，精准获取经纬度与行政区划编码"""
        url = f"https://restapi.amap.com/v3/geocode/geo?address={address}&key={self.amap_key}"
        res = requests.get(url, timeout=10).json()
        if res.get("status") == "1" and res.get("geocodes"):
            info = res["geocodes"][0]
            lng_lat = info["location"].split(",")
            return {
                "success": True,
                "address": info.get("formatted_address"),
                "province": info.get("province"),
                "city": info.get("city"),
                "district": info.get("district"),
                "adcode": info.get("adcode"),
                "location": info.get("location"),
                "lng": float(lng_lat[0]),
                "lat": float(lng_lat[1]),
                "level": info.get("level")
            }
        return {"success": False, "error": res.get("info", "Geocode failed")}

    def fetch_static_map(self, location: str, output_path: str, zoom: int = 15, size: str = "750*500", scale: int = 2) -> bool:
        """下载高分辨率静态切片底图"""
        url = f"https://restapi.amap.com/v3/staticmap?location={location}&zoom={zoom}&size={size}&scale={scale}&markers=large,0xFF0000,A:{location}&key={self.amap_key}"
        res = requests.get(url, timeout=15)
        if res.status_code == 200 and len(res.content) > 1000:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(res.content)
            return True
        return False

    def plan_driving_route(self, origin: str, destination: str) -> Dict[str, Any]:
        """规划运输路线，评估工程重型车辆/材料运输通行距离与耗时"""
        url = f"https://restapi.amap.com/v3/direction/driving?origin={origin}&destination={destination}&strategy=0&key={self.amap_key}"
        res = requests.get(url, timeout=10).json()
        if res.get("status") == "1" and res.get("route", {}).get("paths"):
            path = res["route"]["paths"][0]
            return {
                "success": True,
                "distance_km": round(float(path["distance"]) / 1000.0, 2),
                "duration_min": round(float(path["duration"]) / 60.0, 1),
                "steps": [s.get("instruction") for s in path.get("steps", [])[:8]]
            }
        return {"success": False, "error": res.get("info", "Route planning failed")}

    def search_nearby_materials(self, city: str, keywords: str = "搅拌站|建材|砂石", limit: int = 6) -> List[Dict[str, Any]]:
        """搜索周边商混站、砂石料场等建材供应链 POI"""
        url = f"https://restapi.amap.com/v3/place/text?keywords={keywords}&city={city}&key={self.amap_key}"
        res = requests.get(url, timeout=10).json()
        results = []
        if res.get("status") == "1":
            for poi in res.get("pois", [])[:limit]:
                results.append({
                    "name": poi.get("name"),
                    "type": poi.get("type"),
                    "address": poi.get("address"),
                    "location": poi.get("location")
                })
        return results

if __name__ == "__main__":
    engine = GeoGroundingEngine()
    addr = "贵州省安顺市关岭布依族苗族自治县断桥镇坡舟村"
    geo = engine.geocode(addr)
    print("Geocode Result:\n", json.dumps(geo, ensure_ascii=False, indent=2))

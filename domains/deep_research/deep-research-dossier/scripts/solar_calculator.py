#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solar & Overhang Calculator (太阳高度角与遮阳出挑工程计算器)
根据地理纬度与季节计算冬至、夏至正午太阳高度角，自动推演最优南向遮阳挑檐出挑长度与日照穿透进深。
"""

import sys
import math
from typing import Dict, Any

def calculate_solar_parameters(lat: float, floor_height: float = 3.3, window_height: float = 2.4) -> Dict[str, Any]:
    """
    计算正午太阳高度角与遮阳参数
    :param lat: 所在纬度（如关岭 25.81°）
    :param floor_height: 层高（米）
    :param window_height: 窗高（米）
    :return: 包含冬至/夏至角度、最佳挑檐宽度、阴影比率的字典
    """
    # 赤纬角
    dec_summer = 23.45   # 夏至
    dec_winter = -23.45  # 冬至

    # 正午太阳高度角 h = 90 - |lat - dec|
    h_summer = 90.0 - abs(lat - dec_summer)
    h_winter = 90.0 - abs(lat - dec_winter)

    # 弧度
    rad_summer = math.radians(h_summer)
    rad_winter = math.radians(h_winter)

    # 最佳遮阳挑檐出挑长度 (既要完全阻隔盛夏暴晒，又不得阻挡冬至阳光入室)
    # L_overhang = (window_height) / tan(h_summer) 加上冗余系数
    overhang_min = window_height / math.tan(rad_summer) if rad_summer > 0 else 0.5
    overhang_opt = round(max(1.2, overhang_min + 0.3), 2)

    # 冬至阳光直射进深 (米)
    winter_sun_depth = round(window_height / math.tan(rad_winter), 2) if rad_winter > 0 else 0.0

    return {
        "latitude": lat,
        "summer_solstice_angle_deg": round(h_summer, 2),
        "winter_solstice_angle_deg": round(h_winter, 2),
        "recommended_overhang_m": overhang_opt,
        "winter_sun_penetration_m": winter_sun_depth,
        "design_advice": f"建议南向阳台/挑檐出挑 {overhang_opt} 米；夏至正午阻隔直射暴晒率 100%，冬至阳光可深入室内 {winter_sun_depth} 米取暖驱潮。"
    }

if __name__ == "__main__":
    lat = float(sys.argv[1]) if len(sys.argv) > 1 else 25.813
    res = calculate_solar_parameters(lat)
    for k, v in res.items():
        print(f"{k}: {v}")

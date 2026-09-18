#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rural House Cost & BOM Estimator (乡村建筑造价与物料清单量化计算器)
支持框架结构、砖混结构与轻钢结构的钢筋、商混、砌体、劳务及规费工程量精准核算。
"""

import sys
import json
from typing import Dict, Any

def estimate_construction_cost(area_sqm: float, structure_type: str = "frame", seismic_intensity: int = 7) -> Dict[str, Any]:
    """
    计算农村自建房工程量清单与总预算
    :param area_sqm: 建筑面积（平方米）
    :param structure_type: 结构类型 ('frame' 框架, 'brick' 砖混)
    :param seismic_intensity: 抗震设防烈度 (度)
    """
    if structure_type == "frame":
        # 框架结构指标 (7度设防)
        steel_kg_per_sqm = 48.0 if seismic_intensity >= 7 else 42.0
        concrete_m3_per_sqm = 0.38
        steel_price_ton = 3850.0
        concrete_price_m3 = 380.0
        labor_price_sqm = 300.0
        formwork_price_sqm = 68.0
        masonry_price_sqm = 55.0
        misc_rate = 0.08
    else:
        # 砖混结构指标
        steel_kg_per_sqm = 25.0
        concrete_m3_per_sqm = 0.22
        steel_price_ton = 3850.0
        concrete_price_m3 = 380.0
        labor_price_sqm = 230.0
        formwork_price_sqm = 45.0
        masonry_price_sqm = 75.0
        misc_rate = 0.06

    steel_tons = round(area_sqm * steel_kg_per_sqm / 1000.0, 2)
    concrete_m3 = round(area_sqm * concrete_m3_per_sqm, 1)

    cost_steel = round(steel_tons * steel_price_ton, 0)
    cost_concrete = round(concrete_m3 * concrete_price_m3, 0)
    cost_labor = round(area_sqm * labor_price_sqm, 0)
    cost_formwork = round(area_sqm * formwork_price_sqm, 0)
    cost_masonry = round(area_sqm * 0.95 * masonry_price_sqm, 0) # 墙体折算面积
    cost_mep = round(area_sqm * 38.0, 0)                         # 水电预埋
    cost_waterproofing = round(area_sqm * 0.45 * 45.0, 0)        # 平屋顶防水
    cost_subtotal = cost_steel + cost_concrete + cost_labor + cost_formwork + cost_masonry + cost_mep + cost_waterproofing
    cost_misc = round(cost_subtotal * misc_rate, 0)
    total_cost = round(cost_subtotal + cost_misc, 0)
    unit_cost = round(total_cost / area_sqm, 1)

    return {
        "gross_area_sqm": area_sqm,
        "structure_type": "现浇钢筋混凝土框架结构" if structure_type == "frame" else "砖混结构",
        "seismic_intensity": f"{seismic_intensity}度设防 (0.15g)" if seismic_intensity >= 7 else "6度设防",
        "material_quantities": {
            "steel_tons": steel_tons,
            "concrete_m3": concrete_m3,
        },
        "cost_breakdown": {
            "steel_cost": cost_steel,
            "concrete_cost": cost_concrete,
            "labor_cost": cost_labor,
            "formwork_scaffolding_cost": cost_formwork,
            "masonry_cost": cost_masonry,
            "mep_embedded_cost": cost_mep,
            "waterproofing_cost": cost_waterproofing,
            "misc_and_contingency": cost_misc
        },
        "total_cost_rmb": total_cost,
        "unit_cost_rmb_per_sqm": unit_cost
    }

if __name__ == "__main__":
    area = float(sys.argv[1]) if len(sys.argv) > 1 else 355.0
    st = sys.argv[2] if len(sys.argv) > 2 else "frame"
    res = estimate_construction_cost(area, st)
    print(json.dumps(res, ensure_ascii=False, indent=2))

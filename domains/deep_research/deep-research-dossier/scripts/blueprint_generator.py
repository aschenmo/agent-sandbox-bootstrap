#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Architectural Blueprint Generator (建筑平面图矢量生成引擎)
专门针对 贵州关岭断桥镇坡舟村郎先组 10m×30m 场地生成 1:100 高精度建筑工程布局图
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def draw_master_plan(output_path: str):
    """绘制总平面布局规划图 (10m x 30m 地块分区：前院 7m + 主宅 17m + 后院 6m)"""
    fig, ax = plt.subplots(figsize=(8, 16), dpi=200)
    
    # 30m x 10m 总红线边界 (X: 0~10m, Y: 0~30m)
    # 南在下 (Y=0), 北在上 (Y=30), 西在左 (X=0), 东在右 (X=10)
    ax.set_xlim(-1.5, 11.5)
    ax.set_ylim(-2, 32)
    ax.set_aspect('equal')
    ax.axis('off')

    # 背景
    rect_bg = patches.Rectangle((0, 0), 10, 30, linewidth=2, edgecolor='#1b3b6f', facecolor='#f8f9fa', linestyle='-')
    ax.add_patch(rect_bg)

    # 1. 前院 (Y: 0 ~ 7m, 70㎡)
    rect_front = patches.Rectangle((0, 0), 10, 7, linewidth=1.5, edgecolor='#2b9348', facecolor='#e8f5e9', alpha=0.8)
    ax.add_patch(rect_front)
    ax.text(5, 3.5, "【南向开敞前院】\n进深 7.0m × 面宽 10.0m (70㎡)\n• 露天私家车位 (硬化地面)\n• 入户景观绿化 & 农忙晒场\n• 标高 -0.450 (室外自然地坪)", 
            ha='center', va='center', fontsize=10, color='#1b5e20', fontweight='bold')

    # 2. 主宅主体 (Y: 7 ~ 24m, 170㎡)
    rect_main = patches.Rectangle((0, 7), 10, 17, linewidth=2.5, edgecolor='#b7094c', facecolor='#fff0f3')
    ax.add_patch(rect_main)
    ax.text(5, 15.5, "【2.5层 现代极简主宅建筑主体】\n进深 17.0m × 面宽 10.0m (单层基底 170㎡)\n\n• 现浇钢筋混凝土框架结构 (7度抗震设防 0.15g)\n• 室内首层地坪标高 ±0.000 (比院落抬高 450mm 防潮)\n• 1F: 堂屋 + 向阳老人套房 + 双厨(柴火+现代) + 储物 + 客卧\n• 2F: 主卧套房 + 4间次卧 + 中央起居厅\n• 2.5F: 景观客卧/茶室 + 110㎡全平屋顶大晒台\n• 总建筑面积: 约 355㎡ (造价严格锁定 28~34 万元)", 
            ha='center', va='center', fontsize=10, color='#800f2f', fontweight='bold')

    # 3. 后院 (Y: 24 ~ 30m, 60㎡)
    rect_back = patches.Rectangle((0, 24), 10, 6, linewidth=1.5, edgecolor='#55a630', facecolor='#f1faee', alpha=0.8)
    ax.add_patch(rect_back)
    ax.text(5, 27, "【北向生活后院】\n进深 6.0m × 面宽 10.0m (60㎡)\n• 柴火堆放区 & 柴火灶烟道排烟缓冲\n• 通往后菜园与后门生活通道 (倒垃圾/运柴)\n• 三格式化粪池与后勤杂物区", 
            ha='center', va='center', fontsize=10, color='#2b9348', fontweight='bold')

    # 尺寸标注线
    # 总宽 10m
    ax.annotate('', xy=(0, -0.8), xytext=(10, -0.8), arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))
    ax.text(5, -1.5, "总面宽 10.00 m", ha='center', va='center', fontsize=11, fontweight='bold')

    # 总长 30m (左侧)
    ax.annotate('', xy=(-0.8, 0), xytext=(-0.8, 30), arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))
    ax.text(-1.3, 15, "总进深 30.00 m", ha='center', va='center', fontsize=11, fontweight='bold', rotation=90)

    # 分段尺寸 (右侧)
    ax.annotate('', xy=(10.8, 0), xytext=(10.8, 7), arrowprops=dict(arrowstyle='<->', color='#555', lw=1))
    ax.text(11.3, 3.5, "前院 7.0m", ha='center', va='center', fontsize=9, rotation=90)
    ax.annotate('', xy=(10.8, 7), xytext=(10.8, 24), arrowprops=dict(arrowstyle='<->', color='#555', lw=1))
    ax.text(11.3, 15.5, "主宅 17.0m", ha='center', va='center', fontsize=9, rotation=90)
    ax.annotate('', xy=(10.8, 24), xytext=(10.8, 30), arrowprops=dict(arrowstyle='<->', color='#555', lw=1))
    ax.text(11.3, 27, "后院 6.0m", ha='center', va='center', fontsize=9, rotation=90)

    # 指北针 (右上角)
    ax.annotate('北 (N)', xy=(9, 31.2), xytext=(9, 29.8),
                arrowprops=dict(facecolor='#d90429', edgecolor='black', width=3, headwidth=10),
                ha='center', va='bottom', fontsize=10, fontweight='bold', color='#d90429')

    plt.title("贵州关岭断桥镇坡舟村郎先组自建房 - 地块总平面规划图 (10m × 30m)\n[前院 7m + 现代平顶主宅 17m + 后院 6m]", 
              fontsize=13, fontweight='bold', pad=20, color='#0f2027')
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Master plan saved: {output_path}")

def draw_first_floor_plan(output_path: str):
    """绘制一层平面工程建筑施工布局图 (10m x 17m 室内净布局)"""
    fig, ax = plt.subplots(figsize=(11, 16), dpi=200)
    ax.set_xlim(-2, 12)
    ax.set_ylim(-2, 19)
    ax.set_aspect('equal')
    ax.axis('off')

    # 外轮廓墙体 (10m x 17m, Y: 0~17, X: 0~10)
    # 南向在下 (Y=0), 北向在上 (Y=17)
    outer_wall = patches.Rectangle((0, 0), 10, 17, linewidth=3.5, edgecolor='#1d3557', facecolor='#ffffff')
    ax.add_patch(outer_wall)

    # 绘制房间隔墙与功能分区
    # 1. 传统大堂屋/中堂 (居中偏南, 面宽 4.8m x 进深 6.2m, 约 30㎡)
    # 位置: X: 2.6 ~ 7.4m, Y: 0 ~ 6.2m
    rect_tangwu = patches.Rectangle((2.6, 0), 4.8, 6.2, linewidth=2, edgecolor='#1d3557', facecolor='#f8f9fa')
    ax.add_patch(rect_tangwu)
    ax.text(5.0, 3.1, "【传统宽敞大堂屋】\n4.8m × 6.2m (29.8㎡)\n• 正中大门迎前院阳光\n• 北侧背景墙设照壁/神龛位\n• 农村红白喜事/家族聚会议事大厅", 
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1d3557')

    # 2. 向阳老人房 (带独立卫浴, 位于西南角采光最佳处, X: 0 ~ 4.2m, Y: 0 ~ 4.5m)
    # 调整: 堂屋 X=3.6~8.2m 或 老人房在东/西侧。
    # 优化布局:
    # 面宽 10m 分为: 西侧 4.0m (老人房套间), 东侧 6.0m (堂屋 4.2m + 门厅走道 1.8m)
    # 重绘更合理的柱网布局 (X轴开间: 4.2m + 1.8m + 4.0m = 10m; Y轴进深: 4.5m + 4.5m + 4.2m + 3.8m = 17m)

    rooms = [
        # (x, y, w, h, name, color)
        # 南向西侧: 向阳长辈老人套房 (4.2m x 4.8m = 20.2㎡)
        (0.2, 0.2, 4.0, 5.0, "【向阳尊享老人房 (卧①)】\n4.0m × 5.0m (20.0㎡)\n• 南向落地大窗，光照充沛\n• 无障碍平地无门槛防滑", "#e8eaf6"),
        # 老人房独立卫生间 (位于老人房北侧 2.0m x 2.2m)
        (0.2, 5.2, 2.2, 2.0, "老人房独卫\n2.2m×2.0m\n适老扶手/防滑", "#e1f5fe"),
        # 农资储物间 (位于老人房独卫旁 1.8m x 2.0m)
        (2.4, 5.2, 1.8, 2.0, "【农具储物间】\n1.8m×2.0m\n放农资/杂物", "#fff9c4"),

        # 南向偏东: 传统大堂屋 (面宽 5.6m x 进深 6.8m = 38㎡)
        (4.4, 0.2, 5.4, 7.0, "【传统宽阔大中堂/大堂屋】\n5.6m × 7.0m (39.2㎡)\n• 南向双开实木迎福大门\n• 正中北立面庄严神龛照壁位\n• 挑空宏大，红白喜事宴席核心", "#fce4ec"),

        # 中部西侧: 室内客卧② (4.0m x 3.8m = 15.2㎡)
        (0.2, 7.4, 4.0, 4.0, "【首层舒适客卧 (卧②)】\n4.0m × 4.0m (16.0㎡)\n• 侧向全明开窗采光", "#ede7f6"),

        # 中部居中: 楼梯间与公卫 (楼梯宽 2.6m x 长 4.0m)
        (4.4, 7.4, 2.8, 4.0, "【双跑楼梯间】\n2.8m × 4.0m\n楼梯下做隐藏储物柜", "#e0e0e0"),
        # 中部客卫 (2.4m x 2.2m)
        (7.4, 7.4, 2.4, 2.2, "【首层公共卫生间】\n2.4m×2.2m (干湿分离)", "#e1f5fe"),
        # 过道/小景天窗
        (7.4, 9.8, 2.4, 1.6, "换鞋玄关/洗手台", "#f5f5f5"),

        # 北侧: 宽敞大餐厅 (4.0m x 5.0m = 20㎡, 设12人大圆桌)
        (0.2, 11.6, 4.0, 5.2, "【多功能聚会大餐厅】\n4.0m × 5.2m (20.8㎡)\n• 容纳 10~12 人喜庆大圆桌\n• 邻近双厨，端菜动线极短", "#fff3e0"),

        # 北侧东部: 现代洁净大厨房 (2.8m x 5.2m)
        (4.4, 11.6, 2.8, 5.2, "【现代洁净大厨房】\n2.8m × 5.2m (14.5㎡)\n• L型石英石台面/燃气集成灶\n• 宽敞明亮无油烟", "#e0f2f1"),

        # 东北角: 传统土柴火灶厨房 (2.4m x 5.2m, 带独立后门通道)
        (7.4, 11.6, 2.4, 5.2, "【传统土柴火灶房】\n2.4m × 5.2m (12.5㎡)\n• 双眼大铁锅土灶台\n• 独立排烟通屋顶\n• 开后门通后院运柴/倒灰", "#ffebee")
    ]

    for (x, y, w, h, name, col) in rooms:
        rect = patches.Rectangle((x, y), w, h, linewidth=1.5, edgecolor='#333333', facecolor=col, alpha=0.9)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, name, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#212121')

    # 标注门洞与开启弧线
    # 主入户大门 (南向 Y=0, X: 6.2~8.0m)
    ax.plot([6.2, 8.0], [0, 0], color='#d90429', linewidth=4)
    ax.text(7.1, -0.4, "主入户双开大门 (宽 1.8m)", ha='center', va='top', fontsize=9, color='#d90429', fontweight='bold')

    # 后院门 (北向 Y=17, X: 8.0~9.2m)
    ax.plot([8.0, 9.2], [17, 17], color='#2b9348', linewidth=4)
    ax.text(8.6, 17.4, "后生活门 (通后院菜园/运柴火)", ha='center', va='bottom', fontsize=9, color='#2b9348', fontweight='bold')

    # 轴网标注
    # X轴尺寸 (面宽 10m)
    ax.annotate('', xy=(0, -1.0), xytext=(10, -1.0), arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))
    ax.text(5, -1.5, "建筑总面宽 10.00 m (轴网跨度 4.2m + 5.8m)", ha='center', va='center', fontsize=10, fontweight='bold')

    # Y轴尺寸 (进深 17m)
    ax.annotate('', xy=(-0.8, 0), xytext=(-0.8, 17), arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))
    ax.text(-1.3, 8.5, "建筑总进深 17.00 m", ha='center', va='center', fontsize=10, fontweight='bold', rotation=90)

    plt.title("首层建筑工程平面布局图 (1:100 等比例方案)\n[占地 170㎡ | 堂屋 + 向阳老人套房 + 双厨联动 + 储物间 + 餐厅 + 客卧]", 
              fontsize=13, fontweight='bold', pad=22, color='#0f2027')
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"First floor plan saved: {output_path}")

def draw_second_floor_plan(output_path: str):
    """绘制二层建筑平面布局图 (5间舒适卧室 + 中央起居厅 + 景观阳台)"""
    fig, ax = plt.subplots(figsize=(11, 16), dpi=200)
    ax.set_xlim(-2, 12)
    ax.set_ylim(-2, 19)
    ax.set_aspect('equal')
    ax.axis('off')

    outer_wall = patches.Rectangle((0, 0), 10, 17, linewidth=3.5, edgecolor='#1d3557', facecolor='#ffffff')
    ax.add_patch(outer_wall)

    rooms = [
        # 南向主卧大套房 (带独卫与衣帽间, 4.2m x 5.0m = 21㎡)
        (0.2, 0.2, 4.0, 5.0, "【豪华主卧套房 (卧③)】\n4.0m × 5.0m (20.0㎡)\n• 南向大落地窗\n• 带独立卫浴 & 步入式衣帽间", "#e8eaf6"),
        (0.2, 5.2, 2.2, 2.0, "主卧独卫\n2.2m×2.0m", "#e1f5fe"),
        (2.4, 5.2, 1.8, 2.0, "衣帽间\n1.8m×2.0m", "#fff9c4"),

        # 南向次卧④ (4.0m x 4.0m = 16㎡) + 景观大阳台
        (4.4, 2.0, 5.4, 5.2, "【南向景观次卧 (卧④)】\n5.4m × 5.2m (28.0㎡ / 超大客套)\n• 直通南向出挑 1.35m 遮阳阳台\n• 远眺打邦河谷田园风光", "#fce4ec"),
        # 南向出挑阳台 (出挑 1.35m, 阻隔夏至烈日)
        (4.4, 0.2, 5.4, 1.8, "【南向出挑遮阳景观阳台】\n出挑 1.35m (夏季遮阳/冬季采光)", "#e0f2f1"),

        # 中部起居厅 (4.0m x 4.0m)
        (0.2, 7.4, 4.0, 4.0, "【二层家庭温馨起居厅】\n4.0m × 4.0m (16.0㎡)\n• 晚间家人看电视/聊天私密厅", "#ede7f6"),

        # 中部楼梯与公卫
        (4.4, 7.4, 2.8, 4.0, "【双跑楼梯间】\n2.8m × 4.0m", "#e0e0e0"),
        (7.4, 7.4, 2.4, 2.2, "【二层公共卫生间】\n2.4m×2.2m", "#e1f5fe"),
        (7.4, 9.8, 2.4, 1.6, "洗衣/收纳区", "#f5f5f5"),

        # 北向三间次卧 (保证总共8间卧室)
        # 北向卧室⑤ (4.0m x 5.2m = 20.8㎡)
        (0.2, 11.6, 4.0, 5.2, "【宽敞次卧 (卧⑤)】\n4.0m × 5.2m (20.8㎡)\n• 北向全景窗/清爽安静", "#fff3e0"),
        # 北向卧室⑥ (2.8m x 5.2m = 14.5㎡)
        (4.4, 11.6, 2.8, 5.2, "【阳光次卧 (卧⑥)】\n2.8m × 5.2m (14.5㎡)\n• 儿童房/书房兼卧", "#e0f2f1"),
        # 北向卧室⑦ (2.4m x 5.2m = 12.5㎡)
        (7.4, 11.6, 2.4, 5.2, "【静谧次卧 (卧⑦)】\n2.4m × 5.2m (12.5㎡)\n• 青年房/独立客房", "#ffebee")
    ]

    for (x, y, w, h, name, col) in rooms:
        rect = patches.Rectangle((x, y), w, h, linewidth=1.5, edgecolor='#333333', facecolor=col, alpha=0.9)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, name, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#212121')

    # 尺寸标注
    ax.annotate('', xy=(0, -1.0), xytext=(10, -1.0), arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))
    ax.text(5, -1.5, "建筑总面宽 10.00 m", ha='center', va='center', fontsize=10, fontweight='bold')

    ax.annotate('', xy=(-0.8, 0), xytext=(-0.8, 17), arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))
    ax.text(-1.3, 8.5, "建筑总进深 17.00 m", ha='center', va='center', fontsize=10, fontweight='bold', rotation=90)

    plt.title("二层建筑工程平面布局图 (1:100 等比例方案)\n[建面 155㎡ | 5间卧室(含主卧大套) + 家庭起居厅 + 双卫 + 出挑遮阳阳台]", 
              fontsize=13, fontweight='bold', pad=22, color='#0f2027')
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Second floor plan saved: {output_path}")

def draw_roof_plan(output_path: str):
    """绘制 2.5层与平屋顶大晒台平面布置图"""
    fig, ax = plt.subplots(figsize=(11, 16), dpi=200)
    ax.set_xlim(-2, 12)
    ax.set_ylim(-2, 19)
    ax.set_aspect('equal')
    ax.axis('off')

    outer_wall = patches.Rectangle((0, 0), 10, 17, linewidth=3.5, edgecolor='#1d3557', facecolor='#ffffff')
    ax.add_patch(outer_wall)

    # 1. 顶层封闭房间 (X: 3.5 ~ 9.8, Y: 7.0 ~ 13.0, 约 40㎡)
    rect_room = patches.Rectangle((3.6, 7.0), 6.2, 5.0, linewidth=2, edgecolor='#1d3557', facecolor='#e8f5e9')
    ax.add_patch(rect_room)
    ax.text(6.7, 9.5, "【顶层景观多功能客房 (卧⑧) & 储物茶水间】\n6.2m × 5.0m (31.0㎡)\n• 独立第8间景观卧室/家庭影音/茶室\n• 楼梯间直通顶层，设水吧台与洗衣间", 
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1b5e20')

    # 2. 超大全平屋顶晾晒露台 (其余面积约 130㎡)
    rect_roof_south = patches.Rectangle((0.2, 0.2), 9.6, 6.6, linewidth=1.5, edgecolor='#388e3c', facecolor='#fffde7', linestyle='--')
    ax.add_patch(rect_roof_south)
    ax.text(5.0, 3.5, "【南向超大全景屋顶晒台 (全面积平屋顶踩踏)】\n9.6m × 6.6m (63.3㎡)\n• 现代极简风格全平屋顶\n• 农忙暴晒稻谷/玉米/香肠腊肉\n• 夏夜观星露营、烧烤聚会", 
            ha='center', va='center', fontsize=10, fontweight='bold', color='#f57f17')

    rect_roof_north = patches.Rectangle((0.2, 12.2), 9.6, 4.6, linewidth=1.5, edgecolor='#388e3c', facecolor='#fffde7', linestyle='--')
    ax.add_patch(rect_roof_north)
    ax.text(5.0, 14.5, "【北向屋顶观景平台】\n9.6m × 4.6m (44.2㎡)\n• 俯瞰打邦河谷山水全景\n• 设有太阳能热水器与集中光伏位", 
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#f57f17')

    # 尺寸标注
    ax.annotate('', xy=(0, -1.0), xytext=(10, -1.0), arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))
    ax.text(5, -1.5, "建筑总面宽 10.00 m", ha='center', va='center', fontsize=10, fontweight='bold')

    ax.annotate('', xy=(-0.8, 0), xytext=(-0.8, 17), arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))
    ax.text(-1.3, 8.5, "建筑总进深 17.00 m", ha='center', va='center', fontsize=10, fontweight='bold', rotation=90)

    plt.title("2.5层 多功能房与全平屋顶大晒台平面图 (1:100)\n[顶层卧⑧ + 110㎡ 现代平顶全踩踏晒台 | 满足粮食晾晒与现代极简度假风]", 
              fontsize=13, fontweight='bold', pad=22, color='#0f2027')
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Roof plan saved: {output_path}")

if __name__ == "__main__":
    out_dir = "/home/chenmo/.gemini/antigravity-cli/brain/9e8680b1-89fa-484e-9eea-fcd3f333fbc9"
    draw_master_plan(f"{out_dir}/plan_master_30x10.png")
    draw_first_floor_plan(f"{out_dir}/plan_1f_30x10.png")
    draw_second_floor_plan(f"{out_dir}/plan_2f_30x10.png")
    draw_roof_plan(f"{out_dir}/plan_roof_30x10.png")

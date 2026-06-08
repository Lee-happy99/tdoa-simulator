# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.font_manager as fm
import os

# ------------------- 中文字体配置 -------------------
font_path = os.path.join(os.path.dirname(__file__), 'simhei.ttf')
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = fm.FontProperties(fname=font_path).get_name()
else:
    st.warning("字体文件 simhei.ttf 未找到，将使用默认字体（可能显示方块）")
plt.rcParams['axes.unicode_minus'] = False

# ------------------- 页面配置 -------------------
st.set_page_config(page_title="无源定位：圆定位演示", layout="wide")

# 修正标题居中、减小与下方文字的行距
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem !important;
    }
    h1 {
        font-size: 1.8rem !important;
        text-align: center !important;
        margin-top: 0rem !important;
        margin-bottom: 0.2rem !important;
        line-height: 1.2 !important;
    }
    /* 调整标题下方说明文字的间距 */
    .stMarkdown p {
        margin-top: 0rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("📡 无源定位：从单站测距到三站协同锁定")
st.markdown("**拖动左侧滑块调整三个侦察站的位置，观察圆交点如何唯一确定目标**")

# ------------------- 侧边栏（紧凑布局） -------------------
st.sidebar.header("📍 侦察站坐标 (km)")

col1, col2 = st.sidebar.columns(2)
with col1:
    x1 = st.slider("站1 x", -20.0, 20.0, -8.0, 0.5)
with col2:
    y1 = st.slider("站1 y", -20.0, 20.0, 0.0, 0.5)

col1, col2 = st.sidebar.columns(2)
with col1:
    x2 = st.slider("站2 x", -20.0, 20.0, 8.0, 0.5)
with col2:
    y2 = st.slider("站2 y", -20.0, 20.0, 0.0, 0.5)

col1, col2 = st.sidebar.columns(2)
with col1:
    x3 = st.slider("站3 x", -20.0, 20.0, 0.0, 0.5)
with col2:
    y3 = st.slider("站3 y", -20.0, 20.0, 12.0, 0.5)

st.sidebar.markdown("---")
col1, col2 = st.sidebar.columns(2)
with col1:
    target_x = st.slider("🎯 目标点 x", -20.0, 20.0, 5.0, 0.5)
with col2:
    target_y = st.slider("🎯 目标点 y", -20.0, 20.0, 5.0, 0.5)

# ------------------- 辅助函数 -------------------
def distance(p1, p2):
    return np.hypot(p1[0]-p2[0], p1[1]-p2[1])

def circle_intersection(c1, r1, c2, r2):
    x1, y1 = c1
    x2, y2 = c2
    dx, dy = x2 - x1, y2 - y1
    d = np.hypot(dx, dy)
    if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
        return []
    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h = np.sqrt(r1**2 - a**2)
    xm = x1 + (dx * a / d)
    ym = y1 + (dy * a / d)
    rx = -dy * (h / d)
    ry = dx * (h / d)
    return [(xm + rx, ym + ry), (xm - rx, ym - ry)]

# ------------------- 计算 -------------------
s1 = np.array([x1, y1])
s2 = np.array([x2, y2])
s3 = np.array([x3, y3])
target = np.array([target_x, target_y])

d1 = distance(s1, target)
d2 = distance(s2, target)
d3 = distance(s3, target)

intersections_12 = circle_intersection(s1, d1, s2, d2)

# ------------------- 绘图 -------------------
fig, ax = plt.subplots(figsize=(8, 7))
ax.set_xlim(-20, 20)
ax.set_ylim(-20, 20)
ax.set_xlabel("x (km)")
ax.set_ylabel("y (km)")
ax.grid(True, alpha=0.3)
ax.set_aspect('equal')

# 侦察站
ax.plot(x1, y1, 'o', color='blue', markersize=10)
ax.plot(x2, y2, 'o', color='blue', markersize=10)
ax.plot(x3, y3, 'o', color='blue', markersize=10)
ax.text(x1, y1-1.2, "侦察站1", color='blue', fontsize=10, ha='center', weight='bold')
ax.text(x2, y2-1.2, "侦察站2", color='blue', fontsize=10, ha='center', weight='bold')
ax.text(x3, y3-1.2, "侦察站3", color='blue', fontsize=10, ha='center', weight='bold')

# 目标点（红色五角星，放大）
ax.plot(target_x, target_y, 'r*', markersize=22, label='_nolegend_')
ax.text(target_x + 1.2, target_y + 1.5, "目标点", color='red', fontsize=11, ha='left', weight='bold')

# 测距圆
circle1 = Circle(s1, d1, edgecolor='blue', facecolor='none', linewidth=1.5, linestyle='--')
circle2 = Circle(s2, d2, edgecolor='blue', facecolor='none', linewidth=1.5, linestyle='--')
circle3 = Circle(s3, d3, edgecolor='blue', facecolor='none', linewidth=1.5, linestyle='--')
ax.add_patch(circle1)
ax.add_patch(circle2)
ax.add_patch(circle3)

# 歧义点
low_sat_orange = '#FFB347'
if len(intersections_12) == 2:
    for i, (ix, iy) in enumerate(intersections_12):
        ax.plot(ix, iy, 'o', markerfacecolor='white', markeredgecolor=low_sat_orange,
                markersize=12, markeredgewidth=2.5)
        if i == 0:
            ax.text(ix - 1.8, iy - 1.5, f"歧义点1", color=low_sat_orange, fontsize=10, ha='center', weight='bold')
        else:
            ax.text(ix + 1.5, iy - 1.5, f"歧义点2", color=low_sat_orange, fontsize=10, ha='center', weight='bold')
    st.sidebar.success("✅ 站1与站2有两个交点（双解歧义）")

    unique_idx = None
    for idx, (ix, iy) in enumerate(intersections_12):
        if abs(np.hypot(ix - s3[0], iy - s3[1]) - d3) < 0.5:
            unique_idx = idx
            break

    if unique_idx is not None:
        ix, iy = intersections_12[unique_idx]
        ax.plot(ix, iy, 'o', color='lime', markersize=10, zorder=10, markeredgecolor='darkgreen', markeredgewidth=1)
        ax.text(ix, iy + 1.8, "✓ 唯一解", color='green', fontsize=11, ha='center', weight='bold')
        st.sidebar.success("🎉 三站协同：唯一锁定目标点（第三圆通过其中一个交点）")
    else:
        st.sidebar.info("🔍 第三个圆未精确通过任一交点，调整目标或站址观察唯一锁定")
else:
    st.sidebar.warning("❌ 站1与站2的圆不相交，请调整站址或目标位置")

# 图例
ax.plot([], [], 'b--', label='测距圆')
ax.plot([], [], 'bo', label='侦察站')
ax.plot([], [], 'r*', markersize=10, label='目标点')
ax.plot([], [], 'o', markerfacecolor='white', markeredgecolor=low_sat_orange, markersize=8, label='双站交点（歧义）')
ax.plot([], [], 'o', color='lime', markersize=8, label='三站唯一解')
ax.legend(loc='upper right')

st.pyplot(fig, use_container_width=True)

with st.expander("📖 无源定位原理（点击展开）"):
    st.markdown("""
    - **单站测距**：一个侦察站只能确定目标在以站为圆心、距离为半径的圆上，无法定位具体点。  
    - **双站相交**：两个圆一般有两个交点，产生歧义，无法唯一确定目标。  
    - **三站协同**：第三个圆会通过其中一个交点，从而消除歧义，实现唯一锁定。  
    - **操作提示**：拖动左侧滑块调整侦察站或目标位置，观察两个歧义点（橙色空心圆）以及第三个圆如何锁定正确交点。
    """)

# 侧边栏链接已注释

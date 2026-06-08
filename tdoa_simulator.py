# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.font_manager import FontProperties
import io

# 设置中文字体（解决云端方框问题）
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="无源定位原理演示", layout="wide")
st.title("📡 无源定位：从单站测距到三站协同锁定")
st.markdown("**拖动左侧滑块，观察三个侦察站如何逐步确定目标位置**")

# ------------------- 侧边栏控制 -------------------
st.sidebar.header("📍 侦察站坐标 (km)")
x1 = st.sidebar.slider("站1 x", -20.0, 20.0, -8.0, 0.5)
y1 = st.sidebar.slider("站1 y", -20.0, 20.0, 0.0, 0.5)
x2 = st.sidebar.slider("站2 x", -20.0, 20.0, 8.0, 0.5)
y2 = st.sidebar.slider("站2 y", -20.0, 20.0, 0.0, 0.5)
x3 = st.sidebar.slider("站3 x", -20.0, 20.0, 0.0, 0.5)
y3 = st.sidebar.slider("站3 y", -20.0, 20.0, 12.0, 0.5)

target_x = st.sidebar.slider("🎯 目标点 x", -20.0, 20.0, 5.0, 0.5)
target_y = st.sidebar.slider("🎯 目标点 y", -20.0, 20.0, 5.0, 0.5)

# 三个站坐标
s1 = np.array([x1, y1])
s2 = np.array([x2, y2])
s3 = np.array([x3, y3])
target = np.array([target_x, target_y])

# 计算各站到目标的距离
d1 = np.linalg.norm(target - s1)
d2 = np.linalg.norm(target - s2)
d3 = np.linalg.norm(target - s3)

# ------------------- 绘图 -------------------
fig, ax = plt.subplots(figsize=(9, 8))
ax.set_xlim(-20, 20)
ax.set_ylim(-20, 20)
ax.set_xlabel("x (km)")
ax.set_ylabel("y (km)")
ax.grid(True, alpha=0.3)
ax.set_aspect('equal')

# 1. 画三个侦察站（蓝色实心圆）
ax.plot(x1, y1, 'o', color='blue', markersize=10, label='_nolegend_')
ax.plot(x2, y2, 'o', color='blue', markersize=10, label='_nolegend_')
ax.plot(x3, y3, 'o', color='blue', markersize=10, label='_nolegend_')
# 蓝色字体标注
ax.text(x1, y1-1.2, "侦察站1", color='blue', fontsize=10, ha='center', weight='bold')
ax.text(x2, y2-1.2, "侦察站2", color='blue', fontsize=10, ha='center', weight='bold')
ax.text(x3, y3-1.2, "侦察站3", color='blue', fontsize=10, ha='center', weight='bold')

# 2. 画目标点（红色实心五角星）
ax.plot(target_x, target_y, 'r*', markersize=18, label='_nolegend_')
ax.text(target_x, target_y+1.2, "目标点", color='red', fontsize=10, ha='center', weight='bold')

# 3. 画三个圆（以侦察站为圆心，距离为半径）
circle1 = Circle(s1, d1, edgecolor='blue', facecolor='none', linewidth=1.5, linestyle='--')
circle2 = Circle(s2, d2, edgecolor='blue', facecolor='none', linewidth=1.5, linestyle='--')
circle3 = Circle(s3, d3, edgecolor='blue', facecolor='none', linewidth=1.5, linestyle='--')
ax.add_patch(circle1)
ax.add_patch(circle2)
ax.add_patch(circle3)

# 4. 计算并标注两个站相交的交点（站1和站2）
def circle_intersection(c1, r1, c2, r2):
    """返回两个圆的交点列表（可能0,1,2个）"""
    x1, y1 = c1
    x2, y2 = c2
    dx, dy = x2 - x1, y2 - y1
    d = np.hypot(dx, dy)
    if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
        return []
    a = (r1**2 - r2**2 + d**2) / (2*d)
    h = np.sqrt(r1**2 - a**2)
    xm = x1 + (dx * a / d)
    ym = y1 + (dy * a / d)
    rx = -dy * (h / d)
    ry = dx * (h / d)
    return [(xm + rx, ym + ry), (xm - rx, ym - ry)]

intersections = circle_intersection(s1, d1, s2, d2)
if len(intersections) == 2:
    # 用橙色圆点标注两个交点
    ax.plot(intersections[0][0], intersections[0][1], 'o', color='orange', markersize=8, label='_nolegend_')
    ax.plot(intersections[1][0], intersections[1][1], 'o', color='orange', markersize=8, label='_nolegend_')
    ax.text(intersections[0][0], intersections[0][1]+0.8, "交点1", color='orange', fontsize=9, ha='center')
    ax.text(intersections[1][0], intersections[1][1]+0.8, "交点2", color='orange', fontsize=9, ha='center')
    st.sidebar.success("✅ 站1与站2有两个交点（双解歧义）")
elif len(intersections) == 1:
    st.sidebar.info("⚪ 站1与站2相切，仅一个交点")
else:
    st.sidebar.warning("❌ 站1与站2的圆不相交")

# 5. 判断三个圆是否交于唯一一点（实际就是目标点附近）
# 简单判断：站3的圆是否经过站1&站2的某个交点
if len(intersections) == 2:
    # 分别计算两个交点与站3的距离，是否接近 d3
    for ix, (ix_, iy_) in enumerate(intersections):
        dist_to_s3 = np.hypot(ix_ - s3[0], iy_ - s3[1])
        if abs(dist_to_s3 - d3) < 0.5:  # 允许一定误差
            st.sidebar.success("🎉 **三站协同：唯一锁定目标点**（站3的圆通过其中一个交点）")
            # 用绿色高亮那个正确交点
            ax.plot(ix_, iy_, 'o', color='lime', markersize=12, markeredgecolor='black', label='_nolegend_')
            ax.text(ix_, iy_+1.2, "唯一解", color='lime', fontsize=10, weight='bold')
            break
    else:
        st.sidebar.info("🔍 站3的圆未与站1&站2的交点精确重合，调整目标或站址观察唯一锁定现象")
else:
    st.sidebar.info("请调整站址或目标位置，使站1与站2产生两个交点，再加入站3实现唯一锁定")

# 图例说明（手动）
ax.plot([], [], 'b--', label='测距圆 (半径=距离)')
ax.plot([], [], 'bo', label='侦察站')
ax.plot([], [], 'r*', label='目标点')
ax.plot([], [], 'o', color='orange', label='双站交点 (歧义)')
ax.plot([], [], 'o', color='lime', label='三站唯一解')
ax.legend(loc='upper right')

st.pyplot(fig)

# 教学说明
st.info("""
**📖 观察指导（对应微课AI赋能点①）**
- **单站**：一个侦察站只能画出一个圆（目标可能在圆周上任意点）。
- **双站**：两个圆一般相交于**两个点**（双解歧义），无法唯一确定目标。
- **三站**：引入第三个侦察站，它的圆只会通过其中一个交点，从而**消除歧义、唯一锁定**。
> ✨ 拖动滑块改变站址或目标位置，观察圆交点的变化。尝试让三站共线，看定位误差如何放大。
""")

# 学生访问链接提示
st.sidebar.markdown("---")
st.sidebar.subheader("📱 学生访问方式")
app_url = "https://你的应用名.streamlit.app"  # 请替换为实际部署后的链接
st.sidebar.info(
    f"**已部署在云端**\n\n教师复制下方链接，用在线二维码生成器（如 cli.im）制作二维码，插入课件即可。\n\n"
    f"👉 `{app_url}`"
)
st.sidebar.caption("部署成功后，浏览器地址栏的 URL 就是你的应用链接。")

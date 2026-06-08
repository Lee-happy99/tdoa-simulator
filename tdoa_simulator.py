# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 08:47:58 2026

@author: ASUS
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import qrcode
from PIL import Image
import io
import socket

# ------------------- 页面配置 -------------------
st.set_page_config(page_title="TDOA定位仿真器", layout="wide")
st.title("📡 TDOA时差定位交互仿真（AI赋能教学）")
st.markdown("**拖动左侧滑块改变三个侦察站的位置，观察双曲线交点如何锁定目标**")

# ------------------- 侧边栏：用户调节三个站坐标 -------------------
st.sidebar.header("📍 侦察站坐标（单位：km）")
x1 = st.sidebar.slider("站1 - x", -20.0, 20.0, -10.0, 0.5)
y1 = st.sidebar.slider("站1 - y", -20.0, 20.0, 0.0, 0.5)
x2 = st.sidebar.slider("站2 - x", -20.0, 20.0, 10.0, 0.5)
y2 = st.sidebar.slider("站2 - y", -20.0, 20.0, 0.0, 0.5)
x3 = st.sidebar.slider("站3 - x", -20.0, 20.0, 0.0, 0.5)
y3 = st.sidebar.slider("站3 - y", -20.0, 20.0, 15.0, 0.5)

# 真实目标位置（可设置固定值或也可用滑块）
target_x = st.sidebar.slider("🎯 真实目标 x", -20.0, 20.0, 5.0, 0.5)
target_y = st.sidebar.slider("🎯 真实目标 y", -20.0, 20.0, 5.0, 0.5)

# ------------------- 辅助函数 -------------------
def distance(p1, p2):
    return np.hypot(p1[0]-p2[0], p1[1]-p2[1])

def time_difference(p_target, p_station1, p_station2):
    """返回目标到站2与站1的距离差（c=1，单位km）"""
    return distance(p_target, p_station2) - distance(p_target, p_station1)

def hyperbola_equation(p, s1, s2, delta_d):
    """双曲线方程残差：abs( d(p,s2)-d(p,s1) - delta_d )"""
    return abs(distance(p, s2) - distance(p, s1) - delta_d)

def find_intersection(s1, s2, s3, delta_d12, delta_d13, bounds=(-20,20)):
    """数值求解两条双曲线的交点（用最小化方法）"""
    def objective(p):
        return hyperbola_equation(p, s1, s2, delta_d12) + hyperbola_equation(p, s1, s3, delta_d13)
    # 多起点优化
    best_x, best_val = None, np.inf
    for x0 in np.linspace(bounds[0], bounds[1], 10):
        for y0 in np.linspace(bounds[0], bounds[1], 10):
            res = minimize(objective, [x0, y0], bounds=[bounds, bounds], method='L-BFGS-B')
            if res.fun < best_val:
                best_val = res.fun
                best_x = res.x
    return best_x

# ------------------- 计算距离差 -------------------
s1 = np.array([x1, y1])
s2 = np.array([x2, y2])
s3 = np.array([x3, y3])
target = np.array([target_x, target_y])

delta_d12 = time_difference(target, s1, s2)
delta_d13 = time_difference(target, s1, s3)

# ------------------- 绘制双曲线和交点 -------------------
fig, ax = plt.subplots(figsize=(8, 6))

# 绘制侦察站
ax.scatter(*s1, c='red', s=100, label='站1', zorder=5)
ax.scatter(*s2, c='blue', s=100, label='站2', zorder=5)
ax.scatter(*s3, c='green', s=100, label='站3', zorder=5)
ax.scatter(target[0], target[1], c='black', marker='*', s=200, label='真实目标', zorder=5)

# 生成网格并绘制等值线（双曲线）
grid_x = np.linspace(-20, 20, 200)
grid_y = np.linspace(-20, 20, 200)
X, Y = np.meshgrid(grid_x, grid_y)
Z12 = np.abs(np.hypot(X - s2[0], Y - s2[1]) - np.hypot(X - s1[0], Y - s1[1]) - delta_d12)
Z13 = np.abs(np.hypot(X - s3[0], Y - s3[1]) - np.hypot(X - s1[0], Y - s1[1]) - delta_d13)

# 绘制两条双曲线（取残差最小的轮廓线）
contour12 = ax.contour(X, Y, Z12, levels=[0.05], colors='red', linewidths=2, linestyles='--')
contour13 = ax.contour(X, Y, Z13, levels=[0.05], colors='blue', linewidths=2, linestyles='--')

# 求解交点
est_pos = find_intersection(s1, s2, s3, delta_d12, delta_d13)
if est_pos is not None:
    ax.scatter(est_pos[0], est_pos[1], c='orange', marker='^', s=150, label='TDOA估计位置', zorder=6)
    error = np.hypot(est_pos[0]-target[0], est_pos[1]-target[1])
    st.sidebar.metric("定位误差 (km)", f"{error:.2f}")
else:
    st.sidebar.warning("交点求解失败，调整站址使三站不共线")

ax.set_xlim(-20, 20)
ax.set_ylim(-20, 20)
ax.set_xlabel("x (km)")
ax.set_ylabel("y (km)")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_title("TDOA双曲线定位演示\n红色虚线: 站1-站2 时差双曲线; 蓝色虚线: 站1-站3 时差双曲线")

st.pyplot(fig)

# 文字解释
st.info("💡 **观察要点**：\n"
        "- 两条双曲线通常有两个交点（对称），但结合战场先验信息（如目标所在半平面）可确定唯一解。\n"
        "- 当三个站共线或接近共线时，定位误差会急剧增大——这就是“几何精度稀释”现象。\n"
        "- 尝试把站2或站3拖到与站1、站2几乎一条直线上，观察误差如何变化。")

# ------------------- 二维码生成（自动获取本机局域网IP） -------------------
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

local_ip = get_local_ip()
port = 8501  # Streamlit默认端口
app_url = f"http://{local_ip}:{port}"

# 生成二维码
qr = qrcode.QRCode(box_size=4, border=2)
qr.add_data(app_url)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="black", back_color="white")

# 显示二维码
st.sidebar.markdown("---")
st.sidebar.subheader("📱 手机扫码访问")
st.sidebar.image(qr_img, caption=f"扫码即可进入仿真器", use_container_width=True)
st.sidebar.caption(f"或手动访问: {app_url}")
st.sidebar.info("**教学使用**：学生连接与电脑相同的Wi-Fi，扫码后即可在手机上拖动滑块，观察双曲线动态变化。")
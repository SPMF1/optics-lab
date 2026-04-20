import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# 1. 页面配置与样式
st.set_page_config(page_title="Fusion Optics Lab", layout="wide", page_icon="🔬")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 2. 核心物理工具函数

def wavelength_to_rgb(wavelength):
    """
    将波长(nm)转换为RGB归一化值 (0-1)
    复刻 HTML 版本的真彩色逻辑
    """
    gamma = 0.8
    intensity_max = 255.0
    
    if wavelength >= 380 and wavelength <= 440:
        r = -(wavelength - 440) / (440 - 380)
        g = 0.0
        b = 1.0
    elif wavelength < 490:
        r = 0.0
        g = (wavelength - 440) / (490 - 440)
        b = 1.0
    elif wavelength < 510:
        r = 0.0
        g = 1.0
        b = -(wavelength - 510) / (510 - 490)
    elif wavelength < 580:
        r = (wavelength - 510) / (580 - 510)
        g = 1.0
        b = 0.0
    elif wavelength < 645:
        r = 1.0
        g = -(wavelength - 645) / (645 - 580)
        b = 0.0
    elif wavelength <= 780:
        r = 1.0
        g = 0.0
        b = 0.0
    else:
        r = 0.0
        g = 0.0
        b = 0.0

    # 强度校正
    if wavelength >= 380 and wavelength < 420:
        factor = 0.3 + 0.7 * (wavelength - 380) / (420 - 380)
    elif wavelength >= 420 and wavelength <= 700:
        factor = 1.0
    elif wavelength > 700 and wavelength <= 780:
        factor = 0.3 + 0.7 * (780 - wavelength) / (780 - 700)
    else:
        factor = 0.0

    r = int(np.clip((r * factor) ** gamma * intensity_max, 0, 255))
    g = int(np.clip((g * factor) ** gamma * intensity_max, 0, 255))
    b = int(np.clip((b * factor) ** gamma * intensity_max, 0, 255))
    
    return (r/255, g/255, b/255)

def create_grid(size_px, screen_range):
    """
    创建 2D 坐标网格 (复刻 HTML 中的 numeric.linspace 逻辑)
    """
    x = np.linspace(-screen_range, screen_range, size_px)
    y = np.linspace(-screen_range, screen_range, size_px)
    # 创建网格矩阵
    # 注意：这里我们手动构建类似 MATLAB/HTML 的 meshgrid 效果
    # XX 是水平坐标，YY 是垂直坐标
    XX, YY = np.meshgrid(x, y)
    R = np.sqrt(XX**2 + YY**2)
    return XX, YY, R

# 3. 物理实验模拟类

class FusionLab:
    def __init__(self):
        self.wavelength = 632.8 # nm (默认红光)
        self.grid_size = 300    # 分辨率
        self.screen_range = 0.01 # 屏幕范围 (m)

    def youngs_double_slit(self, d_slit, L_screen, photon_count):
        """杨氏双缝模拟"""
        XX, YY, R = create_grid(self.grid_size, self.screen_range)
        
        # 物理公式：I = cos^2(pi * d * x / (lambda * L))
        # 这里的 x 对应 XX
        phase = (np.pi * d_slit * XX) / (self.wavelength * 1e-9 * L_screen)
        intensity = np.cos(phase)**2
        
        return intensity, "Young's Interference (Fringes)"

    def michelson(self, path_diff, tilt_angle):
        """迈克尔逊模拟 (复刻 HTML 逻辑)"""
        XX, YY, R = create_grid(self.grid_size, self.screen_range)
        
        # 物理公式复刻：
        # OPD = 2d + 2*x*theta + (r^2)/|d| (近似项用于模拟圆环曲率)
        # 注意单位统一：path_diff 是 m, tilt_angle 是 rad
        
        opd = 2 * path_diff + 2 * XX * tilt_angle
        
        # 模拟圆环的曲率项 (当 d 不为 0 时)
        if abs(path_diff) > 1e-9:
             opd += (R**2) / (2 * abs(path_diff)) # 简化的菲涅尔近似项
        
        phase = (2 * np.pi / (self.wavelength * 1e-9)) * opd
        intensity = np.cos(phase / 2)**2
        
        return intensity, "Michelson Interference (Rings/Linear)"

# 4. 网页界面构建

st.title("🔬 Fusion Optics Lab: Wave-Particle Duality")
st.markdown("Combining **Python Power** with **HTML-style Physics Logic**.")

# 侧边栏：全局设置
st.sidebar.header("⚙️ Global Settings")
lab = FusionLab()
lab.wavelength = st.sidebar.slider("Wavelength (nm)", 400, 780, 632)
exp_type = st.sidebar.radio("Select Experiment", ("Young's Double Slit", "Michelson Interferometer"))

# 侧边栏：实验参数
st.sidebar.header("Parameters")
if exp_type == "Young's Double Slit":
    d_slit = st.sidebar.slider("Slit Separation d (mm)", 0.1, 2.0, 0.5) * 1e-3
    L_screen = st.sidebar.slider("Screen Distance L (m)", 0.5, 2.0, 1.0)
else:
    path_diff = st.sidebar.slider("Path Difference d (um)", -10.0, 10.0, 0.0) * 1e-6
    tilt_angle = st.sidebar.slider("Mirror Tilt (mrad)", -2.0, 2.0, 0.0) * 1e-3

# 模拟控制
sim_running = st.sidebar.button("🚀 Run Particle Simulation")
st.sidebar.markdown("---")
st.sidebar.caption("Note: This simulation uses true-color rendering based on wavelength.")

# 主界面布局
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Real-time Accumulation")
    plot_placeholder = st.empty()
    status_text = st.empty()

with col2:
    st.subheader("Theoretical Pattern (True Color)")
    # 最终的高清光栅图
    final_placeholder = st.empty()

# 5. 模拟逻辑

if sim_running:
    # 1. 计算理论图样
    if exp_type == "Young's Double Slit":
        intensity, title = lab.youngs_double_slit(d_slit, L_screen, 0)
    else:
        intensity, title = lab.michelson(path_diff, tilt_angle)
    
    # 2. 生成真彩色图像数据
    # 获取对应波长的 RGB 颜色
    rgb_color = wavelength_to_rgb(lab.wavelength)
    
    # 创建 RGB 图像数组 (H, W, 3)
    # 将强度应用到颜色上
    img_h, img_w = intensity.shape
    rgb_img = np.zeros((img_h, img_w, 3))
    for i in range(3):
        rgb_img[:, :, i] = intensity * rgb_color[i]
    
    # 显示最终理论图 (右侧)
    final_placeholder.image(rgb_img, caption=f"Theoretical {title}", clamp=True, use_column_width=True)

    # 3. 粒子累积动画 (左侧)
    # 将 2D 强度展平作为概率分布
    prob_flat = intensity.ravel()
    prob_flat = prob_flat / prob_flat.sum()
    
    total_photons = 5000
    batch_size = 200
    current_hits = []
    
    progress_bar = st.progress(0)
    
    for i in range(total_photons // batch_size):
        # 随机采样
        indices = np.random.choice(len(prob_flat), size=batch_size, p=prob_flat)
        current_hits.extend(indices)
        
        # 绘图更新
        fig, ax = plt.subplots(figsize=(5, 5))
        
        # 还原坐标
        hits_y, hits_x = np.unravel_index(current_hits, intensity.shape)
        
        # 绘制散点 (模拟粒子打在屏幕上的效果)
        # 为了美观，限制显示的点数，防止过密
        display_limit = 2000
        if len(hits_x) > display_limit:
            # 随机抽取显示
            show_idx = np.random.choice(len(hits_x), display_limit, replace=False)
            ax.scatter(hits_x[show_idx], hits_y[show_idx], s=1, c=[rgb_color], alpha=0.5)
        else:
            ax.scatter(hits_x, hits_y, s=1, c=[rgb_color], alpha=0.5)
            
        ax.set_title(f"Accumulation: {len(current_hits)} Photons")
        ax.set_xlim(0, img_w)
        ax.set_ylim(0, img_h)
        ax.axis('off')
        
        plot_placeholder.pyplot(fig)
        plt.close(fig)
        
        time.sleep(0.02) # 控制速度
        
    progress_bar.progress(1.0)
    status_text.text("Simulation Complete!")

else:
    st.info("Adjust parameters in the sidebar and click 'Run Particle Simulation' to see the effect.")

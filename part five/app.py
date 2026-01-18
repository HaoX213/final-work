import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import CubicSpline
from streamlit_drawable_canvas import st_canvas
import time

# 尝试导入 OpenAI，如果未安装则由 fallback 处理
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# ==========================================
# 0. 全局配置 & 视觉风格 (CSS)
# ==========================================
st.set_page_config(
    page_title="傅里叶变换艺术馆 (AI版)",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 强制 Dark Mode & 霓虹配色 CSS
st.markdown("""
<style>
    /* 全局背景设为深色 */
    .stApp {
        background-color: #0E1117;
    }
    
    /* 强制所有文字颜色 - 亮灰白 */
    h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown, .stRadio label, .stExpander, li {
        color: #E0E0E0 !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 标题高亮 - 赛博朋克青色 */
    h1, h2, h3 {
        color: #00F0FF !important; 
        text-shadow: 0 0 8px rgba(0, 240, 255, 0.5);
    }
    
    /* AI 分析框样式 */
    .stAlert {
        border: 1px solid #00F0FF;
        background-color: rgba(0, 240, 255, 0.05);
        color: #E0E0E0;
    }
    
    /* 侧边栏 */
    [data-testid="stSidebar"] {
        background-color: #11141d;
        border-right: 1px solid #333;
    }
    
    /* Components Style Tweaks */
    iframe { border-radius: 8px; border: 2px solid #333; }
    .stButton button { border: 1px solid #00F0FF; color: #00F0FF; background: transparent; transition: all 0.3s; }
    .stButton button:hover { background-color: #00F0FF; color: #0E1117; }
    
    /* Canvas Background Force White - Targeting Iframe */
    iframe[title="streamlit_drawable_canvas.st_canvas"] {
        background-color: #FFFFFF !important;
    }
    /* 增强选择器 */
    div[data-testid="stIFrame"] iframe {
        background-color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

COLORS = {
    'cyan': '#00FFFF', 'yellow': '#FFFF00', 'red': '#FF4B4B', 
    'grid': '#333333', 'gray': '#888888', 'neon_green': '#00FFCC'
}
NEON_PALETTE = ['#FF00FF', '#FFFF00', '#00FF00', '#FF6600', '#00FFFF']

# ==========================================
# 1. AI 助教核心模块 (Fourier Assistant)
# ==========================================

def get_api_key():
    """安全地获取 API Key"""
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return None
    return None

def get_ai_response(prompt, system_role="You are a helpful physics teaching assistant. Reply in Chinese."):
    """调用 AI API 或返回 Fallback"""
    api_key = get_api_key()
    
    # 1. 检查可用性
    if not api_key:
        return None # 触发离线逻辑
    if not OPENAI_AVAILABLE:
        return None
        
    # 2. 调用 API
    try:
        # 获取配置，支持自定义代理和模型
        base_url = st.secrets.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model_name = st.secrets.get("OPENAI_MODEL", "gpt-3.5-turbo")
        
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        content = response.choices[0].message.content
        return f"傅里叶小助手: {content}"
    except Exception as e:
        print(f"❌ AI API Error: {str(e)}")
        return None

def render_ai_chat_area():
    """侧边栏全局问答区"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    # 放在侧边栏底部
    with st.sidebar.expander("🤖 傅里叶小助手：问我问题", expanded=False):
        # 显示历史
        for msg in st.session_state.chat_history[-6:]:
             role_label = "我" if msg['role'] == "user" else "AI"
             # 简单样式
             st.markdown(f"**{role_label}**: {msg['content']}")
             st.markdown("---")
             
        user_query = st.chat_input("输入关于信号的问题...", key="sidebar_chat_input")
        
        if user_query:
            # 1. User Message
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            # 2. AI Response
            context_prompt = f"请简短地用中文回答关于傅里叶变换或信号处理的问题: {user_query}。字数控制在100字以内。"
            ai_reply = get_ai_response(context_prompt)
            
            # Fallback
            if ai_reply is None:
                ai_reply = "傅里叶小助手: [系统离线] 抱歉，无法连接到大脑。可能是 Key 未配置或网络问题。"
            
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
            st.rerun()

# --- 预设文本库 (Fallbacks) ---
FALLBACK_EXPLANATIONS = {
    "方波": "傅里叶小助手: 你选择了**方波**。方波包含丰富的奇次谐波（1f, 3f, 5f...），且高频分量衰减缓慢。这导致了边缘的激烈跳变。请注意观察合成时的**吉布斯现象**——那些在跳变边缘倔强突起的“小耳朵”！",
    "三角波": "傅里叶小助手: 这是**三角波**。它看起来比方波柔和，因为它虽然也有奇次谐波，但高频分量能量衰减极快（按 1/n² 衰减）。只需很少的正弦波就能合成出非常平滑的三角形。",
    "锯齿波": "傅里叶小助手: **锯齿波**包含了所有整数倍的谐波（既有奇次也有偶次）。它的声音听起来非常明亮甚至刺耳，是减法合成器中常用的基础波形。",
    "正弦波": "傅里叶小助手: 完美的**正弦波**！它是傅里叶世界的“原子”。在频域瀑布图中，你应该只能看到的一根孤独而挺拔的柱子（基波），没有任何杂音。",
    "自定义": "傅里叶小助手: 这是你独创的波形！试着调节 N 值，看看需要多少个正弦波才能模仿出你画的这般模样。",
    "High_Complexity": "傅里叶小助手: 哇，这个图形好复杂！它包含很多转折和细节，这意味着我们需要大量的“频率圆”来重构它。试着把 N 拉到最大，看看细节是如何被填补的。",
    "Low_Complexity": "傅里叶小助手: 这个图形这非常圆润简洁。根据奥卡姆剃刀原理，大概只需要前几个低频分量（大圆）就足以概括它的灵魂了。"
}

# ==========================================
# 2. 核心数学模块
# ==========================================

# --- 1D Logic ---
def get_1d_fft_data(y_dense, top_n=10):
    N = len(y_dense)
    yf = np.fft.rfft(y_dense)
    xf = np.fft.rfftfreq(N, d=1.0/N)
    
    amplitudes = np.abs(yf) * 2.0 / N
    amplitudes[0] /= 2.0 # DC fix
    phases = np.angle(yf)
    
    comps = []
    for i in range(len(xf)):
        comps.append({'freq': xf[i], 'amp': amplitudes[i], 'phase': phases[i], 'complex': yf[i]})
    
    ac_comps = comps[1:] 
    ac_comps.sort(key=lambda x: x['amp'], reverse=True)
    return ac_comps[:top_n], comps[0]

# --- 2D Logic ---
def compute_2d_fft(coords):
    # 1. 坐标居中 (Centering)
    center = np.mean(coords, axis=0) # (cx, cy)
    centered = coords - center
    z = centered[:, 0] + 1j * centered[:, 1]
    
    # 2. FFT 计算
    N = len(z)
    fft_vals = np.fft.fft(z)
    coeffs = fft_vals / N
    
    components = []
    freqs_k = np.fft.fftfreq(N) * N # Get integer frequencies
    
    for i in range(N):
        k = int(round(freqs_k[i]))
        c = coeffs[i]
        components.append({'freq': k, 'complex': c, 'amp': np.abs(c), 'phase': np.angle(c)})
        
    # 3. 频率排序 (Frequency Sorting)
    # 按能量集中度排序：0, -1, 1, -2, 2 ...
    components.sort(key=lambda x: (abs(x['freq']), x['freq']))
    
    return components, center

def get_epicycle_geometry(components, t, center):
    # Start chain at center
    current_pos = center[0] + 1j*center[1]
    
    # Vectors with gaps (None insertion)
    vectors_x = []
    vectors_y = []
    
    # Circles with gaps (None insertion)
    circles_x = []
    circles_y = []
    
    # Circle shape template
    theta = np.linspace(0, 2*np.pi, 30)
    theta = np.append(theta, 0) # Close circle
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    
    for comp in components:
        radius = comp['amp']
        freq = comp['freq']
        phase = comp['phase']
        
        # Calculate next position
        angle = 2 * np.pi * freq * t + phase
        vector = radius * np.exp(1j * angle)
        next_pos = current_pos + vector
        
        # 1. Vector Segment: Start -> End -> None
        vectors_x.extend([current_pos.real, next_pos.real, None])
        vectors_y.extend([current_pos.imag, next_pos.imag, None])
        
        # 2. Circle Path: Points -> None
        # Limit small circles for performance/visual clarity
        if radius > 0.5: 
            cx = current_pos.real + radius * cos_t
            cy = current_pos.imag + radius * sin_t
            circles_x.extend(cx)
            circles_x.append(None)
            circles_y.extend(cy)
            circles_y.append(None)
        
        # Move forward
        current_pos = next_pos
            
    final_tip = current_pos
    
    return vectors_x, vectors_y, circles_x, circles_y, final_tip

# ==========================================
# 3. 页面一：一维信号实验室
# ==========================================
def render_page_1d():
    st.title("🔬 一维信号实验室 (1D Signal Lab)")
    st.markdown("通过交互体验，理解**时域与频域**的对偶关系。")

    # --- Session State ---
    if "ai_analysis_1d" not in st.session_state:
        st.session_state.ai_analysis_1d = FALLBACK_EXPLANATIONS["自定义"]
    
    def update_analysis_preset():
        preset = st.session_state.preset_1d
        if preset in FALLBACK_EXPLANATIONS:
            # 预设波形直接用静态文本（或者也可以调用 AI）
            # 为了省钱和速度，这里预设波形使用静态文本，但加上AI前缀模拟分析
            # 如果想让 AI 每次都分析，可以这里调用 get_ai_response
             st.session_state.ai_analysis_1d = FALLBACK_EXPLANATIONS[preset]

    # --- Sidebar ---
    st.sidebar.subheader("🎛️ 信号发生器")
    
    preset_options = ["自定义", "方波", "正弦波", "三角波", "锯齿波"]
    if 'preset_1d' not in st.session_state:
        st.session_state.preset_1d = "自定义"

    def on_preset_change():
        preset = st.session_state.preset_1d
        if preset == "方波":
             st.session_state.sliders_1d = [1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0]
        elif preset == "正弦波":
             st.session_state.sliders_1d = [0.0, 0.7, 1.0, 0.7, 0.0, -0.7, -1.0, -0.7]
        elif preset == "三角波":
             st.session_state.sliders_1d = [0.0, 0.5, 1.0, 0.5, 0.0, -0.5, -1.0, -0.5]
        elif preset == "锯齿波":
             st.session_state.sliders_1d = np.linspace(1.0, -1.0, 8).tolist()
        
        update_analysis_preset()
    
    st.sidebar.selectbox("选择预设波形", preset_options, key="preset_1d", on_change=on_preset_change)
    
    if 'sliders_1d' not in st.session_state:
        st.session_state.sliders_1d = [0.0, 0.7, 1.0, 0.7, 0.0, -0.7, -1.0, -0.7]

    cols = st.sidebar.columns(2)
    new_sliders = []
    for i in range(8):
        with cols[i%2]:
            val = st.slider(f"P{i}", -2.0, 2.0, value=float(st.session_state.sliders_1d[i]), key=f"s_{i}")
            new_sliders.append(val)
    st.session_state.sliders_1d = new_sliders 
    
    # --- Processing ---
    # Interpolation
    x_nodes = np.linspace(0, 1, 9, endpoint=True)
    y_nodes = np.array(new_sliders + [new_sliders[0]])
    cs = CubicSpline(x_nodes, y_nodes, bc_type='periodic')
    x_dense = np.linspace(0, 1, 400)
    y_dense = cs(x_dense)
    
    # FFT
    top_comps, dc_comp = get_1d_fft_data(y_dense, top_n=8)

    # --- Part 1: Time Domain ---
    col_main, col_info = st.columns([2, 1])
    
    with col_main:
        st.subheader("1. 时域波形 (Time Domain)")
        fig_time = go.Figure()
        fig_time.add_trace(go.Scatter(x=x_dense, y=y_dense, line=dict(color=COLORS['cyan'], width=3), name='Signal'))
        fig_time.update_layout(height=300, template="plotly_dark", margin=dict(l=0,r=0,t=20,b=20))
        st.plotly_chart(fig_time, use_container_width=True)
        
        # AI Analyze Button
        if st.button("🧠 AI 分析当前波形"):
            with st.spinner("AI 正在观察你的波形..."):
                # 简单描述波形特征给 AI
                mean_val = np.mean(np.abs(y_dense))
                peak_val = np.max(np.abs(y_dense))
                prompt = f"用户设计了一个自定义 1D 波形。平均振幅 {mean_val:.2f}，峰值 {peak_val:.2f}。请分析其可能的听感和物理特性，并给出 50 字左右的点评。"
                resp = get_ai_response(prompt)
                if resp:
                    st.session_state.ai_analysis_1d = resp
                else: 
                     st.session_state.ai_analysis_1d = FALLBACK_EXPLANATIONS["自定义"]
        
        st.info(st.session_state.ai_analysis_1d)

    # --- Part 2: Synthesis ---
    st.divider()
    st.subheader("2. 频域合成 (Synthesis)")
    
    col_syn_ctrl, col_syn_plot = st.columns([1, 2])
    with col_syn_ctrl:
        st.markdown("调整 **N** (合成频率数)，观察如何用简单的正弦波逼近复杂波形。")
        n_syn = st.slider("N 值", 0, 8, 3)
        st.caption("当 N 较小时，我们只能看到波形的'轮廓'。当 N 增大，细节逐渐显现。")
        st.markdown(f"> **吉布斯现象**: 注意当 N={n_syn} 时，在尖锐边缘处的'过冲'现象。")

    with col_syn_plot:
        y_recon = np.ones_like(x_dense) * dc_comp['amp']
        for i in range(n_syn):
            c = top_comps[i]
            y_recon += c['amp'] * np.cos(c['freq'] * x_dense * 2 * np.pi + c['phase'])
            
        fig_syn = go.Figure()
        fig_syn.add_trace(go.Scatter(x=x_dense, y=y_dense, line=dict(color='gray', dash='dash'), name='Original'))
        fig_syn.add_trace(go.Scatter(x=x_dense, y=y_recon, line=dict(color=COLORS['red'], width=3), name='Synthesis'))
        # Error fill
        fig_syn.add_trace(go.Scatter(x=x_dense, y=y_recon, line=dict(width=0), hoverinfo="skip", showlegend=False))
        fig_syn.add_trace(go.Scatter(x=x_dense, y=y_dense, fill='tonexty', fillcolor='rgba(255, 75, 75, 0.2)', line=dict(width=0), name='Error'))
        
        fig_syn.update_layout(height=350, template="plotly_dark", margin=dict(l=0,r=0,t=20,b=20))
        st.plotly_chart(fig_syn, use_container_width=True)

    # --- Part 3: Waterfall ---
    st.divider()
    st.subheader("3. 频率瀑布流 (Frequency Waterfall)")
    st.markdown("这展示了不同频率的正弦波是如何像积木一样排列的。后排是低频（轮廓），前排是高频（细节）。")
    
    fig_3d = go.Figure()
    # Original at back
    fig_3d.add_trace(go.Scatter3d(x=x_dense, y=np.zeros_like(x_dense), z=y_dense, mode='lines', line=dict(color=COLORS['cyan'], width=5), name="Original"))
    
    for i, c in enumerate(top_comps[:5]):
        cy = c['amp'] * np.cos(c['freq']*x_dense*2*np.pi + c['phase'])
        # y position represents frequency rank
        fig_3d.add_trace(go.Scatter3d(x=x_dense, y=np.full_like(x_dense, i+1), z=cy, mode='lines', line=dict(color=NEON_PALETTE[i%5], width=3), name=f"Freq {c['freq']:.0f}"))
        
    fig_3d.update_layout(
        height=500, template="plotly_dark", 
        scene=dict(
            xaxis_title="Time", 
            yaxis_title="Freq Rank", 
            zaxis_title="Amplitude", 
            camera=dict(eye=dict(x=1.6, y=1.6, z=0.6))
        ),
        margin=dict(l=0,r=0,t=0,b=0)
    )
    st.plotly_chart(fig_3d, use_container_width=True)

# ==========================================
# 4. 页面二：二维绘图艺术馆
# ==========================================
def render_page_2d():
    st.title("🎨 二维绘图艺术馆 (2D Fourier Art)")
    st.markdown("用**复数傅里叶变换 (FFT)** 重构你的灵魂画作。")

    col_draw, col_ctrl = st.columns([1, 1.5])
    
    with col_draw:
        st.caption("请在下方绘制任意闭合图形（如五角星、花朵、签名）：")
        # Can注入 CSS 确保白色背景
        canvas = st_canvas(
            fill_color="rgba(0,0,0,0)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=300, width=300,
            drawing_mode="freedraw",
            key="c2d_new"
        )
        
    # Data Processing
    coords = None
    coords_len = 0
    # Original Path (Visual with breaks)
    orig_x_visual = []
    orig_y_visual = []
    
    if canvas.json_data and len(canvas.json_data["objects"]) > 0:
        all_pts = [] # For FFT (Continuous)
        
        for obj in canvas.json_data["objects"]:
            if "path" in obj:
                stroke_pts = []
                for cmd in obj["path"]:
                     # Parse path commands: 'M', 'L', 'Q', 'C' etc.
                     # We take the last coordinate pair as the point on curve
                    if len(cmd) >= 3: 
                        pt = [cmd[-2], cmd[-1]]
                        stroke_pts.append(pt)
                        all_pts.append(pt)
                
                # Append to visual arrays with NaN break for Plotly
                if stroke_pts:
                    pts_arr = np.array(stroke_pts)
                    # Flip Y for visualization immediately to match coordinate system
                    xs = pts_arr[:, 0]
                    ys = 300 - pts_arr[:, 1]
                    
                    orig_x_visual.extend(xs.tolist())
                    orig_x_visual.append(None) # Break line
                    orig_y_visual.extend(ys.tolist())
                    orig_y_visual.append(None) # Break line
        
        if len(all_pts) > 3:
            coords = np.array(all_pts)
            coords[:, 1] = 300 - coords[:, 1] # Flip Y for math
            
            # --- 注意：这里不再进行人工闭合，完全交给 FFT 处理 ---
            coords_len = len(coords)

    # Update AI if drawing changed
    if "last_coords_len" not in st.session_state:
        st.session_state.last_coords_len = 0
    
    ai_triggered = False
    if coords_len != st.session_state.last_coords_len and coords_len > 10:
        st.session_state.last_coords_len = coords_len
        ai_triggered = True

    with col_ctrl:
        st.subheader("参数控制 & AI 洞察")
        
        if coords is not None:
            # AI Insight
            if ai_triggered:
                with st.spinner("AI 正在鉴赏你的画作..."):
                    if coords_len > 50:
                        p = f"用户画了一个包含{coords_len}个点的复杂图形。请赞叹其复杂度并建议如何使用FFT重构。"
                        fb = FALLBACK_EXPLANATIONS["High_Complexity"]
                    else:
                        p = f"用户画了一个仅有{coords_len}个点的简单图形。请评价其简洁美。"
                        fb = FALLBACK_EXPLANATIONS["Low_Complexity"]
                    
                    resp = get_ai_response(p)
                    st.session_state.ai_analysis_2d = resp if resp else fb
            
            if "ai_analysis_2d" in st.session_state:
                st.success(st.session_state.ai_analysis_2d)

            components, center = compute_2d_fft(coords)
            max_n = len(components)
            
            n_val = st.slider("圆/频率数量 (N)", 1, max_n, min(30, max_n))
            st.caption(f"使用前 {n_val} 个频率分量进行重构。增加 N 可还原更多细节。")
            
            if st.button("▶ 播放动画 (Play Animation)", type="primary"):
                st.session_state.run_animation_2d = True
        else:
            st.info("👈 请先在左侧画点东西...")
            return

    # Animation Area
    st.divider()
    if coords is not None and st.session_state.get('run_animation_2d'):
        sel_comps = components[:n_val]
        
        # Frames setting
        n_frames = 120 
        # 修改关键点：让时间稍微小于 1.0 (例如 0.99)，
        # 避免 t=1.0 时傅里叶级数严格回到起点 (周期性)，从而在视觉上产生闭合
        times = np.linspace(0, 0.995, n_frames)
        
        # Init Figure with Dark Background
        fig = go.Figure()

        # --- Pre-calculate State At t=0 for Initialization ---
        # 这一步至关重要：如果初始 Trace 数据为空，Plotly 动画可能无法正确渲染后续帧的线条和形状。
        # 我们先计算出第一帧的数据，填入初始 Figure 中，确保“所见即所得”。
        init_vx, init_vy, init_cx, init_cy, init_tip = get_epicycle_geometry(sel_comps, times[0], center)
        
        # 1. Original Path (Trace 0)
        fig.add_trace(go.Scatter(
            x=orig_x_visual, y=orig_y_visual, 
            mode='lines', 
            line=dict(color='grey', dash='dot', width=1), 
            connectgaps=False, # Important
            name='原始路径',
            hoverinfo='skip'
        ))
        
        # 2. Drawn Path (Trace 1)
        # 初始化为起点，而不是空列表
        fig.add_trace(go.Scatter(
            x=[init_tip.real], y=[init_tip.imag], 
            mode='lines', 
            line=dict(color='#00FFFF', width=4), 
            name='重构路径'
        ))
        
        # 3. Vectors (Trace 2)
        # 初始化为 t=0 时的矢量链
        fig.add_trace(go.Scatter(
            x=init_vx, y=init_vy, 
            mode='lines+markers', 
            line=dict(color='#FFFF00', width=2), 
            marker=dict(size=4, color='white'),
            connectgaps=False, # CRITICAL for Vectors
            name='矢量链'
        ))
        
        # 4. Circles (Trace 3)
        # 初始化为 t=0 时的圆
        fig.add_trace(go.Scatter(
            x=init_cx, y=init_cy, 
            mode='lines', 
            opacity=0.3, 
            line=dict(color='grey', width=1), 
            connectgaps=False, # CRITICAL for Circles
            name='矢量圆',
            hoverinfo='skip'
        ))
        
        # 5. Pen Tip (Trace 4)
        # 初始化为 t=0 时的笔尖
        fig.add_trace(go.Scatter(
            x=[init_tip.real], y=[init_tip.imag],
            mode='markers',
            marker=dict(color='red', size=5),
            name='笔尖'
        ))

        # Generate Frames
        frames = []
        drawn_path_x = []
        drawn_path_y = []
        
        step_progress_bar = st.progress(0)
        
        for k, t in enumerate(times):
            # Calculate geometry
            vx, vy, cx, cy, tip = get_epicycle_geometry(sel_comps, t, center)
            
            drawn_path_x.append(tip.real)
            drawn_path_y.append(tip.imag)
            
            frames.append(go.Frame(data=[
                go.Scatter(x=orig_x_visual, y=orig_y_visual), # Trace 0
                go.Scatter(x=drawn_path_x, y=drawn_path_y), # Trace 1
                go.Scatter(x=vx, y=vy), # Trace 2
                go.Scatter(x=cx, y=cy), # Trace 3
                go.Scatter(x=[tip.real], y=[tip.imag]) # Trace 4
            ], name=f"f{k}"))
            
            if k % 10 == 0: step_progress_bar.progress((k + 1) / n_frames)

        step_progress_bar.empty()
        
        fig.update(frames=frames)
        
        # Layout Setting
        if len(orig_x_visual) > 0:
            valid_x = [x for x in orig_x_visual if x is not None]
            valid_y = [y for y in orig_y_visual if y is not None]
            min_x, max_x = np.min(valid_x), np.max(valid_x)
            min_y, max_y = np.min(valid_y), np.max(valid_y)
            span = max(max_x - min_x, max_y - min_y) * 1.3
            mid_x, mid_y = (min_x + max_x)/2, (min_y + max_y)/2
        else:
             mid_x, mid_y = 150, 150
             span = 300
        
        fig.update_layout(
            template="plotly_dark",
            height=700,
            paper_bgcolor='#0E1117',
            xaxis=dict(range=[mid_x - span/2, mid_x + span/2], visible=False, scaleanchor='y'),
            yaxis=dict(range=[mid_y - span/2, mid_y + span/2], visible=False, scaleratio=1),
            updatemenus=[dict(
                type="buttons", 
                buttons=[dict(label="▶ 播放", method="animate", args=[None, dict(frame=dict(duration=20, redraw=True), fromcurrent=True, mode="immediate")])],
                x=0.5, y=0.05, xanchor="center",
                bgcolor="#333", bordercolor="#00F0FF", font=dict(color="#00F0FF")
            )],
            margin=dict(l=0,r=0,t=0,b=0),
            showlegend=True,
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0.5)')
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 5. 主程序
# ==========================================
def main():
    st.sidebar.title("🌌 导航")
    page = st.sidebar.radio("选择实验室", ["一维信号实验室", "二维绘图艺术馆"])
    
    # 渲染页面
    if page == "一维信号实验室":
        render_page_1d()
    else:
        render_page_2d()
        
    # 全局组件
    render_ai_chat_area()

if __name__ == "__main__":
    main()

# 🌌 傅里叶变换艺术馆 (AI版) | Fourier Transform Art Museum

这是一个基于 Streamlit 构建的交互式教学应用，旨在通过可视化的方式帮助用户直观理解傅里叶变换（Fourier Transform）。项目融合了赛博朋克风格的 UI 设计与 AI 智能助手，通过一维信号合成与二维绘图重构两个实验室，生动展示了时域与频域的奥秘。

![UI Preview](https://img.shields.io/badge/Style-Cyberpunk-00F0FF) ![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## ✨ 主要功能

### 1. 🔬 一维信号实验室 (1D Signal Lab)
探索一维波形的合成与分解：
*   **多波形预设**：支持方波、三角波、锯齿波、正弦波及自定义手绘波形。
*   **交互式合成**：拖动滑块调整波形参数，实时观察合成效果。
*   **吉布斯现象可视化**：通过调整合成频率数量 ($N$)，直观感受傅里叶级数逼近过程中的过冲现象。
*   **3D 频率瀑布流**：在三维空间中展示不同频率分量（正弦波）如何叠加构成总波形。
*   **AI 波形分析**：智能分析当前波形的物理特性与听感特征。

### 2. 🎨 二维绘图艺术馆 (2D Fourier Art)
用数学重构你的灵魂画作：
*   **自由绘图板**：在白色画布上绘制任意闭合图形（如花朵、签名、五角星）。
*   **复数 FFT 重构**：应用二维（复数）傅里叶变换算法，计算图形的频率系数。
*   **Epicycle 动画**：展示矢量圆（本轮）如何首尾相连，通过旋转绘制出原始路径。
    *   *修复特性*：优化了开放路径的显示，消除了首尾强制相连的视觉瑕疵。
    *   *性能优化*：支持调整圆的数量 ($N$)，平衡细节还原度与计算性能。
*   **AI 艺术鉴赏**：AI 根据画作的复杂度提供趣味点评。

### 3. 🤖 AI 智能助教
*   内置 OpenAI 接口（需配置 Key），提供实时的信号处理知识问答。
*   辅助分析波形特征与绘图复杂度。

## 🛠️ 技术栈

*   **Python 3.8+**
*   **Streamlit**: Web 应用框架
*   **NumPy & SciPy**: 科学计算与插值算法
*   **Plotly**: 高性能交互式图表与动画
*   **Streamlit Drawable Canvas**: 前端绘图组件
*   **OpenAI API**: 智能化支持

## 🚀 快速开始

### 1. 环境准备
确保已安装 Python 环境，推荐使用虚拟环境。

```bash
# 克隆仓库或下载代码
git clone [repository-url]
cd [project-folder]

# 安装依赖
pip install -r requirements.txt
```

`requirements.txt` 参考内容：
```txt
streamlit
numpy
scipy
plotly
streamlit-drawable-canvas
openai
```

### 2. 配置 AI (可选)
如果需要使用 AI 功能，请在项目根目录创建 `.streamlit/secrets.toml` 文件，并添加 API Key：

```toml
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
OPENAI_BASE_URL = "https://api.openai.com/v1" # 可选，用于自定义代理
OPENAI_MODEL = "gpt-3.5-turbo" # 可选
```

### 3. 运行应用
在终端中执行：

```bash
streamlit run app.py
```

浏览器将自动打开 `http://localhost:8501`。

## 📝 注意事项

*   **画布背景**：二维绘图部分采用了强制 CSS 注入，确保画布在深色模式下背景为纯白，线条为纯黑，以便清晰观察。
*   **动画性能**：在二维重构中，如果图形非常复杂，建议适当降低 $N$ 值以保证动画流畅度。
*   **离线模式**：未配置 OpenAI Key 时，应用将使用内置的 Fallback 文本库，核心绘图与数学演示功能不受影响。

---
*Created with ❤️ by Xu from JNU

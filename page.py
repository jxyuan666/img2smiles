import os
import sys

# ==========================================
# 🚀 魔法1：本地断网部署（欺骗环境变量）
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.environ['HOME'] = PROJECT_ROOT
os.environ['USERPROFILE'] = PROJECT_ROOT

# 做完伪装后，再导入 DECIMER
from DECIMER import predict_SMILES
import streamlit as st
from PIL import Image
from rdkit import Chem
from rdkit.Chem import Draw

# ==========================================
# 🚀 魔法2：性能提速（将模型加载锁死在内存中）
# ==========================================
@st.cache_resource(show_spinner=False)
def load_and_predict(image_path):
    # 第一次运行会稍慢，之后秒开
    return predict_SMILES(image_path)

# ==========================================
# 1. 页面全局配置与 CSS 样式注入
# ==========================================
st.set_page_config(page_title="DECIMER Pro 识别平台", layout="wide", page_icon="🔬")

custom_css = """
<style>
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
    .css-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
        height: 100%;
    }
    .upload-zone { border: 2px dashed #4C51BF; background-color: #F7FAFC; }
    .render-zone { border: 2px solid #38B2AC; background-color: #E6FFFA; text-align: center;}
    .zone-title { font-size: 1.2rem; font-weight: bold; color: #2D3748; margin-bottom: 15px; border-bottom: 2px solid #EDF2F7; padding-bottom: 5px;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 2. 页面标题区
# ==========================================
st.markdown(
    """
    <div style="text-align: center; padding-bottom: 10px;">
        <h1 style="color: #FFC8C4; margin-bottom: 5px;"> DECIMER Pro: 分子图像识别与校验系统</h1>
        <p style="color: #4A5568; font-size: 1.1rem; margin-top: 0;">通过深度学习提取化学结构，并实时进行二维结构校验。</p>
    </div>
    """, 
    unsafe_allow_html=True
)
st.write("---")

# ==========================================
# 3. 核心布局排版
# ==========================================
col_left, col_spacing, col_right = st.columns([4, 0.5, 5])

# ------------- 【左侧：图像输入区】 -------------
with col_left:
    st.markdown('<div class="css-card upload-zone"><div class="zone-title"> 1. 图像输入区</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("拖拽、选择图片，或点击此处后使用 Ctrl+V 粘贴 (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="待识别的原始分子图", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("") 
    convert_btn = st.button(" 识别图像", use_container_width=True, type="primary")

# ------------- 【右侧：识别与复现区】 -------------
with col_right:
    st.markdown('<div class="css-card"><div class="zone-title">🧬 2. 识别与复现区</div>', unsafe_allow_html=True)
    
    if convert_btn:
        if not uploaded_file:
            st.warning("请先在左侧上传或粘贴分子图片！")
        else:
            with st.spinner("Thinking..."):
                
                # 暂存图片
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    # ✅ 调用带缓存的识别函数
                    smiles_result = load_and_predict(temp_path)
                    
                    # ✅ 显示提取成功的 SMILES
                    st.success("✅ 图像特征提取成功！")
                    st.markdown("**提取的 SMILES 序列 (点击右上角图标复制):**")
                    st.code(smiles_result, language="text")
                    st.write("---")
                    
                    # ✅ RDKit 图像复原区
                    st.markdown("**二维结构复现校验:**")
                    st.markdown('<div class="render-zone">', unsafe_allow_html=True)
                    mol = Chem.MolFromSmiles(smiles_result)
                    
                    if mol:
                        rendered_img = Draw.MolToImage(mol, size=(400, 400))
                        st.image(rendered_img, caption="由获取到的 SMILES 重新渲染", width=300)
                    else:
                        st.error("警告：Decimer 给出的smiles出现语法错误，rdkit无法解码！请检查输入图片的质量或尝试其他图片。")
                    
                    st.markdown('</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"转换过程中发生崩溃：{e}")
                
                finally:
                    # ✅ 清理临时图片文件
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    else:
        st.info(" 请在左侧上传图片并点击“开始高精度转换”。校验结果将在此处显示。")
        
    # ✅ 极其重要：闭合右侧卡片的 div 标签！没有它页面就会崩溃黑屏！
    st.markdown('</div>', unsafe_allow_html=True)
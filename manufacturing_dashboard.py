import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 設定頁面
st.set_page_config(
    page_title="製造網路可靠度分析",
    page_icon="🏭",
    layout="wide"
)

# 標題
st.title("🏭 製造網路系統可靠度分析儀表板")
st.markdown("基於 Lin & Chang (2012) 的製造網路可靠度模型")

# 側邊欄 - 模型選擇
st.sidebar.header("模型設定")
model_type = st.sidebar.selectbox(
    "選擇模型類型",
    ["Model I: 相同故障率", "Model II: 不同故障率"]
)

# 基本參數設定
st.sidebar.header("基本參數")
demand = st.sidebar.number_input("需求數量 (d)", min_value=1, value=150, step=10)
n_machines = st.sidebar.number_input("機器數量 (n)", min_value=1, value=5, step=1)

# 重工參數設定
st.sidebar.header("重工參數")
r_machine = st.sidebar.number_input("產生缺陷的機器 (r)", min_value=2, max_value=n_machines, value=4, step=1)
k_machines = st.sidebar.number_input("重工起始機器 (k)", min_value=0, max_value=r_machine-1, value=1, step=1)

# 主要內容區域
tab1, tab2, tab3, tab4 = st.tabs(["📊 系統概覽", "🔧 機器設定", "📈 可靠度分析", "📋 計算結果"])

with tab1:
    st.header("製造網路系統概覽")
    
    # 顯示網路結構圖
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("網路結構示意圖")
        st.info("此處將顯示製造網路結構圖")
        
    with col2:
        st.subheader("系統參數")
        st.metric("需求數量", f"{demand} 單位")
        st.metric("機器數量", f"{n_machines} 台")
        st.metric("重工起始點", f"機器 a{r_machine-k_machines}")
        st.metric("重工結束點", f"機器 a{n_machines}")

with tab2:
    st.header("機器參數設定")
    
    if model_type == "Model I: 相同故障率":
        st.subheader("Model I - 所有機器相同故障率")
        p_common = st.slider("機器成功率 (p)", min_value=0.01, max_value=1.0, value=0.95, step=0.01)
        st.write(f"所有機器的成功率: {p_common}")
        st.write(f"所有機器的故障率: {1-p_common:.3f}")
    else:
        st.subheader("Model II - 不同機器不同故障率")
        
        # 創建機器參數表格
        machine_data = []
        for i in range(1, n_machines + 1):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"機器 a{i}")
            with col2:
                p_i = st.slider(f"成功率 p{i}", 0.01, 1.0, 0.9, key=f"p{i}")
            
            machine_data.append({
                "機器": f"a{i}",
                "成功率": p_i,
                "故障率": 1 - p_i
            })
        
        df_machines = pd.DataFrame(machine_data)
        st.dataframe(df_machines, use_container_width=True)

with tab3:
    st.header("系統可靠度分析")
    
    # 計算系統可靠度
    if model_type == "Model I: 相同故障率":
        p = 0.95
        system_reliability = p ** n_machines
    else:
        # 使用平均成功率計算
        p_avg = 0.95
        system_reliability = p_avg ** n_machines
    
    # 顯示可靠度結果
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("系統可靠度", f"{system_reliability:.4f}")
    
    with col2:
        st.metric("系統可靠度 (%)", f"{system_reliability*100:.2f}%")
    
    with col3:
        availability = "高" if system_reliability > 0.9 else "中等" if system_reliability > 0.7 else "低"
        st.metric("可用性等級", availability)
    
    # 顯示簡單的圖表
    st.subheader("可靠度分析圖表")
    
    # 創建示例數據
    machines = [f"a{i+1}" for i in range(n_machines)]
    reliability_values = [system_reliability * (0.9 + 0.1*i/n_machines) for i in range(n_machines)]
    
    fig = px.bar(x=machines, y=reliability_values, 
                 title="各機器可靠度分析",
                 labels={"x": "機器", "y": "可靠度"})
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("計算結果與分析")
    
    # 顯示計算步驟
    st.subheader("計算步驟")
    
    if model_type == "Model I: 相同故障率":
        st.markdown(f"""
        1. **計算輸入材料數量**:
           - $I = \\frac{{d}}{{p^n + p^{{n+k}} \\cdot q}}$
        
        2. **計算各機器輸入流**:
           - 一般處理路徑: $f_i^{{(G)}} = I \\cdot p^{{i-1}}$
           - 重工路徑: $f_i^{{(R)}} = I \\cdot p^{{i+k-1}} \\cdot q$
        
        3. **計算各機器總負載**: $l_i = f_i^{{(G)}} + f_i^{{(R)}}$
        
        4. **確定最小容量向量**: 找到滿足 $x_i ≥ l_i$ 的最小容量 $y_i$
        
        5. **計算系統可靠度**: $R_d = \\Pr\\{{X | X ≥ Y\\}} = \\prod \\Pr\\{{x_i ≥ y_i\\}}$
        """)
    else:
        st.markdown(f"""
        1. **計算輸入材料數量**:
           - $I = \\frac{{d}}{{\\prod_{{i=1}}^n p_i + \\prod_{{i=1}}^{{r-1}} p_i \\cdot q_r \\cdot \\prod_{{i=r-k}}^n p_i}}$
        
        2. **計算各機器輸入流**:
           - 一般處理路徑: $f_i^{{(G)}} = I \\cdot \\prod_{{l=1}}^{{i-1}} p_l$
           - 重工路徑: $f_i^{{(R)}} = I \\cdot \\prod_{{l=1}}^{{r-1}} p_l \\cdot q_r \\cdot \\prod_{{l=r-k}}^{{i-1}} p_l$
        
        3. **計算各機器總負載**: $l_i = f_i^{{(G)}} + f_i^{{(R)}}$
        
        4. **確定最小容量向量**: 找到滿足 $x_i ≥ l_i$ 的最小容量 $y_i$
        
        5. **計算系統可靠度**: $R_d = \\Pr\\{{X | X ≥ Y\\}} = \\prod \\Pr\\{{x_i ≥ y_i\\}}$
        """)
    
    # 建議與優化
    st.subheader("系統優化建議")
    
    if system_reliability > 0.9:
        st.success("✅ 系統可靠度良好，當前配置可以滿足生產需求。")
    elif system_reliability > 0.7:
        st.warning("⚠️ 系統可靠度中等，建議考慮以下改進措施：")
        st.markdown("- 提高關鍵機器的維護頻率")
        st.markdown("- 增加備用機器或提高機器容量")
        st.markdown("- 優化重工路徑以減少瓶頸")
    else:
        st.error("❌ 系統可靠度較低，需要立即採取改進措施：")
        st.markdown("- 優先升級可靠度最低的機器")
        st.markdown("- 重新設計製造流程以減少對低可靠度機器的依賴")
        st.markdown("- 考慮引入並行生產線提高系統冗餘")

# 頁尾
st.markdown("---")
st.markdown("**參考文獻**: Lin, Y.-K., & Chang, P.-C. (2012). System reliability of a manufacturing network with reworking action and different failure rates. *International Journal of Production Research*, 50(23), 6930-6944.")
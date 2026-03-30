import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 画面の設定
st.set_page_config(page_title="機種分析プロ版", layout="wide")
st.title("📊 14日間トレンド分析（軸固定カスタム）")

# ファイルの読み込み
uploaded_file = st.file_uploader("ここにExcelファイルをドロップしてください", type=["xlsx"])

if uploaded_file:
    # --- データ読み込み ---
    raw_df = pd.read_excel(uploaded_file, header=None)
    
    header_row = 0
    found = False
    for i, row in raw_df.iterrows():
        if "日付" in [str(v) for v in row.values]:
            header_row = i
            found = True
            break
            
    if found:
        df = pd.read_excel(uploaded_file, header=header_row)
        df.columns = df.columns.astype(str).str.strip().str.replace('稼動時間', '稼働時間')
        df = df.dropna(subset=['日付'])
        
        target_cols = ['稼働時間', '売上金額', '粗利金額']
        if all(c in df.columns for c in target_cols):
            for col in target_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # --- 指標の計算 ---
            df['アウト'] = df['稼働時間'] * 6000
            df['玉粗利'] = df.apply(lambda x: x['粗利金額'] / x['アウト'] if x['アウト'] > 0 else 0, axis=1)
            
            # 14日間移動平均
            days = 14
            df['アウト_MA'] = df['アウト'].rolling(window=days, min_periods=1).mean()
            df['売上_MA'] = df['売上金額'].rolling(window=days, min_periods=1).mean()
            df['玉粗利_MA'] = df['玉粗利'].rolling(window=days, min_periods=1).mean()

            # --- グラフの作成 ---
            fig = go.Figure()

            # アウト（青・太線）
            fig.add_trace(go.Scatter(x=df['日付'], y=df['アウト_MA'], name='アウト(14日平均)', line=dict(color='#1f77b4', width=4)))

            # 売上（緑・点線）
            fig.add_trace(go.Scatter(x=df['日付'], y=df['売上_MA'], name='売上(14日平均)', line=dict(color='#2ca02c', width=2, dash='dot')))

            # 玉粗利（赤・実線）：右軸
            fig.add_trace(go.Scatter(x=df['日付'], y=df['玉粗利_MA'], name='玉粗利(14日平均)', line=dict(color='#d62728', width=3), yaxis="y2"))

            # 中央値（アウト30,000）の補助線を追加
            fig.add_hline(y=30000, line_dash="dash", line_color="gray", annotation_text="アウト 30,000")

            # レイアウト調整
            fig.update_layout(
                title="【14日間移動平均】稼働・売上・玉粗利（軸固定）",
                xaxis_title="日付",
                yaxis=dict(
                    title="アウト / 売上 (円)",
                    side="left",
                    range=[0, 60000],  # 0から60,000に設定
                    gridcolor='lightgrey'
                ),
                yaxis2=dict(
                    title="玉粗利 (円)",
                    overlaying='y',
                    side='right',
                    range=[-6.0, 1.0],  # -6から1.0に設定
                    zeroline=True,
                    zerolinecolor='black',
                    zerolinewidth=3, # 粗利0の線を強調
                    tickformat=".2f"
                ),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='white'
            )

            st.plotly_chart(fig, use_container_width=True)
            st.success("指定された軸範囲（左0-6万、右-6-1、中央値強調）で作成しました。")
            
        else:
            st.error("必要な項目が見つかりません。")
    else:
        st.error("Excelの中に『日付』が見つかりませんでした。")
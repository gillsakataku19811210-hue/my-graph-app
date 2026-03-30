import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 画面の設定
st.set_page_config(page_title="機種分析アプリ", layout="wide")
st.title("📊 パチンコ・パチスロ 14日間トレンド分析")

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
        
        # 表記ゆれの吸収とクリーニング
        df.columns = df.columns.astype(str).str.strip().str.replace('稼動時間', '稼働時間')
        df = df.dropna(subset=['日付'])
        
        target_cols = ['稼働時間', '売上金額', '粗利金額']
        if all(c in df.columns for c in target_cols):
            for col in target_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # ① アウトの計算
            df['アウト'] = df['稼働時間'] * 6000
            
            # --- 14日間移動平均に変更 ---
            days = 14
            df['アウト_MA'] = df['アウト'].rolling(window=days, min_periods=1).mean()
            df['売上_MA'] = df['売上金額'].rolling(window=days, min_periods=1).mean()
            df['粗利_MA'] = df['粗利金額'].rolling(window=days, min_periods=1).mean()

            # --- グラフの作成 ---
            fig = go.Figure()

            # アウト（青・太線）
            fig.add_trace(go.Scatter(
                x=df['日付'], y=df['アウト_MA'], 
                name=f'アウト({days}日平均)', 
                line=dict(color='#1f77b4', width=4)
            ))

            # 売上（緑・点線）
            fig.add_trace(go.Scatter(
                x=df['日付'], y=df['売上_MA'], 
                name=f'売上({days}日平均)', 
                line=dict(color='#2ca02c', width=2, dash='dot')
            ))

            # 粗利（赤・太線）：右軸
            fig.add_trace(go.Scatter(
                x=df['日付'], y=df['粗利_MA'], 
                name=f'粗利({days}日平均)', 
                line=dict(color='#d62728', width=4), 
                yaxis="y2"
            ))

            # レイアウト調整（見やすさ重視）
            fig.update_layout(
                title=f"【{days}日間移動平均】稼働・収益推移",
                xaxis_title="日付",
                yaxis=dict(
                    title="アウト / 売上 (円)",
                    side="left",
                    gridcolor='lightgrey'
                ),
                yaxis2=dict(
                    title="粗利 (円)",
                    overlaying='y',
                    side='right',
                    showgrid=False,
                    zeroline=True, # 0の線を強調（赤字かどうかの境目）
                    zerolinecolor='black',
                    zerolinewidth=2
                ),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='white' # 背景を白くして見やすく
            )

            st.plotly_chart(fig, use_container_width=True)
            st.success(f"{days}日移動平均でグラフを作成しました。")
            
        else:
            st.error("必要な項目（稼働時間、売上、粗利）がExcelに見つかりません。")
    else:
        st.error("Excelの中に『日付』という項目が見つかりませんでした。")
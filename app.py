import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 画面の設定
st.set_page_config(page_title="機種分析アプリ(期間切替版)", layout="wide")
st.title("📊 パチンコ・パチスロ トレンド分析")

# --- サイドバーで期間を選択 ---
st.sidebar.header("表示設定")
days_option = st.sidebar.radio(
    "移動平均の期間を選択してください",
    (7, 14, 30),
    index=1, # 初期値は14日
    format_func=lambda x: f"{x}日間平均 ( {x}D )"
)

# ファイルの読み込み
uploaded_file = st.file_uploader("ここにExcelファイルをドロップしてください", type=["xlsx"])

if uploaded_file:
    # --- タイトル（D4セル）の取得 ---
    title_df = pd.read_excel(uploaded_file, header=None, nrows=5)
    try:
        target_title = title_df.iloc[3, 3] 
        if pd.isna(target_title):
            target_title = "機種分析グラフ"
    except:
        target_title = "機種分析グラフ"

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
        
        # 表記ゆれの吸収
        df.columns = df.columns.astype(str).str.strip().str.replace('稼動時間', '稼働時間')
        df = df.dropna(subset=['日付'])
        
        target_cols = ['稼働時間', '売上金額', '粗利金額']
        if all(c in df.columns for c in target_cols):
            for col in target_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # --- 指標の計算 ---
            df['アウト'] = df['稼働時間'] * 6000
            df['玉単価'] = df.apply(lambda x: x['売上金額'] / x['アウト'] if x['アウト'] > 0 else 0, axis=1)
            df['玉粗利'] = df.apply(lambda x: x['粗利金額'] / x['アウト'] if x['アウト'] > 0 else 0, axis=1)
            
            # 選択された期間で移動平均を計算
            days = days_option
            df['アウト_MA'] = df['アウト'].rolling(window=days, min_periods=1).mean()
            df['玉単価_MA'] = df['玉単価'].rolling(window=days, min_periods=1).mean()
            df['玉粗利_MA'] = df['玉粗利'].rolling(window=days, min_periods=1).mean()

            # --- グラフの作成 ---
            fig = go.Figure()

            # アウト（青・太線）
            fig.add_trace(go.Scatter(x=df['日付'], y=df['アウト_MA'], name=f'アウト({days}D平均)', line=dict(color='#1f77b4', width=4)))
            # 玉単価（緑・点線）
            fig.add_trace(go.Scatter(x=df['日付'], y=df['玉単価_MA'], name=f'玉単価({days}D平均)', line=dict(color='#2ca02c', width=2, dash='dot'), yaxis="y2"))
            # 玉粗利（赤・実線）
            fig.add_trace(go.Scatter(x=df['日付'], y=df['玉粗利_MA'], name=f'玉粗利({days}D平均)', line=dict(color='#d62728', width=3), yaxis="y2"))

            # レイアウト調整
            fig.update_layout(
                title=f"【{target_title}】 {days}日間トレンド分析",
                xaxis_title="日付",
                height=800,
                yaxis=dict(title="アウト", side="left", range=[0, 60000], dtick=5000, gridcolor='lightgrey'),
                yaxis2=dict(title="玉単価 / 玉粗利 (円)", overlaying='y', side='right', range=[-6, 6], dtick=1, showgrid=True, gridcolor='rgba(200, 200, 200, 0.2)', zeroline=True, zerolinecolor='black', zerolinewidth=3, tickformat=".2f"),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='white'
            )

            st.plotly_chart(fig, use_container_width=True)
            st.sidebar.success(f"現在は {days}D 平均を表示中")
            
        else:
            st.error("必要な項目が見つかりません。")
    else:
        st.error("Excelの中に『日付』が見つかりませんでした。")
「売上金額」を「玉単価」に変更ですね。
玉単価（売上 / アウト）は、その台が1個のアウトに対していくら売上を上げているかを示す、パチンコ営業の収益性を測る重要指標です。

今回の修正では、**「売上（緑の点線）」を「玉単価（緑の点線）」に書き換え、玉単価も玉粗利と同じく右側の軸（0〜6円の範囲）**に表示するように調整しました。これにより、「1個のアウトからいくら売れて（玉単価）、いくら残ったか（玉粗利）」が同じ目盛りで比較できるようになります。

修正版：app.py（これをコピーしてGitHubに上書きしてください）
Python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 画面の設定
st.set_page_config(page_title="機種分析アプリ(玉単価版)", layout="wide")
st.title("📊 パチンコ・パチスロ 14日間トレンド分析")

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
            
            # 玉単価の計算（売上 / アウト）
            df['玉単価'] = df.apply(lambda x: x['売上金額'] / x['アウト'] if x['アウト'] > 0 else 0, axis=1)
            
            # 玉粗利の計算（粗利 / アウト）
            df['玉粗利'] = df.apply(lambda x: x['粗利金額'] / x['アウト'] if x['アウト'] > 0 else 0, axis=1)
            
            # 14日間移動平均
            days = 14
            df['アウト_MA'] = df['アウト'].rolling(window=days, min_periods=1).mean()
            df['玉単価_MA'] = df['玉単価'].rolling(window=days, min_periods=1).mean()
            df['玉粗利_MA'] = df['玉粗利'].rolling(window=days, min_periods=1).mean()

            # --- グラフの作成 ---
            fig = go.Figure()

            # アウト（青・太線）：左軸
            fig.add_trace(go.Scatter(
                x=df['日付'], y=df['アウト_MA'], 
                name=f'アウト({days}日平均)', 
                line=dict(color='#1f77b4', width=4)
            ))

            # 玉単価（緑・点線）：右軸
            fig.add_trace(go.Scatter(
                x=df['日付'], y=df['玉単価_MA'], 
                name=f'玉単価({days}日平均)', 
                line=dict(color='#2ca02c', width=2, dash='dot'),
                yaxis="y2"
            ))

            # 玉粗利（赤・実線）：右軸
            fig.add_trace(go.Scatter(
                x=df['日付'], y=df['玉粗利_MA'], 
                name=f'玉粗利({days}日平均)', 
                line=dict(color='#d62728', width=3), 
                yaxis="y2"
            ))

            # レイアウト調整
            fig.update_layout(
                title=f"【{target_title}】 14日間トレンド (アウト/玉単価/玉粗利)",
                xaxis_title="日付",
                height=800,
                # 左軸：アウト（0〜60,000）
                yaxis=dict(
                    title="アウト",
                    side="left",
                    range=[0, 60000], 
                    dtick=5000,
                    gridcolor='lightgrey'
                ),
                # 右軸：玉単価・玉粗利（-6〜6）
                yaxis2=dict(
                    title="玉単価 / 玉粗利 (円)",
                    overlaying='y',
                    side='right',
                    range=[-6, 6],
                    dtick=1,
                    showgrid=True,
                    gridcolor='rgba(200, 200, 200, 0.2)',
                    zeroline=True,
                    zerolinecolor='black',
                    zerolinewidth=3,
                    tickformat=".2f"
                ),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='white'
            )

            st.plotly_chart(fig, use_container_width=True)
            st.success("玉単価と玉粗利を右軸に表示しました。")
            
        else:
            st.error("必要な項目が見つかりません。")
    else:
        st.error("Excelの中に『日付』が見つかりませんでした。")
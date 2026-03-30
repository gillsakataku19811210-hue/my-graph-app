import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 画面の設定
st.set_page_config(page_title="機種分析アプリ", layout="wide")
st.title("📊 パチンコ・パチスロ機種分析")

# ファイルの読み込み
uploaded_file = st.file_uploader("ここにExcelファイルをドロップしてください", type=["xlsx"])

if uploaded_file:
    # --- データ読み込みの工夫 ---
    raw_df = pd.read_excel(uploaded_file, header=None)
    
    # 「日付」という文字が含まれる行（ヘッダー行）を自動で探す
    header_row = 0
    found = False
    for i, row in raw_df.iterrows():
        if "日付" in [str(v) for v in row.values]:
            header_row = i
            found = True
            break
            
    if found:
        # 見つけた行をヘッダーとして読み込み直す
        df = pd.read_excel(uploaded_file, header=header_row)
        
        # 列名の前後にある空白を削除し、さらに「稼動」を「稼働」に統一する
        df.columns = df.columns.astype(str).str.strip().str.replace('稼動時間', '稼働時間')

        # 「日付」列を基準に、空行を削除
        df = df.dropna(subset=['日付'])
        
        # 必要な列名があるかチェック
        target_cols = ['稼働時間', '売上金額', '粗利金額']
        missing_cols = [c for c in target_cols if c not in df.columns]
        
        if not missing_cols:
            # 数値データに変換
            for col in target_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # ① アウトの計算 (稼働時間 * 6000)
            df['アウト'] = df['稼働時間'] * 6000
            
            # 7日間の移動平均を計算
            df['アウト_7MA'] = df['アウト'].rolling(window=7, min_periods=1).mean()
            df['売上_7MA'] = df['売上金額'].rolling(window=7, min_periods=1).mean()
            df['粗利_7MA'] = df['粗利金額'].rolling(window=7, min_periods=1).mean()

            # グラフの作成
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['日付'], y=df['アウト_7MA'], name='アウト(7日平均)', line=dict(color='royalblue', width=3)))
            fig.add_trace(go.Scatter(x=df['日付'], y=df['売上_7MA'], name='売上(7日平均)', line=dict(color='seagreen', width=2)))
            fig.add_trace(go.Scatter(x=df['日付'], y=df['粗利_7MA'], name='粗利(7日平均)', line=dict(color='crimson', width=3), yaxis="y2"))

            fig.update_layout(
                title="【7日移動平均】トレンド推移",
                xaxis_title="日付",
                yaxis=dict(title="アウト・売上"),
                yaxis2=dict(title="粗利", overlaying='y', side='right'),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig, use_container_width=True)
            st.success("グラフの表示に成功しました！")
            
        else:
            st.error(f"Excelの中に以下の列が見つかりません: {', '.join(missing_cols)}")
    else:
        st.error("Excelの中に『日付』という項目が見つかりませんでした。")
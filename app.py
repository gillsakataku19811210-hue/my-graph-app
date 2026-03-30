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
    # 最初はヘッダーなしで読み込み、「日付」という文字がある行を探す
    raw_df = pd.read_excel(uploaded_file, header=None)
    
    # 「日付」という文字が含まれる行の番号を探す
    header_row = 0
    for i, row in raw_df.iterrows():
        if "日付" in row.values:
            header_row = i
            break
            
    # 見つけた行をヘッダーとして読み込み直す
    df = pd.read_excel(uploaded_file, header=header_row)
    # --------------------------

    # 「日付」列が正しく読み込めたか確認して処理
    if '日付' in df.columns:
        # 日付や数値に変換できない行（空行など）を掃除
        df = df.dropna(subset=['日付'])
        
        # 数値データが文字列（カンマ付きなど）になっていた場合に数値へ変換
        cols_to_fix = ['稼働時間', '売上金額', '粗利金額']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 指標の計算
        df['アウト'] = df['稼働時間'] * 6000
        
        # 7日間の移動平均を計算
        df['アウト_7MA'] = df['アウト'].rolling(window=7).mean()
        df['売上_7MA'] = df['売上金額'].rolling(window=7).mean()
        df['粗利_7MA'] = df['粗利金額'].rolling(window=7).mean()

        # グラフの作成
        fig = go.Figure()
        # アウト（青）
        fig.add_trace(go.Scatter(x=df['日付'], y=df['アウト_7MA'], name='アウト(7日平均)', line=dict(color='blue', width=3)))
        # 売上（緑）
        fig.add_trace(go.Scatter(x=df['日付'], y=df['売上_7MA'], name='売上(7日平均)', line=dict(color='green', width=2)))
        # 粗利（赤）を右側の軸に表示
        fig.add_trace(go.Scatter(x=df['日付'], y=df['粗利_7MA'], name='粗利(7日平均)', line=dict(color='red', width=3), yaxis="y2"))

        fig.update_layout(
            title="【7日移動平均】アウト・売上・粗利 推移",
            xaxis_title="日付",
            yaxis=dict(title="アウト・売上"),
            yaxis2=dict(title="粗利", overlaying='y', side='right'),
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)
        st.success("グラフを表示しました！")
    else:
        st.error("Excelの中に『日付』という列名が見つかりませんでした。フォーマットを確認してください。")
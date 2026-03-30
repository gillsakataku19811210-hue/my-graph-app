import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 画面の設定
st.set_page_config(page_title="機種分析アプリ", layout="wide")
st.title("📊 パチンコ・パチスロ機種分析")

# ファイルの読み込み
uploaded_file = st.file_uploader("ここにExcelファイルをドロップしてください", type=["xlsx"])

if uploaded_file:
    # 5行目からデータを読み込む設定
    df = pd.read_excel(uploaded_file, header=4)
    df = df.dropna(subset=['日付']) # 日付がない行は消す
    
    # 指標の計算
    df['アウト'] = df['稼働時間'] * 6000
    
    # 7日間の移動平均を計算
    df['アウト_7MA'] = df['アウト'].rolling(window=7).mean()
    df['売上_7MA'] = df['売上金額'].rolling(window=7).mean()
    df['粗利_7MA'] = df['粗利金額'].rolling(window=7).mean()

    # グラフの作成
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['日付'], y=df['アウト_7MA'], name='アウト(7日平均)', line=dict(color='blue', width=3)))
    fig.add_trace(go.Scatter(x=df['日付'], y=df['売上_7MA'], name='売上(7日平均)', line=dict(color='green', width=2)))
    fig.add_trace(go.Scatter(x=df['日付'], y=df['粗利_7MA'], name='粗利(7日平均)', line=dict(color='red', width=3), yaxis="y2"))

    fig.update_layout(
        title="【7日移動平均】推移グラフ",
        yaxis=dict(title="アウト・売上"),
        yaxis2=dict(title="粗利", overlaying='y', side='right'),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.success("グラフを表示しました！")
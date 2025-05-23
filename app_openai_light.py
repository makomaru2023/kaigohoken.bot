import streamlit as st
import json
import os
from openai import OpenAI

# ページ設定（軽量化）
st.set_page_config(
    page_title="介護保険制度情報チャットボット",
    page_icon="👵",
    layout="centered",
    initial_sidebar_state="collapsed"  # サイドバーを初期状態で折りたたむ
)

# タイトルとヘッダー（シンプル化）
st.title("介護保険制度情報チャットボット")
st.markdown("厚生労働省公表資料（2025年4月時点）に基づいた情報を提供します。")

# APIキーの設定（環境変数から取得）
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    st.warning("OpenAI APIキーが設定されていません。環境変数 'OPENAI_API_KEY' を設定してください。")
    api_key = st.text_input("OpenAI APIキーを入力", type="password")

# セッション状態の初期化（最小限）
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "こんにちは、介護保険制度について質問があればお答えします。"}
    ]

# チャット履歴の表示（最適化）
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ユーザー入力（シンプル化）
if prompt := st.chat_input("質問を入力してください"):
    # ユーザーメッセージを表示
    with st.chat_message("user"):
        st.write(prompt)
    
    # ユーザーメッセージをセッションに追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # OpenAIを使用して回答を生成
    if api_key:
        with st.spinner('回答を生成中...'):
            try:
                client = OpenAI(api_key=api_key)
                
                system_prompt = """
                あなたは介護保険に詳しい相談員です。以下のガイドラインに従って回答してください：
                
                1. 専門用語が出たら（）で短く補足してください
                2. 根拠条文・省令・厚労省資料名を文末に簡潔に記載してください
                3. 法律・個別ケース判断が必要な場合は「市区町村の介護保険担当窓口へ確認を」と促してください
                4. 最新情報が未反映の可能性があれば「最終確認日: 2025-04-01」と明記してください
                5. 簡潔かつ明確に回答してください
                """
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500  # 回答の長さを制限
                )
                
                answer = response.choices[0].message.content
                
            except Exception as e:
                answer = f"エラーが発生しました: {str(e)}"
    else:
        answer = "APIキーが設定されていないため、回答を生成できません。"
    
    # アシスタントの回答を表示
    with st.chat_message("assistant"):
        st.write(answer)
    
    # アシスタントの回答をセッションに追加
    st.session_state.messages.append({"role": "assistant", "content": answer})

# フッター（シンプル化）
st.caption("注意: このチャットボットは一般的な情報提供を目的としています。個別の状況に応じた正確な情報は、お住まいの市区町村の介護保険担当窓口にご確認ください。")

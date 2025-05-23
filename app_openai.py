import streamlit as st
import json
import os
from openai import OpenAI

# ページ設定
st.set_page_config(
    page_title="介護保険制度情報チャットボット",
    page_icon="👵",
    layout="centered"
)

# タイトルとヘッダー
st.title("介護保険制度情報チャットボット")
st.markdown("厚生労働省公表資料（2025年4月時点）に基づいた情報を提供します。")

# APIキーの設定（環境変数から取得するか、入力フォームから取得）
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("OpenAI APIキーを入力してください", type="password")
    if not api_key:
        st.warning("OpenAI APIキーを入力してください。APIキーは環境変数 'OPENAI_API_KEY' としても設定できます。")

# セッション状態の初期化
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# サイドバーに情報を表示
with st.sidebar:
    st.header("このチャットボットについて")
    st.markdown("""
    **機能**:
    - 介護保険制度の概要・利用手続き・費用の目安を説明
    - 専門用語は（）で短く補足
    - 根拠条文・省令・厚労省資料名を記載
    - 最新情報の確認日を明記
    
    **最終確認日**: 2025-04-01
    """)
    
    # 質問例を表示
    st.subheader("質問例")
    example_questions = [
        "介護保険制度とは何ですか？",
        "要介護認定の申請方法は？",
        "在宅サービスには何がありますか？",
        "介護保険の自己負担はいくらですか？",
        "第2号被保険者とは？",
        "住宅改修は何円まで補助される？"
    ]
    
    for q in example_questions:
        if st.button(q, key=f"example_{q}"):
            st.session_state.user_input = q
            st.experimental_rerun()

# OpenAIを使用して回答を生成する関数
def generate_response_with_openai(question, name=""):
    try:
        if not api_key:
            return "OpenAI APIキーが設定されていません。APIキーをサイドバーに入力するか、環境変数として設定してください。"
        
        client = OpenAI(api_key=api_key)
        
        system_prompt = """
        あなたは介護保険に詳しい相談員です。以下のガイドラインに従って回答してください：
        
        1. 専門用語が出たら（）で短く補足してください
        2. 根拠条文・省令・厚労省資料名を文末に簡潔に記載してください（例: 「介護保険法 第7条」）
        3. 法律・個別ケース判断が必要な場合は「市区町村の介護保険担当窓口へ確認を」と必ず促してください
        4. 最新情報が未反映の可能性があれば「最終確認日: 2025-04-01」のように明記してください
        5. 年金・医療保険の話に逸れたら、その関連範囲で簡潔に答えたうえで、専門窓口案内に切り替えてください
        
        禁止事項：
        * 医師・弁護士資格を有するかのような断定的助言は行わないでください
        * ユーザーの個人情報を保持／記録する行為は行わないでください
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        answer = response.choices[0].message.content
        
        if name:
            answer = f"{name}さん、{answer}"
            
        return answer
    
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# チャット履歴の表示
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"**あなた**: {chat['content']}")
    else:
        st.markdown(f"**ボット**: {chat['content']}")

# ユーザー情報入力
name = st.text_input("お名前（任意）", key="user_name")

# ユーザー入力
user_input = st.text_area("介護保険制度について質問してください", key="user_input", height=100)

# 送信ボタン
if st.button("質問する") and user_input and api_key:
    # ユーザーメッセージをチャット履歴に追加
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # ローディング表示
    with st.spinner('回答を生成中...'):
        # OpenAIを使用して回答を生成
        response = generate_response_with_openai(user_input, name)
    
    # ボットの応答をチャット履歴に追加
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # 入力欄をクリア
    st.session_state.user_input = ""
    
    # 画面を更新して新しいチャット履歴を表示
    st.experimental_rerun()

# フッター
st.markdown("---")
st.markdown("**注意**: このチャットボットは一般的な情報提供を目的としています。個別の状況に応じた正確な情報は、お住まいの市区町村の介護保険担当窓口にご確認ください。")

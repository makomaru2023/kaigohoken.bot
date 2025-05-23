import streamlit as st
import json
import re
import pandas as pd
from datetime import datetime

# 最終更新日
LAST_UPDATED = "2025-04-01"

# データの読み込み
with open('rehab_data.json', 'r', encoding='utf-8') as f:
    care_data = json.load(f)

# ページ設定
st.set_page_config(
    page_title="介護保険制度情報チャットボット",
    page_icon="👵",
    layout="centered"
)

# タイトルとヘッダー
st.title("介護保険制度情報チャットボット")
st.markdown("厚生労働省公表資料（2025年4月時点）に基づいた情報を提供します。")

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

# 専門用語に補足を追加する関数
def format_technical_terms(response):
    terms = {
        "要介護認定": "(心身の状態を調査し介護の必要度を判定する制度)",
        "要支援": "(日常生活に部分的な支援が必要な状態)",
        "要介護": "(日常生活に常時介護が必要な状態)",
        "ケアマネジャー": "(介護支援専門員)",
        "居宅介護支援事業所": "(ケアプラン作成などを行う事業所)",
        "地域包括支援センター": "(高齢者の総合相談窓口)",
        "特定疾病": "(40-64歳の方が介護保険を利用できる特定の病気)",
        "第1号被保険者": "(65歳以上の方)",
        "第2号被保険者": "(40-64歳の医療保険加入者)"
    }
    
    for term, explanation in terms.items():
        if term in response and not f"{term}{explanation}" in response:
            response = response.replace(term, f"{term}{explanation}", 1)
    
    return response

# 回答に引用情報を追加する関数
def add_citation(response, category):
    citations = {
        "general": "介護保険法 第1条、第2条",
        "eligibility": "介護保険法 第9条、第10条",
        "certification": "介護保険法 第27条、第32条",
        "care_levels": "介護保険法 第7条",
        "services_home": "介護保険法 第8条",
        "services_facility": "介護保険法 第8条",
        "community_services": "介護保険法 第8条の2",
        "cost": "介護保険法 第40条、第41条",
        "care_plan": "介護保険法 第8条第23項、第46条",
        "prevention": "介護保険法 第115条の45",
        "caregivers": "介護休業法、育児・介護休業法"
    }
    
    if category in citations:
        response += f"\n\n（根拠：{citations[category]}）"
    
    # 市区町村への確認を促す文言を追加
    if re.search(r'(個別|ケース|判断|申請|手続き|認定)', response):
        response += "\n\n詳細や個別のケースについては、お住まいの市区町村の介護保険担当窓口へご確認ください。"
    
    # 医療保険や年金に関する内容が含まれる場合
    if re.search(r'(医療保険|健康保険|年金)', response):
        response += "\n\n医療保険・年金制度の詳細については、専門の窓口（市区町村の国民健康保険課、年金事務所等）にお問い合わせください。"
    
    # 最終更新日を追加
    response += f"\n\n最終確認日: {LAST_UPDATED}"
    
    return response

# 応答を生成する関数
def generate_response(user_message):
    user_message = user_message.lower()
    
    # 医師・弁護士資格を必要とする質問かチェック
    medical_legal_keywords = ['診断', '治療', '薬', '処方', '訴訟', '裁判', '賠償', '契約']
    if any(keyword in user_message for keyword in medical_legal_keywords):
        return "ご質問の内容は医療や法律の専門的な判断を要するものです。医師や弁護士など、適切な専門家にご相談ください。介護保険制度の一般的な情報についてはお答えできます。\n\n最終確認日: " + LAST_UPDATED
    
    # 個人情報に関する質問かチェック
    personal_info_keywords = ['あなたの名前', '個人情報', '電話番号', '住所', 'メールアドレス']
    if any(keyword in user_message for keyword in personal_info_keywords):
        return "申し訳ありませんが、個人情報の収集や保持は行っておりません。介護保険制度に関するご質問にお答えすることができます。\n\n最終確認日: " + LAST_UPDATED
    
    # 応答を検索
    for category in care_data:
        for keyword in care_data[category]['keywords']:
            if keyword in user_message:
                responses = care_data[category]['responses']
                response = responses[-1] if len(responses) > 2 else responses[0]  # 最新の回答を優先
                response = format_technical_terms(response)
                response = add_citation(response, category)
                return response
    
    # 挨拶への応答
    greetings = ['こんにちは', 'こんばんは', 'おはよう', 'やあ', 'ハロー']
    for greeting in greetings:
        if greeting in user_message:
            return f"{greeting}！介護保険制度について何か質問がありますか？私は厚生労働省公表資料（2025年4月時点）に基づいて、制度の概要・利用手続き・費用の目安などを説明できます。\n\n最終確認日: {LAST_UPDATED}"
    
    # デフォルトの応答
    default_responses = [
        "申し訳ありませんが、その質問についての情報は持っていません。介護保険制度や介護サービスについて質問してみてください。",
        "もう少し具体的に質問していただけますか？例えば「介護保険とは」や「要介護認定について」などについて聞くことができます。",
        "介護保険制度の特定の側面について知りたい場合は、お気軽にお尋ねください。"
    ]
    default_response = default_responses[0]
    return default_response + f"\n\n最終確認日: {LAST_UPDATED}"

# ユーザー情報入力
name = st.text_input("お名前（任意）", key="user_name")

# チャット履歴の表示
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"**あなた**: {chat['content']}")
    else:
        st.markdown(f"**ボット**: {chat['content']}")

# ユーザー入力
user_input = st.text_area("介護保険制度について質問してください", key="user_input", height=100)

# 送信ボタン
if st.button("質問する") and user_input:
    # ユーザーメッセージをチャット履歴に追加
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # 応答を生成
    if name:
        response = f"{name}さん、"
    else:
        response = ""
    
    response += generate_response(user_input)
    
    # ボットの応答をチャット履歴に追加
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # 入力欄をクリア
    st.session_state.user_input = ""
    
    # 画面を更新して新しいチャット履歴を表示
    st.experimental_rerun()

# フッター
st.markdown("---")
st.markdown("**注意**: このチャットボットは一般的な情報提供を目的としています。個別の状況に応じた正確な情報は、お住まいの市区町村の介護保険担当窓口にご確認ください。")

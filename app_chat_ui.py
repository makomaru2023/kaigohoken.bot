import streamlit as st
from streamlit_chat import message
import json
import os
from openai import OpenAI
import random

# ページ設定
st.set_page_config(
    page_title="介護保険制度情報チャットボット",
    page_icon="👵",
    layout="wide"
)

# 最終更新日
LAST_UPDATED = "2025-04-01"

# データの読み込み
with open('rehab_data.json', 'r', encoding='utf-8') as f:
    care_data = json.load(f)

# タイトルとヘッダー
st.title("介護保険制度情報チャットボット")
st.markdown("厚生労働省公表資料（2025年4月時点）に基づいた情報を提供します。")

# APIキーの設定（環境変数から取得するか、入力フォームから取得）
api_key = os.environ.get("OPENAI_API_KEY")

# セッション状態の初期化
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    # 初期メッセージを追加
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": "こんにちは、介護保険についてご相談ですね。どのようなことでお困りですか？"
    })

if 'generated' not in st.session_state:
    st.session_state.generated = ["こんにちは、介護保険についてご相談ですね。どのようなことでお困りですか？"]
if 'past' not in st.session_state:
    st.session_state.past = []

# 2カラムレイアウト
col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("このチャットボットについて")
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
            st.session_state.past.append(q)
            
            # データベースから回答を生成
            response = generate_response_from_database(q)
            st.session_state.generated.append(response)
            st.session_state.chat_history.append({"role": "user", "content": q})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
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
    
    # 最終更新日を追加
    response += f"\n\n最終確認日: {LAST_UPDATED}"
    
    return response

# データベースから応答を生成する関数
def generate_response_from_database(user_message):
    user_message = user_message.lower()
    
    # 応答を検索
    for category in care_data:
        for keyword in care_data[category]['keywords']:
            if keyword in user_message:
                responses = care_data[category]['responses']
                response = random.choice(responses)
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
    default_response = random.choice(default_responses)
    return default_response + f"\n\n最終確認日: {LAST_UPDATED}"

# OpenAIを使用して回答を生成する関数（APIキーがある場合）
def generate_response_with_openai(question):
    try:
        if not api_key:
            return generate_response_from_database(question)
        
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
        
        return response.choices[0].message.content
    
    except Exception as e:
        # APIエラーの場合はデータベースから回答を生成
        return generate_response_from_database(question)

with col1:
    # チャット履歴の表示
    if st.session_state.generated:
        for i in range(len(st.session_state.generated)):
            if i < len(st.session_state.past):
                message(st.session_state.past[i], is_user=True, key=f"user_{i}")
            message(st.session_state.generated[i], key=f"bot_{i}")
    
    # ユーザー入力
    user_input = st.text_input("あなたの質問をどうぞ", key="user_input")
    
    # 送信ボタン
    if user_input:
        # ユーザーメッセージを履歴に追加
        st.session_state.past.append(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # APIキーがあればOpenAIを使用、なければデータベースから回答
        if api_key:
            response = generate_response_with_openai(user_input)
        else:
            response = generate_response_from_database(user_input)
        
        # ボットの応答を履歴に追加
        st.session_state.generated.append(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # 入力欄をクリア
        st.session_state.user_input = ""
        
        # 画面を更新
        st.experimental_rerun()

# フッター
st.markdown("---")
st.markdown("**注意**: このチャットボットは一般的な情報提供を目的としています。個別の状況に応じた正確な情報は、お住まいの市区町村の介護保険担当窓口にご確認ください。")

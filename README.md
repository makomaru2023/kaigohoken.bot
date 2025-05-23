# kaigohoken.bot

## 介護保険制度情報チャットボット

このプロジェクトは、介護保険法に関する情報を提供するシンプルなチャットボットです。

## 機能

- 介護保険制度の基本情報の提供
- 要介護認定の仕組みと申請方法の説明
- 様々な介護サービス（在宅・施設・地域密着型）の紹介
- 介護保険の費用や自己負担に関する情報
- 介護予防や家族介護者支援に関する情報

## 技術スタック

- Python 3
- Flask（Webフレームワーク）
- HTML/CSS/JavaScript（フロントエンド）

## セットアップ方法

1. 必要なパッケージをインストールします：

```
pip install -r requirements.txt
```

2. アプリケーションを実行します：

```
python app.py
```

3. ブラウザで以下のURLにアクセスします：

```
http://localhost:5000
```

## 使い方

- テキスト入力欄に質問を入力し、「送信」ボタンをクリックするか、Enterキーを押します。
- 提案されたボタンをクリックして、一般的な質問をすることもできます。

## カスタマイズ

`rehab_data.json` ファイルを編集することで、チャットボットの応答内容をカスタマイズできます。

注意: ファイル名は元のプロジェクト名（rehab-chatbot）に由来して「rehab_data.json」のままですが、内容は介護保険法に関する情報に更新されています。

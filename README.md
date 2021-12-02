# charmy.py
Bot for Legion server, developed with Discord.py

# 本アプリケーションについて
ソーシャルゲーム「アサルトリリィ Last Bullet」のレギオン用に開発、運用中の
Discord.pyをベースにしたBotサービスです。

[Discord Bot 最速チュートリアル【Python&Heroku&GitHub】 - Qiita](https://qiita.com/1ntegrale9/items/aa4b373e8895273875a8)

を基に環境を構築し、Heroku上にデプロイし運用しています。

## 各種ファイル情報

### discordbot.py
PythonによるDiscordBotのアプリケーションファイルです。

### functions.py
共通関数を格納したpythonファイルです。

### cogs(DIR)
discordbot.pyが使用する各種機能(クラス)群のpythonファイルを格納しているディレクトリです。

### requirements.txt
使用しているPythonのライブラリ情報の設定ファイルです。

### Procfile
Herokuでのプロセス実行コマンドの設定ファイルです。

### runtime.txt
Herokuでの実行環境の設定ファイルです。

### app.json
Herokuデプロイボタンの設定ファイルです。

### .github/workflows/flake8.yaml
GitHub Actions による自動構文チェックの設定ファイルです。

### .gitignore
Git管理が不要なファイル/ディレクトリの設定ファイルです。

### LICENSE
このリポジトリのコードの権利情報です。MITライセンスの範囲でご自由にご利用ください。

### README.md
このドキュメントです。



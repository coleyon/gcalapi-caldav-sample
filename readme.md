# Summary

Gsuite 上の任意のユーザが保有する Google Calendar の内容を、 CalDAV サーバへ複製するプログラム

# Deploy

Cloud functions 上にデプロイし、次のような構成例で定期的に自動実行するバッチジョブとしてセットアップできる

    cron(Cloud Scheduler) -publish-> (Pub/Sub) <-subscribe- this app(Cloud Functions)


* 実行基盤
  * [Python Script on the Cloud Function](https://cloud.google.com/functions/docs/writing/?hl=ja)
* 定時実行機構
  * [Cloud Function](https://cloud.google.com/functions/docs/calling/pubsub?hl=ja)
    * [Pub/Sub を使用して Cloud Function をトリガーする](https://cloud.google.com/scheduler/docs/tut-pub-sub?hl=ja)
      * [Cloud Scheduler で Pub/Sub に定期的にpubする](https://cloud.google.com/scheduler/docs/quickstart?hl=ja)

# Pre-Requires

* `GCP` - `APIとサービス` - `ライブラリ` - `Google Calendar API`: APIを有効にする
* `GCP` - `IAM`: サービスアカウント(SA) を作成し、キーのJSON形式クレデンシャル (credentials.json) を取得する
* `GSuite` - `セキュリティ` - `詳細設定` - `API クライアント アクセスを管理する` - `Calendar API`
    * `クライアントID`: SA の ClientID
    * `スコープ`: https://www.googleapis.com/auth/calendar.events.readonly, https://www.googleapis.com/auth/calendar.readonly
* `GSuite` - `セキュリティ` - `APIリファレンス` - `APIアクセスを有効にする`: ON
* `GSuite` - `セキュリティ` - `APIアクセス` - `カレンダー`: ON
* `CalDAV Server`: [radicale](https://radicale.org/) などを構築しておく

# Environment Variables

次の環境変数を与えて実行する

| Key                         | Value                     | Summary                                                                            |
| :-------------------------- | :------------------------ | :--------------------------------------------------------------------------------- |
| GOOGLE_APP_CREDENTIALS      | credentials.json          | 認証に用いる GCP サービスアカウントの Credential File Path                         |
| GOOGLE_CALENDAR_ID          | person@your_gsuite_domain | 採取対象とするGoogleカレンダーのID, GSuite 上のカレンダーであれば Google ID である |
| GOOGLE_CONTEXT_ID           | robot@your_gsuite_domain  | Calendar API にアクセスするユーザのGoogle ID                                       |
| CALDAV_SERVER_URL           | http://127.0.0.1:5232/    | CalDAV Server のURL                                                      |
| CALDAV_SERVER_USER          | username                  | CalDAV Server のログインID                                                               |
| CALDAV_SERVER_PASS          | Secr3+                    | CalDAV Server のログインパスワード                                                       |
| CALDAV_SERVER_CALENDAR_NAME | some_calendar_name        | CalDAV Server のカレンダー名                                                             |
| APIQUERY_MAX_RESULTS        | 1000                      | Google API から得るレスポンスの最大件数                                            |
| RANGE_OFFSET_MONTHS         | 2                         | 実行時から起算して、前後何ヶ月分のカレンダーデータを採取するか                     |


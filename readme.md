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
| GOOGLE_ENCRYPTED_CRED       | QOTHA....bI=              | KMSで暗号化した GCP サービスアカウントの JSON 鍵, 作成法は後述のSecurityを参照     |
| GOOGLE_PJ                   | gcp-project-x             | Google Project 名                                                                  |
| GOOGLE_KMS_LOC              | global                    | KMSキーリングの場所 (globalなど)                                                   |
| GOOGLE_KMS_KEYRING          | keyring-name              | KMSキーリング名                                                                    |
| GOOGLE_KMS_KEY              | key-name                  | KMSキー名                                                                          |
| GOOGLE_CALENDAR_ID          | person@your_gsuite_domain | 採取対象とするGoogleカレンダーのID, GSuite 上のカレンダーであれば Google ID である |
| GOOGLE_CONTEXT_ID           | robot@your_gsuite_domain  | Calendar API にアクセスするユーザのGoogle ID                                       |
| CALDAV_SERVER_URL           | http://127.0.0.1:5232/    | radicale (CalDAVサーバ) のURL                                                      |
| CALDAV_SERVER_USER          | username                  | radicaleのログインID                                                               |
| CALDAV_SERVER_PASS          | Secr3+                    | radicaleのログインパスワード                                                       |
| CALDAV_SERVER_CALENDAR_NAME | some_calendar_name        | radicaleのカレンダー名                                                             |
| APIQUERY_MAX_RESULTS        | 1000                      | Google API から得るレスポンスの最大件数                                            |
| RANGE_OFFSET_MONTHS         | 2                         | 実行時から起算して、前後何ヶ月分のカレンダーデータを採取するか                     |

# VS Code Debug Setting

settings.json (user)

    {
        // workspace settings.json
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": false,
        "python.linting.flake8Enabled": true,
        "python.envFile": "${workspaceFolder}/.env",
        "python.pythonPath": "~\\.virtualenvs\\${venv}\\Scripts\\python.exe",
        "python.venvPath": "~\\.virtualenvs\\${venv}\\Scripts\\python.exe",
        "python.testing.unittestEnabled": false,
        "python.terminal.activateEnvironment": true,
        "python.testing.autoTestDiscoverOnSaveEnabled": true,
        "python.testing.unittestArgs": [
            "-v",
            "-s",
            "./tests",
            "-p",
            "*test*.py"
        ],
        "python.testing.pytestEnabled": false,
        "python.testing.nosetestsEnabled": false,
        "files.eol": "\n",
        "files.encoding": "utf8",
        "python.testing.promptToConfigure": false
    }

launch.json

    {
        "version": "0.2.0",
        "configurations": [{
            "name": "debug",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}",
            },
            "args": []
        }]
    }

# Dependencies

* [Radicale Specs](https://github.com/Kozea/Radicale/issues/103#issuecomment-34162753)
  * [ics - RFC 5545](https://icspy.readthedocs.io/en/stable/index.html)
  * [CalDAV - RFC 4791](https://pythonhosted.org/caldav/index.html)

# Authentication Mechanisms

**Authorization pre requires**

1. GCP の機能である [Google Calendar API](https://developers.google.com/calendar/v3/reference/calendars) を介して、GSuite 上の各ユーザの Calendar 情報にアクセスできる
2. プログラムは、GSuite からアクセス許可を受けた[GCP上のサービスアカウント](https://qiita.com/tnagao3000/items/3d210582bc7f1ca218cc)で[OAuth2認証](https://developers.google.com/identity/protocols/OAuth2ServiceAccount)されなければならない
3. 更に GSuite 側ではCalendarAPIへのアクセスに関して、対象サービスアカウントに対して[操作範囲（スコープ）](https://developers.google.com/identity/protocols/googlescopes#calendarv3)を[認可](https://support.google.com/a/answer/162106?hl=ja)しなければならない
4. サービスアカウントの OAuth2 認証には、サービスアカウントの JSON 形式 Credencial を利用する

**Library pre requires**

* [Google API Client Library for Python](https://github.com/googleapis/google-api-python-client)
  * [documentation](https://github.com/googleapis/google-api-python-client/blob/master/docs/README.md)
    * [Calendar API v3 Reference](http://googleapis.github.io/google-api-python-client/docs/dyn/calendar_v3.html)


# Security

以下の手続により暗号化済み認証情報を得ることにより、ソースコードにクレデンシャルのような認証情報を含める必要をなくす。
バケットにサービスアカウントの credentials.json を配置し、次のようにKMSを用いて暗号化したクレデンシャルを得る。

    $ gcloud kms keyrings create service-account-credentials --location=global
    $ gcloud kms keys create gcal-api-json-cred \
        --location=global \
        --keyring=service-account-credentials \
        --purpose=encryption
    $ gcloud kms encrypt \
        --plaintext-file=./credentials.json \
        --ciphertext-file=credentials.json.enc \
        --location=global \
        --keyring=service-account-credentials \
        --key=gcal-api-json-cred

暗号化したクレデンシャルはASCII化し、環境変数 `GOOGLE_ENCRYPTED_CRED` の値として実行プログラムに投入する。

    $ python
    > from base64 import b64encode
    > from io import open
    > with open('credentials.json.enc', 'rb') as f:
    >     b64encode(f.read()).decode('ascii')
    >>> QOsAErqw....bI=


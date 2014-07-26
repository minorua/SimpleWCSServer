Simple WCS Server - version beta

This application is a simple WCS (Web Coverage Service) server, which can serve coverages to WCS clients such as QGIS.

GDALがサポートする形式のファイルをWCS配信します。また標高データを国土地理院のサーバ([地理院標高タイル](http://portal.cyberjapan.jp/help/development/demtile.html))から取得してWCS配信することもできます。
対応するWCSバージョンは1.0.0です。QGISで動作確認しています。他のWCSクライアントでは利用できるか確認しておりません。

使い方
------
* 設定ファイル`settings.py`を編集して初期設定をして下さい。初期設定をしなくてもサンプルデータと地理院標高タイルは利用できます。
* OSGeo4W 64bitでQGISをインストールした場合は、`start_simple_server.bat`を実行するだけでサーバが起動します。OSGeo4W 32bitやスタンドアロンインストーラでインストールした場合は予め`start_simple_server.bat`内のパスを変更してから実行して下さい。
* QGISのWCSレイヤの追加ダイアログからWCSコネクションの作成ダイアログを開き、`http://localhost:8000/wcs.py`への接続情報を登録した後、レイヤをマップキャンバスに追加して下さい。

留意点
------
* `settings.py`でレイヤ情報を変更した場合はサーバの再起動が必要です。またQGISにキャッシュされているサーバ情報を削除するためにキャッシュディレクトリも削除して下さい。キャッシュディレクトリの場所はオプションダイアログのネットワークページで知ることができます。
* QGISでGDALのWCSドライバ経由で利用する場合、オプションダイアログの凡例で「ラスタアイコンの作成」のチェックを外すとQGISの動作が著しく遅くなることを避けられます。
* 地理院標高タイルはキャッシュディレクトリ(初期設定では./cache)以下にキャッシュされます。空き容量の十分にあるドライブに置いて利用して下さい。
* 地理院標高タイルを利用する場合は[地理院タイル利用規約](http://portal.cyberjapan.jp/help/termsofuse.html)に従って下さい。

License
-------
MIT License

_Copyright (c) 2014 Minoru Akagi_

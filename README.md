Simple WCS Server
=================
Version beta

This application is a simple WCS ([Web Coverage Service](http://www.opengeospatial.org/standards/wcs)) server, which can serve coverages to WCS clients such as QGIS.

GDALがサポートするファイル形式のラスタデータをWCS配信します。DEMから作成した陰影段彩図や国土地理院のサーバ([地理院標高タイル](http://portal.cyberjapan.jp/help/development/demtile.html))から取得した標高データを配信することもできます。
対応するWCSバージョンは1.0.0です。QGISで動作確認しています。他のWCSクライアントでは利用できるか確認しておりません。

使い方
------
1. 設定ファイル`settings.py`を編集して初期設定をして下さい。初期設定をしなくてもサンプルデータと地理院標高タイルは利用できます。
2. OSGeo4W 64bitでQGISをインストールした場合は、`start_simple_server.bat`を実行するだけでサーバが起動します。OSGeo4W 32bitやスタンドアロンインストーラでインストールした場合は予め`start_simple_server.bat`内のパスを変更してから実行して下さい。
3. QGISのWCSレイヤの追加ダイアログからWCSコネクションの作成ダイアログを開き、`http://localhost:8000/wcs.py`への接続情報を登録します。
4. 接続ボタンを押してカバレッジ一覧を取得し、マップキャンバスに追加するカバレッジを選択します。

* 地理院標高タイルを[Qgis2threejs](https://github.com/minorua/Qgis2threejs)で地形データとして利用するにはGDALの[WCSドライバ](http://www.gdal.org/frmt_wcs.html)経由で読み込む必要があります。`gdal_wcs_xml`ディレクトリの`gsidem.xml`を「ラスタデータの追加」ダイアログで開きます。

留意点
------
* `settings.py`でレイヤ情報を変更した場合はサーバの再起動が必要です。またQGISにキャッシュされているレイヤ情報を削除するためにキャッシュディレクトリも削除して下さい。キャッシュディレクトリの場所はオプションダイアログのネットワークページで知ることができます。
* QGISでGDALのWCSドライバ経由で利用する場合、オプションダイアログの「凡例」タブで「ラスタアイコンの作成」のチェックを外すとQGISの動作が著しく遅くなることを避けられます。
* 地理院標高タイルはキャッシュディレクトリ(初期設定では./cache)以下にキャッシュされます。空き容量の十分にあるドライブに置いて利用して下さい。
* 地理院標高タイルを利用する場合は[国土地理院コンテンツ利用規約](http://portal.cyberjapan.jp/help/termsofuse.html)に従って下さい。

License
-------
MIT License

_Copyright (c) 2014 Minoru Akagi_

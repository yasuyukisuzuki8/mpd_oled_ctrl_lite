# mpd_oled_ctrl_lite
Takazineさんが作成された秋月電子のSO1602AW というI2C-OLEDを使ってMPD(Music Player Daemon)の曲名を表示するpythonスクリプトの、曲名を表示しない軽量版です。

### 導入方法
まず GitHubから mpd_oled_ctrl_lite をダウンロードしてください。

<> Code ▼ → Download ZIP か、またはgitをインストール済の場合は、
```
git clone https://github.com/yasuyukisuzuki8/mpd_oled_ctrl_lite.git
```

上記の git clone の方法では、/home/user名/mpd_oled_ctrl_lite/ 配下に oled_ctrl_s_lite.py がコピーされます。必要に応じてホームディレクトリの /home/pi や /home/volumio などに oled_ctrl_s_lite.py を移動して利用ください。

以降の導入方法はTakazinさんが作成、「りちぇるかあれ」さんがPython3に移植されたオリジナル版と基本的に同じです。

以下のサイトを参照し、

[Volumio/MoodAudioに秋月電子のI2CタイプOLEDを接続して曲名などを表示するPython3版](https://nw-electric.way-nifty.com/blog/2022/03/post-302231.html)

kakasiは使いませんので、「kakasiをインストール」をスキップし、

oled_ctrl_s_20220323.py を oled_ctrl_s_lite.py に読み替えてインストール、実行してください。

上記サイトの「りちぇるかあれ」さんのコメント（投稿: りちぇるかあれ | 2022年4月 7日 (木) 17時17分）にも書いてありますが、現時点で Volumio3 は Python2 が標準になっています。Python3 は python ではなく python3コマンドで動作します。Volumio では Python3 用の smbus モジュールを入手してください。
```
sudo apt update
```
```
sudo apt install -y python3-smbus
```
systemdにサービスを登録する前に、コマンドラインで動作確認すると良いでしょう。smbus モジュールが無ければ、ImportError: No module named smbus というエラーが出ます。
```
python3 ./oled_ctrl_s_lite.py
```

### Takazineさんのオリジナル版との共通点

* ラズパイ起動後にOLEDにMPDのバージョンを表示します。
* STOP, PLAY, PAUSEというMPDの再生ステータスを表示します。
* STOP中はラズパイのIPアドレスを表示します。
* MPDのVolumeレベルを表示します。

### Takazineさんのオリジナル版との相違点

* オリジナル版はPLAY/PAUSE中に曲名、アーティスト名、サンプルレートをOLEDにスクロール表示しますが、この軽量版はサンプルレートしか表示しません。
* オリジナル版はPLAY/PAUSE中に再生経過時間を表示しますが、この軽量版は表示しません。
* オリジナル版は上記情報を表示するために0.25秒ごとにMPDをポーリングしますが、この軽量版はその必要がないのでMPDの再生ステータスやキューなどに変更があるまで停止します。

オリジナル版：
```python3
while True:
    time.sleep(0.25)
    try:
        oled.disp()
```

軽量版：
```python3
while True:
    oled.soc.send(b'idle\n')
    ret = oled.soc.recv(bufsize).decode()
    try:
        oled.disp()
```

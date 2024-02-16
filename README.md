# mpd_oled_ctrl_lite
Takazineさんが作成された秋月電子のSO1602AW というI2C-OLEDを使ってMPD(Music Player Daemon)の曲名を表示するpythonスクリプトの、曲名を表示しない軽量版です。

### 導入方法
まず GitHubから mpd_oled_ctrl_lite をダウンロードしてください。

<> Code ▼ → Download ZIP か、またはgitをインストール済の場合は、
```
$ git clone https://github.com/yasuyukisuzuki8/mpd_oled_ctrl_lite.git
```

以降の導入方法はTakazinさんが作成、「りちぇるかあれ」さんがPython3に移植されたオリジナル版と基本的に同じです。

以下のサイトを参照し、

[Volumio/MoodAudioに秋月電子のI2CタイプOLEDを接続して曲名などを表示するPython3版](https://nw-electric.way-nifty.com/blog/2022/03/post-302231.html)

kakasiは使いませんので、「kakasiをインストール」をスキップし、

oled_ctrl_s_20220323.py を oled_ctrl_s_lite.py に読み替えてインストール、実行してください。

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
first = True # First exec of the while loop
    while True:
        if first == True:
            time.sleep(1)
            oled.disp()
            first = False
        else:
            oled.soc.send(b'idle\n')
            ret = oled.soc.recv(bufsize).decode()
        try:
            oled.disp()
```

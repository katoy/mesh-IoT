# MESH で IoT

Mesh を色々 試していきます。

## 天気予報

<https://support.meshprj.com/hc/ja/articles/212118588-SDK%E3%81%A7%E3%81%AE%E4%BD%9C%E4%BE%8B%E3%82%92%E6%95%99%E3%81%88%E3%81%A6%E3%81%8F%E3%81%A0%E3%81%95%E3%81%84>
 MESH SDKの説明にある "天気予報ブロック" を変更してみました。

### 変更点

- カスタムブロックのイメージ画像
- パラメータを location (名前) -> log, lat (緯度、軽度)

緯度、軽度は google マップで簡単に調べることが可能です。

- <https://pc-chain.com/sns/google-map-get-coordinates/>
- 【Googleマップ】緯度・経度（座標）を表示する

### 使い方

SDK の作成画面で, cusptoms/weather.json  を読み込みます。
その後、code- execute スクリプト中の APPID を open-weather サイトで取得した 値に編集して save します)

(あらかじめ、json 中の APPID を テキストエディタで (open-weather の appid の値に編集してから、読み込んでも良いです)

MESH のレシピ作成画面で、カスタムブロック weather を取り込みます。
weather を編集画面にドラッグして、Mesh のブロックと繋げていきます。

![images/weather.png](images/weather.png)

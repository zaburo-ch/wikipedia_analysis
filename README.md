Wikipedia関連
======================
Wikipediaのデータを扱うようなコードが置いてあります。  


pagerank_wiki.py、pagerank.py
----
Wikipedia内のページに限定してPageRankを計算するプログラムです。
```
python pagerank_wiki.py
```
として実行すると次のような動作をします。
* [http://dumps.wikimedia.org](http://dumps.wikimedia.org)より1日分のデータを取得  
* 国コードがjaのもののうち閲覧数上位10000ページを取り出す  
* 各ページの記事内のリンクをエッジとした有向グラフつくる  
* 有向グラフ内でPageRankを計算し大きい順に出力する  

取り出すページ数やPageRankでのダンピングファクターなどは簡単に変更できます。  
pagerank.pyには遷移確率行列からPageRankを計算する処理が書かれています。  

wikipedia.py
----
Wikipediaに存在する記事のうち最も距離のはなれている記事の組み合わせを探すプログラムです。  
詳しくは[こちら](http://zaburoapp.blog.fc2.com/blog-entry-26.html)

やっていることは次の通りです。
* [http://dumps.wikimedia.org](http://dumps.wikimedia.org)から1時間ごとの閲覧数のデータを1日分取ってくる  
* 国コード(?)がjaの物だけ抽出する  
* 標準ライブラリのCounterで各ページの1日分の閲覧数をカウントする  
* 閲覧数上位10000ページを取り出す  
* 1ページずつ開き記事内の/wiki/で始まるリンクを抽出する  
* リンクがあれば距離1なければINFとして(ディクショナリで)隣接行列をつくる  
* ワーシャルフロイド法で全点間最短距離を求める  
* ソートして表示  
```
python wikipedia.py 20141101
```
のようにして日付指定して使います。  
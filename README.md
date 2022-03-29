# README
## 検索画面について
### json（クライアント->サーバー）
    [
        {
            tag:"B",
            name:"情報工学",
        },
        {
            tag:"B",
            name:"物理学",
        },
        {
            tag:"F",
            name:"情報量",
            parent:"<<parent-name>>",
        },
        {
            tag:"F",
            name:"エントロピー",
            parent:"<<parent-name>>",
        },
        {
            tag:"F",
            name:"弾性",
            parent:"<<parent-name>>",
        },
    ]
### json(サーバー->クライアント)
```
{
    "urls": [
        {
            "id": "<<url id>>",
            "url": "http~~",
            "tiltle": "わんわん"
        },
        {
            "id": "<<url id>>",
            "url": "http~~",
            "tiltle": "わんわん2"
        },
        {
            "id": "<<url id>>",
            "url": "http~~",
            "tiltle": "わんわん3"
        }
    ],
    "finetags": [
        {
            "parent": "aa",
            "childlen": [
                "わー",
                "わんわん"
            ]
        },
        {
            "parent": "bb",
            "childlen": [
                "わー",
                "わんわん"
            ]
        }
    ]
}
```
### JavaScriptのフロー
データ送受信について  
1. Trueになっている要素をB/F種類ごとに集める  
1. 送信する
1. 返信される
1. urlの属性設定
1. FineTagの属性設定

見栄えについて  
1. 返信されてから
1. URLの羅列
1. FineTagの表示  
---  
## 登録画面について  
URLを入力  
URLじゃなかった  
    自動  
URLとregisterがすでに有る  
    スパム認定  
URLが登録され、registerがない  
    regiterに登録  
URLもregisterもない  
    URLに登録  
    registerに登録  

---
## 評価ページ(detail)
### 現状データとタグの編集
保存ボタンを押してから初めて実行されるようにする
JavaScript側で  
- 削除データ  
- 追加データ  

を仕分けてから送る
```
Btagのボタンを押したとき->消す作業はフロント
受信
{
    "name":"あいう",
}
送信
{
    ["marumaru","sankaku"]
}
```
```
送信ボタン
{
    "del":[
        {
            "tag":"B",
            "name":"あいう"
        },
        {
            "tag":"B",
            "name":"かきく"
        },
        {
            "tag":"F",
            "name":"えお",
            "parent":"あいう"
        },
        {
            "tag":"F",
            "name":"aiu",
            "parent":"あいう"
        }
    ],
    "add":[
        {
            "tag":"B",
            "name":"さしす"
        },
        {
            "tag":"F",
            "name":"seso",
            "parent":"さしす"
        }
    ]
}
```

---# OurBookMark

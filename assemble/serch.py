from .models import URL,URL_BigTag,URL_FineTag,BigTag,FineTag
from django.db import connection

def selecter(tag_data):
    """ タグの存在する種類に合わせて変数値を変更 """
    """
    0 ... タグなし
    1 ... F,B がある
    2 ... Bだけがある
    3 ... Fだけがある
    """
    _PATTRERN = 0
    reqBs = []
    reqFs = []
    if len(tag_data) == 0:
        _PATTRERN = 0
    else:
        for tag in tag_data:
            if(tag["tag"] == "B"):
                reqBs.append(tag["name"])
            elif(tag["tag"] == "F"):
                vartpl = (tag["name"],tag["parent"])
                reqFs.append(vartpl)
                
        if len(reqBs)>0 and len(reqFs)>0:
            _PATTRERN = 1
        elif len(reqFs)==0:
            _PATTRERN = 2
        elif len(reqBs)==0:
            _PATTRERN = 3
    
    dict = {
        'PATTERN':_PATTRERN,
        'reqBs':reqBs,
        'reqFs':reqFs,
    }
    print(dict)

    return dict

def urlSerch(selecter,reqBs,reqFs):
    """
    selecterはint型
    reqBsは文字列のリスト型
    reqFsは文字列のタプル型 タグ名,親 の組み合わせ
    例)
    reqBs = ["情報工学","熱力学",]
    reqFs = [("エントロピー","<<bigtag_name>>"),
            ("デクリメント","<<bigtag_name>>")]
    """
    urls = []
    esconv = EscConvert()
    cursor = connection.cursor()
    if selecter == 0:
        urlOs = list(URL.objects.all()[:30].values())
        for url in urlOs:
            urls.append({
                'id':url["id"],
                'url':url["url"],
                'title':url["title"],
            })
    elif selecter == 1:
        """ 
        reqFs タプルリスト[0]がタグ名,[1]が親タグ名
        reqBs 文字列リスト
        """
        reqFs_set = set()
        reqBs_set = set()
        reqFs_list = list(set(reqFs))
        for reqf in reqFs_list:
            reqfz_ped = esconv.convert(reqf[0])
            reqfo_ped = esconv.convert(reqf[1])
            reqFs_set.add((reqfz_ped,reqfo_ped))
        for reqb in reqBs:
            reqb_ped = esconv.convert(reqb)
            reqBs_set.add(reqb_ped)
        # Bタグ検索テーブルのwhere句
        whereque = whereMake(reqBs_set,"bigtag")
        paralenB = whereque["len"]
        whstrB = whereque["where"]
        # Fタグ検索テーブルのwhere句
        paralenF=len(reqFs_set)
        whstrF="where"
        for reqf in reqFs_set:
            whstrF = whstrF+f'(assemble_finetag.tag="{reqf[0]}" AND assemble_bigtag.tag="{reqf[1]}") OR '
        whstrF = whstrF[:-3]
        com = f'''
        select urlbyf.* from 
        (
        select assemble_url.*
        from assemble_url 
        join assemble_url_finetag 
        on assemble_url_finetag.url_id = assemble_url.id  
        join assemble_finetag 
        on assemble_url_finetag.tag_id = assemble_finetag.id 
        join assemble_bigtag
        on assemble_finetag.parent_id = assemble_bigtag.id
        {whstrF}
        group by assemble_url.id 
        having count(assemble_url.id)>={paralenF}
        ) as urlbyf
        join 
        (
        select assemble_url.*
        from assemble_url
        join assemble_url_bigtag
        on assemble_url_bigtag.url_id = assemble_url.id
        join assemble_bigtag 
        on assemble_url_bigtag.tag_id = assemble_bigtag.id
        {whstrB}
        group by assemble_url.id
        having count(assemble_url.id)>={paralenB}
        ) as urlbyb
        on urlbyf.id = urlbyb.id
        '''
        print(com)
        cursor.execute(com)
        rows = cursor.fetchall()
        for row in rows:
            urls.append({
                'id':row[0],
                'url':row[1],
                'title':row[2],
            })
    elif selecter == 2:
        reqBs_set = set()
        for reqb in reqBs:
            reqb_ped = esconv.convert(reqb)
            reqBs_set.add(reqb_ped)
        whereque = whereMake(reqBs_set,"bigtag")
        paralen = whereque["len"]
        whstr = whereque["where"]

        com = f'''
        select assemble_url.*
        from assemble_url 
        join assemble_url_bigtag 
        on assemble_url.id = assemble_url_bigtag.url_id 
        join assemble_bigtag 
        on assemble_url_bigtag.tag_id = assemble_bigtag.id 
        {whstr} 
        group by assemble_url.id 
        having count(assemble_url.id)>={paralen}
        '''
        print(com)
        cursor.execute(com)
        rows = cursor.fetchall()
        for row in rows:
            urls.append({
                'id':row[0],
                'url':row[1],
                'title':row[2],
            })
    elif selecter == 3:
        """
        Ftagについてくるデータはtag文字列データとparent_idデータ
        つまりBtagが存在しないことがない
        でもGETパラメーターのときはこれ通るな。
        reqFs = ["~~","~~",]
        """
        reqFs_set = set()
        for reqf in reqFs:#重複を消す
            reqf_ped = esconv.convert(reqf)
            reqFs_set.add(reqf_ped)
        
        whereque = whereMake(reqFs_set,"finetag")
        paralen = whereque["len"]
        whstr = whereque["where"]

        com = f'''
        select assemble_url.*
        from assemble_url 
        join assemble_url_finetag 
        on assemble_url.id = assemble_url_finetag.url_id 
        join assemble_finetag 
        on assemble_url_finetag.tag_id = assemble_finetag.id 
        {whstr} 
        group by assemble_url.id 
        having count(assemble_url.id)>={paralen}
        '''
        cursor.execute(com)
        rows = cursor.fetchall()
        for row in rows:
            urls.append({
                'id':row[0],
                'url':row[1],
                'title':row[2],
            })

    return urls

def finetagSerch(reqBs):
    esconv = EscConvert()
    cursor = connection.cursor()
    reqBs_set = set()
    for reqb in reqBs:
        reqb_ped = esconv.convert(reqb)
        reqBs_set.add(reqb_ped)
    whstr = "("
    for req in reqBs_set:
        whstr = whstr + f'"{req}",'
    whstr = whstr[:-1] + ")"

    com = f'''
    select 
    assemble_finetag.tag,assemble_bigtag.tag 
    from assemble_finetag 
    join assemble_bigtag 
    on assemble_finetag.parent_id = assemble_bigtag.id 
    where assemble_bigtag.tag in {whstr}
    '''
    #print(com)
    cursor.execute(com)
    rows = cursor.fetchall()
    finetags = []
    childlen=[]
    for req in reqBs_set:
        childlen.clear()
        for row in rows:
            if(row[1] == req):
                childlen.append(row[0])
            else :
                pass
        finetags.append({
            "parent":req,
            "childlen":childlen.copy(),
        })
    return finetags

def finetagSend(reqBs,sendF):
    esconv = EscConvert()
    cursor = connection.cursor()
    reqBs_set = set()
    for reqb in reqBs:
        reqb_ped = esconv.convert(reqb)
        reqBs_set.add(reqb_ped)
    whstr = "("
    for req in reqBs_set:
        whstr = whstr + f'"{req}",'
    whstr = whstr[:-1] + ")"

    com = f'''
    select 
    assemble_finetag.tag,assemble_bigtag.tag 
    from assemble_finetag 
    join assemble_bigtag 
    on assemble_finetag.parent_id = assemble_bigtag.id 
    where assemble_bigtag.tag in {whstr}
    '''
    #print(com)
    cursor.execute(com)
    rows = cursor.fetchall()
    finetags = []
    childlen=[]
    for req in reqBs_set:
        childlen.clear()
        for row in rows:
            if(row[1] == req):
                if {"tag":row[0],"parent":req} in sendF:
                    pushed = True
                else:
                    pushed = False
                childlen.append((
                    row[0],
                    pushed
                    ))
            else :
                pass
        finetags.append({
            "parent":req,
            "childlen":childlen.copy(),
        })
    return finetags

class EscConvert():
    escs = {
        "'":"シングルクォーテーション",
        "`":"バッククオート",
        '"':"ダブルクオーテーション",
        '-':"ハイフン",
        '~':"チルダ",
        '|':"パイプ",
        "\\":"バックスラッシュ",
        ";":"セミコロン",
        ":":"コロン",
        "^":"キャレット",
    }
    def convert(self,src):
        dst = src
        for key,value in self.escs.items():
            dst = dst.replace(key,value)
        return dst

def whereMake(reqSet,tagkind):
    """
    set型入れる
    """
    # where句作成
    paralen = len(reqSet)
    whstr = f"where assemble_{tagkind}.tag in("
    for req in reqSet:
        whstr = whstr+f'"{req}",'
    whstr = whstr[:-1]+")"
    # ここまで

    info = {
        "len":paralen,
        "where":whstr,
    }
    return info
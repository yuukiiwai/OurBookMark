from distutils.debug import DEBUG
import re
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from requests.api import request
from .models import URL,Regist,BigTag, URL_BigTag,FineTag, URL_FineTag
from .forms import URLForm
from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup
import requests
import mechanize
import uuid as uuid_lib
from users.models import User
from django.db.models import Q
from django.http import JsonResponse
import json
from .serch import selecter as ser_sel,urlSerch,finetagSerch,EscConvert,finetagSend
from .regist import selecter as reg_sel

# Create your views here.

def top(request):
    urls = URL.objects.all()[:30]
    bigTags = BigTag.objects.all()
    context = {
        'urls':urls,
        'bigTags':bigTags,
    }
    return render(request,'assemble/top.html',context)

@login_required
def register(request):
    if request.method =="POST":
        form = URLForm(request.POST)
        if form.is_valid:
            #
            if DEBUG:
                insuserid = str(request.user.id).replace('-','')
            else :
                insuserid = str(request.user.id)
            sel = reg_sel(request.POST['url'],insuserid)
            print("sel")
            print(sel)
            if sel == 0:
                form = URLForm()
                context = {
                    'form':form,
                    'pushErr':True
                }
                return render(request,'assemble/register.html',context)
            else:
                try:
                    title = BeautifulSoup(requests.get(request.POST['url']).content,"html.parser").find("title").text
                except AttributeError:
                    browser = mechanize.Browser()
                    browser.open(request.POST['url'])
                    title = browser.title()
                newurl = URL.objects.get_or_create(url = request.POST['url'],title=title)[0]
                regist = Regist.objects.get_or_create(
                    registered_by = request.user,
                    url = newurl
                )
                return redirect('assemble:detail',url_id = newurl.id)
            #
    
    form = URLForm()
    context = {
        'form':form,
        'pushErr':False
    }
    return render(request,'assemble/register.html',context)

def detail(request,url_id):
    bigTags = BigTag.objects.all()
    """ 
    つながっているBigTag,FineTag,Registを収集
    joinさせて取ってくるとB有りF無しが取れなかったりするから今は無理。理解が足りない
    OR parent = b.id でbigtagをjoinするとfがnullのときBが出ない
    AND parent = b.id でbigtagをjoinするとFと関係の無いBが同じ列に居る
    
    url -> url_bigtag -> bigtag
    url -> url_finetag -> finetag
    url -> regist
    """
    cursor = connection.cursor()
    url = get_object_or_404(URL,id=url_id)
    if DEBUG:
        url_id_str = str(url_id).replace("-","")
    else:
        url_id_str = str(url_id)
    bcom = f'''
    select assemble_bigtag.tag 
    from assemble_url 
    join assemble_url_bigtag 
    on assemble_url.id = assemble_url_bigtag.url_id 
    join assemble_bigtag 
    on assemble_url_bigtag.tag_id = assemble_bigtag.id 
    where assemble_url.id = '{url_id_str}'
    order by assemble_bigtag.tag
    '''
    fcom = f'''
    select assemble_finetag.tag ,assemble_bigtag.tag
    from assemble_url 
    join assemble_url_finetag 
    on assemble_url.id = assemble_url_finetag.url_id 
    join assemble_finetag 
    on assemble_url_finetag.tag_id = assemble_finetag.id 
    join assemble_bigtag 
    on assemble_finetag.parent_id = assemble_bigtag.id
    where assemble_url.id = '{url_id_str}'
    order by assemble_bigtag.tag
    '''
    rcom = f'''
    select users_user.username,users_user.id 
    from users_user 
    join assemble_regist 
    on assemble_regist.registered_by_id = users_user.id 
    where assemble_regist.url_id = '{url_id_str}'
    '''
    print(bcom)
    print(fcom)
    print(rcom)
    btag = []
    ftag = []
    registers = []
    registersid = []
    cursor.execute(bcom)
    rows = cursor.fetchall()
    for row in rows:
        btag.append(row[0])
    cursor.execute(fcom)
    rows = cursor.fetchall()
    for row in rows:
        ftag.append({
            "tag":row[0],
            "parent":row[1]
            })
    cursor.execute(rcom)
    rows = cursor.fetchall()
    for row in rows:
        registers.append(row[0])
        registersid.append(str(row[1]))
    
    administer = False
    if DEBUG:
        compare = str(request.user.id).replace("-","")
    else :
        compare = str(request.user.id)
    print(registersid)
    print(compare)
    if compare in registersid:
        administer = True
    if administer == True:
        fineTags = finetagSend(btag,ftag)

    context = {
        #全ユーザー向け
        'url':url,
        'registers':registers,
        'btag':btag,
        'ftag':ftag,
    }
    if administer:
        context |= {
            #投稿者向け
            'admin':administer,
            'bigTags':bigTags,
            'fineTags':fineTags,
        }
    print(context)
    return render(request,'assemble/detail.html',context)

def serch(request):
    bigTags = BigTag.objects.all()
    furl = URL.objects.all()[:1][0]
    urls = URL.objects.all()[1:30]
    idstr = str(request.user.id).replace('-','')
    print(idstr)
    context = {
        'bigTags':bigTags,
        'furl':furl,
        'urls':urls,
    }
    return render(request,"assemble/serch.html",context)

def serchprocess(request):
    if request.method == "POST":
        urls = []
        finetags = []
        reqdic = json.loads(request.body.decode())
        
        conv_data = ser_sel(reqdic)
        sel = conv_data["PATTERN"]
        reqBs = conv_data["reqBs"]
        reqFs = conv_data["reqFs"]

        urls = urlSerch(selecter=sel,reqBs=reqBs,reqFs=reqFs)
        print(urls)
        if len(reqBs) != 0: 
            finetags = finetagSerch(reqBs=reqBs)
        context = {
            'urls':urls,
            'finetags':finetags,
        }
        print(context)
        return JsonResponse(context)
    else :
        pass

def tagD(request):
    if request.method == "POST":
        finetags = []
        reqB = json.loads(request.body.decode())
        # print(reqB)
        conv = EscConvert()
        reqBp=conv.convert(reqB)
        com = f'''
        select 
        assemble_finetag.tag 
        from assemble_finetag 
        join assemble_bigtag 
        on assemble_finetag.parent_id = assemble_bigtag.id 
        where assemble_bigtag.tag = '{reqBp}'
        order by assemble_bigtag.tag
        '''
        cursor = connection.cursor()
        cursor.execute(com)
        rows = cursor.fetchall()
        for row in rows:
            finetags.append(row[0])
        context = {
            "finetags":finetags
        }
        return JsonResponse(context)

def tagSaveApi(request):
    if request.method == "POST":
        cursor = connection.cursor()
        difData = json.loads(request.body.decode())
        urlid = difData["id"]
        addB = difData["add"]["B"]
        addF = difData["add"]["F"]
        delB = difData["del"]["B"]
        delF = difData["del"]["F"]
        # add bigtag relation
        for aB in addB:
            com = f'''
            select id from assemble_bigtag where tag = "{aB}"
            '''
            cursor.execute(com)
            bid = cursor.fetchone()[0]
            URL_BigTag.objects.create(tag_id = bid,url_id = urlid)
        
        # delete bigtag relation
        for aB in delB:
            com = f'''
            select id from assemble_bigtag where tag = "{aB}"
            '''
            cursor.execute(com)
            bid = cursor.fetchone()[0]
            delrec = URL_BigTag.objects.get(tag_id=bid,url_id = urlid)
            delrec.delete()
        
        # add finetag relation
        for aF in addF:
            com = f'''
            select assemble_finetag.id from assemble_finetag
            join assemble_bigtag
            on assemble_finetag.parent_id = assemble_bigtag.id
            where assemble_finetag.tag = "{aF['tagname']}" AND assemble_bigtag.tag = "{aF['parent']}" 
            '''
            cursor.execute(com)
            fid = cursor.fetchone()[0]
            URL_FineTag.objects.create(tag_id = fid,url_id = urlid)

        # delete finetag relation
        for aF in delF:
            com = f'''
            select assemble_finetag.id from assemble_finetag
            join assemble_bigtag
            on assemble_finetag.parent_id = assemble_bigtag.id
            where assemble_finetag.tag = "{aF['tagname']}" AND assemble_bigtag.tag = "{aF['parent']}" 
            '''
            cursor.execute(com)
            fid = cursor.fetchone()[0]
            delrec = URL_FineTag.objects.get(tag_id = fid,url_id = urlid)
            delrec.delete()

        context = {
            "hello":"HELLO"
        }
        return JsonResponse(context)
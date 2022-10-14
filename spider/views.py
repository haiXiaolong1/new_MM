from django.shortcuts import render
import random
import re
import requests
from lxml import etree
from urllib import parse
from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from supply import models
# Create your views here.
import json
import datetime
import time
import pymysql
import numpy as np
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

def get_source(name):
    url="http://www.weather.com.cn/"#天气网地址
    opt=Options()#设置无头浏览器配置
    opt.add_argument('--window-size=1920,1080')
    opt.add_argument("--headless")
    opt.add_argument("--disable-gpu")
    web=Chrome(options=opt)
    for i in range(10):#自省，当请求失败时再次发出请求，循环十次如果仍未有正确结果则退出
        try:
            web.get(url)
            time.sleep(1)
            web.find_element(By.XPATH,'//*[@id="txtZip"]').send_keys(name)
            time.sleep(1.5)
            web.find_element(By.XPATH,'//*[@id="txtZip"]').send_keys(Keys.ENTER)
            web.switch_to.window(web.window_handles[-1])
            time.sleep(1)
            websource=web.page_source#获取当天情况的源码
            web.find_element(By.XPATH,'//*[@id="someDayNav"]/li[2]').click()#获取7天天气的源码
            time.sleep(1)
            return [websource,web.page_source]
        except:
            print('本次请求获取源码失败，请等待...')
def get_1_detail(source):
    mainPage=BeautifulSoup(source,'html.parser')
    detail_div=mainPage.find('div',class_='t')
    lief=mainPage.find('div',class_='livezs')
    nowdata=[]
    liefdata=[]
    now_date=detail_div.find('p').text
    nowdata.append(now_date)
    humidity=detail_div.find('div',class_='h').find('em').text
    nowdata.append(humidity)
    now_temp=detail_div.find('div',class_='tem').find('span').text
    nowdata.append(now_temp)
    now_wind=detail_div.find('div',class_='w').find('span').text
    nowdata.append(now_wind)
    now_wind_level=detail_div.find('div',class_='w').find('em').text
    nowdata.append(now_wind_level)
    now_air=detail_div.find('div',class_='pol').find('span').text
    nowdata.append(now_air)

    influ=lief.find_all('li')[0].find('span').text
    liefdata.append(influ)
    influ_suggest=lief.find_all('li')[0].find('p').text
    liefdata.append(influ_suggest)
    sport=lief.find_all('li')[1].find('span').text
    liefdata.append(sport)
    sport_suggest=lief.find_all('li')[1].find('p').text
    liefdata.append(sport_suggest)
    allergy='暂无数据'
    if lief.find_all('li')[2].find('span'):
        allergy=lief.find_all('li')[2].find('span').text
    liefdata.append(allergy)
    allergy_suggest=lief.find_all('li')[2].find('p').text
    liefdata.append(allergy_suggest)
    cloth=lief.find_all('li')[3].find('span').text
    liefdata.append(cloth)
    cloth_suggest=lief.find_all('li')[3].find('p').text
    liefdata.append(cloth_suggest)
    car=lief.find_all('li')[4].find('span').text
    liefdata.append(car)
    car_suggest=lief.find_all('li')[4].find('p').text
    liefdata.append(car_suggest)
    ray=lief.find_all('li')[5].find('span').text
    liefdata.append(ray)
    ray_suggest=lief.find_all('li')[5].find('p').text
    liefdata.append(ray_suggest)
    return [nowdata,liefdata]
def get_7_weather(name,source):
    mainPage=BeautifulSoup(source,'html.parser')
    alist=mainPage.find("div",id='7d').find('ul').find_all('li')
    temp=mainPage.find('div',id='weatherChart').find('div',class_='split').find('p',class_='tem').text
    temp=temp.split(',')[0][5:].strip().strip('℃')

    datelist=[]
    min=[]
    max=[]
    weatherlist=[]
    for li in alist:
        date=datetime.date.today().__str__()[:-2]+li.find('h1').text[:-1]
        weather=li.find('p').text
        max_temp=temp
        if li.find('span').text:
            max_temp=li.find('span').text.strip('℃')
        min_temp=li.find('i').text.strip('℃')

        datetime.datetime.strptime(date[:-4],"%Y-%m-%d")
        datelist.append(str(datetime.datetime.strptime(date[:-4],"%Y-%m-%d"))[:-8])
        # datelist.append(int(date[8:-4]))
        weatherlist.append(weather)
        min.append(float(min_temp))
        max.append(float(max_temp))
    return [datelist,weatherlist,max,min]

def getResultByName(name):
    url=f"https://so.biqusoso.com/s.php?ie=utf-8&siteid=qu-la.com&q={name}"
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34"
        ,"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Cookie": "BIDUPSID=411397ADCA5FA50A2E41AB2A6D40C08D; PSTM=1644477760; BD_UPN=12314753; __yjs_duid=1_76cb500678e0fad7f03158136645e2641644737380783; BAIDUID=3E36D1A4894DF97FCE7A1491E4480FB1:FG=1; BDUSS=GltV0FWVkRVUlpmUmZTdkJ2ZUFsRU5hTGk5cE1FZllNUDJlZkZVS1BuUy1HdVppSVFBQUFBJCQAAAAAAAAAAAEAAABU70SkMTIyysfO0jczAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL6NvmK-jb5iS; BDUSS_BFESS=GltV0FWVkRVUlpmUmZTdkJ2ZUFsRU5hTGk5cE1FZllNUDJlZkZVS1BuUy1HdVppSVFBQUFBJCQAAAAAAAAAAAEAAABU70SkMTIyysfO0jczAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL6NvmK-jb5iS; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; BD_CK_SAM=1; PSINO=1; BAIDUID_BFESS=3E36D1A4894DF97FCE7A1491E4480FB1:FG=1; ZD_ENTRY=baidu; RT=\"z=1&dm=baidu.com&si=069naiho9oif&ss=l8y2i71l&sl=4&tt=1bt&bcn=https://fclog.baidu.com/log/weirwood?type=perf&ld=8yt&ul=cpj&hd=cq4\"; BA_HECTOR=0h2k252l0501208h2g0580ip1hjvgat1a; ZFY=1XzLj93E1kpXAhM4o8EUDdn9AOKxd44U5VVIzgsTFoI:C; H_PS_PSSID=36553_37356_36884_34813_37402_37395_36789_37422_26350_37284_37370_37468; baikeVisitId=affeb5e8-219a-4516-826e-0de9cd824380; COOKIE_SESSION=30_0_9_9_9_7_1_0_9_7_1_0_2943_0_0_0_1664959705_0_1664971057|9#1495_123_1664439634|9; BDRCVFR[S4-dAuiWMmn]=FZ_Jfs2436CUAqWmykCULPYrWm1n1fz; H_PS_645EC=fb17pzl/2XwZhS0n9FDV1F/CCfmCwgk98+A/SjJhkCq1c9noJ/9N//Q4IQ8vLo2yVw",

        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
    }
    res=requests.get(url=url,headers=headers)
    res.encoding='utf-8'
    obj=re.compile(r'"><a href="(?P<href>.*?)".*?">(?P<title>.*?)</a>.*?<span class="s4">(?P<author>.*?)</span>',re.S)
    result=obj.finditer(res.text)
    titles=[]
    hrefs=[]
    authors=[]
    lists=[]
    for i in result:
        titles.append(i.group('title'))
        hrefs.append(i.group('href'))
        authors.append(i.group('author'))
        d={}
        d['title']=i.group('title')
        d['href']=i.group('href')
        d['author']=i.group('author')
        lists.append(d)
    return lists

def getSourceByHref(href):
    headers={
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "max-age=0",
        "cookie": "Hm_lvt_4238f39670ba0f28c33f896ff335e60a=1665575408; Hm_lpvt_4238f39670ba0f28c33f896ff335e60a=1665576883",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42"
    }
    res=requests.get(url=href,headers=headers)
    res.encoding='gbk'
    tree=etree.HTML(res.text)
    lis=tree.xpath('//*[@id="list"]/div[3]/ul[2]/li')
    chapters=[]
    urls=[]
    lists=[]
    for li in lis:

        d={}
        d['url']=parse.urljoin(href,li.xpath('./a/@href')[0])
        d['chapter']=li.xpath('./a/text()')[0]
        urls.append(parse.urljoin(href,li.xpath('./a/@href')[0]))
        chapters.append(li.xpath('./a/text()')[0])
        lists.append(d)
    return urls,chapters,lists
def getTxtByUrl(url):
    headers={
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "max-age=0",
        "cookie": "Hm_lvt_4238f39670ba0f28c33f896ff335e60a=1665575408; Hm_lpvt_4238f39670ba0f28c33f896ff335e60a=1665576883",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42"
    }
    res=requests.get(url=url,headers=headers)
    res.encoding='gbk'
    tree=etree.HTML(res.text)
    text=tree.xpath('//*[@id="txt"]/text()')
    return text


def get_weather(request):
    name=request.GET.get('name','')
    result={}
    if name:
        source=get_source(name)
        nowdata,liefdata=get_1_detail(source[0])
        sevendata=get_7_weather(name,source[1])
        result['datelist']=sevendata[0]
        result['weather']=sevendata[1]
        result['max']=sevendata[2]
        result['min']=sevendata[3]
        result['name']=name
        result['nowdata']=nowdata
        result['life']=liefdata
    # print(sevendata)
    return render(request,'searchweather.html',result)


def get_fiction(request):
    name=request.GET.get('name','')
    lists=[]

    if name:
        lists=getResultByName(name)

    return render(request,'fiction.html',{"lists":lists,"name":name})


def get_chapters(request):
    href=request.GET.get('href')
    title=request.GET.get('title')
    urls,chapters,lists=getSourceByHref(href)
    request.session['urls']=urls
    request.session['chapters']=chapters
    return render(request,'chapters.html',{"lists":lists,"title":title})


def get_chapter(request):
    url=request.GET.get('url')
    title=request.GET.get('title')
    index=request.session['urls'].index(url)
    next=''
    previous=''
    if index<len(request.session['urls'])-1:
        next=f'chapter?url={request.session["urls"][index+1]}&title={request.session["chapters"][index+1]}'
    if index>0:
        previous=f'chapter?url={request.session["urls"][index-1]}&title={request.session["chapters"][index-1]}'
    txt=getTxtByUrl(url)
    return render(request,'chapter.html',{"txt":txt,"title":title,"previous":previous,"next":next})


def get_picture(request):
    url=request.GET.get('url',"https://www.umei.cc/katongdongman/")
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34"
        ,"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Cookie": "BIDUPSID=411397ADCA5FA50A2E41AB2A6D40C08D; PSTM=1644477760; BD_UPN=12314753; __yjs_duid=1_76cb500678e0fad7f03158136645e2641644737380783; BAIDUID=3E36D1A4894DF97FCE7A1491E4480FB1:FG=1; BDUSS=GltV0FWVkRVUlpmUmZTdkJ2ZUFsRU5hTGk5cE1FZllNUDJlZkZVS1BuUy1HdVppSVFBQUFBJCQAAAAAAAAAAAEAAABU70SkMTIyysfO0jczAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL6NvmK-jb5iS; BDUSS_BFESS=GltV0FWVkRVUlpmUmZTdkJ2ZUFsRU5hTGk5cE1FZllNUDJlZkZVS1BuUy1HdVppSVFBQUFBJCQAAAAAAAAAAAEAAABU70SkMTIyysfO0jczAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL6NvmK-jb5iS; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; BD_CK_SAM=1; PSINO=1; BAIDUID_BFESS=3E36D1A4894DF97FCE7A1491E4480FB1:FG=1; ZD_ENTRY=baidu; RT=\"z=1&dm=baidu.com&si=069naiho9oif&ss=l8y2i71l&sl=4&tt=1bt&bcn=https://fclog.baidu.com/log/weirwood?type=perf&ld=8yt&ul=cpj&hd=cq4\"; BA_HECTOR=0h2k252l0501208h2g0580ip1hjvgat1a; ZFY=1XzLj93E1kpXAhM4o8EUDdn9AOKxd44U5VVIzgsTFoI:C; H_PS_PSSID=36553_37356_36884_34813_37402_37395_36789_37422_26350_37284_37370_37468; baikeVisitId=affeb5e8-219a-4516-826e-0de9cd824380; COOKIE_SESSION=30_0_9_9_9_7_1_0_9_7_1_0_2943_0_0_0_1664959705_0_1664971057|9#1495_123_1664439634|9; BDRCVFR[S4-dAuiWMmn]=FZ_Jfs2436CUAqWmykCULPYrWm1n1fz; H_PS_645EC=fb17pzl/2XwZhS0n9FDV1F/CCfmCwgk98+A/SjJhkCq1c9noJ/9N//Q4IQ8vLo2yVw",

        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
    }
    res=requests.get(url=url,headers=headers)
    res.encoding='utf-8'
    mainPage=BeautifulSoup(res.text,'html.parser')
    divs=mainPage.find_all('div',class_='taotu-main')
    themes=mainPage.find_all('div',class_='taotu-nav')
    result=[]
    obj=re.compile('<li>.*?href="(?P<url>.*?)".*?title="(?P<name>.*?)".*?data-original="(?P<src>.*?)"',re.S)

    for i in range(len(divs)):
        title=themes[i].find('span').text
        more=parse.urljoin('https://www.umei.cc/meinvtupian/',themes[i].find('a').attrs['href'])
        its=obj.finditer(str(divs[i]))
        theme=[]
        for it in its:
            d={}
            name=it.group('name')
            src=it.group('src')
            u=parse.urljoin(url,it.group('url'))
            d['name']=name
            d['src']=src
            d['title']=title.strip()
            d['more']=more
            d['url']=u
            theme.append(d)
        result.append(theme)

    return render(request,'picture.html',{"themes":result})


def get_bigImage(request):
    url=request.GET.get('url')
    name=request.GET.get('name')
    title=request.GET.get('title')
    res=requests.get(url)
    res.encoding='utf-8'
    tree=etree.HTML(res.text)
    obj=re.compile('"big-pic">.*?src="(?P<src>.*?)"',re.S)
    src=[]
    src.append(obj.search(res.text).group('src'))
    # src=tree.xpath('/html/body/div[3]/div[2]/div[6]/a/img/@src')[0]
    divs=tree.xpath('/html/body/div[3]/div[2]/div[9]/ul')
    if divs:
        lis=tree.xpath('/html/body/div[3]/div[2]/div[9]/ul/li')
    for i in range(len(lis)-3):
        u="htt"+url.strip(".htm")+"_"+str(i+2)+".htm"
        print(u)
        res=requests.get(u)
        res.encoding='utf-8'
        src.append(obj.search(res.text).group('src'))
    return render(request,'bigImage.html',{"src":src,"name":name,"title":title})


def get_more(request):
    url=request.GET.get('url')
    res=requests.get(url)
    res.encoding='utf-8'
    tree=etree.HTML(res.text)
    previous=''
    next=''
    end=''
    count=0
    alla=tree.xpath('//*[@id="pageNum"]/a')
    if len(alla)>3:
        previous=parse.urljoin(url,tree.xpath('//*[@id="pageNum"]/a[2]/@href')[0])
        next=parse.urljoin(url,tree.xpath('//*[@id="pageNum"]/a[4]/@href')[0])
        end=parse.urljoin(url,tree.xpath('//*[@id="pageNum"]/a[last()]/@href')[0])
    else:
        if "首页"==tree.xpath('//*[@id="pageNum"]/a[1]/text()')[0]:
            previous=parse.urljoin(url,tree.xpath('//*[@id="pageNum"]/a[2]/@href')[0])
            next=''
            end=''
        else:
            next=parse.urljoin(url,tree.xpath('//*[@id="pageNum"]/a[2]/@href')[0])
            previous=''
            end=parse.urljoin(url,tree.xpath('//*[@id="pageNum"]/a[last()]/@href')[0])
    title=tree.xpath('/html/body/div[5]/div[2]/div[1]/div[1]/span/text()')[0].strip()[:-3]
    print(title,next,previous,end)
    obj=re.compile('"item masonry_brick">.*?href="(?P<href>.*?)".*?data-original="(?P<src>.*?)".*?alt="(?P<name>.*?)"',re.S)
    its=obj.finditer(res.text)
    # print(res.text)
    th=[]
    for it in its:
        d={}
        d['href']=parse.urljoin(url,it.group('href'))
        d['src']=parse.urljoin(url,it.group('src'))
        d['name']=it.group('name')
        th.append(d)
    print(th)
    return render(request,'more.html',{"title":title,"th":th,"previous":previous,"next":next})

def getImageByname(name):
    url='https://cn.bing.com/images/search'
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34"
    }
    para={
        "q": name,
        "qs": "n",
        "form": "QBIR",
        "qft":  "filterui:imagesize-large",
        "sp": "-1",
        "pq": name,
        "sc": "10-4",
        "cvid": "6E8ADA353A0343609BBF188B663E90C2",
        "ghsh": "0",
        "ghacc": "0",
        "first": "1",
        "tsc": "ImageHoverTitle"
    }
    res=requests.get(url,headers=headers,params=para)
    obj=re.compile('img_cont hoff.*?src="(?P<small>.*?)".*?图像结果.*?href="(?P<bighref>.*?)" h=.*?aria-label="(?P<name>.*?)"',re.S)
    results=[]
    smalls=[]
    bighrefs=[]
    names=[]
    for i in obj.finditer(res.text):
        small=i.group('small')
        bighref=parse.urljoin(url,i.group('bighref').replace("&amp;","@@"))
        # print(small,bighref)
        d={}
        smalls.append(small)
        bighrefs.append(bighref)
        d["small"]=small
        d["bighref"]=bighref
        d["name"]=i.group('name')
        results.append(d)
        # print(bighref)
    return smalls,bighrefs,names,results

def getBigImageByHerf(href):
    opt=Options()#设置无头浏览器配置
    opt.add_argument('--window-size=1920,1080')
    opt.add_argument("--headless")
    opt.add_argument("--disable-gpu")
    web=Chrome(options=opt)
    web.get(href.replace("@@","&"))
    time.sleep(0.5)
    text=web.page_source
    print(href)
    obj=re.compile('</span><img src="(?P<src>.*?)"',re.S)
    src=[]
    for i in obj.finditer(text):
        src.append(i.group('src'))
    return src

def getNextByname(name,index):
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34"
    }
    para={
        "q": name,
        "first": index,
        "count": "35",
        "cw": "1243",
        "ch": "260",
        "relp": "35",
        "tsc": "ImageHoverTitle",
        "datsrc": "I",
        "layout": "RowBased_Landscape",
        "apc": "0",
        "mmasync": "1",
        "dgState": "x*353_y*1521_h*181_c*1_i*36_r*9",
        "IG": "ED728D3EEF304AD4BE0DE0886BDA651F",
        "SFX": "2",
        "iid": "images.5530"
    }
    url="https://cn.bing.com/images/async"
    res=requests.get(url,headers=headers,params=para)
    obj=re.compile('img_cont hoff.*?src="(?P<small>.*?)".*?图像结果.*?aria-label="(?P<name>.*?)".*?href="(?P<bighref>.*?)" h=',re.S)
    results=[]
    smalls=[]
    bighrefs=[]
    names=[]
    print(res.text)
    for i in obj.finditer(res.text):
        small=i.group('small')
        bighref=parse.urljoin(url,i.group('bighref').replace("&amp;","@@"))
        # print(small,bighref)
        d={}
        smalls.append(small)
        bighrefs.append(bighref)
        d["small"]=small
        d["bighref"]=bighref
        d["name"]=i.group('name')
        results.append(d)
    return smalls,bighrefs,names,results


def get_picturesearch(request):
    name=request.GET.get('name','')
    next=request.GET.get('next',0)
    previous=request.GET.get('previous',0)
    print(previous)
    if next==0 and previous==0:
        smalls,bighrefs,names,results=getImageByname(name)
        next=1
        previous=0
    elif next:
        next=int(next)+35
        smalls,bighrefs,names,results=getNextByname(name,next)
        previous=next
        print(next,previous)
    elif previous:
        previous=int(previous)-35
        next=previous
        smalls,bighrefs,names,results=getNextByname(name,previous)
    print("cwcecq",previous,next)
    return render(request,'picturesearch.html',{"results":results,"name":name,"previous":previous,"next":next})



def get_bigPicture(request):
    url=request.GET.get('url')
    name=request.GET.get('name')
    title=request.GET.get('title')
    src=getBigImageByHerf(url)
    return render(request,'bigImage.html',{"src":src,"name":name,"title":title})
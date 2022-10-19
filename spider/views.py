import asyncio
import aiohttp
import random
import re
import requests
from lxml import etree
from urllib import parse
from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from spider.models import Audio,Image,Picture,New1,New2,New3,Audiosrc,Video,Gupiao,New4
from django.core.paginator import Paginator
# Create your views here.
import json
import datetime
import time
import os
import pymysql
import numpy as np
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor
from moviepy import *
from moviepy.editor import *

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
        "form": "IRFLTR",
        "qft":  "filterui:imagesize-custom_1080_1920",
        "sp": "1",
        "sc": "1-0",
        "cvid": "6E8ADA353A0343609BBF188B663E90C2",
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

def get_mp3(url):
    res=requests.get(url)
    obj=re.compile('audio controls src="(?P<src>.*?)"')
    src=obj.search(res.text).group('src')
    return src

def get_mp3List(url,index=1):
    res=requests.get(url+str(index))
    obj=re.compile('<article id=".*?<a href="(?P<href>.*?)">(?P<name>.*?)</a>',re.S)
    hrefs=[]
    names=[]
    results=[]
    for i in obj.finditer(res.text):
        href=i.group('href')
        name=i.group('name')
        d={}
        d['href']=href
        src=get_mp3(href)
        d['src']=src
        d['name']=name
        hrefs.append(href)
        names.append(name)
        results.append(d)
    return hrefs,names,results
def save(url,id):
    obj=re.compile('<article id=".*?<a href="(?P<href>.*?)">(?P<name>.*?)</a>',re.S)
    res=requests.get(url)
    for i in obj.finditer(res.text):
        href=i.group('href')
        name=i.group('name')
        if not Audio.objects.filter(src=get_mp3(href)).first():
            Audio.objects.create(src=get_mp3(href),name=name)
    print(id+2)

def update_list():
    res=requests.get("https://asmrlove.club/")
    obj=re.compile('<article id=".*?<a href="(?P<href>.*?)">(?P<name>.*?)</a>',re.S)
    end=re.compile('dots">.*?href=".*?>(?P<end>.*?)<',re.S)
    n=int(end.search(res.text).group('end'))
    for i in obj.finditer(res.text):
        href=i.group('href')
        name=i.group('name')
        if not Audio.objects.filter(name=name).first():
            Audio.objects.create(src=get_mp3(href),name=name)
    print(1)
    with ThreadPoolExecutor(20) as t:
        for id in range(n-1):
            url="https://asmrlove.club/?paged="+str(id+2)
            t.submit(save,url=url,id=id)
    return None

def get_mp3src(url):
    res=requests.get(url)
    obj=re.compile('controls="controls" src="(?P<src>.*?)"')
    src=obj.search(res.text).group('src')
    return src
def get_mp3urls(index=1):
    url=f'https://shaonvbaike.buzz/list/8a8188a67e5924b0017ee2cd0b36200e/{index}'
    res=requests.get(url)
    obj=re.compile('"colList".*?<a href="(?P<href>.*?)".*?<h2>(?P<name>.*?)</h2>',re.S)
    for i in obj.finditer(res.text):
        href=parse.urljoin(url,i.group('href'))
        name=i.group('name')
        src=get_mp3src(href)
        if not Audio.objects.filter(name=name).first():
            Audio.objects.create(src=src,name=name)
    print(index)

def up_list(request):
    with ThreadPoolExecutor(40) as t:
        for id in range(56):
            t.submit(get_mp3urls,id+1)
    return None


def get_audioList(request):
    if request.session["info"]["id"] == "1":
        if request.GET.get("update"):
            update_list()
        lists=Audio.objects.filter().all()
        return render(request,'audioList.html',{"results":lists})
    return HttpResponse({"msg":"你没有权限"})


def get_audio(request):
    if request.session['info']['id'] !="1":
        return HttpResponse({"msg":"你没有权限"})
    name=request.GET.get('name')
    src=request.GET.get('src')
    return render(request,"audio.html",{"src":src,"name":name})
def get_audios(request,name):

    with open(f'../supply/static/audios/{name}','rb') as f:
        response = HttpResponse()
        response.write(f.read())
        response['Content-Type'] ='audio/mpeg'
        response['Content-Length'] =os.path.getsize(f'../supply/static/audios/{name}')
        return response



def updatasource(url,type=""):
    headers={
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42",
        "x-requested-with": "XMLHttpRequest"
    }
    obj=re.compile('egeli_pic_dl.*?<a href="(?P<href>.*?)".*?src="(?P<src>.*?)".*?title="(?P<name>.*?)"',re.S)
    r=[]
    for i in range(1,1000):
        try:
            res=requests.get(url+str(i)+".html",headers=headers)
        except:
            break
        its=obj.finditer(res.text)
        for it in its :
            href=it.group('href')
            big=getBigSrc(href)
            if not big:
                big=it.group('src').replace("edpic_360_360","edpic_source")
            src=it.group('src')+"@@"+big
            name=it.group('name')
            d={}
            d['href']=href
            d['src']=src
            # d['src']=src.replace()
            d["name"]=name
            d['type']=type
            if not Image.objects.filter(name=name,type=type).first():
                Image.objects.create(name=name,type=type,src=src)
            print(type,i)
            r.append(d)
        if len(obj.findall(res.text))<16:
            break
    print('over')
    return r

def getBigSrc(herf):
    headers={
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42",
        "x-requested-with": "XMLHttpRequest"
    }
    res=requests.get(herf,headers=headers)
    obj=re.compile('class="swiper-slide.*?src="(?P<src>.*?)"',re.S)
    src=[]
    for i in obj.finditer(res.text):
        src.append(i.group('src').replace("edpic","edpic_source"))
    src="@@".join(src)
    return src

def save_pic(obj,txt):
    for i in obj.finditer(str(txt)):
        href=i.group('href')
        src=i.group('src')+get_src(href)
        name=i.group('name')
        if not Picture.objects.filter(name=name).first():
            Picture.objects.create(name=name,src=src)
    print('over')

def get_list(url):
    res=requests.get(url)
    mainPage=BeautifulSoup(res.text,'html.parser')
    txt=mainPage.find("div",class_='ms_main_box')
    obj=re.compile('<li>.*?href="(?P<href>.*?)">.*?src="(?P<src>.*?)".*?html">(?P<name>.*?)<',re.S)
    save_pic(obj,txt)
    with ThreadPoolExecutor(100) as t:
        for n in range(1,412):
            u=url+f"list_{str(n)}.html"
            res=requests.get(u)
            mainPage=BeautifulSoup(res.text,'html.parser')
            txt=mainPage.find("div",class_='ms_main_box')
            t.submit(save_pic,obj,txt)
            # if len(obj.findall(str(txt)))<15:
            #     print('break')
            #     break
            print(n)
    return None

def get_src(href):


    res=requests.get(href)
    mainPage=BeautifulSoup(res.text,'html.parser')
    txt=mainPage.find("div",class_='ms_art_body')
    obj=re.compile('alt="(?P<name>.*?)".*?src="(?P<src>.*?)"',re.S)
    src=''
    for i in obj.finditer(str(txt)):
        src=src+"@@"+i.group('src')
    return src



def get_wallpaper(request):
    t=request.GET.get('type')
    pnum=int(request.GET.get('page',1))
    if t=="44":
        if request.session['info']['id'] !="1":
            return HttpResponse({"msg":"你没有权限"})
        get4list()
        lists=New4.objects.filter().all()
        for i in range(len(lists)):
            lists[i].src=lists[i].src.split("@@")[0]
        pages=Paginator(lists,200)
        try:
            page = pages.page(pnum)  # 获取当前页
        except Exception as e:
            pnum= pages.num_pages  # 如果没有搜索页设置默认数显示最后一页
            page = pages.page(pnum)  # 没有搜索页显示最后一页

        return render(request,'imageList.html',{"results":lists,"page":page,"n":4})
    if t=="4":
        if request.session['info']['id'] !="1":
            return HttpResponse({"msg":"你没有权限"})
        lists=New4.objects.filter().all()

        for i in range(len(lists)):
            lists[i].src=lists[i].src.split("@")[0]
        pages=Paginator(lists,200)
        try:
            page = pages.page(pnum)  # 获取当前页
        except Exception as e:
            pnum= pages.num_pages  # 如果没有搜索页设置默认数显示最后一页
            page = pages.page(pnum)  # 没有搜索页显示最后一页
        return render(request,'imageList.html',{"results":lists,"page":page,"n":4})

    if t=="33":
        if request.session['info']['id'] !="1":
            return HttpResponse({"msg":"你没有权限"})
        get3list()
        lists=New3.objects.filter().all()
        for i in range(len(lists)):
            lists[i].src=lists[i].src.split("@")[0]
        pages=Paginator(lists,200)
        try:
            page = pages.page(pnum)  # 获取当前页
        except Exception as e:
            pnum= pages.num_pages  # 如果没有搜索页设置默认数显示最后一页
            page = pages.page(pnum)  # 没有搜索页显示最后一页

        return render(request,'imageList.html',{"results":lists,"page":page,"n":3})
    if t=="3":
        if request.session['info']['id'] !="1":
            return HttpResponse({"msg":"你没有权限"})
        lists=New3.objects.filter().all()

        for i in range(len(lists)):
            lists[i].src=lists[i].src.split("@")[0]
        pages=Paginator(lists,200)
        try:
            page = pages.page(pnum)  # 获取当前页
        except Exception as e:
            pnum= pages.num_pages  # 如果没有搜索页设置默认数显示最后一页
            page = pages.page(pnum)  # 没有搜索页显示最后一页
        return render(request,'imageList.html',{"results":lists,"page":page,"n":3})

    if t=="22":
        get2list()
        lists=New2.objects.filter().all()
        for i in range(len(lists)):
            lists[i].src=lists[i].src.split("@@")[0]
        pages=Paginator(lists,200)
        try:
            page = pages.page(pnum)  # 获取当前页
        except Exception as e:
            pnum= pages.num_pages  # 如果没有搜索页设置默认数显示最后一页
            page = pages.page(pnum)  # 没有搜索页显示最后一页
        return render(request,'imageList.html',{"results":lists,"page":page,"n":2})
    if t=="2":
        lists=New2.objects.filter().all()
        for i in range(len(lists)):
            lists[i].src=lists[i].src.split("@@")[0]
        pages=Paginator(lists,200)
        try:
            page = pages.page(pnum)  # 获取当前页
        except Exception as e:
            pnum= pages.num_pages  # 如果没有搜索页设置默认数显示最后一页
            page = pages.page(pnum)  # 没有搜索页显示最后一页
        return render(request,'imageList.html',{"results":lists,"page":page,"n":2})

    if t=="11":
        get1list()
        lists=New1.objects.filter().all()
        for i in range(len(lists)):
            lists[i].src=lists[i].src.split("@@")[0]
        pages=Paginator(lists,200)
        try:
            page = pages.page(pnum)  # 获取当前页
        except Exception as e:
            pnum= pages.num_pages  # 如果没有搜索页设置默认数显示最后一页
            page = pages.page(pnum)  # 没有搜索页显示最后一页
        return render(request,'imageList.html',{"results":lists,"page":page,"n":1})
    if t=="1":
        lists=New1.objects.filter().all()
        for i in range(len(lists)):
            lists[i].src=lists[i].src.split("@@")[0]
        pages=Paginator(lists,200)
        try:
            page = pages.page(pnum)  # 获取当前页
        except Exception as e:
            pnum= pages.num_pages  # 如果没有搜索页设置默认数显示最后一页
            page = pages.page(pnum)  # 没有搜索页显示最后一页
        return render(request,'imageList.html',{"results":lists,"page":page,"n":1})


    if t=="00":
        url='http://www.zhanans.com/mntp/'
        get_list(url)
        lists=Picture.objects.filter().all()
        for i in range(len(lists)):
            lists[i].src=lists[i].src.split("@@")[0]
        pages=Paginator(lists,200)
        try:
            page = pages.page(pnum)  # 获取当前页
        except Exception as e:
            pnum= pages.num_pages  # 如果没有搜索页设置默认数显示最后一页
            page = pages.page(pnum)  # 没有搜索页显示最后一页
        return render(request,'imageList.html',{"results":lists,"page":page,"n":0})
    if t=="0":
        lists=Picture.objects.filter().all()
        for i in range(len(lists)):
            lists[i].src=lists[i].src.split("@@")[0]
        pages=Paginator(lists,200)
        try:
            page = pages.page(pnum)  # 获取当前页
        except Exception as e:
            pnum= pages.num_pages  # 如果没有搜索页设置默认数显示最后一页
            page = pages.page(pnum)  # 没有搜索页显示最后一页
        return render(request,'imageList.html',{"results":lists,"page":page,"n":0})

    if request.GET.get("update"):
        urls=['https://mm.enterdesk.com/dalumeinv/','https://mm.enterdesk.com/rihanmeinv/','https://mm.enterdesk.com/gangtaimeinv/',
              'https://mm.enterdesk.com/dongmanmeinv/','https://mm.enterdesk.com/qingchunmeinv/','https://mm.enterdesk.com/keaimeinv/',
              'https://www.enterdesk.com/zhuomianbizhi/fengjing/','https://www.enterdesk.com/zhuomianbizhi/dongmankatong/',
              'https://sj.enterdesk.com/woman/','https://sj.enterdesk.com/anime/','https://sj.enterdesk.com/gaoxiaotupian/']
        types=['大陆','日韩','港台','动漫','清纯','可爱','风景壁纸','动漫壁纸','手机唯美','手机卡通','手机搞笑']

        with ThreadPoolExecutor(20) as t:
            for i in range(len(urls)):
                t.submit(updatasource,urls[i],types[i])
    lists=Image.objects.filter().all()

    for i in range(len(lists)):
        lists[i].src=lists[i].src.split("@@")[0]
    pages=Paginator(lists,200)
    try:
        page = pages.page(pnum)  # 获取当前页
    except Exception as e:
        pnum= pages.num_pages  # 如果没有搜索页设置默认数显示最后一页
        page = pages.page(pnum)  # 没有搜索页显示最后一页
    return render(request,'imageList.html',{"results":lists,"page":page})


def get_bigWallpaper(request):
    t=request.GET.get('t')
    n=request.GET.get('n')
    id=request.GET.get('id')
    if n:
        if int(n)==1:
            o=New1.objects.filter(id=id).first()
            src=o.src.split("@@")[1:]
            name=o.name
            title=o.type
            return render(request,'bigImage.html',{"src":src,"name":name,"title":title})
        if int(n)==3:
            if request.session['info']['id'] !="1":
                return HttpResponse({"msg":"你没有权限"})
            o=New3.objects.filter(id=id).first()
            src=o.src.split("@")[1:]
            name=o.name
            title=o.type
            return render(request,'bigImage.html',{"src":src,"name":name,"title":title})
        if int(n)==2:
            o=New2.objects.filter(id=id).first()
            src=o.src.split("@@")[1:]
            name=o.name
            title=o.type
            return render(request,'bigImage.html',{"src":src,"name":name,"title":title})
        if int(n)==4:
            o=New4.objects.filter(id=id).first()
            src=o.src.split("@@")[1:]
            name=o.name
            title=o.type
            return render(request,'bigImage.html',{"src":src,"name":name,"title":title})
    if t:
        o=Image.objects.filter(id=id).first()
        src=o.src.split("@@")[1:]
        name=o.name
        title=o.type
        return render(request,'bigImage.html',{"src":src,"name":name,"title":title})
    o=Picture.objects.filter(id=id).first()
    src=o.src.split("@@")[1:]
    name=o.name
    title=o.name
    return render(request,'bigImage.html',{"src":src,"name":name,"title":title})

def get4list():
    type=['fantasy-girls-wallpapers','anime-girl-wallpapers','nature-wallpapers','digital-universe-wallpapers']
    types=['唯美','动漫','自然','宇宙']
    with ThreadPoolExecutor(4) as t:
        for i in range(4):
            t.submit(get_4list,type[i],types[i])


def get_4list(type,types):
    for page in range(1,1000):
        url=f'https://hdqwalls.com/{type}/sort/views/page/{page}'
        res=requests.get(url)
        obj=re.compile("caption hidden-md hidden-sm hidden-xs.*?title='(?P<name>.*?)'.*?src='(?P<src>.*?)'",re.S)
        it=obj.finditer(res.text)
        n=0
        for i in it:
            src=i.group('src')
            name=i.group('name')
            bigsrc=src.replace('/thumb','')
            src=src+"@@"+bigsrc
            if not New4.objects.filter(src=src).first():
                New4.objects.create(src=src,name=name,type=types)
            n+=1
        print(types,page)
        if n<18:
            break



def get1list():
    ts=['街拍','套图','微博','写真']
    for i in range(2,6):
        for j in range(1,20):
            url=f"https://www.xiushe4k.com/?cat={str(i)}&paged={str(j)}"
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34"
                ,"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Cookie": "BIDUPSID=411397ADCA5FA50A2E41AB2A6D40C08D; PSTM=1644477760; BD_UPN=12314753; __yjs_duid=1_76cb500678e0fad7f03158136645e2641644737380783; BAIDUID=3E36D1A4894DF97FCE7A1491E4480FB1:FG=1; BDUSS=GltV0FWVkRVUlpmUmZTdkJ2ZUFsRU5hTGk5cE1FZllNUDJlZkZVS1BuUy1HdVppSVFBQUFBJCQAAAAAAAAAAAEAAABU70SkMTIyysfO0jczAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL6NvmK-jb5iS; BDUSS_BFESS=GltV0FWVkRVUlpmUmZTdkJ2ZUFsRU5hTGk5cE1FZllNUDJlZkZVS1BuUy1HdVppSVFBQUFBJCQAAAAAAAAAAAEAAABU70SkMTIyysfO0jczAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL6NvmK-jb5iS; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; BD_CK_SAM=1; PSINO=1; BAIDUID_BFESS=3E36D1A4894DF97FCE7A1491E4480FB1:FG=1; ZD_ENTRY=baidu; RT=\"z=1&dm=baidu.com&si=069naiho9oif&ss=l8y2i71l&sl=4&tt=1bt&bcn=https://fclog.baidu.com/log/weirwood?type=perf&ld=8yt&ul=cpj&hd=cq4\"; BA_HECTOR=0h2k252l0501208h2g0580ip1hjvgat1a; ZFY=1XzLj93E1kpXAhM4o8EUDdn9AOKxd44U5VVIzgsTFoI:C; H_PS_PSSID=36553_37356_36884_34813_37402_37395_36789_37422_26350_37284_37370_37468; baikeVisitId=affeb5e8-219a-4516-826e-0de9cd824380; COOKIE_SESSION=30_0_9_9_9_7_1_0_9_7_1_0_2943_0_0_0_1664959705_0_1664971057|9#1495_123_1664439634|9; BDRCVFR[S4-dAuiWMmn]=FZ_Jfs2436CUAqWmykCULPYrWm1n1fz; H_PS_645EC=fb17pzl/2XwZhS0n9FDV1F/CCfmCwgk98+A/SjJhkCq1c9noJ/9N//Q4IQ8vLo2yVw",
                'Connection': 'close',
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
            }
            res=requests.get(url,headers=headers)
            obj=re.compile('<li.*?cxudy-list-format"><a href="(?P<href>.*?)".*?data-original="(?P<src>.*?)".*?alt="(?P<name>.*?)"',re.S)
            lis=obj.findall(res.text)
            n=len(lis)
            print(n)
            if n>0:
                with ThreadPoolExecutor(20) as t:
                    t.submit(save1,obj,res,ts,i)
                    print(i)
                if n < 20:
                    break



def save1(obj,res,ts,i):
    for it in obj.finditer(res.text):
        href=it.group('href')
        src=it.group('src')+get1src(href)
        name=it.group('name')
        ty=ts[i-2]
        if not New1.objects.filter(name=name,type=ty).first():
            New1.objects.create(src=src,name=name,type=ty)

def get1src(href):
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34"
        ,"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Cookie": "BIDUPSID=411397ADCA5FA50A2E41AB2A6D40C08D; PSTM=1644477760; BD_UPN=12314753; __yjs_duid=1_76cb500678e0fad7f03158136645e2641644737380783; BAIDUID=3E36D1A4894DF97FCE7A1491E4480FB1:FG=1; BDUSS=GltV0FWVkRVUlpmUmZTdkJ2ZUFsRU5hTGk5cE1FZllNUDJlZkZVS1BuUy1HdVppSVFBQUFBJCQAAAAAAAAAAAEAAABU70SkMTIyysfO0jczAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL6NvmK-jb5iS; BDUSS_BFESS=GltV0FWVkRVUlpmUmZTdkJ2ZUFsRU5hTGk5cE1FZllNUDJlZkZVS1BuUy1HdVppSVFBQUFBJCQAAAAAAAAAAAEAAABU70SkMTIyysfO0jczAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL6NvmK-jb5iS; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; BD_CK_SAM=1; PSINO=1; BAIDUID_BFESS=3E36D1A4894DF97FCE7A1491E4480FB1:FG=1; ZD_ENTRY=baidu; RT=\"z=1&dm=baidu.com&si=069naiho9oif&ss=l8y2i71l&sl=4&tt=1bt&bcn=https://fclog.baidu.com/log/weirwood?type=perf&ld=8yt&ul=cpj&hd=cq4\"; BA_HECTOR=0h2k252l0501208h2g0580ip1hjvgat1a; ZFY=1XzLj93E1kpXAhM4o8EUDdn9AOKxd44U5VVIzgsTFoI:C; H_PS_PSSID=36553_37356_36884_34813_37402_37395_36789_37422_26350_37284_37370_37468; baikeVisitId=affeb5e8-219a-4516-826e-0de9cd824380; COOKIE_SESSION=30_0_9_9_9_7_1_0_9_7_1_0_2943_0_0_0_1664959705_0_1664971057|9#1495_123_1664439634|9; BDRCVFR[S4-dAuiWMmn]=FZ_Jfs2436CUAqWmykCULPYrWm1n1fz; H_PS_645EC=fb17pzl/2XwZhS0n9FDV1F/CCfmCwgk98+A/SjJhkCq1c9noJ/9N//Q4IQ8vLo2yVw",
        'Connection': 'close',
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
    }
    res=requests.get(href,headers=headers)
    obj=re.compile('<img class="alignnone size-full.*?src="(?P<src>.*?)".*?alt')
    src=''
    for it in obj.finditer(res.text):
        src=src+"@@"+it.group('src')
    return src

def get3list():
    with ThreadPoolExecutor(20) as t:
        for i in range(1,42):
            t.submit(save3,i)
        print('over')
def save3(i):
    url=f"https://fljloli.ml/ajax/buscar_posts.php?post=&cat=&tag=&search=&page=&index={str(i)}&ver=36"
    res=requests.get(url)
    obj=re.compile('a mob="0" webp="0.*?href="(?P<href>.*?)".*?data-src="(?P<src>.*?)".*?alt="(?P<name>.*?)"',re.S)
    ls=obj.findall(res.text)
    for l in ls:
        href=l[0]
        src=l[1]+get3src(href)
        name=l[2]
        if not New3.objects.filter(src=src).first():
            New3.objects.create(src=src,name=name,type='和谐')
    print(i)


def get3src(href):
    res=requests.get(href)
    obj=re.compile('<div data-src="(?P<src>.*?)"',re.S)
    src=''
    for i in obj.finditer(res.text):
        src=src+"@"+i.group('src')
    return src



def get2list():
    ts=['中国','韩国','台湾','日本']
    # 6,1400
    for i in range(3,6):
        with ThreadPoolExecutor(200) as t:
            for j in range(1,1400):
                print(i,j)
                url=f"https://meitua.top/arttype/2{str(i)}a-{str(j)}.html"
                res=requests.get(url)
                obj=re.compile('<li><a class="thumbnail".*?src="(?P<src>.*?)".*?"(?P<name>.*?)".*?href="(?P<href>.*?)"',re.S)
                ls=obj.findall(res.text)
                t.submit(save2,ls,ts[i-2])
                if len(ls)<24:
                    break

def save2(ls,ty):
    for l in ls:
        href=parse.urljoin("https://meitua.top/",l[2])
        src=l[0]+get2src(href)
        name=l[1]
        if not New2.objects.filter(src=src).first():
            New2.objects.create(src=src,name=name,type=ty)

def get2src(href):
    res=requests.get(href)
    o=re.compile('\[rihide](.*?)\[/rihide]',re.S)
    obj=re.compile('<img class="img" src="(?P<src>.*?)">',re.S)
    src=''
    t=res.text
    l=o.findall(res.text)
    if len(l)>0:
        t=l[0]
    for i in obj.finditer(t):
        src=src+"@@"+i.group('src')
    return src


def get_search_list(keys,page):
    url=f"https://search.bilibili.com/all?keyword={keys}&from_source=webtop_search&spm_id_from=333.1007&search_source=2&page={page}&o=360"
    res=requests.get(url)
    obj=re.compile('<li class="video-item matrix"><a href="//(?P<href>.*?)".*?title="(?P<name>.*?)"',re.S)
    its=obj.finditer(res.text)
    i=0
    for it in its:
        href="https://"+it.group('href')
        name=it.group('name').replace('/','-').replace('\\','-')+str(i)
        i+=1
        src,s=get_bili_src(href)
        addr="audios/"+name+".mp3"
        if not Audiosrc.objects.filter(name=name).filter().first():
            save_bili_src(href,src,name)
            Audiosrc.objects.create(src=addr,name=name)
        print(i)

def get_bili_src(href):
    res=requests.get(href)
    obj=re.compile('<title data-vue-meta="true">(?P<name>.*?)</title>.*?"video":.*?"baseUrl":"(?P<video>.*?)".*?"audio":.*?"baseUrl":"(?P<audio>.*?)"',re.S)
    se=obj.search(res.text)
    au=se.group('audio')
    vi=se.group('video')
    name=se.group('name').replace('/','-').replace('\\','-')
    print(name)
    return au,name


def save_bili_src(href,src,name):
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34"
        ,"referer":href,
    }
    text=requests.get(url=src,headers=headers,timeout=(3.05,27)).content
    with open(f'../supply/static/audios/{name}.mp3',mode='wb') as f:
        f.write(text)


def audio_download(keys,pages):
    with ThreadPoolExecutor(20) as t:
        for i in range(1,pages):
            t.submit(get_search_list,keys,i)
            print(i)

def get_qiwen(request):
    keys=request.GET.get('keys')
    pages=request.GET.get('pages')
    link=request.GET.get('link')
    num=request.GET.get("num",0)
    if link:
        get_next(link,num)
    if keys and pages:
        audio_download(keys,int(pages))
    res=Audiosrc.objects.filter().all()
    for i in range(len(res)):
        if res[i].id<637:
            res[i].src="/static/"+str(res[i].src,'utf-8')
        else:
            res[i].src="/datas/"+str(res[i].src,'utf-8')
        res[i].name=str(res[i].name,'utf-8')
    return render(request,'qiwen.html',{"results":res,"keys":keys,"pages":pages,"link":link,"num":num})

def get_qi(request):
    id=request.GET.get('id')
    au=Audiosrc.objects.filter(id=id).first()
    name=str(au.name,'utf-8')
    src=str(au.src,'utf-8')
    return render(request,'qi.html',{"name":name,"src":src})

def get_next(link,num):
    # url='https://www.bilibili.com/video/BV14k4y167Qc/'
    url=link
    res=requests.get(url)
    obj=re.compile('framepreview-box"><a href="(?P<href>.*?)".*?<p title="(?P<name>.*?)".*?<div class="upname">',re.S)
    src,name=get_bili_src(url)
    name="".join(name.split(' ')).strip('_哔哩哔哩_bilibili').split("|")[0]
    addr="audios/"+name+".mp3"
    if not Audiosrc.objects.filter(name=name).filter().first():
        Audiosrc.objects.create(src=addr,name=name)
        save_bili_src(url,src,name)
        print('over')
    n=0
    for i in obj.finditer(res.text):
        n+=1
        if n>int(num):
            break
        href=parse.urljoin(url,i.group('href'))
        name=i.group('name')
        src,s=get_bili_src(href)
        print(name)
        addr="audios/"+name+".mp3"
        if not Audiosrc.objects.filter(name=name).filter().first():
            Audiosrc.objects.create(src=addr,name=name)
            save_bili_src(href,src,name)
    print(1)





def save_au_vi(href,au,vi,name):
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34"
        ,"referer":href,
    }
    text=requests.get(url=au,headers=headers).content
    au_p=f'{name}.mp3'
    vi_p=f'{name}.mp4'
    with open(au_p, mode='wb') as f:
        f.write(text)
    print(1)
    text=requests.get(url=vi,headers=headers).content
    with open(vi_p, mode='wb') as f:
        f.write(text)
    print(2)
    return au_p,vi_p
def get_bili(href):
    res=requests.get(href)
    obj=re.compile('<title data-vue-meta="true">(?P<name>.*?)</title>.*?"video":.*?"baseUrl":"(?P<video>.*?)".*?"audio":.*?"baseUrl":"(?P<audio>.*?)"',re.S)
    se=obj.search(res.text)
    au=se.group('audio')
    vi=se.group('video')
    name=se.group('name')
    print(name)
    return au,vi,name


def get_next_video(link,num):
    # url='https://www.bilibili.com/video/BV14k4y167Qc/'
    url=link
    res=requests.get(url)
    obj=re.compile('framepreview-box"><a href="(?P<href>.*?)".*?<p title="(?P<name>.*?)".*?<div class="upname">',re.S)
    au,vi,name=get_bili(url)
    name="".join(name.split(' ')).strip('_哔哩哔哩_bilibili').replace('|','-').replace('\\','-').replace('/','-')
    if not Video.objects.filter().first():
        au_p,vi_p=save_au_vi(url,au,vi,name)
        save_video(vi_p,au_p,name)
        name=name+"f"
        addr="videos/"+name+".mp4"
        Video.objects.create(src=addr,name=name)
    n=0
    for i in obj.finditer(res.text):
        n+=1
        if n> int(num):
            break
        href=parse.urljoin(url,i.group('href'))
        name=i.group('name').replace('|','-').replace('\\','-').replace('/','-')
        au,vi,n=get_bili(href)
        addr="videos/"+name+".mp4"
        save_video(vi_p,au_p,name)
        if not Video.objects.filter().first():
            Video.objects.create(src=addr,name=name)
        print(au,vi,n,name)

def delete_file(path):
    if os.path.exists(path):  # 如果文件存在
        os.remove(path)

def save_video(video_path,audio_path,name):
    # 提取音轨
    audio = AudioFileClip(audio_path)
    # 读入视频
    video = VideoFileClip(video_path)
    # 将音轨合并到视频中
    video = video.set_audio(audio)
    # 输出
    video.write_videofile(f"{name}f.mp4")
    # delete_file(video_path)
    # delete_file(audio_path)
    print('有音频视频处理完成')

def get_video(request):
    link=request.GET.get('link')
    num=request.GET.get('num',0)
    if link:
        get_next_video(link,num)
    r=Video.objects.filter().all()
    return render(request,'video.html',{"results":r})


def see_video(request):
    id=request.GET.get('id')
    s=Video.objects.filter(id=id).first()
    src=s.src
    name=s.name
    return render(request,'vi.html',{"src":src,"name":name})


def delete_audio(request):
    id = request.GET.get("uid")
    Audio.objects.filter(id=int(id)).delete()
    notify = []

    notify.append(dict(id=0, tittle="提示", context="音频 {} 删除成功".format(id), type="success", position="top-center"))
    request.session["notify"] = notify

    return JsonResponse({"status": True})


def delete_audiosrc(request):
    id = request.GET.get("uid")
    # delete_file('')
    Audiosrc.objects.filter(id=int(id)).delete()
    notify = []

    notify.append(dict(id=0, tittle="提示", context="音频 {} 删除成功".format(id), type="success", position="top-center"))
    request.session["notify"] = notify

    return JsonResponse({"status": True})


def gupiao(request):
    pnum=int(request.GET.get('page',1))
    lists=Gupiao.objects.filter().all()
    pages=Paginator(lists,200)
    try:
        page = pages.page(pnum)  # 获取当前页
    except Exception as e:
        pnum= pages.num_pages  # 如果没有搜索页设置默认数显示最后一页
        page = pages.page(pnum)  # 没有搜索页显示最后一页
    return render(request,'gupiao.html',{"results":lists,"page":page})
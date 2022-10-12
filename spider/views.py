from django.shortcuts import render
import random
import re
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


def get_1_data(request):
    name=request.GET.get('name')
    source=get_source(name)
    nowdata,liefdata=get_1_detail(source[0])
    print(nowdata,liefdata)
    return render(request,'searchweather.html')


def get_7_data(request):
    return None


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
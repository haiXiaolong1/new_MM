from django.shortcuts import render, HttpResponse,redirect
import xlsxwriter as xls
# Create your views here.

from supply import models
from django.http import HttpResponseBadRequest
from django.views.generic import View
from django import forms
import django_excel as excel
import json
from datetime import datetime


class formatController:
    def __init__(self,workbook):
        self.wk=workbook

    def titleF(self):
        form=self.wk.add_format({
            'bold': True,
            'align': 'center',  # 水平居中
            'valign': 'vcenter',  # 垂直居中
            'border':2,
            'border_color':'white',
            'font_color':'white',
        })
        form.set_bg_color('#5b9bd5')
        return form

    def rowF(self):
        form1=self.wk.add_format({
            'bold': False,
            'align': 'center',  # 水平居中
            'valign': 'vcenter',  # 垂直居中
            'border':1,
            'border_color':'white',
        })
        form1.set_bg_color('#bdd6ee')
        form2=self.wk.add_format({
            'bold': False,
            'align': 'center',  # 水平居中
            'valign': 'vcenter',  # 垂直居中
            'border': 1,
            'border_color': 'white',
        })
        form2.set_bg_color('#deeaf6')
        return [form1,form2]

    def editF(self):
        form=self.wk.add_format({
            'bold': False,
            'align': 'center',  # 水平居中
            'valign': 'vcenter',  # 垂直居中
            'border': 1,
            'border_color': 'white',
        })
        form.set_bg_color("#eaeaea")
        return form

class UploadFileForm(forms.Form):
    file = forms.FileField()


class TestDjangoExcelUpload(View):
    def get(self, request):
        form = UploadFileForm()
        return render(request, 'upload_form.html', context={'form': form})

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filehandle = request.FILES['file']
            sheet = filehandle.get_sheet()  # 对准
            print(sheet.to_array())
            data = sheet.to_array()
            da = data[2:]
            for ea in da:
                add_supply_axu(ea,request)

            #return HttpResponse(data)
            return redirect("/supply/list/")
        else:
            return HttpResponse("出错了")

import time
class TestDjangoExcelDownload(View):

    def get(self, request):
        name = "supplyTemp"
        ts = int(time.time())
        file_name = name + str(ts)+'.xlsx'
        x_io = BytesIO()
        work_book = xlsxwriter.Workbook(x_io)
        fc = formatController(work_book)
        tf = fc.titleF()
        ef = fc.editF()
        work_sheet = work_book.add_worksheet(name)
        work_sheet.set_column("A:B",10,ef)
        work_sheet.merge_range("A1:B1","编辑供应商",tf)
        work_sheet.write(1, 0, "供应商名称",tf)
        work_sheet.write(1, 1, "供应商地址",tf)
        work_book.close()
        print(type(work_book))
        res = HttpResponse()
        res["Content-Type"] = "application/octet-stream"
        res["Content-Disposition"] = 'filename="'+file_name+'"'
        res.write(x_io.getvalue())
        return res



def add_supply_axu(data_each,request):
    n = 10000000
    if models.Gongyingshang.objects.first():
        n = models.Gongyingshang.objects.all().order_by('-id').first().id[1:]
    sid = "s" + str(int(n) + 1)  # 编号递增，这样计算避免删除后出现错误
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id = request.session["info"]['id']
    named=data_each[0]
    addressd=data_each[1]

    models.Gongyingshang.objects.create(name=named, address=addressd, createtime=time
                                        , id=sid, updatetime=time, createnumberid_id=id,
                                        updatenumberid_id=id)

from django.http import HttpResponse
from io import BytesIO
import xlsxwriter

def new_excel(request):
    x_io = BytesIO()
    work_book = xlsxwriter.Workbook(x_io)
    work_sheet = work_book.add_worksheet("excel-1")
    work_sheet.write(0,0,"test")
    work_sheet.data_validation("A1:A5", {'validate':'list', 'source':[1, 2, 3, 4]})
    work_book.close()
    res = HttpResponse()
    res["Content-Type"] = "application/octet-stream"
    res["Content-Disposition"] = 'filename="userinfos.xlsx"'
    res.write(x_io.getvalue())

    return res

from supply import models
from django.db import connection
class TestDjangoExcelDownload_ac(View):
    def get(self, request):
        #sheet = excel.pe.Sheet([["姓名", "登录密码","邮箱","职位","是否激活","公司编号"]])
        office = ["系统管理员","供应商员工","采购员工","库存员工","采购经理","库存经理","生产经理"]
        name = "acTemp"
        ts = int(time.time())
        file_name = name + str(ts)+'.xlsx'

        x_io = BytesIO()
        work_book = xlsxwriter.Workbook(x_io)
        fc = formatController(work_book)
        tf = fc.titleF()
        ef = fc.editF()
        rf = fc.rowF()
        work_sheet = work_book.add_worksheet(name)
        srow,scol=1,3
        work_sheet.set_column("D:H",10,ef)
        work_sheet.merge_range("D1:H1","编辑员工",tf)
        work_sheet.write(srow + 0, scol+0, "姓名",tf)
        work_sheet.write(srow + 0, scol+1, "登录密码",tf)
        work_sheet.write(srow + 0, scol+2, "邮箱",tf)
        work_sheet.write(srow + 0, scol+3, "职位",tf)
        work_sheet.write(srow + 0, scol+4, "公司编号",tf)

        gs=models.Gongsi.objects.all().values("myid",'name')
        gsb=[]
        work_sheet.set_column("A:B", 11)
        work_sheet.merge_range("A1:B1", "公司列表", tf)
        work_sheet.write(1, 0, "公司编号", tf)
        work_sheet.write(1, 1, "公司名称", tf)

        for i in range(len(gs)):
            work_sheet.write(2+i, 0, gs[i]["myid"], rf[i%2])
            work_sheet.write(2+i, 1, gs[i]["name"], rf[i%2])
            gsb.append(gs[i]["myid"])

        work_sheet.data_validation("G3:G20",{'validate':'list','source':office,'dropdown':True})
        work_sheet.data_validation("H3:H20",{'validate':'list','source':gsb,'dropdown':True})

        work_book.close()
        res = HttpResponse()
        res["Content-Type"] = "application/octet-stream"
        res["Content-Disposition"] = 'filename="'+file_name+'"'
        res.write(x_io.getvalue())
        return res

class TestDjangoExcelUpload_ac(View):
    def get(self, request):
        form = UploadFileForm()
        return render(request, 'upload_form.html', context={'form': form})

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filehandle = request.FILES['file']
            sheet = filehandle.get_sheet()  # 对准
            print(sheet.to_array())
            data = sheet.to_array()

            da = data[1:]
            for ea in da:
                if ea[5] != "":
                    add_account_axu(ea[:6],request)

            #return HttpResponse(data)
            return redirect("/account/ac/list/")
        else:
            return HttpResponse("出错了")

def add_account_axu(data_each,request):
    n = 1000
    if models.Yuangong.objects.first():
        n = models.Yuangong.objects.all().order_by('-id').first().id[1:]
    long = 4
    tcc = str(int(n) + 1)
    adt=4-len(tcc)
    sid = "e" + adt*'0'+str(tcc)  # 编号递增，这样计算避免删除后出现错误

    named=data_each[0]
    passworded=data_each[1]
    emailed=data_each[2]
    officed=data_each[3]
    actived=data_each[4]
    bussinessd=data_each[5]


    cursor = connection.cursor()
    query_recreation = 'insert  into  yuangong(id,password,email,office,username,isactive,businessid_id)' \
                       "  values('"+str(sid)+"','"+str(passworded)+"','"+str(emailed)  \
                       +"','"+str(officed)+"','"+str(named) +"','"+str(actived) +"','"+str(bussinessd)+"')"
    cursor.execute(query_recreation)

class TestDjangoExcelDownload_mt(View):

    def get(self, request):
        name = "mtTemp"
        ts = int(time.time())
        file_name = name + str(ts)+'.xlsx'

        x_io = BytesIO()
        work_book = xlsxwriter.Workbook(x_io)
        fc=formatController(work_book)
        tf = fc.titleF()
        ef=fc.editF()
        rf=fc.rowF()
        work_sheet = work_book.add_worksheet(name)
        work_sheet.merge_range('A1:C1', '参考信息', tf)
        tl=1 #表头行所占行数
        work_sheet.merge_range('A{}:C{}'.format(tl+1,tl+1), '供应商列表',tf)
        yu = models.Gongyingshang.objects.all().values("id", "name","address")
        gys=[]
        for i in range(len(yu)):
            work_sheet.write(i + 1+tl, 0, yu[i]['id'], rf[i%2])
            work_sheet.write(i + 1+tl, 1, yu[i]['name'], rf[i%2])
            work_sheet.write(i + 1+tl, 2, yu[i]['address'], rf[i%2])
            gys.append(yu[i]['id'])
        i+=2

        work_sheet.merge_range('A{}:C{}'.format(tl+i+1,tl+i+1), '物料列表', tf)

        wu = models.Wuliao.objects.all().values("id", "type", "desc")
        wl=[]
        for j in range(len(wu)):
            work_sheet.write(i+j + 1+tl, 0, wu[j]['id'], rf[j%2])
            work_sheet.write(i+j + 1+tl, 1, wu[j]['type'], rf[j%2])
            work_sheet.write(i+j + 1+tl, 2, wu[j]['desc'], rf[j%2])
            wl.append(wu[j]['id'])
        work_sheet.set_column('A1:C1', 11)

        work_sheet.set_column('E:F', 11,ef)
        work_sheet.merge_range('E1:F1', '添加供应关系', tf)
        work_sheet.write(1, 4, "供应商编号",tf)
        work_sheet.write(1, 5, "物料编号", tf)
        work_sheet.data_validation("E3:E20", {'validate': 'list', 'source': gys,'dropdown':True})
        work_sheet.data_validation("F3:F20", {'validate': 'list', 'source': wl,'dropdown':True})

        work_book.close()
        res = HttpResponse()
        res["Content-Type"] = "application/octet-stream"
        res["Content-Disposition"] = 'filename="'+file_name+'"'
        res.write(x_io.getvalue())

        return res

def dictfetchall(cursor):
    "将游标返回的结果保存到一个字典对象中"
    desc = cursor.description
    return [
    dict(zip([col[0] for col in desc], row))
    for row in cursor.fetchall()
    ]


class TestDjangoExcelUpload_mt(View):


    def get(self, request):
        form = UploadFileForm()
        return render(request, 'upload_form.html', context={'form': form})

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filehandle = request.FILES['file']
            sheet = filehandle.get_sheet()  # 对准
            #print(sheet.to_array())

            data = sheet.to_array()

            da = data[1:]

            temp1 = []
            temp2 = []
            temp=[]
            for ea in da:
                if ea[0] != "" and ea[1] != "":
                    temp1.append(ea[:2][0])
                    temp2.append(ea[:2][1])

                    #add_mt_axu(ea[:2],request)

            c=[]
            for i in range(len(temp1)):
                temp=[]
                temp.append(temp1[i])
                temp.append(temp2[i])
                c.append(temp)


            flag = 1
            q_l=[]
            for j in range(len(c)):
                try:
                    models.Gongyingshang.objects.get(id=c[j][0])
                    models.Wuliao.objects.get(id=c[j][1])
                except:
                    flag = 0
                    q_l.append(j+1)

            strq=""
            for e in q_l:
                strq=strq+str(e)+","

            if (flag==0):
                #print(q_l)
                return render(request, 'mt_vali_list.html', {
                    'data': c,
                    'q_ind':q_l,
                    'r_ind':strq[:-1]
                })

            for ea in da:
                if ea[0] != "" and ea[1] != "":
                    add_mt_axu(ea[:2],request)


            return redirect("/supply/material/list/")
        else:
            return HttpResponse("出错了")

def add_mt_axu(data_each,request):
    uid = request.session["info"]['id']
    td = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    gysid=data_each[0]
    wlid=data_each[1]

    cursor = connection.cursor()
    query_recreation = 'insert  into  gongyingguanxi(createtime,updatetime,createid_id,materialid_id,supplyid_id,updateid_id)' \
                       "  values('"+str(td)+"','"+str(td)+"','"+str(uid)  \
                       +"','"+str(wlid)+"','"+str(gysid) +"','"+str(uid)+"')"
    cursor.execute(query_recreation)



from django.shortcuts import render, HttpResponse,redirect

# Create your views here.

from supply import models
from django.http import HttpResponseBadRequest
from django.views.generic import View
from django import forms
import django_excel as excel
import json
from datetime import datetime


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

            da = data[1:]
            for ea in da:
                add_supply_axu(ea,request)

            #return HttpResponse(data)
            return redirect("/supply/list/")
        else:
            return HttpResponse("出错了")

import time
class TestDjangoExcelDownload(View):

    def get(self, request):
        sheet = excel.pe.Sheet([["供应商名称name", "供应商地址address"]])
        name = "供应商上传批量模板"

        ts = int(time.time())
        return excel.make_response(sheet, "xlsx",file_name=name+str(ts))


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

        office = [
            ("系统管理员"),
            ("供应商员工"),
            ("采购员工"),
            ("库存员工"),
            ("采购经理"),
            ("库存经理"),
            ("生产经理")
        ]


        name = "acTemp"

        ts = int(time.time())
        file_name = name + str(ts)+'.xlsx'


        x_io = BytesIO()
        work_book = xlsxwriter.Workbook(x_io)
        cen_format = work_book.add_format({'align':'center'})
        merge_format = work_book.add_format({
            'bold': True,
            'align': 'center',  # 水平居中
            'valign': 'vcenter',  # 垂直居中
        })
        work_sheet = work_book.add_worksheet(name)
        work_sheet.write(0, 0, "姓名")
        work_sheet.write(0, 1, "登录密码")
        work_sheet.write(0, 2, "邮箱")
        work_sheet.write(0, 3, "职位")
        work_sheet.write(0, 4, "是否激活")
        work_sheet.write(0, 5, "公司编号")


        work_sheet.merge_range('J1:K1', '职位录入参考', merge_format)

        for i in range(len(office)):
            work_sheet.write(i+1, 9, i,cen_format)
            work_sheet.write(i+1, 10, office[i],cen_format)

        yu = models.Gongsi.objects.all().values("name", "myid")
        #print(yu)


        work_sheet.merge_range('J10:K10', '公司-编号参考', merge_format)


        for i in range(len(yu)):
            work_sheet.write(i + 11, 9, yu[i]['myid'], cen_format)
            work_sheet.write(i + 11, 10, yu[i]['name'], cen_format)

        work_sheet.set_column('J1:K1', 15)

        #work_sheet.data_validation("D2:D10", {'validate': 'list', 'source': office})
        #work_sheet.data_validation("E2:E10", {'validate': 'list', 'source': [0,1]})

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

        time_used = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        name = "mtTemp"
        ts = int(time.time())
        file_name = name + str(ts)+'.xlsx'

        x_io = BytesIO()
        work_book = xlsxwriter.Workbook(x_io)
        cen_format = work_book.add_format({'align':'center'})
        merge_format = work_book.add_format({
            'bold': True,
            'align': 'center',  # 水平居中
            'valign': 'vcenter',  # 垂直居中
        })
        work_sheet = work_book.add_worksheet(name)
        work_sheet.write(0, 0, "供应商编号",cen_format)
        work_sheet.write(0, 1, "物料编号",cen_format)


        work_sheet.merge_range('E1:G1', '供应商-编号参考', merge_format)
        yu = models.Gongyingshang.objects.all().values("id", "name","address")
        for i in range(len(yu)):
            work_sheet.write(i + 1, 4, yu[i]['id'], cen_format)
            work_sheet.write(i + 1, 5, yu[i]['name'], cen_format)
            work_sheet.write(i + 1, 6, yu[i]['address'], cen_format)

        work_sheet.merge_range('I1:K1', '物料-编号参考', merge_format)

        wu = models.Wuliao.objects.all().values("id", "type", "desc")
        for i in range(len(wu)):
            work_sheet.write(i + 1, 8, wu[i]['id'], cen_format)
            work_sheet.write(i + 1, 9, wu[i]['type'], cen_format)
            work_sheet.write(i + 1, 10, wu[i]['desc'], cen_format)

        work_sheet.set_column('A1:B1', 10)
        work_sheet.set_column('E1:G1', 11)
        work_sheet.set_column('I1:K1', 11)

        #work_sheet.data_validation("D2:D10", {'validate': 'list', 'source': office})
        #work_sheet.data_validation("E2:E10", {'validate': 'list', 'source': [0,1]})

        work_book.close()
        res = HttpResponse()
        res["Content-Type"] = "application/octet-stream"
        res["Content-Disposition"] = 'filename="'+file_name+'"'
        res.write(x_io.getvalue())

        return res



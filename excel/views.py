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
        work_sheet = work_book.add_worksheet(name)
        work_sheet.write(0, 0, "姓名")
        work_sheet.write(0, 1, "登录密码")
        work_sheet.write(0, 2, "邮箱")
        work_sheet.write(0, 3, "职位")
        work_sheet.write(0, 4, "是否激活")
        work_sheet.write(0, 5, "公司编号")

        work_sheet.data_validation("D2:D10", {'validate': 'list', 'source': office})
        work_sheet.data_validation("E2:E10", {'validate': 'list', 'source': [0,1]})
        work_book.close()
        res = HttpResponse()
        res["Content-Type"] = "application/octet-stream"
        res["Content-Disposition"] = 'filename="'+file_name+'"'
        res.write(x_io.getvalue())

        return res
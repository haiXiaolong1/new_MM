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


# ex:/assetinfo/test_django_excel_upload
class TestDjangoExcelUpload(View):
    """测试使用django-excel上传文件"""

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
# ex:/assetinfo/test_django_excel_download
class TestDjangoExcelDownload(View):
    """测试使用django-excel下载文件"""

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

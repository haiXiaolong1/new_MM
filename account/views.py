from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
# Create your views here.
from supply import models
from supply.views import form_check, all_message_by_user
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
def ac_list(request):
    yu=models.Yuangong.objects.exclude(office="7").all()
    gs=models.Gongsi.objects.all()
    return render(request,'account.html',{"queryset":yu,"gongsi":gs,"title":"员工列表"})
# 添加用户
def ac_add(request):
    n=10000
    if models.Yuangong.objects.first():
        n=models.Yuangong.objects.all().order_by('-id').first().id[1:]
    num = str(int(n)+1)#编号递增，这样计算避免删除后出现错误
    cal = 4 - len(num)
    sid="e"+ "0"*cal +num
    o=request.POST
    isactive = o['isactive']
    bid=o["businessid_id"]
    toCheck = [o['username'], o['password'],o['email'],bid]
    types = ['nan', 'nan','nan','nan']
    res = form_check(toCheck, types)
    notify=[]
    if not validateEmail(o['email']):
        res["error"][2]="请输入正确的邮箱"
        res["status"]=False
    if res["status"]:
        models.Yuangong.objects.create(office=o['office'],username=o['username'],password=o['password'],email=o['email']
                                        ,id=sid,isactive=isactive,businessid_id=bid)
        notify.append(dict(id=0, tittle="提示", context="员工 {} 创建成功".format(sid), type="success", position="top-center"))
        request.session["notify"] = notify
    return JsonResponse(res)
# 编辑用户时返回用户原始数据
def ac_detail(request):
    id=request.GET.get("uid")
    ac=models.Yuangong.objects.filter(id=id).values("office",'password','username',"email","isactive","businessid_id").first()
    if not ac:
        return JsonResponse({"status":False,"error":"数据不存在"})

    return JsonResponse({"account":ac,"status":True})

# 保存编辑用户的最新数据
def ac_edit(request):
    id=request.GET.get("uid")
    o=request.POST
    notify=[]
    isactive = o['isactive']
    bid=o["businessid_id"]
    toCheck = [o['username'], o['password'],o['email'],bid]
    types = ['nan', 'nan','nan','nan']
    res = form_check(toCheck, types)
    if not validateEmail(o['email']):
        res["error"][2]="请输入正确的邮箱"
        res["status"]=False
    if res["status"]:
        models.Yuangong.objects.filter(id=id).update(office=o['office'],username=o['username'],password=o['password'],email=o['email']
                                                 ,isactive=isactive,businessid=o['businessid_id'])
        notify.append(dict(id=0, tittle="提示", context="员工 {} 编辑成功".format(id), type="success", position="top-center"))
        request.session["notify"] = notify
    return JsonResponse(res)

# 删除用户
@csrf_exempt
def ac_delete(request):
    id=request.POST.get("uid")
    notify=[]
    gc=models.Gongyingshang.objects.filter(createnumberid_id=id).first()
    gu=models.Gongyingshang.objects.filter(updatenumberid_id=id).first()
    cc=models.Caigouxuqiu.objects.filter(createuserid_id=id).first()
    cu=models.Caigouxuqiu.objects.filter(verifyuserid_id=id).first()
    xj=models.Xunjiadan.objects.filter(createuserid_id=id).first()
    cg=models.Caigoudan.objects.filter(createuserid_id=id).first()
    if gc or gu or cc or cu or xj or cg:
        notify.append(dict(id=0, tittle="提示", context="员工 {} 有关联的供应商或待处理订单，不能删除".format(id), type="error", position="top-center"))
        request.session["notify"] = notify
        return JsonResponse({"status":False})
    notify.append(dict(id=0, tittle="提示", context="员工 {} 删除成功".format(id), type="success", position="top-center"))
    request.session["notify"] = notify
    models.Yuangong.objects.filter(id=id).delete()
    return JsonResponse({"status":True})


def ac_password(request):

    return render(request,'password.html')

from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header
import random
import re


def validateEmail(email):
    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
        return True
    else:
        return False

data = {
    'sender':"3425053441@qq.com", # 发送者邮箱，自己用可写死
    'password':"vbgejeqczrszcjfh", # 在开启SMTP服务后，可以生成授权码，此处为授权码
    'subject':"NEW MM验证码", # 邮件主题名，没有违规文字都行
}
class SendEmail:
    def __init__(self, data,receiver):
        self.sender = data.get('sender','3425053441@qq.com') # 发送者QQ邮箱
        self.receiver = receiver # 接收者邮箱
        self.password = data.get('password','vbgejeqczrszcjfh')
        self.subject = data.get('subject','NEWMM验证码')

    def load_message(self):
        verification_code = self.generate_verification()
        text = f'验证码为：{verification_code}'
        message = MIMEText(text, "plain", "utf-8") # 文本内容，文本格式，编码
        message["Subject"] = Header(self.subject, "utf-8") # 邮箱主题
        message["From"] = Header(self.sender, "utf-8") # 发送者
        message["To"] = Header(self.receiver, "utf-8") # 接收者
        return message,verification_code

    def send_email(self):
        message,verification_code = self.load_message()
        smtp = SMTP_SSL("smtp.qq.com")  #需要发送者QQ邮箱开启SMTP服务
        smtp.login(self.sender, self.password)
        smtp.sendmail(self.sender, self.receiver, message.as_string())
        return verification_code

    # 生成6位随机数验证码
    def generate_verification(self):
        random_list = list(map(lambda x:random.randint(0,9),[y for y in range(6)])) # 这里使用map函数跟lambda匿名函数来生成随机的六位数
        code = "".join('%s' % i for i in random_list)
        return code
def ac_send(request):
    # 发送邮箱验证码
    error=["",""]
    id=request.POST.get("username")
    y=models.Yuangong.objects.filter(id=id).first()
    if not y:
        error[0]="请输入正确的员工号"
        return JsonResponse({"status":False,"errors":error})
    email=request.POST.get("email")
    if str(email).strip()=="":
        error[1]="请输入邮箱"
        return JsonResponse({"status":False,"errors":error})
    if not validateEmail(email):
        error[1]="请输入正确的邮箱"
        return JsonResponse({"status":False,"errors":error})
    if email!=y.email:
        error[1]="请输入对应员工编号的邮箱"
        return JsonResponse({"status":False,"errors":error})
    verification = SendEmail(data=data,receiver=email).send_email()
    request.session['valid']=verification
    return JsonResponse({"status":True})

def ac_login(request):
    error=["","","",""]
    va=request.session.get("valid")
    id=request.POST.get("username")
    valid=request.POST.get("valid")
    password=request.POST.get("password")
    y=models.Yuangong.objects.filter(id=id).first()
    if not y:
        error[0]="请输入正确的员工号"
        return JsonResponse({"status":False,"errors":error})
    email=request.POST.get("email")
    if str(email).strip()=="":
        error[1]="请输入邮箱"
        return JsonResponse({"status":False,"errors":error})
    if not validateEmail(email):
        error[1]="请输入正确的邮箱"
        return JsonResponse({"status":False,"errors":error})
    if email!=y.email:
        error[1]="请输入对应员工编号的邮箱"
        return JsonResponse({"status":False,"errors":error})
    if not valid :
        error[2]="请输入邮箱验证码"
        return JsonResponse({"status":False,"errors":error})
    if not password:
        error[3]="请输入新密码"
        return JsonResponse({"status":False,"errors":error})
    if valid!=va :
        error[2]="邮箱验证码不正确"
        return JsonResponse({"status":False,"errors":error})
    models.Yuangong.objects.filter(id=id).update(password=password)
    ins=models.Yuangong.objects.filter(id=id).first()
    request.session.pop("valid")
    request.session["info"] = {"name": ins.username, "id": ins.id
        , "office": ins.office, "business": ins.businessid.name, "officename": ins.get_office_display()}
    request.session["messageFlow"] = all_message_by_user(None, ins.id)
    request.session['produceActive']=True #控制是否向生产经理抄送操作记录
    return JsonResponse({"status": True})

# 修改个人信息（密保等）
def r_massage(request):
    if request.method == "GET":
        sq = models.Securityquestion.objects.all()
        return render(request, 'r_massage.html', locals())
    else:
        name = request.POST.get("name")
        sq = request.POST.get("sq")
        verification = request.POST.get("verification")
        models.Yuangong.objects.filter(id=request.session['info']['id']).update(username=name, question=sq,
                                                                                verification=verification)
        # 更新session
        request.session['info']['name'], request.session['info']['verification'], request.session['info'][
            'question'] = name, verification, sq
        messages.success(request, "修改成功！", locals())
        return redirect('/account/ac/r_massage/')


# 修改密码
def r_password(request):
    if request.method == "GET":
        return render(request, 'r_password.html', locals())
    else:
        old_password = request.POST.get("old_password")
        new1_password = request.POST.get("new1_password")
        new2_password = request.POST.get("new2_password")
        old_pass = models.Yuangong.objects.filter(id=request.session['info']['id']).values()[0]['password']
        if old_pass == old_password:
            if new1_password == new2_password:
                models.Yuangong.objects.filter(id=request.session['info']['id']).update(password=new1_password)
                messages.success(request, "修改成功！", locals())
                return redirect('/account/ac/r_password/')
            else:
                messages.success(request, "两次新密码不一致！", locals())
                return redirect('/account/ac/r_password/')
        else:
            messages.success(request, "原密码错误！", locals())
            return redirect('/account/ac/r_password/')

def ac_excel(request):
    if request.method == "GET":
        return render(request, 'accountexcel.html')


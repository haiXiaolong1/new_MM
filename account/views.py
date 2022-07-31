from django.shortcuts import render,HttpResponse

# Create your views here.
from supply import models
from supply.views import form_check, all_message_by_user
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
def ac_list(request):
    yu=models.Yuangong.objects.all()
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
    issuper = 0
    bid=o["businessid_id"]
    toCheck = [o['username'], o['password'],o['email'],bid]
    types = ['nan', 'nan','nan','nan']
    res = form_check(toCheck, types)
    if not validateEmail(o['email']):
        res["error"][2]="请输入正确的邮箱"
        res["status"]=False

    if res["status"]:
        models.Yuangong.objects.create(office=o['office'],username=o['username'],password=o['password'],email=o['email']
                                        ,id=sid,isactive=isactive,issuper=issuper,businessid_id=bid)
    return JsonResponse(res)
# 编辑用户时返回用户原始数据
def ac_detail(request):
    id=request.GET.get("uid")
    ac=models.Yuangong.objects.filter(id=id).values("office",'password','username',"email","isactive","issuper","businessid_id").first()
    if not ac:
        return JsonResponse({"status":False,"error":"数据不存在"})
    return JsonResponse({"account":ac,"status":True})

# 保存编辑用户的最新数据
def ac_edit(request):
    id=request.GET.get("uid")
    o=request.POST
    isactive = o['isactive']
    issuper = 0
    bid=o["businessid_id"]
    toCheck = [o['username'], o['password'],o['email'],bid]
    types = ['nan', 'nan','nan','nan']
    res = form_check(toCheck, types)
    if not validateEmail(o['email']):
        res["error"][2]="请输入正确的邮箱"
        res["status"]=False
    if res["status"]:
        models.Yuangong.objects.filter(id=id).update(office=o['office'],username=o['username'],password=o['password'],email=o['email']
                                                 ,isactive=isactive,issuper=issuper,businessid=o['businessid_id'])

    return JsonResponse(res)

# 删除用户
@csrf_exempt
def ac_delete(request):
    id=request.POST.get("uid")
    gc=models.Gongyingshang.objects.filter(createnumberid_id=id).first()
    gu=models.Gongyingshang.objects.filter(updatenumberid_id=id).first()
    cc=models.Caigouxuqiu.objects.filter(createuserid_id=id).first()
    cu=models.Caigouxuqiu.objects.filter(verifyuserid_id=id).first()
    if gc or gu or cc or cu :
        return JsonResponse({"status":False})
    print(id)
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
    'sender':"2393226759@qq.com", # 发送者邮箱，自己用可写死
    'password':"gnpdimapluwcebja", # 在开启SMTP服务后，可以生成授权码，此处为授权码
    'subject':"NEW MM验证码", # 邮件主题名，没有违规文字都行
}
class SendEmail:
    def __init__(self, data,receiver):
        self.sender = data.get('sender','2393226759@qq.com') # 发送者QQ邮箱
        self.receiver = receiver # 接收者邮箱
        self.password = data.get('password','gnpdimapluwcebja')
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
    va=request.session['valid']
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
    request.session["info"] = {"name": ins.username, "id": ins.id, "issuper": ins.issuper
        , "office": ins.office, "business": ins.businessid.name, "officename": ins.get_office_display()}
    request.session["messageFlow"] = all_message_by_user(None, ins.id)
    return JsonResponse({"status": True})

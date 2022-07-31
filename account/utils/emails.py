from django.test import TestCase

# Create your tests here.
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header
import random

data = {
    'sender':"2393226759@qq.com", # 发送者邮箱，自己用可写死
    'password':"gnpdimapluwcebja", # 在开启SMTP服务后，可以生成授权码，此处为授权码
    'subject':"xxx验证码", # 邮件主题名，没有违规文字都行
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

#调用
#receiver里放上发送对象的邮箱
# verification = SendEmail(data=data,receiver='3312317207@qq.com').send_email()
# print(verification)


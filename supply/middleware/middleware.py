
from django.shortcuts import redirect
from django.utils.deprecation import  MiddlewareMixin
import re
class AuthMW(MiddlewareMixin):
    # 通过自定义中间件进行登录认证

    def process_request(self,request):
        if request.path_info == "/login/" or request.path_info == "/account/ac/password/" or \
                request.path_info == "/account/ac/send/" or request.path_info == "/account/ac/login/":
            return
        if re.match("^(/admin)(.)*",request.path_info):
            return
        if re.match("^(/favicon.ico)(.)*",request.path_info):
            return
        if request.path_info == "/forgot/":
            return
        if request.path_info == "/supply/r_password/":
            return
        if request.path_info == "/initial/":
            return
        if request.path_info == "/guide/":
            return
        if not request.session.get("info"):
            return redirect('/initial/')

        return
